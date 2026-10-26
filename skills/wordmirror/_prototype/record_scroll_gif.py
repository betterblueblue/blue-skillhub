# -*- coding: utf-8 -*-
"""给 ai_eyes_demo.html 录一段滚动 GIF：按各幕分配时长匀速下滚，逐帧截图后拼 GIF。
用法：python record_scroll_gif.py
产物：shots/scroll_story.gif（不进 git 的图片放 shots/ 下，规则同其他截图）
"""
import io, os, sys, urllib.request

from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, 'ai_eyes_demo.html')
OUT = os.path.join(HERE, 'shots', 'scroll_story.gif')

INDEX = '--index' in sys.argv   # 录 demo_home 里的 index.html（六节报告页）
MP4 = '--mp4' in sys.argv       # 出 mp4 而非 gif

VIEW_W, VIEW_H = 1280, 800      # 录制视口；--vertical 竖屏（手机端布局），mp4 横屏给 1080p
if '--vertical' in sys.argv:
    VIEW_W, VIEW_H = 720, 1280
elif MP4:
    VIEW_W, VIEW_H = 1920, 1080
GIF_W = VIEW_W                  # 原始帧不缩，体积交给 ffmpeg 调色板控制
FPS = 12                        # 输出帧率
if MP4:
    OUT = os.path.join(HERE, 'shots', 'index_story.mp4' if INDEX else 'scroll_story.mp4')

# 每幕（section id, 分配秒数）：钉住的戏全靠滚动进度驱动，秒数就是那一幕的播放时长
SCENES = [('hero', 8.0), ('#sec-portrait', 2.0), ('#sec-lines', 2.4), ('#sec-promises', 2.0),
          ('#sec-insights', 2.2), ('#sec-ai-eyes', 2.0), ('#sec-wrapped', 2.6)] if INDEX else \
         [('#s-mirror', 5.0), ('#s-phone', 4.5), ('#s-chat', 5.5), ('#s-wall', 4.0)]
HEAD_DWELL = 1.0                # 片头停在全雾镜面上的时间
TAIL_DWELL = 2.0                # 片尾停住，循环回放不突兀


def serve(root=None):
    import http.server, functools, threading
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root or HERE)
    srv = http.server.HTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def live_segments(page):
    """录屏模式：每段 (起 scrollY, 止 scrollY, 秒数)，滚动交给页面 rAF 连续驱动。"""
    secs = []
    for sel, _ in SCENES:
        el = page.locator('.story' if sel == 'hero' else sel)
        if not el.count():
            continue
        top = el.evaluate('e => e.getBoundingClientRect().top + scrollY')
        secs.append((top, el.bounding_box()['height'], sel == 'hero'))
    segs, pos = [(0, 0, HEAD_DWELL)], 0
    for (top, h, pinned), (_, dur) in zip(secs, SCENES):
        end = top + h - VIEW_H if pinned else \
            min(top - 24, page.evaluate('document.documentElement.scrollHeight') - VIEW_H)
        end = max(end, pos)
        segs.append((pos, end, dur)); pos = end
    segs.append((pos, pos, TAIL_DWELL))
    return segs


SCROLL_JS = """segs => (async () => {
  for (const [a, b, d] of segs) {
    const t0 = performance.now();
    while (true) {
      const k = Math.min(1, (performance.now() - t0) / 1000 / d);
      scrollTo(0, a + (b - a) * k);
      if (k >= 1) break;
      await new Promise(r => requestAnimationFrame(r));
    }
  }
})()"""


def frame_positions(page):
    """每帧一个 scrollY：先片头停顿，再按各幕秒数匀速切分滚动距离。
    index 模式下 'hero' 指 .story 钉住区，其余 section 只滚到顶部对齐。"""
    secs = []
    for sel, _ in SCENES:
        if sel == 'hero':
            el = page.locator('.story')
        else:
            el = page.locator(sel)
        if not el.count():
            continue
        top = el.evaluate('e => e.getBoundingClientRect().top + scrollY')
        secs.append((top, el.bounding_box()['height'], sel == 'hero'))
    pos = [0] * int(HEAD_DWELL * FPS)
    for i, ((top, h, pinned), (_, dur)) in enumerate(zip(secs, SCENES)):
        start = pos[-1] if pos else 0
        if pinned:
            end = top + h - VIEW_H                       # 钉住区滚完整段行程
        else:
            end = min(top - 24, page.evaluate('document.documentElement.scrollHeight') - VIEW_H)
            end = max(end, start)
        n = max(2, int(dur * FPS))
        pos += [start + (end - start) * k / n for k in range(1, n + 1)]
    pos += [pos[-1]] * int(TAIL_DWELL * FPS)
    return [int(p) for p in pos]


def main():
    if INDEX:
        root = os.path.join(HERE, 'demo_home', 'products', 'html')
        if not os.path.exists(os.path.join(root, 'index.html')):
            sys.exit('没有演示 index，先跑 build_index_demo.py')
    elif not os.path.exists(DEMO):
        sys.exit('没有 %s，先跑 build_ai_eyes_proto.py --demo' % DEMO)
    srv = serve(os.path.join(HERE, 'demo_home', 'products', 'html') if INDEX else HERE)
    url = 'http://127.0.0.1:%d/index.html' % srv.server_address[1] if INDEX else \
          'http://127.0.0.1:%d/ai_eyes_demo.html' % srv.server_address[1]
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        if MP4:
            # 原生录屏：Chromium 合成器直接出 ~25fps webm，滚动由 rAF 驱动，真平滑
            import subprocess, glob, time
            vdir = os.path.join(HERE, 'shots', '_rec')
            os.makedirs(vdir, exist_ok=True)
            t_ctx = time.time()
            ctx = browser.new_context(viewport={'width': VIEW_W, 'height': VIEW_H},
                                      record_video_dir=vdir,
                                      record_video_size={'width': VIEW_W, 'height': VIEW_H})
            page = ctx.new_page()
            page.goto(url)
            page.add_style_tag(content='html{scroll-behavior:auto!important}')
            page.wait_for_timeout(2500)
            segs = live_segments(page)
            total = sum(d for _, _, d in segs)
            t_scroll = time.time()            # 滚动起点墙钟 → 换算 webm 内偏移剪掉片头
            page.evaluate(SCROLL_JS, segs)
            page.wait_for_timeout(400)
            ctx.close()                       # 关 context 才落盘
            browser.close()
            webm = sorted(glob.glob(os.path.join(vdir, '*.webm')),
                          key=os.path.getmtime)[-1]
            off = max(0.0, t_scroll - t_ctx - 0.3)
            subprocess.run(['ffmpeg', '-y', '-ss', '%.2f' % off, '-i', webm,
                            '-vf', 'fps=30', '-c:v', 'libx264', '-crf', '19',
                            '-preset', 'slow', '-pix_fmt', 'yuv420p',
                            '-movflags', '+faststart', OUT],
                           check=True, capture_output=True)
            print('录屏完成 %.1fs → %s' % (total, OUT))
            return
        page = browser.new_page(viewport={'width': VIEW_W, 'height': VIEW_H})
        page.goto(url)
        page.add_style_tag(content='html{scroll-behavior:auto!important}')  # 关掉平滑滚动，否则每帧都在半路
        page.wait_for_timeout(2500)      # 等字体和画布
        ys = frame_positions(page)
        frames = []
        for i, y in enumerate(ys):
            # scrollTo 后等两个 rAF：钉住舞台的位移是 rAF 驱动的，等它应用完再截，不然帧间上下跳
            page.evaluate('y => new Promise(r => {scrollTo(0, y);'
                          ' requestAnimationFrame(() => requestAnimationFrame(r))})', y)
            png = page.screenshot(type='png')
            img = Image.open(io.BytesIO(png)).convert('RGB')
            img = img.resize((GIF_W, int(GIF_W * VIEW_H / VIEW_W)), Image.LANCZOS)
            frames.append(img)
            if i % 20 == 0:
                print('帧 %d/%d' % (i + 1, len(ys)))
        if MP4:
            tmp = os.path.join(HERE, 'shots', '_frames')
            os.makedirs(tmp, exist_ok=True)
            for i, f in enumerate(frames):
                f.save(os.path.join(tmp, '%04d.png' % i))
            import subprocess, shutil
            subprocess.run(['ffmpeg', '-y', '-framerate', str(FPS), '-i', os.path.join(tmp, '%04d.png'),
                            '-c:v', 'libx264', '-crf', '21', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                            OUT], check=True)
            shutil.rmtree(tmp)
        else:
            frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=1000 // FPS,
                           loop=0, optimize=True)
        page.close()
    srv.shutdown()
    print('写好了 %s（%d 帧，%.1f KB）' % (OUT, len(frames), os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    main()
