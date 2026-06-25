#!/usr/bin/env python3
"""验证 6 个 cell 的关键源码文件是否完整。"""
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "eval", "runs", "blind-2026-06-25-v5")
CELLS = ["C1", "C2", "C3", "C4", "C5", "C6"]

CHECKS = [
    ("test-projects/prisma-express-ts/prisma/schema.prisma", "B3/B6"),
    ("test-projects/prisma-express-ts/src/controllers/auth.controller.ts", "B6"),
    ("test-projects/prisma-express-ts/src/services/auth.service.ts", "B6"),
    ("test-projects/prisma-express-ts/src/middlewares/auth.ts", "B6"),
    ("test-projects/ruoyi-vue/ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java", "B2"),
    ("test-projects/ruoyi-vue/ruoyi-framework/src/main/java/com/ruoyi/framework/aspectj/LogAspect.java", "B1"),
]

all_ok = True
for cell in CELLS:
    cell_root = os.path.join(ROOT, f"cell-{cell}")
    missing = []
    for rel, case in CHECKS:
        full = os.path.join(cell_root, rel)
        if not os.path.exists(full):
            missing.append(f"  {case}: {rel}")
    if missing:
        all_ok = False
        print(f"cell-{cell}: MISSING")
        for m in missing:
            print(m)
    else:
        print(f"cell-{cell}: OK (all {len(CHECKS)} key files present)")

# Also check no change-impact residue
for cell in CELLS:
    for proj in ["prisma-express-ts", "ruoyi-vue"]:
        ci = os.path.join(ROOT, f"cell-{cell}", "test-projects", proj, "change-impact")
        if os.path.exists(ci):
            print(f"  WARNING: change-impact residue in cell-{cell}/{proj}")

print()
print("Result:", "ALL OK" if all_ok else "HAS MISSING FILES")
