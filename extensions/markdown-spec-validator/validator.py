def validate_spec(content):
    issues = []

    required_sections = [
        "Requirements",
        "Tasks",
        "Plan"
    ]

    for section in required_sections:
        if f"## {section}".lower() not in content.lower():
            issues.append(f"Missing section: {section}")

    # Detect TODO placeholders
    if "TODO" in content:
        issues.append("Contains TODO placeholders")

    # Validate heading structure
    if "### Requirements" in content:
        issues.append(
            "Requirements should use level 2 heading (##)"
        )

    # Check empty sections
    lines = content.splitlines()

    for i, line in enumerate(lines):
        if line.startswith("##"):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                if next_line == "":
                    issues.append(
                        f"Empty section detected: {line}"
                    )

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


if __name__ == "__main__":
    sample = """
# AI Agent

## Requirements

TODO
"""

    result = validate_spec(sample)

    print(result)