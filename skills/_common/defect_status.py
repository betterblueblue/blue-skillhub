#!/usr/bin/env python3
"""缺陷状态判定——intent-adversarial（A5）和 intent-verify（V10）两个交付门禁共用。

判定规则（宁可误拦，不可放行）：
  - 状态列写成状态流转时（如 `open→fixed(复验 3/3)`），只看最后一个状态。
  - 最后一个状态以 `fixed` 或 `已修复` 开头才算已关闭（大小写不敏感，忽略首尾的 ` 和 *）。
  - 其余一律按未关闭处理，包括 open、unfixed、not fixed、未修复、修复中、空白。

历史：两处门禁原来用 `"fixed" not in status.lower()` 子串判断，
`unfixed`、`not fixed` 会被当成已修复放行，`已修复` 反而被拦。
"""

from __future__ import annotations

import re

_TRANSITION_RE = re.compile(r"→|->|=>")
_CLOSED_PREFIXES = ("fixed", "已修复")


def defect_is_closed(status: str) -> bool:
    """缺陷状态是否为已关闭（已修复）。"""
    final = _TRANSITION_RE.split(status or "")[-1]
    final = final.strip().strip("`*").strip().lower()
    return final.startswith(_CLOSED_PREFIXES)
