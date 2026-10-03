"""Keep the Makefile help aligned with its documented sections."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_make_help_groups_targets_by_section_without_pipe_color() -> None:
    result = subprocess.run(["make", "help"], cwd=ROOT, capture_output=True, text=True, check=True)
    output = result.stdout

    sections = (
        "General",
        "Setup and Installation",
        "Interactive Examples",
        "Code Quality",
        "Testing",
        "Dependencies",
        "Build",
        "Release",
        "Cleanup",
        "Validation",
    )
    positions = [output.index(f"\n  {section}\n") for section in sections]
    assert positions == sorted(positions)
    assert "  help" in output[positions[0] : positions[1]]
    assert "  test-galaga" in output[positions[4] : positions[5]]
    assert "  release" in output[positions[7] : positions[8]]
    assert "\x1b[" not in output
