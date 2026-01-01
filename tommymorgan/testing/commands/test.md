---
name: tommymorgan:test
description: Smart testing with plan-awareness - automatically selects appropriate testing strategy based on context
argument-hint: "[test description]"
allowed-tools:
  - Task
  - Read
  - Glob
  - Grep
  - Bash
---

# Smart Test Command

Intelligent test command that adapts to context:
- **Plan-aware mode**: Reads Gherkin scenarios from plan and validates implementation
- **Standalone mode**: Parses description to determine appropriate test type

## Workflow

### Step 1: Detect Plan File

Search for plan file in current project:

```bash
# Look in project plans directories
find . -path "*/plans/*.md" -type f | grep -E "(apps|libs|tools)" | sort -r | head -1
```

If plan file found, go to **Step 2: Plan-Aware Mode**
If no plan file, go to **Step 3: Standalone Mode**

### Step 2: Plan-Aware Mode

**When plan file exists**, use Gherkin scenarios to guide testing:

1. **Read the plan file**:
   ```
   Read(<plan_file_path>)
   ```

2. **Parse Gherkin sections**:
   - Extract User Requirements section → Browser testing scenarios
   - Extract Technical Specifications section → API/CLI testing scenarios

3. **Determine test types based on Gherkin content**:

   **For User Requirements** (always browser testing):
   - User-focused scenarios test UI flows
   - Launch browser-explorer agent

   **For Technical Specifications** (analyze keywords):
   - API indicators: "endpoint", "POST", "GET", "REST", "GraphQL", "status code"
     → Launch api-explorer agent
   - CLI indicators: "command", "script", "shell", "exit code", "stdout"
     → Launch cli-tester agent

4. **Launch appropriate agents**:

   For browser testing:
   ```typescript
   Task({
     subagent_type: "exploratory-tester:browser-explorer",
     description: "Test User Requirements scenarios",
     prompt: `Validate implementation against User Requirements:

${user_requirements_gherkin}

Test each scenario systematically. Report findings.`
   })
   ```

   For API testing:
   ```typescript
   Task({
     subagent_type: "exploratory-tester:api-explorer",
     description: "Test Technical Specifications",
     prompt: `Validate API implementation against Technical Specifications:

${technical_specs_gherkin}

Test endpoints, authentication, error handling. Report findings.`
   })
   ```

   For CLI testing:
   ```typescript
   Task({
     subagent_type: "exploratory-tester:cli-tester",
     description: "Test CLI specifications",
     prompt: `Validate CLI implementation against Technical Specifications:

${technical_specs_gherkin}

Test commands, output, exit codes. Report findings.`
   })
   ```

5. **Report results**:
   - Scenarios validated ✓
   - Failures found ✗
   - Return to implementation if failures

### Step 3: Standalone Mode

**When no plan file**, parse user's test description:

1. **Analyze description for test type signals**:

   **Browser testing signals**:
   - Keywords: "UI", "page", "form", "button", "login", "navigate", "click"
   - Default choice if ambiguous

   **API testing signals**:
   - Keywords: "API", "endpoint", "/api/", "POST", "GET", "REST", "GraphQL"
   - URL patterns

   **CLI testing signals**:
   - Keywords: "command", "script", "CLI", "binary", "shell"

2. **Launch appropriate agent** with user's description:

   ```typescript
   Task({
     subagent_type: "exploratory-tester:<type>-explorer",
     description: "Exploratory testing",
     prompt: `$ARGUMENTS

Conduct comprehensive exploratory testing. Report findings.`
   })
   ```

3. **Default to browser** if ambiguous

### Step 4: Report Results

Summarize testing session:
```
## Testing Complete

**Mode**: Plan-aware / Standalone
**Type**: Browser / API / CLI
**Scenarios tested**: N
**Passed**: X
**Failed**: Y

<details of failures>
```

## Usage Examples

**With plan**:
```
/tommymorgan:test
```
→ Automatically reads plan, tests all scenarios

**Without plan** (browser):
```
/tommymorgan:test the login flow
```
→ Browser testing of login functionality

**Without plan** (API):
```
/tommymorgan:test POST /api/users endpoint
```
→ API testing of users endpoint

**Without plan** (CLI):
```
/tommymorgan:test the deploy script
```
→ CLI testing of deployment script
