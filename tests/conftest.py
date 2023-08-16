from pathlib import Path

import pytest

AUDIO = "./tests/test_recording.wav"
EAF = "./tests/test.eaf"

    
@pytest.fixture()
def audio() -> Path:
    return Path(AUDIO)
