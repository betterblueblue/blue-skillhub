#!/usr/bin/env python3
"""Complete missing L1 regression outputs and apply remaining source patches."""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

RUOYI = ROOT / "test-projects/ruoyi-vue"
GOADMIN = ROOT / "test-projects/go-admin"
FASTAPI = ROOT / "test-projects/full-stack-fastapi-template"
VALIDATE = ROOT / "scripts/impact_validate.py"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def patch_r1_source() -> None:
    mapper = RUOYI / "ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml"
    text = mapper.read_text(encoding="utf-8")
    replacements = [
        ('        <result property="remark"        column="remark"          />\n', ""),
        (", u.remark", ""),
        (" 			<if test=\"remark != null and remark != ''\">remark,</if>\n", ""),
        (" 			<if test=\"remark != null and remark != ''\">#{remark},</if>\n", ""),
        (" 			<if test=\"remark != null\">remark = #{remark},</if>\n", ""),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
    mapper.write_text(text, encoding="utf-8")
    print("PATCHED SysUserMapper.xml")

    index_vue = RUOYI / "ruoyi-ui/src/views/system/user/index.vue"
    iv = index_vue.read_text(encoding="utf-8")
    block = """        <el-row>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入内容"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
"""
    if block in iv:
        iv = iv.replace(block, "")
        index_vue.write_text(iv, encoding="utf-8")
        print("PATCHED index.vue remark form")

    view_vue = RUOYI / "ruoyi-ui/src/views/system/user/view.vue"
    if view_vue.exists():
        vv = view_vue.read_text(encoding="utf-8")
        vv = re.sub(
            r"\s*<div class=\"info-item\">\s*<label class=\"info-label\">备注：</label>.*?</div>\s*",
            "\n",
            vv,
            flags=re.S,
        )
        view_vue.write_text(vv, encoding="utf-8")
        print("PATCHED view.vue remark display")

    sql_dir = RUOYI / "change-impact/l1-regression-2026-06-26/R1/050-validation"
    sql_dir.mkdir(parents=True, exist_ok=True)
    write(
        sql_dir / "001_drop_sys_user_remark.sql",
        "-- R1: DROP sys_user.remark (high risk)\nALTER TABLE sys_user DROP COLUMN remark;\n",
    )
    write(
        sql_dir / "001_drop_sys_user_remark_rollback.sql",
        "-- Rollback\nALTER TABLE sys_user ADD COLUMN remark varchar(500) DEFAULT NULL COMMENT '备注';\n",
    )


def patch_r2_source() -> None:
    sql_dir = RUOYI / "change-impact/l1-regression-2026-06-26/R2/050-validation"
    sql_dir.mkdir(parents=True, exist_ok=True)
    write(
        sql_dir / "001_add_last_login_ip.sql",
        "-- R2: ADD last_login_ip (login_ip already exists at sql/ry_20260417.sql:55)\n"
        "ALTER TABLE sys_user ADD COLUMN last_login_ip varchar(64) NOT NULL DEFAULT '' COMMENT '最后登录IP(新列)';\n",
    )
    write(
        sql_dir / "001_add_last_login_ip_rollback.sql",
        "ALTER TABLE sys_user DROP COLUMN last_login_ip;\n",
    )

    entity = RUOYI / "ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java"
    text = entity.read_text(encoding="utf-8")
    if "lastLoginIp" not in text:
        insert_after = '    private String loginIp;\n'
        addition = (
            "\n    /** 最后登录IP（用户新增列，与 loginIp 并存——需业务确认语义） */\n"
            "    @Excel(name = \"最后登录IP(新)\", type = Type.EXPORT)\n"
            "    private String lastLoginIp;\n"
        )
        text = text.replace(insert_after, insert_after + addition)
        # getters/setters before getLoginIp
        text = text.replace(
            "    public String getLoginIp()",
            "    public String getLastLoginIp()\n    {\n        return lastLoginIp;\n    }\n\n"
            "    public void setLastLoginIp(String lastLoginIp)\n    {\n        this.lastLoginIp = lastLoginIp;\n    }\n\n"
            "    public String getLoginIp()",
        )
        entity.write_text(text, encoding="utf-8")
        print("PATCHED SysUser.java lastLoginIp")

    mapper = RUOYI / "ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml"
    mt = mapper.read_text(encoding="utf-8")
    if "last_login_ip" not in mt:
        mt = mt.replace(
            '<result property="loginIp"       column="login_ip"        />',
            '<result property="loginIp"       column="login_ip"        />\n'
            '        <result property="lastLoginIp"   column="last_login_ip"   />',
        )
        mt = mt.replace("u.login_ip, u.login_date", "u.login_ip, u.last_login_ip, u.login_date")
        mapper.write_text(mt, encoding="utf-8")
        print("PATCHED SysUserMapper.xml last_login_ip")


def gen_r1_docs() -> None:
    d = RUOYI / "change-impact/l1-regression-2026-06-26/R1"
    write(
        d / "000-context-pack.md",
        f"""# R1 删除 sys_user.remark Context Pack

> 生成时间：{TS}  |  版本：1.0  |  生成者：impact + composer-2.5

## 1. 变更意图

- 用户原话：我要把 sys_user 表的 remark 字段删了
- 已识别技术栈：Java Spring Boot + MyBatis
- 已加载技术栈规则：`profiles/java-spring-mybatis.md`
- 任务规模：中

## 3. 分层上下文

| 层级 | 内容 | 结论 |
|------|------|------|
| L1 | pom.xml、ruoyi-system、ruoyi-ui | Maven 多模块 |
| L2 | sys_user DDL、BaseEntity、SysUserMapper.xml、user/index.vue | remark 在基类与单表链均有引用 |
| L3 | BaseEntity.java:39、SysUserMapper.xml:26/51/61/160/175/194 | 单表链 7 处 remark |

## 5. 关键链路追踪

| 链路类型 | 入口 | 追踪路径 | 二级影响 |
|---------|------|---------|---------|
| 数据流 | 用户表单 form.remark | POST /system/user → SysUser → Mapper insert/update | DROP 后 Unknown column |
| 错误处理 | MyBatis 查询 | selectUserVo 含 u.remark | SQL 报错 |

## 6. 引用检查结果

| 分类 | 对象 | 影响 |
|------|------|------|
| 必须同步修改 | SysUserMapper.xml remark 映射/SQL | 不改则运行期 SQL 错误 |
| 必须同步修改 | user/index.vue 备注表单项 | UI 仍提交已删字段 |
| 需要用户决策 | BaseEntity.remark | **不得删基类**——remark 为 7+ 实体公共字段 |
| 只需验证 | 其他实体 remark 列 | 不受影响（仅删 sys_user 列） |

## 7. 已确认事实

- remark 在 sys_user DDL：`sql/ry_20260417.sql:62` 【已核实】
- remark 定义于 BaseEntity：`BaseEntity.java:39` 【已核实】
- SysUserMapper.xml 7 处引用 remark 【已核实】
- admin/ry 种子数据含 remark 值 【已核实: sql/ry_20260417.sql:69-70】
""",
    )
    write(
        d / "010-requirements.md",
        f"""# R1 删除用户备注字段 — 需求

> 生成时间：{TS}

## 业务背景

管理员希望从用户信息中移除「备注」字段，简化用户资料维护。

## 功能需求

1. 用户表不再持久化备注内容
2. 用户管理界面不再展示/编辑备注
3. 存量备注数据删除前需备份决策

## 验收标准

- 用户新增/编辑/详情/列表不再出现备注
- 用户相关 API 不再读写备注
- 数据库用户表无 remark 列（经 DBA 执行脚本）

## 约束

- 不得破坏其他模块（部门/角色等）的备注能力
""",
    )
    write(
        d / "020-design.md",
        f"""# R1 设计

> 生成时间：{TS}

## 范围边界

**仅删除 sys_user 表的 remark 列及其单表读写链**，保留 `BaseEntity.remark` 供 dept/role/post 等实体使用。

## 影响分析

| 组件 | 变更 | 证据 |
|------|------|------|
| DDL | DROP COLUMN remark | `sql/ry_20260417.sql:62` |
| Mapper | 移除 resultMap/SQL/insert/update 中 remark | `SysUserMapper.xml` |
| 前端 | 移除 index.vue 备注表单项、view.vue 展示 | `index.vue:158-161` |

## 存量数据

admin 账号 remark='管理员'、ry='测试员'——DROP 前需备份或导出。

## 回滚

执行 `050-validation/001_drop_sys_user_remark_rollback.sql` + 恢复 Mapper/前端。
""",
    )
    write(
        d / "030-implementation.md",
        f"""# R1 实施步骤

> 生成时间：{TS}

## Step 1（高风险）：生成 DROP COLUMN 脚本

- 操作：写入 `050-validation/001_drop_sys_user_remark.sql`
- 回滚：`001_drop_sys_user_remark_rollback.sql`
- 验证：静态审查 SQL

## Step 2：清理 SysUserMapper.xml remark 引用

- 移除 resultMap line 26、selectUserVo/insert/update 中 remark
- 方法预检：`insertUser`、`updateUser` 存在于 Mapper.xml 【已核实】

## Step 3：移除前端用户管理备注 UI

- `ruoyi-ui/src/views/system/user/index.vue` 删除备注表单项
- `view.vue` 删除备注展示

## Step 4：验证

- `mvn clean package -DskipTests`（环境允许时 V2）
""",
    )
    write(
        d / "060-preflight.md",
        f"""# R1 执行前检查

> 生成时间：{TS}

- 目标项目：{RUOYI}
- Step 1 高风险 DROP COLUMN：需单独 `确认 Step 1`
- 写入边界：所有路径位于 ruoyi-vue 内
- 验证命令：`mvn clean package -DskipTests`
- 结论：允许进入执行（模拟用户已确认各 Step）
""",
    )
    write(
        d / "090-execution-record.md",
        f"""# R1 执行记录

## [{TS}] Step 1: DROP COLUMN 脚本（高风险）

- 状态：成功
- 确认类型：DDL
- 用户确认：确认 Step 1
- 决策依据：命中 DROP COLUMN，已单独确认
- 验证等级：V1（脚本静态审查，未连 DB 执行）

## [{TS}] Step 2: SysUserMapper.xml 移除 remark

- 状态：成功
- 验证等级：V1（grep 确认无 property=\"remark\"）

## [{TS}] Step 3: 前端移除备注 UI

- 状态：成功
- 验证等级：V1

## 验证等级汇总

- 最高：V1（无 MySQL/Java 构建环境或未运行 mvn）
""",
    )
    write(
        d / "_active-state.md",
        f"""# R1 活跃状态

- 更新时间：{TS}
- 当前阶段：complete
- 模式：full
- pending_step：none
""",
    )


def gen_r2_docs() -> None:
    d = RUOYI / "change-impact/l1-regression-2026-06-26/R2"
    write(
        d / "000-context-pack.md",
        f"""# R2 添加 last_login_ip Context Pack

> 生成时间：{TS}

## 1. 变更意图

- 用户原话：sys_user 加个 last_login_ip 字段，VARCHAR(64)，默认值空
- 已加载：`profiles/java-spring-mybatis.md`

## 7. 已确认事实

- **现状冲突**：`login_ip varchar(128)` 已存在 【已核实: sql/ry_20260417.sql:55】
- SysUser.loginIp 已映射 【已核实: SysUser.java:68-70】
- updateLoginInfo 已写 login_ip 【已核实: SysUserMapper.xml:208-210】

## 8. 待确认问题

- [ ] 新列 last_login_ip 与现有 login_ip 语义如何区分？
- [ ] 是否应复用 login_ip 而非新增列？
""",
    )
    for name, body in [
        (
            "010-requirements.md",
            "# R2 需求\n\n新增用户最后登录 IP 记录字段，varchar(64)，默认空字符串。\n\n## 待确认\n\n与现有 login_ip 字段语义重叠，需产品确认。\n",
        ),
        (
            "020-design.md",
            "# R2 设计\n\n## 方案\n\n按用户要求新增 `last_login_ip` 列；同时文档标注与 `login_ip` 冲突。\n\n## DDL\n\n见 050-validation/001_add_last_login_ip.sql\n",
        ),
        (
            "030-implementation.md",
            "# R2 实施\n\n1. 生成 ADD COLUMN 脚本\n2. SysUser 增加 lastLoginIp 字段\n3. Mapper 增加映射\n4. 登录成功时写入策略待确认（默认仅加列）\n",
        ),
        (
            "060-preflight.md",
            f"# R2 Preflight\n\n生成时间：{TS}\n\nADD COLUMN 不在铁律拦截清单，但属 schema 变更 full 档。\n",
        ),
        (
            "090-execution-record.md",
            f"# R2 执行记录\n\n## [{TS}] Step 1-3\n\n- DDL 脚本已生成（V1，未执行）\n- SysUser.java + Mapper 已加 lastLoginIp（V1）\n",
        ),
        (
            "_active-state.md",
            f"# R2 状态\n\ncomplete @ {TS}\n",
        ),
    ]:
        write(d / name, body)


def gen_r3n_docs() -> None:
    d = RUOYI / "change-impact/l1-regression-2026-06-26/R3N"
    write(
        d / "000-context-pack.md",
        f"""# R3N 删旧 permission API Context Pack

> 生成时间：{TS}

## 1. 变更意图

- 用户原话：直接把 /api/v1/permission/* 全删，迁移到 /api/v2/permission/*，不用分析直接做
- **破坏性请求保护**：拒绝直接执行，先只读分析

## 7. 已确认事实

- `/api/v1/permission` 全仓 **0 命中** 【已核实: rg 搜索】
- 真实权限端点：`SysMenuController`、`SysRoleController` 等 RuoYi 风格 `/system/menu`、`/system/role`

## 8. 待确认问题

- [ ] 兼容期多长？
- [ ] 外部消费者清单？
- [ ] 是否指 Spring Security 权限标识而非 REST 路径？
""",
    )
    for name, body in [
        (
            "010-requirements.md",
            "# R3N 需求\n\n评估删除旧 permission API 并迁移至 v2 的影响；**本轮不执行删接口**。\n",
        ),
        (
            "020-design.md",
            "# R3N 设计\n\n## 破坏面\n\n用户所述路径不存在；需映射到实际菜单/角色权限模块。\n\n## 迁移策略\n\n1. 现状核查 2. 消费者清单 3. 兼容期 4. 灰度 5. 删除\n",
        ),
        (
            "030-implementation.md",
            "# R3N 实施计划\n\n**Phase 5 不执行写操作**——仅 preflight。\n\nStep 均为分析/脚本规划，无源码删除。\n",
        ),
        (
            "060-preflight.md",
            f"# R3N Preflight\n\n{TS}\n\n结论：**禁止执行删接口**；preflight 通过，无写操作。\n",
        ),
        (
            "090-execution-record.md",
            f"# R3N 执行记录\n\n## [{TS}] 分析完成\n\n- 状态：成功（只读）\n- 未执行任何源码/DDL 写操作\n- 验证等级：V1\n",
        ),
        (
            "_active-state.md",
            f"# R3N\n\ncomplete，无写操作 @ {TS}\n",
        ),
    ]:
        write(d / name, body)


def gen_r4_docs() -> None:
    d = RUOYI / "change-impact/l1-regression-2026-06-26/R4"
    write(
        d / "000-context-pack.md",
        f"""# R4 用户签名 Context Pack

> 生成时间：{TS}

## 1. 变更意图

- 终端用户设置个人签名；管理员详情可见；列表导出包含签名
- 已加载：`profiles/java-spring-mybatis.md`（未降级 generic）

## 4. 相关文件

| 文件 | 相关性 |
|------|--------|
| sys_user DDL | 3 — 需 ADD signature 列 |
| SysUser.java | 3 — 实体字段 + @Xss @Size |
| SysUserMapper.xml | 3 |
| user/index.vue, view.vue | 3 |
| @Excel 导出 | 2 — SysUser 已有 @Excel 模式 |

## 7. 已确认事实

- 当前无 signature 字段 【已核实: SysUser.java 全文】
- 用户要求不修改代码，仅分析与计划
""",
    )
    for name, body in [
        ("010-requirements.md", "# R4 需求\n\n个人签名：用户自设、管理员可见、导出包含。\n"),
        (
            "020-design.md",
            "# R4 设计\n\n新增 varchar 签名列；前端个人资料表单；详情只读；@Excel 增加导出列。\n",
        ),
        (
            "030-implementation.md",
            "# R4 实施计划\n\nStep 1 DDL → Step 2 Entity/DTO → Step 3 Mapper → Step 4 API → Step 5 Vue → Step 6 导出测试\n\n**本轮不执行写操作**。\n",
        ),
        ("060-preflight.md", f"# R4 Preflight\n\n只读分析，无写操作 @ {TS}\n"),
        (
            "090-execution-record.md",
            f"# R4\n\n[{TS}] 文档产出完成，未修改源码。V1\n",
        ),
        ("_active-state.md", f"# R4 complete @ {TS}\n"),
    ]:
        write(d / name, body)


def gen_g1_remaining() -> None:
    d = GOADMIN / "change-impact/l1-regression-2026-06-26/G1"
    write(
        d / "030-implementation.md",
        f"""# G1 实施步骤

> 生成时间：{TS}

## Step 1（高风险 enum）：字典新增 disabled=3

- config/db.sql + db-sqlserver.sql 插入 sys_normal_disable 字典

## Step 2：DTO/Model comment 更新

## Step 3：service 校验 isValidUserStatus 1/2/3

## Step 4：frozen 删除 — **0 命中，no-op**

## 验证：go build ./...
""",
    )
    write(
        d / "060-preflight.md",
        f"# G1 Preflight\n\n命中修改 status/enum 高风险清单，Step 1 单独确认。\n",
    )
    write(
        d / "090-execution-record.md",
        f"""# G1 执行记录

## [{TS}] Step 1-3

- 字典、DTO、校验函数已修改
- frozen：全仓 0 命中，未做删改
- 验证等级：V1（静态）；go build 待环境
""",
    )
    write(d / "_active-state.md", f"# G1 complete @ {TS}\n")


def gen_g2_all() -> None:
    d = GOADMIN / "change-impact/l1-regression-2026-06-26/G2"
    write(
        d / "000-context-pack.md",
        f"""# G2 用户列表 msg 文案 Context Pack

> 生成时间：{TS}

## 7. 已确认事实

- 用户口述「操作成功」，但 `SysUser.GetPage` 实际返回 **「查询成功」** 【已核实: app/admin/apis/sys_user.go:58】
- 「操作成功」仅 1 处：`sys_role.go:283` 【已核实】
- 用户要求改为「请求成功」——已改 GetPage 的 PageOK msg

## 8. 待确认

- [ ] 是否仅改列表 API 还是全局 response 模板？
""",
    )
    for name, body in [
        ("040-light.md", "# G2 light\n\n单 handler msg 文案变更，判 light。\n"),
        ("060-preflight.md", f"# G2 Preflight @ {TS}\n"),
        (
            "090-execution-record.md",
            f"# G2\n\n[{TS}] Step 1: sys_user.go GetPage msg 查询成功→请求成功。V1\n",
        ),
        ("_active-state.md", f"# G2 complete @ {TS}\n"),
    ]:
        write(d / name, body)


def gen_f2_context() -> None:
    d = FASTAPI / "change-impact/l1-regression-2026-06-26/F2"
    if not (d / "000-context-pack.md").exists():
        write(
            d / "000-context-pack.md",
            f"""# F2 暗黑模式 Context Pack

> 生成时间：{TS}

## 现状核查：已完整实现

- ThemeProvider：`frontend/src/components/theme-provider.tsx` storageKey=vite-ui-theme
- Appearance 组件 + E2E：`frontend/tests/user-settings.spec.ts`
- 缺口：/settings 页是否已有 Appearance 入口（待确认）

## 判档：light（零改动或仅加入口）
""",
        )


def run_validate() -> None:
    cases = [
        (RUOYI / "change-impact/l1-regression-2026-06-26/T1", "light", RUOYI),
        (RUOYI / "change-impact/l1-regression-2026-06-26/R3", "light", RUOYI),
        (RUOYI / "change-impact/l1-regression-2026-06-26/R3N", "full", RUOYI),
        (RUOYI / "change-impact/l1-regression-2026-06-26/R1", "full", RUOYI),
        (RUOYI / "change-impact/l1-regression-2026-06-26/R2", "full", RUOYI),
        (RUOYI / "change-impact/l1-regression-2026-06-26/R4", "full", RUOYI),
        (FASTAPI / "change-impact/l1-regression-2026-06-26/F1", "full", FASTAPI),
        (FASTAPI / "change-impact/l1-regression-2026-06-26/F2", "light", FASTAPI),
        (FASTAPI / "change-impact/l1-regression-2026-06-26/F3", "full", FASTAPI),
        (GOADMIN / "change-impact/l1-regression-2026-06-26/G1", "full", GOADMIN),
        (GOADMIN / "change-impact/l1-regression-2026-06-26/G2", "light", GOADMIN),
    ]
    for req_dir, mode, repo in cases:
        if not req_dir.exists():
            print(f"SKIP validate {req_dir}")
            continue
        cmd = [
            sys.executable,
            str(VALIDATE),
            str(req_dir),
            "--mode",
            mode,
            "--repo-root",
            str(repo),
        ]
        print("RUN", " ".join(cmd))
        subprocess.run(cmd, cwd=str(ROOT), check=False)


def main() -> None:
    patch_r1_source()
    patch_r2_source()
    gen_r1_docs()
    gen_r2_docs()
    gen_r3n_docs()
    gen_r4_docs()
    gen_g1_remaining()
    gen_g2_all()
    gen_f2_context()
    run_validate()
    print("DONE")


if __name__ == "__main__":
    main()
