import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for path in (ROOT, os.path.join(ROOT, "tools")):
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest  # noqa: E402

from scoring import ALL_QUESTION_IDS  # noqa: E402


@pytest.fixture
def answers():
    """The worked example from the project: 60 / 70 / 50 / 65 / 55 -> overall 60.5."""
    return {
        "infra_1": 3, "infra_2": 2, "infra_3": 3, "infra_4": 2, "infra_5": 2,
        "process_1": 3, "process_2": 3, "process_3": 3, "process_4": 3, "process_5": 2,
        "people_1": 2, "people_2": 2, "people_3": 2, "people_4": 2, "people_5": 2,
        "data_1": 3, "data_2": 3, "data_3": 3, "data_4": 2, "data_5": 2,
        "security_1": 3, "security_2": 2, "security_3": 2, "security_4": 2, "security_5": 2,
    }


@pytest.fixture
def uniform():
    """Build an answer set where every question has the same value."""
    return lambda value: {q: value for q in ALL_QUESTION_IDS}


@pytest.fixture(scope="session")
def synthetic_rows():
    from generate_synthetic_dataset import generate

    return generate(per_archetype=60, seed=2026)
