# Documentation

## Living Gherkin Documentation System

### Migration parses Gherkin from plan markdown files
A plan file with gherkin code blocks in any sections: the migration tool processes the plan, it extracts all scenarios from gherkin blocks, it uses intelligent inference to determine user vs technical, sections like "user requirements" or "requirements" are tagged @user, sections like "technical specifications" are tagged @technical, scenario structure is preserved (given/when/then), it handles variations in section naming.

### Smart inference detects similar scenarios
Two scenarios with similar names and steps: the migration compares them, it calculates semantic similarity score, scores above 0.8 are treated as matches, scores below 0.8 are flagged for manual review, similarity weights: 60% name, 40% steps.

### Migration groups scenarios by feature area
Extracted scenarios from multiple plans: the migration creates .feature files, scenarios about the same feature are grouped together, each .feature file has a descriptive feature name, files are named using kebab-case, files are placed in project's specs/ directory.

### Plan tool loads existing living specs
A project path is determined: the plan tool starts reconciliation, it reads all .feature files from specs/ directory, it parses feature and scenario names, it builds a searchable index of existing scenarios, the index supports fuzzy name matching.

### Plan tool records scenario metadata
A user has chosen an action (creates/replaces/extends/removes/deprecates): the plan tool writes the scenario to the plan file, it adds metadata as comments before the scenario, metadata includes living file path and scenario name, metadata includes action type, metadata includes status: todo, metadata includes living updated: no.

### Work tool parses scenario metadata
A plan scenario with metadata comments: the work tool processes the scenario, it extracts the living file path, it extracts the action type, it extracts the status, it extracts the living updated flag, it uses this data to update living specs.

### Work tool applies "creates" action
Scenario metadata with action: creates: the work tool updates living specs, it appends the new scenario to the .feature file, it preserves the @user or @technical tag, it maintains gherkin formatting, it doesn't modify existing scenarios.

### Work tool applies "replaces" action
Scenario metadata with action: replaces and living scenario name: the work tool updates living specs, it finds the existing scenario by name, it completely replaces the scenario text, it preserves the feature structure, other scenarios remain unchanged.

### Work tool applies "extends" action
Scenario metadata with action: extends: the work tool updates living specs, it finds the existing scenario, it adds new given/when/then steps, it preserves existing steps, it maintains step ordering.

### Work tool applies "removes" action
Scenario metadata with action: removes: the work tool updates living specs, it finds and deletes the scenario, the feature structure remains valid, other scenarios are unaffected.

### Work tool applies "deprecates" action
Scenario metadata with action: deprecates: the work tool updates living specs, it adds @deprecated tag to the scenario, it adds a comment explaining deprecation, the scenario text remains intact.

### Work tool enforces strict sequential ordering
I'm working through plan scenarios: i try to start scenario n+1, the tool checks scenario n has status: done, the tool checks scenario n has living updated: yes, if either check fails, it halts with error message, the error shows which scenario is incomplete.

### Doc generator filters scenarios by tag
A .feature file with mixed @user and @technical scenarios: i generate docs with --tags @user, only scenarios tagged @user are included, @technical scenarios are excluded, feature structure is preserved.

### Doc generator converts Gherkin to readable prose
A scenario with given/when/then steps: the doc generator processes it, it converts to narrative format, it uses present tense for user docs, it maintains logical flow, it's readable by non-technical users.

### Doc generator reads existing documentation before updating
A documentation file exists: the doc generator runs, it reads the existing documentation first, it parses the current structure and sections, it identifies which sections correspond to which scenarios, it preserves non-scenario content like prose and examples.

### Doc generator identifies changed scenarios through diff
Existing documentation and current living specs: the doc generator compares them, it detects new scenarios (not in current docs), it detects modified scenarios (changed steps), it detects removed scenarios (in docs but not in specs), it detects unchanged scenarios (same in both).

### Doc generator updates only affected sections
A diff showing 2 changed scenarios out of 10: the doc generator updates documentation, it regenerates sections for the 2 changed scenarios, it preserves sections for the 8 unchanged scenarios, it maintains transitions between sections, the document flows naturally.

### Doc generator preserves non-scenario content
Documentation with explanatory prose, diagrams, and examples: the doc generator updates scenarios, introductory paragraphs are preserved, code examples not derived from scenarios remain, diagrams and images are retained, only scenario-derived content is updated.

### Coverage analyzer finds test files
A project with test files following naming conventions: the coverage analyzer runs, it discovers test files in standard locations, it parses test names and descriptions, it builds a mapping of tests to scenarios.

### Coverage analyzer matches tests to scenarios
A scenario name and a test name: the analyzer compares them, it uses fuzzy matching to find correspondence, exact matches have highest confidence, similar names are flagged for review, unmatched scenarios are reported as gaps.

### Doc generator creates semantic HTML structure
Gherkin scenarios are converted to documentation: the doc generator creates html, it uses semantic html5 elements, headings follow proper hierarchy (h1, h2, h3), lists use proper list markup, code examples have language annotations.

### Migration processes plans incrementally
Many plans need processing: the migration tool runs, it processes plans in batches, it reports progress after each batch, it can resume if interrupted, memory usage stays bounded.

### File paths are validated to prevent path traversal
A scenario metadata specifies a living file path: the work tool processes the path, it validates the path is within the project directory, it rejects paths containing ../ or absolute paths, it sanitizes the filename, it logs any validation failures.

### Doc generator sanitizes content to prevent injection
User-provided scenario text contains special characters: the doc generator creates html, it escapes html special characters, it prevents script injection, it sanitizes markdown content, it validates all links.

### Migration reports detailed progress and errors
The migration tool is processing plans: an error occurs, it logs the error with context (plan file, scenario), it continues processing remaining plans, it generates a summary report at the end, the report includes success/failure counts.

### Work tool logs living spec updates
The work tool updates a living spec: the update completes, it logs which file was updated, it logs what action was performed, it logs the git commit hash, failures are logged with full context.

### Living spec update failure triggers rollback
The work tool is updating a living spec: the file write fails, it rolls back the partial update, it restores the original file, it marks the scenario living updated: no, it reports the error to the user.
