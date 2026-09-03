# -*- coding: utf-8 -*-
"""wm init 的核心：agent 存档探测器。
零硬编码绝对路径——只用"路径模式表"探测本机有哪些 agent 的会话存档。
支持新 agent = 在 AGENT_PATTERNS 加一行，不改代码。

用法（产品化后）：python scripts/detect_agents.py
输出：探测报告（哪些 agent 找到了、多少文件、哪些没找到）
"""
import os, glob, sqlite3

HOME = os.path.expanduser('~')

# 探测表：agent 名 → 候选路径模式（相对 HOME）+ 识别方式
AGENT_PATTERNS = {
    'codex': {
        'patterns': ['.codex/sessions/*/*/*/*.jsonl'],
        'kind': 'jsonl', 'how': '按年/月/日分层的 rollout 文件',
    },
    'claude-code': {
        'patterns': ['.claude/history.jsonl', '.claude/projects/*/*.jsonl'],
        'kind': 'jsonl', 'how': 'history.jsonl 主历史 + 按项目分目录的会话文件',
    },
    'qwen': {
        'patterns': ['.qwen/projects/*/chats/*.jsonl'],
        'kind': 'jsonl', 'how': '按项目的 chats 目录',
    },
    'workbuddy': {
        'patterns': ['.workbuddy/projects/*/*.jsonl'],
        'kind': 'jsonl', 'how': '按项目的会话文件',
    },
    'pi': {
        'patterns': ['.pi/agent/sessions/*/*.jsonl'],
        'kind': 'jsonl', 'how': '按项目的 session 文件',
    },
    'atomcode': {
        'patterns': ['.atomcode/datalog/*/*.jsonl'],
        'kind': 'jsonl', 'how': 'datalog 目录',
    },
    'antigravity': {
        'patterns': ['.gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl'],
        'kind': 'jsonl', 'how': 'brain transcript（conversations/*.db 是 protobuf，不用）',
    },
    'zcode': {
        'patterns': ['.zcode/cli/db/db.sqlite'],
        'kind': 'sqlite', 'how': 'SQLite（session/message/part 三表）',
    },
    'grok': {
        'patterns': ['.grok/logs/unified.jsonl'],
        'kind': 'none', 'how': '只有运行日志无对话正文——找到了也不采',
    },
    'cursor': {
        'patterns': ['AppData/Roaming/Cursor/User/globalStorage/state.vscdb',
                     'AppData/Roaming/Cursor/User/workspaceStorage/*/state.vscdb'],
        'kind': 'sqlite', 'how': 'state.vscdb 的 cursorDiskKV 表（bubbleId 气泡，richText 正文）',
    },
    'catpaw': {
        'patterns': ['.catpaw/projects/*/*/agent-transcripts/transcript.txt'],
        'kind': 'txt', 'how': 'IDE 版会话 transcript（user:/assistant: 纯文本，日期取文件 mtime）',
    },
    'dsh': {
        'patterns': ['.dsh/sessions/*/*/session.jsonl.zstd'],
        'kind': 'zstd', 'how': 'DeepSeek Harness 会话（zstd jsonl，user/message 事件，需 zstandard）',
    },
}

def detect():
    report = []
    for agent, cfg in AGENT_PATTERNS.items():
        found = []
        for pat in cfg['patterns']:
            found += [f for f in glob.glob(os.path.join(HOME, pat)) if os.path.isfile(f)]
        if found:
            total = sum(os.path.getsize(f) for f in found)
            report.append((agent, len(found), total, cfg['kind'], cfg['how']))
        else:
            report.append((agent, 0, 0, cfg['kind'], cfg['how']))
    return report

if __name__ == '__main__':
    print('wm init · 探测你机器上的 agent 存档')
    print('=' * 62)
    n_ok = 0
    for agent, n, size, kind, how in detect():
        if n > 0:
            n_ok += 1
            size_h = '%.1f MB' % (size / 1048576) if size >= 1048576 else '%d KB' % (size // 1024)
            print(' ✓ %-13s %4d 个文件  %8s   (%s)' % (agent, n, size_h, how))
        else:
            note = '没找到，跳过' if kind != 'none' else '本机无正文，跳过'
            print(' - %-13s %s' % (agent, note))
    print('=' * 62)
    print('可采集 agent: %d 个。' % n_ok)
