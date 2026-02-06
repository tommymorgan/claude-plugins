---
name: tommymorgan:plan
description: Create a new feature plan via brainstorming with Gherkin requirements
argument-hint: "feature description"
allowed-tools:
  - Task
  - Skill
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Create Feature Plan

Create a comprehensive feature plan through collaborative brainstorming, generating Gherkin scenarios with expert review and quality assurance.

## Workflow

### Step 1: Invoke Brainstorming

Use the Skill tool to invoke the brainstorming skill:

```
Skill("tommymorgan:brainstorming")
```

Brainstorm the feature described by the user: $ARGUMENTS

The brainstorming skill handles question strategy, approach exploration, and section-level expert review.

### Step 2: Determine Project Location

Infer the project location from context:
- Current working directory
- Recently accessed files
- Conversation context

Projects live in `apps/`, `libs/`, or `tools/` directories.

If ambiguous, use AskUserQuestion to ask:
"Which project does this feature belong to?"
Options: List detected projects from apps/, libs/, tools/

### Step 3: Technology Checkpoint

After brainstorming completes and before writing Technical Specifications, verify technology decisions with the user.

**Scan for existing technology stack:**

Read project files to detect technologies already in use:
- `package.json` — Node.js runtime, frameworks (React, SolidJS, Express, etc.), build tools (Vite, esbuild), test frameworks (Vitest, Jest)
- `pyproject.toml` / `requirements.txt` — Python version, frameworks (FastAPI, Django, Flask)
- `Cargo.toml` — Rust edition, dependencies
- `go.mod` — Go version, modules
- `Dockerfiles` / `docker-compose.yml` — Container runtimes, database versions
- `Makefile` / `justfile` — Build tooling
- `.tool-versions` / `.nvmrc` / `.python-version` — Version managers

Report detected technologies:
```
I see you're using: [SolidJS, Vite, Vitest, pnpm, TypeScript 5.4]
```

**Identify undecided technology decisions:**

Compare what the plan needs against what's already determined. Only ask about decisions that are genuinely open.

Examples of decisions that might be needed:
- Database choice (if plan requires new data storage)
- Authentication approach (if plan adds auth)
- API framework (if plan adds a new service)
- Testing strategy (if project has no existing test setup)

**If technology decisions are needed:**

Present each decision using AskUserQuestion with options that include tradeoffs:
```
This feature needs a database. I see no existing database in the project.

Which database should we use?
Options:
- PostgreSQL (Recommended) — Relational, strong for structured data, well-supported in your Node.js stack
- SQLite — Lightweight, no server needed, good for single-user or embedded use
- MongoDB — Document store, flexible schema, good for unstructured data
```

Do not proceed to Technical Specifications until all technology decisions are confirmed.

**If no technology decisions are needed:**

Report that the existing stack covers all needs:
```
No new technology decisions needed — your existing stack covers this feature.
```

Proceed directly to Gherkin generation.

### Step 4: Generate Gherkin Requirements

Once the design is clear and technology decisions are confirmed, write Gherkin scenarios separated into two sections:

**User Requirements** (language/framework agnostic):
```gherkin
Scenario: <user-focused behavior>
  Given <user context>
  When <user action>
  Then <user outcome>
```

**Technical Specifications** (implementation details):
```gherkin
Scenario: <technical requirement>
  Given <system state>
  When <technical action>
  Then <technical outcome>
```

Cover:
- Happy paths
- Error cases
- Edge cases
- Security considerations
- Accessibility (table stakes)
- Performance (table stakes)

### Step 5: Interactive Reconciliation with Living Specs

**Check for existing living specs:**

```bash
# Check if project has features/ directory
if [ -d "<project>/features" ]; then
  # Load existing .feature files
  ls <project>/features/*.feature 2>/dev/null
fi
```

**If living specs exist:**

For each drafted scenario (both User Requirements and Technical Specifications):

1. **Load existing scenarios** from all .feature files in features/
2. **Find similar scenarios** by comparing scenario names and steps.
   Show potential matches to the user.

3. **Present reconciliation options** using AskUserQuestion:
   ```
   Your drafted scenario: "User logs in successfully"

   Found similar scenario in features/authentication.feature:
     "User authenticates with valid credentials"
     Similarity: 0.85

   How should this scenario relate to the living spec?

   Options:
   - creates: This is a new, independent scenario
   - replaces: This completely replaces the existing scenario
   - extends: This adds to the existing scenario
   - deprecates: This marks the old scenario as obsolete
   - none: These are not related (use different name)
   ```

4. **Record metadata** as comments before each scenario:
   ```gherkin
   # Living: <project>/features/<file>.feature::<scenario-name>
   # Action: creates|replaces|extends|removes|deprecates
   # Status: TODO
   # Living updated: NO
   Scenario: <scenario-text>
   ```

**If no living specs exist:**

Skip reconciliation - all scenarios will have:
```gherkin
# Living: none (initial implementation)
# Action: creates
# Status: TODO
# Living updated: NO
Scenario: <scenario-text>
```

**Benefits:**
- Maintains consistent naming across plans
- Makes relationships explicit
- Work tool knows exactly what to update
- Prevents duplicate/conflicting scenarios

### Step 6: Automated Quality Checklist

Before expert review, validate plan against checklist:

1. **Language/Framework Agnostic User Scenarios**
   - No mention of React, SQL, specific frameworks in User Requirements
   - User scenarios describe outcomes, not implementation

2. **Version Verification**
   - Check actual versions from project files:
     - package.json for Node/npm versions
     - pyproject.toml/requirements.txt for Python
     - docker-compose.yml for database versions
   - Use correct versions in Technical Specifications

3. **No Optional Items**
   - Everything in plan meets quality bar
   - No "nice to have" or "optional" markers

4. **Table Stakes Included**
   - Accessibility considerations present
   - Performance considerations present

### Step 7: Expert Review Panel

Invoke the `/review-features` command to run the expert panel on the generated scenarios:

```
/tommymorgan:review-features <draft-plan-content>
```

The expert panel will:
1. Review scenarios based on content context (auto-detected)
2. Provide prioritized recommendations (Critical/High/Medium)
3. Debate conflicts and reach consensus autonomously
4. Present recommendations incrementally (Critical one-at-a-time, then High/Medium with review style choice)

The `/review-features` command handles the full incremental presentation flow. Refine scenarios based on accepted recommendations.

### Step 8: Affected Documentation

After scenarios are finalized, scan the project for documentation that needs updating.

**Scan for existing documentation:**

Use Glob to find documentation files:
```
Glob("**/*.md", path="<project>")
Glob("**/docs/**", path="<project>")
```

Look for:
- `README.md` — Project overview and usage
- `CLAUDE.md` — AI assistant instructions
- `docs/` directory — User guides, API docs, technical specs
- `CHANGELOG.md` — Release notes
- `CONTRIBUTING.md` — Contributor guidelines
- API documentation (OpenAPI specs, Swagger files)

**Determine which documents are affected:**

For each documentation file found, compare the planned behavioral changes against the document's content. A document is affected if:
- It describes behavior the plan changes
- It references APIs, commands, or features the plan modifies
- It contains examples that will become incorrect

**Write the Affected Documentation section:**

Add a markdown checklist to the plan file:
```markdown
## Affected Documentation

- [ ] Update README.md — describe new Technology Checkpoint step in plan workflow
- [ ] Update docs/user-guide.md — add section on incremental recommendation review
- [ ] Update CLAUDE.md — document new skill availability
```

Each item:
- References a specific document path
- Briefly describes what needs updating
- Is a trackable checkbox item

If no documentation is affected, include the section with a note:
```markdown
## Affected Documentation

No existing documentation is affected by these changes.
```

### Step 9: Local Development Environment Check

Before finalizing plan, verify local dev environment exists or add setup scenarios:

1. **Intelligently detect local dev** (apply good judgment):
   - Container orchestration (Docker, Podman, compose files)
   - Dev server configs (package.json scripts, Makefile, justfile)
   - Environment config patterns (.env files, config templates)
   - Database setup (connection configs, migration scripts)
   - Project-specific tooling

2. **If local dev missing/incomplete**, add setup scenarios:
   - Generate appropriate scenarios for the specific tech stack
   - Not prescriptive - adapt to project needs
   - Must be comprehensive - broken local dev blocks all work

3. **Validation**:
   - Local dev scenarios come first
   - Work command will verify local dev works before starting

### Step 10: Write Plan File

Create the plan file at:
`<project>/plans/YYYY-MM-DD-<slug>.md`

Where:
- `<project>` is the inferred project path (e.g., `apps/web`, `libs/shared`)
- `YYYY-MM-DD` is today's date
- `<slug>` is a kebab-case version of the feature name

Plan file format:
```markdown
# Feature: <title>

**Created**: YYYY-MM-DD
**Goal**: <one-sentence user-facing outcome>

## User Requirements

<!-- TODO -->
Scenario: <user-focused behavior>
  Given <user context>
  When <user action>
  Then <user outcome>

## Technical Specifications

<!-- TODO -->
Scenario: <technical requirement>
  Given <system state>
  When <technical action>
  Then <technical outcome>

## Affected Documentation

- [ ] Update <path> — <brief description of needed update>

## Notes

<design decisions, architectural choices, constraints, context>
```

The **Affected Documentation** section appears after Technical Specifications and before Notes. Each item is a markdown checkbox (`- [ ]`) referencing a specific document path.

Create the plans directory if it doesn't exist:
```bash
mkdir -p <project>/plans
```

### Step 11: Report Completion

After creating the plan, report:

```
Plan created: <path to plan file>

Expert Review Summary:
- All experts reviewed and approved
- [List any major changes from review]

Ready to work. Run /tommymorgan:work to begin.
```

## Important Notes

- Never skip brainstorming, even for "simple" features
- Expert review is mandatory - all conflicts must be resolved
- Automated checklist must pass before expert review
- User Requirements must be language/framework agnostic
- Technical Specifications use actual project versions
- Scenarios ARE the plan - no separate task lists
- Local dev must be verified/planned before implementation
- The plan file is the single source of truth for all future sessions
