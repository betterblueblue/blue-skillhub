export const meta = {
  name: 'eval-b2-impact-md5-bcrypt',
  description: 'B2: impact analysis for MD5 to BCrypt password migration in ruoyi-vue',
  phases: [
    { title: 'Read Skill & Refs', detail: 'Load all skill files and templates' },
    { title: 'Analyze & Classify', detail: 'Execute impact phases with full classification' },
    { title: 'Write Outputs', detail: 'Generate all full documents' },
  ],
}

phase('Read Skill & Refs')
const skillRead = await agent(
  'Read ALL of the following files completely:\n' +
  '1. skills/impact/SKILL.md\n' +
  '2. skills/impact/references/phase-2-context-discovery.md\n' +
  '3. skills/impact/references/phase-3-questioning.md\n' +
  '4. skills/impact/references/dimensions.md\n' +
  '5. skills/impact/references/schema-discovery.md\n' +
  '6. skills/impact/references/style-analysis.md\n' +
  '7. skills/impact/references/phase-5-execution.md\n' +
  '8. skills/impact/references/cross-platform-notes.md\n' +
  '9. skills/impact/templates/000-context-pack.md\n' +
  '10. skills/impact/templates/010-requirements.md\n' +
  '11. skills/impact/templates/020-design.md\n' +
  '12. skills/impact/templates/030-implementation.md\n' +
  '13. skills/impact/templates/060-preflight.md\n\n' +
  'Understand the impact protocol. Key points for B2:\n' +
  '- This is a password encryption migration: MD5 -> BCrypt with backward compatibility\n' +
  '- Triggers full conditions: DB schema change, data migration, login flow change\n' +
  '- 010-requirements.md must contain ONLY business description (no technical details)',
  { label: 'b2-read-skill', phase: 'Read Skill & Refs' }
)

phase('Analyze & Classify')
const analysis = await agent(
  'Execute the FULL impact skill protocol on ruoyi-vue for:\n' +
  'User request: "I see user passwords are encrypted with MD5. I want to change to BCrypt. But there are many existing users with MD5 passwords, cannot invalidate them, need backward compatibility."\n\n' +
  'Working directory: E:/agent/blue-skillhub/test-projects/ruoyi-vue\n' +
  'Output directory: change-impact/blind-v4-step37flash/B2/\n\n' +
  'CRITICAL ANALYSIS:\n' +
  '- DB schema change: password column length (MD5=32 chars -> BCrypt=60 chars)\n' +
  '- Data migration: existing MD5 passwords need dual-algorithm verification\n' +
  '- Login flow change: need to try BCrypt first, fall back to MD5 for old passwords\n' +
  '- New BCrypt passwords should be transparently upgraded on next login\n' +
  '- This MUST be classified as FULL (multiple full triggers)\n\n' +
  'Phase 1 (Intent Capture):\n' +
  '  Output assumption, ambiguities, size (large), success criteria\n\n' +
  'Phase 2 (Context Discovery):\n' +
  '  Find and read these files:\n' +
  '  - ruoyi-common/src/main/java/com/ruoyi/common/utils/sign/Md5Utils.java (MD5 hashing)\n' +
  '  - ruoyi-common/src/main/java/com/ruoyi/common/utils/SecurityUtils.java (password matching, login)\n' +
  '  - ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysUserServiceImpl.java (user service with password ops)\n' +
  '  - ruoyi-system/src/main/resources/mapper/system/SysUserMapper.xml (user SQL)\n' +
  '  - ruoyi-common/src/main/java/com/ruoyi/common/core/domain/entity/SysUser.java (user entity)\n' +
  '  - ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysUserController.java (user management API)\n' +
  '  - ruoyi-admin/src/main/java/com/ruoyi/web/controller/system/SysProfileController.java (profile/password change)\n\n' +
  '  Use grep to find: resetUserPwd, encryptPassword, matchesPassword, Md5Utils\n\n' +
  'Phase 2.5 (Risk Pre-judgment):\n' +
  '  - FULL triggers: DB schema migration, data backfill (dual-algorithm), API contract\n' +
  '  - Mark as "倾向 full"\n\n' +
  'Phase 3 (Socratic Questions):\n' +
  '  Questions about migration strategy, BCrypt strength, rollback plan\n\n' +
  'Phase 3.5 (Tier): FULL\n\n' +
  'Phase 4 (Documents):\n\n' +
  '  000-context-pack.md:\n' +
  '    - Project overview\n' +
  '    - Current password flow (MD5 hash -> store -> compare)\n' +
  '    - Key files and their roles\n\n' +
  '  010-requirements.md (BUSINESS ONLY - strictly no technical details):\n' +
  '    - Business scenario: User account security upgrade\n' +
  '    - Functional requirement: Upgrade password encryption from current to stronger algorithm\n' +
  '    - Compatibility requirement: Existing users can still login during transition\n' +
  '    - Non-functional: Security strength, backward compatibility period, migration speed\n' +
  '    - Business constraint: Cannot force password reset for all users\n' +
  '    - Acceptance criteria\n' +
  '    - FORBIDDEN: table names (sys_user), class names (Md5Utils, SecurityUtils), file paths, code snippets, field types (varchar(32)), algorithm implementation details\n\n' +
  '  020-design.md:\n' +
  '    - Dual-algorithm password verification design\n' +
  '    - Schema migration plan (column length change)\n' +
  '    - Gradual migration strategy (upgrade on login)\n' +
  '    - Code style report per RuoYi conventions\n\n' +
  '  030-implementation.md:\n' +
  '    - PRE-CHECK: Verify all method names exist by grep\n' +
  '      * Grep for: matchesPassword, encryptPassword, resetUserPwd, Md5Utils.hash\n' +
  '      * If a method does not exist, search for the correct name\n' +
  '    - PRE-CHECK: Check exception behavior of getLoginUser (throws vs returns null)\n' +
  '    - Implementation steps with real file paths and line numbers\n' +
  '    - Dual-algorithm verification logic\n' +
  '    - Data migration SQL\n' +
  '    - New BCrypt integration with dependency',
  { label: 'b2-analyze', phase: 'Analyze & Classify' }
)

phase('Write Outputs')
const writeResult = await agent(
  'Check B2 output directory E:/agent/blue-skillhub/test-projects/ruoyi-vue/change-impact/blind-v4-step37flash/B2/\n' +
  'Verify: 000-context-pack.md, 010-requirements.md, 020-design.md, 030-implementation.md\n' +
  'Check 010-requirements.md has NO technical details (no class names, file paths, code, field types)\n' +
  'Check 030-implementation.md has real method names verified by grep\n' +
  'List ALL files in B2 directory.',
  { label: 'b2-write', phase: 'Write Outputs' }
)

return { task: 'B2', result: writeResult }
