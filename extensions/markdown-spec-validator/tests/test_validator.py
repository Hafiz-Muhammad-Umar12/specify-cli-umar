from validator import validate_spec


def test_valid_spec():
    content = """
# Test

## Requirements
Build API

## Tasks
Create routes

## Plan
Use FastAPI
"""

    result = validate_spec(content)

    assert result["valid"] is True


def test_missing_sections():
    content = "# Empty"

    result = validate_spec(content)

    assert result["valid"] is False