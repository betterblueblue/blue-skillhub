export const meta = {
  name: 'eval-b6-pathfinder',
  description: 'B6: pathfinder project map for prisma-express-ts with mandatory facts files',
  phases: [
    { title: 'Read Skill & Refs', detail: 'Load all skill files and references' },
    { title: 'Analyze Project', detail: 'Execute pathfinder phases 1-4 with mandatory facts' },
    { title: 'Write Outputs', detail: 'Verify and finalize output files' },
  ],
}

phase('Read Skill & Refs')
const skillRead = await agent(
  'Read ALL of the following files completely:\n' +
  '1. skills/pathfinder/SKILL.md\n' +
  '2. skills/pathfinder/references/phase-1-sizing.md\n' +
  '3. skills/pathfinder/references/phase-2-explore-domains.md\n' +
  '4. skills/pathfinder/references/phase-3-depth-fill.md\n' +
  '5. skills/pathfinder/references/handoff-contract.md\n' +
  '6. skills/pathfinder/references/cross-platform-notes.md\n' +
  '7. skills/pathfinder/templates/project-map.md\n' +
  '8. skills/pathfinder/scripts/pf_scan.py\n' +
  '9. skills/pathfinder/scripts/pf_git.py\n' +
  '10. skills/pathfinder/scripts/pf_validate.py\n\n' +
  'Understand the full pathfinder protocol. Key points:\n' +
  '- Phase 1.5 is MANDATORY: must run pf_scan.py and pf_git.py to produce facts/scan.json and facts/git.json\n' +
  '- Script Gate (Phase 4): must run pf_validate.py and get exit code 0 before writing _project-map.md\n' +
  '- If facts files are missing, pf_validate.py V6 returns FAIL\n' +
  '- The _project-map.md must include Executive Summary + 14 core sections\n' +
  '- Must include auth-consistency self-check in section [10]\n' +
  '- All facts must be labeled [已核实: evidence] or [推断: 待验证]',
  { label: 'b6-read-skill', phase: 'Read Skill & Refs' }
)

phase('Analyze Project')
const analysis = await agent(
  'Execute the FULL pathfinder skill protocol on the prisma-express-ts project.\n' +
  'Working directory: E:/agent/blue-skillhub/test-projects/prisma-express-ts\n' +
  'Output directory: change-impact/blind-v4-step37flash/B6/\n\n' +
  'Step 1 - Phase 1 (Sizing):\n' +
  '  - Run: git rev-parse --show-toplevel\n' +
  '  - Run: git rev-parse HEAD\n' +
  '  - Count files and directories\n' +
  '  - Determine budget tier (this is a SMALL project ~20 source files)\n\n' +
  'Step 2 - Phase 1.5 (FACTS - HARD GATE, cannot skip):\n' +
  '  - Run: python E:/agent/blue-skillhub/skills/pathfinder/scripts/pf_scan.py . --output change-impact/blind-v4-step37flash/B6/facts/scan.json\n' +
  '  - Run: python E:/agent/blue-skillhub/skills/pathfinder/scripts/pf_git.py . --output change-impact/blind-v4-step37flash/B6/facts/git.json\n' +
  '  - These files MUST exist before proceeding. If scripts fail, fix the issue and retry.\n\n' +
  'Step 3 - Phase 2 (Explore):\n' +
  '  Read these key files to understand the project:\n' +
  '  - package.json (tech stack, deps)\n' +
  '  - prisma/schema.prisma (data model: User, Token, Role enum, TokenType enum)\n' +
  '  - src/app.ts, src/index.ts (entry points)\n' +
  '  - src/routes/v1/index.ts (route map)\n' +
  '  - src/config/passport.ts (JWT strategy - CRITICAL for auth flow)\n' +
  '  - src/middlewares/auth.ts (auth middleware)\n' +
  '  - src/controllers/auth.controller.ts (login/register endpoints)\n' +
  '  - src/services/auth.service.ts (auth business logic)\n' +
  '  - src/services/token.service.ts (token management)\n' +
  '  - src/validators/auth.validation.ts (input validation)\n\n' +
  'Step 4 - Phase 3 (Deep fill):\n' +
  '  Write the project map covering:\n' +
  '  [0] Basic info with git HEAD and credibility markers\n' +
  '  [1] One-line description\n' +
  '  [2] Tech stack (Express + TypeScript + Prisma + PostgreSQL + JWT)\n' +
  '  [3] Architecture/layer map (Mermaid diagram)\n' +
  '  [4] Core features (auth with JWT, user CRUD, token management)\n' +
  '  [5] Key entry points\n' +
  '  [6] Data model overview (User, Token, Role, TokenType - with Mermaid ER diagram)\n' +
  '  [7] External dependencies\n' +
  '  [8] Build/run/test commands\n' +
  '  [9] Risk areas\n' +
  '  [10] Auth/permission model WITH auth-consistency self-check:\n' +
  '      - Read passport.ts line by line, record select fields\n' +
  '      - Read auth.ts line by line, record which fields are used for RBAC\n' +
  '      - Compare: does auth.ts use fields that passport.ts does NOT select?\n' +
  '      - Known issue: passport.ts select only {id, email, name} but auth.ts uses user.role\n' +
  '      - Record this inconsistency in [9] risk areas\n' +
  '  [11] Typical main flow (trace login request end-to-end)\n' +
  '  [12] Documentation\n' +
  '  [13] Not-covered areas\n\n' +
  'Step 5 - Phase 4 Script Gate:\n' +
  '  - Run: python E:/agent/blue-skillhub/skills/pathfinder/scripts/pf_validate.py change-impact/blind-v4-step37flash/B6/_project-map.md --repo-root .\n' +
  '  - If exit code != 0: read errors, fix the map, rerun until exit code = 0\n' +
  '  - Only write _project-map.md after gate passes\n\n' +
  'Step 6 - Phase 5: List all files in the output directory',
  { label: 'b6-analyze', phase: 'Analyze Project' }
)

phase('Write Outputs')
const writeResult = await agent(
  'Check the B6 output directory E:/agent/blue-skillhub/test-projects/prisma-express-ts/change-impact/blind-v4-step37flash/B6/\n' +
  'Verify these files exist:\n' +
  '1. facts/scan.json - must exist with real file count data\n' +
  '2. facts/git.json - must exist with head_short and toplevel\n' +
  '3. _project-map.md - must exist and be validated\n\n' +
  'If any are missing, create them now. Then list ALL files in the B6 directory recursively.',
  { label: 'b6-write', phase: 'Write Outputs' }
)

return { task: 'B6', result: writeResult }
