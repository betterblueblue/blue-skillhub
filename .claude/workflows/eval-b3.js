export const meta = {
  name: 'eval-b3-impactpro-phone',
  description: 'B3: impact-pro analysis for adding phone number to Prisma User model',
  phases: [
    { title: 'Read Skill & Refs', detail: 'Load impact-pro skill, profile, templates' },
    { title: 'Analyze & Classify', detail: 'Execute impact-pro phases with node-express-prisma profile' },
    { title: 'Write Outputs', detail: 'Generate all full documents' },
  ],
}

phase('Read Skill & Refs')
const skillRead = await agent(
  'Read ALL of the following files completely:\n' +
  '1. skills/impact-pro/SKILL.md\n' +
  '2. skills/impact-pro/profiles/node-express-prisma.md\n' +
  '3. skills/impact-pro/profiles/generic.md\n' +
  '4. skills/impact-pro/profiles/_schema.md\n' +
  '5. skills/impact-pro/db-adapters/generic-sql.md\n' +
  '6. skills/impact-pro/references/phase-2-context-discovery.md\n' +
  '7. skills/impact-pro/references/phases-detail.md\n' +
  '8. skills/impact-pro/references/phase-5-execution.md\n' +
  '9. skills/impact-pro/references/cross-platform-notes.md\n' +
  '10. skills/impact-pro/templates/000-context-pack.md\n' +
  '11. skills/impact-pro/templates/010-requirements.md\n' +
  '12. skills/impact-pro/templates/020-design.md\n' +
  '13. skills/impact-pro/templates/030-implementation.md\n' +
  '14. skills/impact-pro/templates/060-preflight.md\n\n' +
  'Understand the impact-pro protocol. Key points for B3:\n' +
  '- This is a Node.js + Express + Prisma + PostgreSQL project\n' +
  '- Load node-express-prisma profile for stack-specific rules\n' +
  '- Phone field: optional in registration, format validation (Chinese phone), unique constraint\n' +
  '- 010-requirements.md must contain ONLY business description',
  { label: 'b3-read-skill', phase: 'Read Skill & Refs' }
)

phase('Analyze & Classify')
const analysis = await agent(
  'Execute the FULL impact-pro skill protocol on prisma-express-ts for:\n' +
  'User request: "I want to add a phone number field to the User model. Registration can be optional, but if filled must be Chinese phone format (11 digits starting with 1), and phone number must be unique (no duplicates)."\n\n' +
  'Working directory: E:/agent/blue-skillhub/test-projects/prisma-express-ts\n' +
  'Output directory: change-impact/blind-v4-step37flash/B3/\n\n' +
  'CRITICAL ANALYSIS:\n' +
  '- Prisma schema change: add phone field to User model with @unique\n' +
  '- DB migration: new unique constraint, existing users get null phone\n' +
  '- Validation: Chinese phone regex (/^1[3-9]\\d{9}$/)\n' +
  '- Registration flow update: accept optional phone\n' +
  '- API contract: User response now includes phone\n' +
  '- MUST be FULL: schema change + unique constraint + migration + API change\n\n' +
  'Phase 1 (Intent Capture):\n' +
  '  Output: assumption, ambiguities, size, success criteria\n\n' +
  'Phase 2 (Tech Stack Detection + Context):\n' +
  '  Detect: Node.js + Express + TypeScript + Prisma + PostgreSQL + JWT\n' +
  '  Load node-express-prisma profile\n' +
  '  Read these files:\n' +
  '  - prisma/schema.prisma (User model - current state)\n' +
  '  - src/validations/auth.validation.ts (register validation rules)\n' +
  '  - src/validations/user.validation.ts (user validation rules)\n' +
  '  - src/validations/custom.validation.ts (custom validation rules)\n' +
  '  - src/services/auth.service.ts (register logic)\n' +
  '  - src/controllers/auth.controller.ts (register endpoint)\n' +
  '  - src/routes/v1/auth.route.ts (route definition)\n' +
  '  - src/controllers/user.controller.ts (user profile endpoints)\n' +
  '  - src/routes/v1/user.route.ts (user routes)\n' +
  '  - src/middlewares/validate.ts (validation middleware)\n\n' +
  '  User scenario coverage verification:\n' +
  '    - Trace registration flow: POST /v1/auth/register -> auth.controller.ts -> auth.service.ts -> Prisma user.create\n' +
  '    - Confirm all files in this path are included\n\n' +
  'Phase 2.5 (Risk Pre-judgment):\n' +
  '  - FULL triggers: schema change, unique constraint, data migration, API contract\n' +
  '  - Mark as "倾向 full"\n\n' +
  'Phase 3 (Socratic Questions):\n' +
  '  Questions about phone format, uniqueness scope, registration behavior\n\n' +
  'Phase 3.5 (Tier): FULL\n\n' +
  'Phase 4 (Documents):\n\n' +
  '  000-context-pack.md:\n' +
  '    - Project: Express + Prisma API server\n' +
  '    - Tech stack details\n' +
  '    - Current User model and auth flow\n\n' +
  '  010-requirements.md (BUSINESS ONLY - strictly no technical details):\n' +
  '    - Business scenario: User identity verification enhancement\n' +
  '    - Functional requirement: Add phone number as optional user identifier\n' +
  '    - Validation requirement: Correct format for entered phone numbers\n' +
  '    - Uniqueness requirement: No duplicate phone numbers in system\n' +
  '    - Non-functional: Registration UX (optional field), data integrity\n' +
  '    - Business constraint: Optional at registration, enforced format when provided\n' +
  '    - Acceptance criteria\n' +
  '    - FORBIDDEN: Prisma schema syntax, model names, field types (String @unique), file paths, code snippets, regex patterns, class names, method names\n\n' +
  '  020-design.md:\n' +
  '    - Per node-express-prisma profile style axes\n' +
  '    - Schema design (Prisma migration)\n' +
  '    - Validation design (custom validator for Chinese phone)\n' +
  '    - API design (register + user profile)\n' +
  '    - Migration design\n' +
  '    - Code style report with complete reference code snippets\n\n' +
  '  030-implementation.md:\n' +
  '    - PRE-CHECK: Verify all method names by grep\n' +
  '    - PRE-CHECK: Check for exception behavior of called methods\n' +
  '    - Implementation steps:\n' +
  '      Step 1: Prisma migration (add phone field)\n' +
  '      Step 2: Custom validation (phone format)\n' +
  '      Step 3: Auth validation (register accepts phone)\n' +
  '      Step 4: Auth service (pass phone to Prisma)\n' +
  '      Step 5: Auth controller (extract phone from request)\n' +
  '      Step 6: User controller/route (expose phone in profile)\n' +
  '    - All with real file paths and line numbers',
  { label: 'b3-analyze', phase: 'Analyze & Classify' }
)

phase('Write Outputs')
const writeResult = await agent(
  'Check B3 output directory E:/agent/blue-skillhub/test-projects/prisma-express-ts/change-impact/blind-v4-step37flash/B3/\n' +
  'Verify: 000-context-pack.md, 010-requirements.md, 020-design.md, 030-implementation.md\n' +
  'Check 010-requirements.md has NO technical details\n' +
  'Check 030-implementation.md has real method names verified by grep\n' +
  'List ALL files in B3 directory.',
  { label: 'b3-write', phase: 'Write Outputs' }
)

return { task: 'B3', result: writeResult }
