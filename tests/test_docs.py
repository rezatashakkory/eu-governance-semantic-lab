"""Quality bar for the documentation: style, links, no placeholders."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN = sorted(
    p
    for p in ROOT.rglob("*.md")
    if not any(part in {".venv", ".git", ".cache", "node_modules"} for part in p.parts)
)

EN_DASH = chr(0x2013)
EM_DASH = chr(0x2014)

REQUIRED = [
    "README.md",
    "LICENSE",
    "STUDY_GUIDE.md",
    "LEARNING_NOTES.md",
    "INTERVIEW_QA.md",
    "DEMO_SCRIPT.md",
    "docs/guide_for_non_technical_users.md",
    "docs/how_to_add_a_concept.md",
    "docs/training_workshop_30min.md",
    "docs/modeling_decisions.md",
    "docs/sources_and_licenses.md",
    "docs/sparql_walkthrough.md",
    "docs/translations_to_review.md",
    "docs/ontology.html",
    "docs/img/overview.jpg",
    "Makefile",
    ".github/workflows/ci.yml",
    ".pre-commit-config.yaml",
]


def prose(text: str) -> str:
    """Markdown without fenced code blocks and inline code."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def test_required_files_exist():
    missing = [name for name in REQUIRED if not (ROOT / name).exists()]
    assert missing == []


def test_markdown_files_were_found():
    assert len(MARKDOWN) >= 12


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_em_dash_en_dash_or_double_hyphen_in_prose(path):
    text = prose(path.read_text(encoding="utf-8"))
    # Ignore table separator rows and html comments, which use hyphens as syntax.
    text = "\n".join(line for line in text.splitlines() if not re.fullmatch(r"[\s|:\-]+", line))
    found = re.findall(rf".{{0,20}}(?:{EN_DASH}|{EM_DASH}|--).{{0,20}}", text)
    assert found == []


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_relative_links_point_to_existing_files(path):
    text = path.read_text(encoding="utf-8")
    broken = []
    for target in re.findall(r"\]\(([^)\s]+)\)", prose(text)):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        file_part = target.split("#", 1)[0]
        if file_part and not (path.parent / file_part).exists():
            broken.append(target)
    assert broken == []


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_placeholder_text(path):
    text = path.read_text(encoding="utf-8")
    found = re.findall(r"\b(?:TODO|FIXME|TBD|lorem ipsum|XXX)\b", text, flags=re.I)
    assert found == []


def test_disclaimer_is_in_the_readme():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "not affiliated with" in text.lower()


def test_no_eu_logo_files():
    names = [
        p.name.lower() for p in ROOT.rglob("*") if p.suffix.lower() in {".png", ".svg", ".jpg"}
    ]
    assert not any("eu-logo" in n or "europa" in n for n in names)
