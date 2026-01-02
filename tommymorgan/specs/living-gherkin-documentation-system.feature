Feature: Living Gherkin Documentation System

  @user
  Scenario: Migration creates living specs from historical plans
      Given a project has multiple historical plans with Gherkin scenarios
      When I run the migration tool
      Then living .feature files are created in the specs/ directory
      And scenarios are grouped by feature area
      And user scenarios are tagged @user
      And technical scenarios are tagged @technical
  
    <!-- DONE -->

  @user
  Scenario: Plan tool shows related living scenarios during reconciliation
      Given I'm creating a new plan with Gherkin scenarios
      And living specs exist for the project
      When the plan tool performs interactive reconciliation
      Then it shows me existing scenarios similar to my drafted scenario
      And it asks whether I'm creating, replacing, extending, or deprecating
      And my choice is recorded as metadata on the plan scenario
  
    <!-- DONE -->

  @user
  Scenario: Work tool updates living specs after completing scenario
      Given I'm implementing a plan with scenario metadata
      When I complete a scenario implementation
      Then the work tool automatically updates the corresponding living spec
      And the scenario status changes to DONE
      And the "Living updated" field changes to YES
      And changes are committed to git
  
    <!-- DONE -->

  @user
  Scenario: User documentation excludes technical details
      Given living specs exist with @user and @technical scenarios
      When I generate user documentation
      Then only @user scenarios appear in the output
      And technical implementation details are excluded
      And the documentation is readable by non-developers
  
    <!-- DONE -->

  @user
  Scenario: Test coverage analysis shows gaps
      Given living specs exist for a project
      And some scenarios have corresponding tests
      When I run coverage analysis
      Then it shows which scenarios have tests
      And it shows which scenarios lack tests
      And it reports overall coverage percentage
  
    <!-- DONE -->

  @user
  Scenario: Developer documentation includes technical specs
      Given living specs exist with @technical scenarios
      When I generate developer documentation
      Then all @technical scenarios appear in the output
      And implementation requirements are clear
      And examples show expected behavior
  
    <!-- DONE -->

  @user
  Scenario: Documentation updates preserve existing style and structure
      Given user documentation already exists
      And living specs have minor changes
      When I regenerate documentation
      Then only the changed sections are updated
      And existing prose and explanations are preserved
      And the documentation voice and style remain consistent
      And the overall structure and organization are maintained
  
    <!-- DONE -->

  @user
  Scenario: Developers can discover living specs for a project
      Given I'm working on a project
      When I want to understand current functionality
      Then I can find living specs in the specs/ directory
      And each .feature file is named clearly by feature area
      And the file structure mirrors logical feature organization
  
    <!-- DONE -->
    @accessibility

  @user
  Scenario: Generated documentation is accessible
      Given documentation is generated from living specs
      When a user with accessibility needs reads the documentation
      Then it works with screen readers
      And it has proper heading hierarchy
      And it includes alt text for any diagrams
      And it has sufficient color contrast
  
    <!-- DONE -->
    @accessibility

  @user
  Scenario: Generated documentation supports keyboard navigation
      Given HTML documentation is generated
      When a user navigates using only keyboard
      Then all interactive elements are keyboard accessible
      And tab order follows logical reading order
      And skip links are available for long pages
  
    <!-- DONE -->
    @performance

  @user
  Scenario: Migration handles large numbers of plans efficiently
      Given a project with 50+ historical plans
      When the migration tool runs
      Then it completes within reasonable time (< 5 minutes)
      And it provides progress feedback
      And it doesn't consume excessive memory

  @user
  Scenario: User logs in successfully
    Given I am on the login page
    When I enter valid credentials
    Then I am redirected to my dashboard

  @technical
  Scenario: Migration parses Gherkin from plan markdown files
      Given a plan file with Gherkin code blocks in any sections
      When the migration tool processes the plan
      Then it extracts all scenarios from gherkin blocks
      And it uses intelligent inference to determine user vs technical
      And sections like "User Requirements" or "Requirements" are tagged @user
      And sections like "Technical Specifications" are tagged @technical
      And scenario structure is preserved (Given/When/Then)
      And it handles variations in section naming
  
    <!-- DONE -->
    @migration

  @technical
  Scenario: Smart inference detects similar scenarios
      Given two scenarios with similar names and steps
      When the migration compares them
      Then it calculates semantic similarity score
      And scores above 0.8 are treated as matches
      And scores below 0.8 are flagged for manual review
      And similarity weights: 60% name, 40% steps
  
    <!-- DONE -->
    @migration

  @technical
  Scenario: Migration groups scenarios by feature area
      Given extracted scenarios from multiple plans
      When the migration creates .feature files
      Then scenarios about the same feature are grouped together
      And each .feature file has a descriptive Feature name
      And files are named using kebab-case
      And files are placed in project's specs/ directory
  
    <!-- DONE -->
    @plan

  @technical
  Scenario: Plan tool loads existing living specs
      Given a project path is determined
      When the plan tool starts reconciliation
      Then it reads all .feature files from specs/ directory
      And it parses Feature and Scenario names
      And it builds a searchable index of existing scenarios
      And the index supports fuzzy name matching
  
    <!-- DONE -->
    @plan

  @technical
  Scenario: Plan tool records scenario metadata
      Given a user has chosen an action (creates/replaces/extends/removes/deprecates)
      When the plan tool writes the scenario to the plan file
      Then it adds metadata as comments before the scenario
      And metadata includes Living file path and scenario name
      And metadata includes Action type
      And metadata includes Status: TODO
      And metadata includes Living updated: NO
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool parses scenario metadata
      Given a plan scenario with metadata comments
      When the work tool processes the scenario
      Then it extracts the Living file path
      And it extracts the Action type
      And it extracts the Status
      And it extracts the Living updated flag
      And it uses this data to update living specs
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool applies "creates" action
      Given scenario metadata with Action: creates
      When the work tool updates living specs
      Then it appends the new scenario to the .feature file
      And it preserves the @user or @technical tag
      And it maintains Gherkin formatting
      And it doesn't modify existing scenarios
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool applies "replaces" action
      Given scenario metadata with Action: replaces and Living scenario name
      When the work tool updates living specs
      Then it finds the existing scenario by name
      And it completely replaces the scenario text
      And it preserves the Feature structure
      And other scenarios remain unchanged
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool applies "extends" action
      Given scenario metadata with Action: extends
      When the work tool updates living specs
      Then it finds the existing scenario
      And it adds new Given/When/Then steps
      And it preserves existing steps
      And it maintains step ordering
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool applies "removes" action
      Given scenario metadata with Action: removes
      When the work tool updates living specs
      Then it finds and deletes the scenario
      And the Feature structure remains valid
      And other scenarios are unaffected
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool applies "deprecates" action
      Given scenario metadata with Action: deprecates
      When the work tool updates living specs
      Then it adds @deprecated tag to the scenario
      And it adds a comment explaining deprecation
      And the scenario text remains intact
  
    <!-- DONE -->
    @work

  @technical
  Scenario: Work tool enforces strict sequential ordering
      Given I'm working through plan scenarios
      When I try to start scenario N+1
      Then the tool checks scenario N has Status: DONE
      And the tool checks scenario N has Living updated: YES
      And if either check fails, it halts with error message
      And the error shows which scenario is incomplete
  
    <!-- DONE -->
    @docs

  @technical
  Scenario: Doc generator filters scenarios by tag
      Given a .feature file with mixed @user and @technical scenarios
      When I generate docs with --tags @user
      Then only scenarios tagged @user are included
      And @technical scenarios are excluded
      And Feature structure is preserved
  
    <!-- DONE -->
    @docs

  @technical
  Scenario: Doc generator converts Gherkin to readable prose
      Given a scenario with Given/When/Then steps
      When the doc generator processes it
      Then it converts to narrative format
      And it uses present tense for user docs
      And it maintains logical flow
      And it's readable by non-technical users
  
    <!-- DONE -->
    @docs

  @technical
  Scenario: Doc generator reads existing documentation before updating
      Given a documentation file exists
      When the doc generator runs
      Then it reads the existing documentation first
      And it parses the current structure and sections
      And it identifies which sections correspond to which scenarios
      And it preserves non-scenario content like prose and examples
  
    <!-- DONE -->
    @docs

  @technical
  Scenario: Doc generator identifies changed scenarios through diff
      Given existing documentation and current living specs
      When the doc generator compares them
      Then it detects new scenarios (not in current docs)
      And it detects modified scenarios (changed steps)
      And it detects removed scenarios (in docs but not in specs)
      And it detects unchanged scenarios (same in both)
  
    <!-- DONE -->
    @docs

  @technical
  Scenario: Doc generator updates only affected sections
      Given a diff showing 2 changed scenarios out of 10
      When the doc generator updates documentation
      Then it regenerates sections for the 2 changed scenarios
      And it preserves sections for the 8 unchanged scenarios
      And it maintains transitions between sections
      And the document flows naturally
  
    <!-- DONE -->
    @docs

  @technical
  Scenario: Doc generator preserves non-scenario content
      Given documentation with explanatory prose, diagrams, and examples
      When the doc generator updates scenarios
      Then introductory paragraphs are preserved
      And code examples not derived from scenarios remain
      And diagrams and images are retained
      And only scenario-derived content is updated
  
    <!-- DONE -->
    @coverage

  @technical
  Scenario: Coverage analyzer finds test files
      Given a project with test files following naming conventions
      When the coverage analyzer runs
      Then it discovers test files in standard locations
      And it parses test names and descriptions
      And it builds a mapping of tests to scenarios
  
    <!-- DONE -->
    @coverage

  @technical
  Scenario: Coverage analyzer matches tests to scenarios
      Given a scenario name and a test name
      When the analyzer compares them
      Then it uses fuzzy matching to find correspondence
      And exact matches have highest confidence
      And similar names are flagged for review
      And unmatched scenarios are reported as gaps
  
    <!-- DONE -->
    @accessibility

  @technical
  Scenario: Doc generator creates semantic HTML structure
      Given Gherkin scenarios are converted to documentation
      When the doc generator creates HTML
      Then it uses semantic HTML5 elements
      And headings follow proper hierarchy (h1, h2, h3)
      And lists use proper list markup
      And code examples have language annotations
  
    <!-- DONE -->
    @performance

  @technical
  Scenario: Migration processes plans incrementally
      Given many plans need processing
      When the migration tool runs
      Then it processes plans in batches
      And it reports progress after each batch
      And it can resume if interrupted
      And memory usage stays bounded
  
    <!-- DONE -->
    @security

  @technical
  Scenario: File paths are validated to prevent path traversal
      Given a scenario metadata specifies a Living file path
      When the work tool processes the path
      Then it validates the path is within the project directory
      And it rejects paths containing ../ or absolute paths
      And it sanitizes the filename
      And it logs any validation failures
  
    <!-- DONE -->
    @security

  @technical
  Scenario: Doc generator sanitizes content to prevent injection
      Given user-provided scenario text contains special characters
      When the doc generator creates HTML
      Then it escapes HTML special characters
      And it prevents script injection
      And it sanitizes markdown content
      And it validates all links
  
    <!-- DONE -->
    @observability

  @technical
  Scenario: Migration reports detailed progress and errors
      Given the migration tool is processing plans
      When an error occurs
      Then it logs the error with context (plan file, scenario)
      And it continues processing remaining plans
      And it generates a summary report at the end
      And the report includes success/failure counts
  
    <!-- DONE -->
    @observability

  @technical
  Scenario: Work tool logs living spec updates
      Given the work tool updates a living spec
      When the update completes
      Then it logs which file was updated
      And it logs what action was performed
      And it logs the git commit hash
      And failures are logged with full context
  
    <!-- DONE -->
    @reliability

  @technical
  Scenario: Living spec update failure triggers rollback
      Given the work tool is updating a living spec
      When the file write fails
      Then it rolls back the partial update
      And it restores the original file
      And it marks the scenario Living updated: NO
      And it reports the error to the user
