from pathlib import Path

from phase0.validators import validate_phase0


def test_phase0_contracts_are_valid() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    results = validate_phase0(data_dir)

    assert len(results) == 3
    assert all(result.ok for result in results), [result.message for result in results]

