# Documentation

## Living Gherkin Documentation System

### Migration creates living specs from historical plans
A project has multiple historical plans with gherkin scenarios: i run the migration tool, living .feature files are created in the specs/ directory, scenarios are grouped by feature area, user scenarios are tagged @user, technical scenarios are tagged @technical.

### Plan tool shows related living scenarios during reconciliation
I'm creating a new plan with gherkin scenarios: living specs exist for the project, the plan tool performs interactive reconciliation, it shows me existing scenarios similar to my drafted scenario, it asks whether i'm creating, replacing, extending, or deprecating, my choice is recorded as metadata on the plan scenario.

### Work tool updates living specs after completing scenario
I'm implementing a plan with scenario metadata: i complete a scenario implementation, the work tool automatically updates the corresponding living spec, the scenario status changes to done, the "living updated" field changes to yes, changes are committed to git.

### User documentation excludes technical details
Living specs exist with @user and @technical scenarios: i generate user documentation, only @user scenarios appear in the output, technical implementation details are excluded, the documentation is readable by non-developers.

### Test coverage analysis shows gaps
Living specs exist for a project: some scenarios have corresponding tests, i run coverage analysis, it shows which scenarios have tests, it shows which scenarios lack tests, it reports overall coverage percentage.

### Developer documentation includes technical specs
Living specs exist with @technical scenarios: i generate developer documentation, all @technical scenarios appear in the output, implementation requirements are clear, examples show expected behavior.

### Documentation updates preserve existing style and structure
User documentation already exists: living specs have minor changes, i regenerate documentation, only the changed sections are updated, existing prose and explanations are preserved, the documentation voice and style remain consistent, the overall structure and organization are maintained.

### Developers can discover living specs for a project
I'm working on a project: i want to understand current functionality, i can find living specs in the specs/ directory, each .feature file is named clearly by feature area, the file structure mirrors logical feature organization.

### Generated documentation is accessible
Documentation is generated from living specs: a user with accessibility needs reads the documentation, it works with screen readers, it has proper heading hierarchy, it includes alt text for any diagrams, it has sufficient color contrast.

### Generated documentation supports keyboard navigation
Html documentation is generated: a user navigates using only keyboard, all interactive elements are keyboard accessible, tab order follows logical reading order, skip links are available for long pages.

### Migration handles large numbers of plans efficiently
A project with 50+ historical plans: the migration tool runs, it completes within reasonable time (< 5 minutes), it provides progress feedback, it doesn't consume excessive memory.

### User logs in successfully
I am on the login page: i enter valid credentials, i am redirected to my dashboard.
