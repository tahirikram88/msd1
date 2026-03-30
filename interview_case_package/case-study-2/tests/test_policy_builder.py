import sys
from importlib import util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "main.py"
spec = util.spec_from_file_location("main", MODULE_PATH)
main = util.module_from_spec(spec)
sys.modules[spec.name] = main
spec.loader.exec_module(main)


def test_build_lifecycle_policy_has_expected_transitions():
    policy = main.build_lifecycle_policy()
    rules = policy["Rules"]
    assert len(rules) == 1
    transitions = rules[0]["Transitions"]
    assert transitions[0]["Days"] == 30
    assert transitions[0]["StorageClass"] == "STANDARD_IA"
    assert transitions[1]["Days"] == 180
    assert transitions[1]["StorageClass"] == "GLACIER"
