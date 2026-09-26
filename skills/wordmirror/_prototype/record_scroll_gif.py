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

VIEW_W, VIEW_H = 1280, 800      # 录制视口
GIF_W = VIEW_W                  # 原始帧不缩，体积交给 ffmpeg 调色板控制
FPS = 12                        # 输出帧率

# 每幕（section id, 分配秒数）：钉住的戏全靠滚动进度驱动，秒数就是那一幕的播放时长
SCENES = [('#s-mirror', 5.0), ('#s-phone', 4.5), ('#s-chat', 5.5), ('#s-wall', 4.0)]
HEAD_DWELL = 1.0                # 片头停在全雾镜面上的时间
TAIL_DWELL = 2.0                # 片尾停住，循环回放不突兀


def serve():
    import http.server, functools, threading
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    srv = http.server.HTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def frame_positions(page):
    """每帧一个 scrollY：先片头停顿，再按各幕秒数匀速切分滚动距离。"""
    secs = []
    for sel, _ in SCENES:
        loc = page.locator(sel)
        box = loc.bounding_box()
        top = loc.evaluate('el => el.getBoundingClientRect().top + scrollY')
        secs.append((top, box['height']))
    pos = [0] * int(HEAD_DWELL * FPS)
    for i, ((top, h), (_, dur)) in enumerate(zip(secs, SCENES)):
        start = pos[-1] if pos else 0
        end = top + h - VIEW_H if i < len(SCENES) - 1 else page.evaluate(
            'document.documentElement.scrollHeight') - VIEW_H
        n = int(dur * FPS)
        pos += [start + (end - start) * k / n for k in range(1, n + 1)]
    pos += [pos[-1]] * int(TAIL_DWELL * FPS)
    return [int(p) for p in pos]


def main():
    if not os.path.exists(DEMO):
        sys.exit('没有 %s，先跑 build_ai_eyes_proto.py --demo' % DEMO)
    srv = serve()
    url = 'http://127.0.0.1:%d/ai_eyes_demo.html' % srv.server_address[1]
    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page(viewport={'width': VIEW_W, 'height': VIEW_H})
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
        frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=1000 // FPS,
                       loop=0, optimize=True)
        page.close()
    srv.shutdown()
    print('写好了 %s（%d 帧，%.1f KB）' % (OUT, len(frames), os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    main()
