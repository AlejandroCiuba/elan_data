# This file contains all test fixtures
# Created by Alejandro Ciuba, alc307@pitt.edu

from pathlib import Path

import pytest

AUDIO = "./tests/test_recording.wav"
EAF = "./tests/test.eaf"


@pytest.fixture()
def audio() -> Path:
    return Path(AUDIO)
