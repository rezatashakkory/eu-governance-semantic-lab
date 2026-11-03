"""SHACL tests: the real data must pass, each deliberately broken file must fail."""

import pytest

from semlab.validation import validate_graph


def test_real_data_conforms(graph):
    result = validate_graph(graph)
    assert result.conforms, result.report_text
    assert result.violations == []


def test_real_data_has_no_warnings(graph):
    assert validate_graph(graph).warnings == []


# (file, text that must appear in a violation message)
NEGATIVE_CASES = [
    ("broken_concept_no_english_label.ttl", "English preferred label"),
    ("broken_concept_no_definition.ttl", "needs a definition"),
    ("broken_duplicate_label.ttl", "already used by another concept"),
    ("broken_two_labels_same_language.ttl", "only one preferred label per language"),
    ("broken_parent_not_updated.ttl", "does not list it as narrower"),
    ("broken_celex_pattern.ttl", "CELEX number such as 32016R0679"),
    ("broken_celex_type_mismatch.ttl", "type letter R"),
    ("broken_dataset_no_license_no_publisher.ttl", "must have a license"),
    ("broken_dataset_no_license_no_publisher.ttl", "must have a publisher"),
]


@pytest.mark.parametrize(("filename", "expected"), NEGATIVE_CASES)
def test_broken_data_fails(with_extra, filename, expected):
    result = validate_graph(with_extra(filename))
    assert not result.conforms
    assert any(expected in f.message for f in result.violations), [
        f.message for f in result.findings
    ]


def test_missing_translations_are_warnings_only(with_extra):
    result = validate_graph(with_extra("broken_missing_translations.ttl"))
    assert result.conforms
    messages = [f.message for f in result.warnings]
    assert any("no French" in m for m in messages)
    assert any("no German" in m for m in messages)


def test_findings_name_the_broken_node(with_extra):
    result = validate_graph(with_extra("broken_celex_pattern.ttl"))
    assert any(f.focus.endswith("act/broken-test") for f in result.violations)
