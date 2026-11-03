from semlab.__main__ import main


def test_validate_succeeds_on_real_data(capsys):
    assert main(["validate"]) == 0
    assert "SHACL: conforms" in capsys.readouterr().out


def test_check_dist_succeeds(capsys):
    assert main(["check-dist"]) == 0
    assert "in sync" in capsys.readouterr().out


def test_queries_lists_and_runs(capsys):
    assert main(["queries"]) == 0
    assert "15" in capsys.readouterr().out
    assert main(["queries", "4"]) == 0
    assert "Personal data" in capsys.readouterr().out
    assert main(["queries", "14"]) == 0
    assert "False" in capsys.readouterr().out
    assert main(["queries", "99"]) == 2


def test_reason_prints_inferences(capsys):
    assert main(["reason"]) == 0
    assert "inferred" in capsys.readouterr().out
