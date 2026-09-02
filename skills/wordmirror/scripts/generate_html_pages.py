# -*- coding: utf-8 -*-
"""薄壳：委托 skill 自带渲染器（scripts/render.py）一次出全所有 HTML。
用法：python scripts/generate_html_pages.py
"""
import os, sys, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rp = os.path.join(BASE, 'scripts', 'render.py')
sys.exit(subprocess.run([sys.executable, rp, 'all']).returncode)
