export const meta = {
  name: 'eval-b1-impact-response-time',
  description: 'B1: impact analysis for adding response time to ruoyi-vue operation logs',
  phases: [
    { title: 'Read Skill & Refs', detail: 'Load all skill files and templates' },
    { title: 'Analyze & Classify', detail: 'Execute impact phases 1-3.5 with coverage semantics check' },
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
  '13. skills/impact/templates/040-light.md\n' +
  '14. skills/impact/templates/060-preflight.md\n\n' +
  'Understand the impact protocol. Key points for B1:\n' +
  '- Phase 2.5 coverage semantics check: user says "每次接口请求" (every API request)\n' +
  '- Existing LogAspect only covers @Log-annotated controller methods\n' +
  '- This is a COVERAGE GAP - must classify as FULL not light\n' +
  '- 010-requirements.md must contain ONLY business description (no table names, class names, file paths, code snippets)',
  { label: 'b1-read-skill', phase: 'Read Skill & Refs' }
)

phase('Analyze & Classify')
const analysis = await agent(
  'Execute the FULL impact skill protocol on ruoyi-vue for:\n' +
  'User request: "I want to add response time recording to the operation log. Every API request should record how many milliseconds it took from entry to return, and the operation log list page should show this time."\n\n' +
  'Working directory: E:/agent/blue-skillhub/test-projects/ruoyi-vue\n' +
  'Output directory: change-impact/blind-v4-step37flash/B1/\n\n' +
  'CRITICAL ANALYSIS STEPS:\n\n' +
  'Phase 1 (Intent Capture):\n' +
  '  Output: Current assumption, ambiguities, task size, success criteria\n\n' +
  'Phase 2 (Context Discovery):\n' +
  '  Find and read these key files:\n' +
  '  - ruoyi-framework/src/main/java/com/ruoyi/framework/aspectj/LogAspect.java (the existing AOP aspect for operation logging)\n' +
  '  - ruoyi-common/src/main/java/com/ruoyi/common/annotation/Log.java (the @Log annotation definition)\n' +
  '  - ruoyi-system/src/main/java/com/ruoyi/system/domain/SysOperLog.java (operation log entity)\n' +
  '  - ruoyi-system/src/main/resources/mapper/system/SysOperLogMapper.xml (SQL mappings)\n' +
  '  - ruoyi-system/src/main/java/com/ruoyi/system/service/impl/SysOperLogServiceImpl.java\n' +
  '  - ruoyi-admin/src/main/java/com/ruoyi/web/controller/monitor/SysOperlogController.java\n' +
  '  - ruoyi-framework/src/main/java/com/ruoyi/framework/manager/factory/AsyncFactory.java\n' +
  '  - The Vue frontend page for operation log list (search in ruoyi-ui/src/views/)\n\n' +
  '  IMPORTANT: Read LogAspect.java to confirm it ONLY intercepts methods annotated with @Log\n' +
  '  IMPORTANT: Identify which controllers/interfaces are NOT covered by @Log\n\n' +
  'Phase 2.5 (Coverage Semantics Check - MANDATORY):\n' +
  '  User phrase: "每次接口请求" = every API request\n' +
  '  Current implementation: LogAspect @Around("@annotation(com.ruoyi.common.annotation.Log)") - only covers @Log-annotated methods\n' +
  '  COVERAGE GAP IDENTIFIED: Un-annotated controllers (login, captcha, etc.) are NOT covered\n' +
  '  CONCLUSION: Cannot be light. Must be "倾向 full" because:\n' +
  '    a) The coverage scope is different (all requests vs @Log only)\n' +
  '    b) Need to either expand LogAspect coverage OR add a global filter\n' +
  '    c) This involves framework-level changes, not just adding a field\n\n' +
  'Phase 3 (Socratic Questions):\n' +
  '  Ask questions based on the coverage gap finding\n\n' +
  'Phase 3.5 (Tier Decision):\n' +
  '  Recommend: FULL\n' +
  '  Evidence: coverage gap between "every request" and "@Log only"\n\n' +
  'Phase 4 (Documents):\n' +
  '  Generate these files (eval mode - generate all without waiting for confirmation):\n\n' +
  '  000-context-pack.md:\n' +
  '    - Project: RuoYi Vue (Java Spring Boot + Vue.js admin framework)\n' +
  '    - Relevant modules: ruoyi-framework (LogAspect), ruoyi-system (SysOperLog), ruoyi-admin (controller)\n' +
  '    - Existing operation log flow\n\n' +
  '  010-requirements.md (BUSINESS ONLY - strictly no technical details):\n' +
  '    - Business scenario: Admin users review system operation history\n' +
  '    - Functional requirement: Record time cost for each API request\n' +
  '    - Display requirement: Show time cost in operation log list\n' +
  '    - Non-functional: Timing accuracy, minimal performance overhead\n' +
  '    - Business constraint: Must not miss any request type\n' +
  '    - Acceptance criteria\n' +
  '    - FORBIDDEN: table names, class names (LogAspect, SysOperLog), file paths, code snippets, field types, annotation names\n\n' +
  '  020-design.md:\n' +
  '    - Coverage analysis: @Log annotation gap\n' +
  '    - Design options for full coverage (global filter vs expanded aspect)\n' +
  '    - Schema change: add time field to operation log\n' +
  '    - Frontend changes\n\n' +
  '  030-implementation.md:\n' +
  '    - Verify all method names by grep before writing\n' +
  '    - Implementation steps with real file paths and line numbers',
  { label: 'b1-analyze', phase: 'Analyze & Classify' }
)

phase('Write Outputs')
const writeResult = await agent(
  'Check B1 output directory E:/agent/blue-skillhub/test-projects/ruoyi-vue/change-impact/blind-v4-step37flash/B1/\n' +
  'Verify these files exist: 000-context-pack.md, 010-requirements.md, 020-design.md, 030-implementation.md\n' +
  'Check 010-requirements.md for FORBIDDEN technical details:\n' +
  '  - Should NOT contain: table names (like sys_oper_log), class names (like LogAspect, SysOperLog), file paths, code snippets, field type definitions (like varchar, bigint)\n' +
  '  - Should contain only: business scenarios, functional requirements, non-functional requirements, constraints, acceptance criteria\n\n' +
  'If 010-requirements.md has technical details, fix it now.\n' +
  'Then list ALL files in the B1 directory recursively.',
  { label: 'b1-write', phase: 'Write Outputs' }
)

return { task: 'B1', result: writeResult }
