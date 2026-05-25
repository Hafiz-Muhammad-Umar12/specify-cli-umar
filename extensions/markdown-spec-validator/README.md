# Markdown Spec Validator

A lightweight Spec Kit extension for validating markdown specifications used in Spec-Driven Development workflows.

## Features

- Validates required sections
- Detects TODO placeholders
- Checks heading hierarchy
- Detects empty sections

## Required Sections

- Requirements
- Tasks
- Plan

## Example

```python
validate_spec(content)
```

## Output

```python
{
  "valid": False,
  "issues": [
    "Missing section: Tasks"
  ]
}
```