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
Skill("superpowers:brainstorming")
```

Brainstorm the feature described by the user: $ARGUMENTS

Ask questions one at a time to understand:
- What problem does this solve?
- Who are the users?
- What are the success criteria?
- What are the constraints?

Explore 2-3 approaches and recommend one.

### Step 2: Determine Project Location

Infer the project location from context:
- Current working directory
- Recently accessed files
- Conversation context

Projects live in `apps/`, `libs/`, or `tools/` directories.

If ambiguous, use AskUserQuestion to ask:
"Which project does this feature belong to?"
Options: List detected projects from apps/, libs/, tools/

### Step 3: Generate Gherkin Requirements

Once the design is clear, write Gherkin scenarios separated into two sections:

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

### Step 4: Automated Quality Checklist

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

### Step 5: Expert Review Panel

Invoke expert reviewers to validate and improve the plan. Experts debate conflicts autonomously and reach consensus.

**Panel Members:**

1. **Marty Cagan** (Product Management)
   - Reviews: User Requirements only
   - Focus: Product value, user outcomes, completeness of user paths
   - Pushback: Technical details in user scenarios

2. **Dave Farley** (Continuous Delivery)
   - Reviews: User Requirements AND Technical Specifications
   - Focus: Testability, automation, CD practices, deployability

3. **OWASP Security Expert**
   - Reviews: Technical Specifications
   - Focus: Auth/authz, input validation, data protection, threat modeling

4. **Jakob Nielsen** (UX/Accessibility)
   - Reviews: User Requirements
   - Focus: Usability depth, accessibility beyond compliance, interaction patterns

5. **Martin Kleppmann** (Data-Intensive Systems)
   - Reviews: Technical Specifications
   - Focus: Scalability, data architecture, performance design

6. **Eric Evans** (Domain-Driven Design)
   - Reviews: User Requirements AND Technical Specifications
   - Focus: Domain modeling, business logic, bounded contexts

7. **Google SRE**
   - Reviews: Technical Specifications
   - Focus: Observability, monitoring, failure modes, operational concerns

**Review Process:**

1. Each expert reviews their assigned sections
2. Experts identify issues and suggest improvements
3. When experts disagree, they debate and reach consensus
4. No user intervention - experts resolve conflicts autonomously
5. Plan is refined based on consensus

**Implementation:**
```
Review each section with appropriate experts
Collect feedback
Resolve conflicts through expert debate
Refine plan based on consensus
```

Instead of separate task lists, use inline comments to track scenario progress:

```gherkin
<!-- TODO -->
Scenario: User logs in successfully
  Given I am on the login page
  When I enter valid credentials
  Then I am redirected to dashboard

<!-- DONE -->
Scenario: Invalid credentials show error
  Given I am on the login page
  When I enter invalid credentials
  Then I see an error message
```

Scenarios ARE the plan. Tests prove scenarios are satisfied. No duplicate tracking needed.

### Step 7: Local Development Environment Check

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

### Step 8: Write Plan File

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

## Notes

<design decisions, architectural choices, constraints, context>
```

Create the plans directory if it doesn't exist:
```bash
mkdir -p <project>/plans
```

### Step 9: Report Completion

After creating the plan, report:

```
Plan created: <path to plan file>

Expert Review Summary:
- All 7 experts reviewed and approved
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
