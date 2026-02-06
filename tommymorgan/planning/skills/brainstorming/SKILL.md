---
name: brainstorming
description: Turn ideas into fully formed designs through collaborative dialogue
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

## The Process

### Phase 1: Understanding the Idea

**Check project context first:**
- Read relevant files, docs, recent commits
- Understand existing patterns and conventions
- Identify constraints from the codebase

**Ask questions one at a time:**
- Only one question per message
- Prefer multiple choice questions when possible
- Open-ended questions are fine when choices aren't clear
- Focus on understanding: purpose, constraints, success criteria

**Key questions to explore:**
- What problem does this solve?
- Who are the users?
- What are the success criteria?
- What are the constraints?
- What already exists that this relates to?

### Phase 2: Exploring Approaches

**Propose 2-3 different approaches:**
- Each approach should be meaningfully different
- Include tradeoffs for each
- Lead with your recommended option
- Explain why you recommend it

**Present options conversationally:**
```
I see three ways to approach this:

**Option 1: [Name]** (Recommended)
[Description]
- Pro: [advantage]
- Con: [disadvantage]

**Option 2: [Name]**
[Description]
- Pro: [advantage]
- Con: [disadvantage]

**Option 3: [Name]**
[Description]
- Pro: [advantage]
- Con: [disadvantage]

I recommend Option 1 because [reasoning].
```

### Phase 3: Presenting the Design

**Once you understand what to build:**
- Break design into sections of 200-300 words
- Before presenting each section to the user, run section-level expert review
- Ask after each section: "Does this section look right?"
- Wait for confirmation before continuing
- Be ready to revise if something doesn't fit

**Section-level expert review:**

Before the user sees each design section, route it to relevant experts based on content keywords:

| Section Content Keywords | Expert(s) Invoked |
|---|---|
| database, schema, migration, storage, persistence, query | Martin Kleppmann (Data-Intensive Systems) |
| page, form, button, display, UI, component, dashboard, click | Jakob Nielsen (Usability) |
| endpoint, request, response, REST, API, HTTP | REST API Guidelines skill + OWASP Security Expert |
| deploy, pipeline, build, release, CI/CD, container | Dave Farley (Continuous Delivery) |
| *(always)* | Marty Cagan (Product Strategy) — reviews every section for product value |

For each section:
1. Draft the section content
2. Identify matching keywords to determine which experts to invoke
3. Run the relevant expert review(s) on the section
4. Incorporate expert feedback into the section
5. Add a brief annotation noting which expert reviewed and what they suggested:
   ```
   > Reviewed by Martin Kleppmann: Suggested adding index strategy for the query pattern described.
   > Reviewed by Marty Cagan: Confirmed this delivers clear user value.
   ```
6. Present the improved section to the user

This adds latency to brainstorming but produces higher-quality designs. The end-of-plan Gherkin review (`/review-features`) still runs as a final pass, but the heavy lifting happens section-by-section here.

**Sections to cover:**
- Architecture overview
- Key components
- Data flow
- Error handling
- Testing approach
- Edge cases

### Phase 4: After the Design

**When invoked from the plan command** (`/tommymorgan:plan`):
- Return the validated design to the calling command
- The plan command handles file creation and expert review

**When invoked standalone:**
- Write validated design to `<project>/plans/YYYY-MM-DD-<topic>.md`
- Include all design decisions and rationale
- Commit the design document

**Implementation (if continuing):**
- Ask: "Ready to implement?"
- Use `/tommymorgan:work` to execute the plan

## Key Principles

**One question at a time**
Don't overwhelm with multiple questions. If a topic needs exploration, break it into sequential questions.

**Multiple choice preferred**
Easier to answer than open-ended. Use when you can enumerate reasonable options.

**YAGNI ruthlessly**
Remove unnecessary features from all designs. Build what's needed now, not what might be needed later.

**Explore alternatives**
Always propose 2-3 approaches before settling. The first idea is rarely the best.

**Incremental validation**
Present design in sections. Validate each before moving on. Catch misunderstandings early.

**Be flexible**
Go back and clarify when something doesn't make sense. The goal is the right design, not finishing fast.

## Anti-Patterns to Avoid

- Asking multiple questions in one message
- Jumping to implementation before design is clear
- Presenting the entire design at once
- Assuming you understand without asking
- Adding features "just in case"
- Skipping the alternatives exploration
