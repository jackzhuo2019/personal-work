# Product Spec Generator

Turn a business description into structured product artifacts:
requirement breakdown → field definitions → state machine → interactive HTML prototype → test cases.
Each step has a review agent that adversarially checks for gaps.

## Pipeline

```
Input: "A library borrowing system"

  Step 1: Requirement Agent   → feature list, user roles, use cases
  Step 2: Data Model Agent    → fields, types, validation rules
  Step 3: State Machine Agent → borrowing state transitions diagram
  Step 4: Prototype Agent     → interactive HTML pages
  Step 5: Review Agent        → edge cases, deadlocks, permission gaps

Output: PRD.md + state-machine.svg + prototype.html + test-cases.json
```

## Usage

```bash
# Generate from a business description
python -m spec_generator "A library borrowing system with overdue reminders"

# Generate and open the prototype
python -m spec_generator "An inventory management system" --open

# Interactive mode (type description in prompt)
python -m spec_generator --interactive
```

## Configuration

Set LLM endpoint in `config/settings.yaml` or via environment variables.

## Requirements

- Python 3.10+
- OpenAI-compatible LLM API