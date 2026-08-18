import pytest

from badger.core.tasks.blood_pressure import BloodPressure


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("Blood Pressure", True),
        ("blood pressure", False),
        ("Blood Pressure ", False),
        ("", False),
        ("Blood Glucose", False),
    ],
)
def test_matches_exact_task_name(entry: str, expected: bool) -> None:
    assert BloodPressure().matches(entry) is expected


def test_task_metadata() -> None:
    task = BloodPressure()

    assert task.id == "blood-pressure"
    assert task.name == "Blood Pressure"
