# This file contains all test fixtures
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from elan_data import ELAN_Data
from pathlib import Path
from typing import (Optional,
                    Generator, )
from unittest import mock

import pytest

import pandas as pd
import xml.etree.ElementTree as ET

# Package directories
ELAN_DATA = "elan_data.ELAN_Data"
ELAN_UTILS = "elan_data.elan_utils"

# Test directories
TEST_DIR = "./tests"
KEYS = f"{TEST_DIR}/keys"

# Keys
CREATED = f"{TEST_DIR}/created"
AUDIO = f"{KEYS}/key.wav"
EAF = f"{KEYS}/key.eaf"
RTTM = f"{KEYS}/key.rttm"
RTTM_FILTERED = f"{KEYS}/key-filtered.rttm"
TXT = f"{KEYS}/key.txt"
TXT_FILTERED = f"{KEYS}/key-filtered.txt"

# Keys - Mock data setup
TIER_NAMES = ["default", "creator", "test_2", "THE FINAL TIER"]
TIER_DATA = pd.read_csv(f"{KEYS}/key.csv", keep_default_na=False)


class MockElan_Data:
    """
    Basic Mock object of Elan_Data providing the absolute basics for testing elan_utils.

    Assumptions
    ---

    - `pd.DataFrame` and all its respective functions work as expected.
    - Likewise with `xml.etree.ElementTree` (and its `ElementTree` object), `pathlib.Path`, and the built-in `list`.
    """

    def __init__(self, init_df: bool = True) -> None:

        with open(EAF, "r", encoding="UTF-8") as src:
            text = "\n".join(src.readlines(-1))
            self.tree = ET.ElementTree(ET.fromstring(text))

        self.file: Path = Path(EAF)
        self.audio: Optional[Path] = Path(AUDIO)
        self.tier_names: list[str] = TIER_NAMES

        if init_df:
            self.tier_data = TIER_DATA
            self.df_status = True
        else:
            self.tier_data = pd.DataFrame()
            self.df_status = False

    @staticmethod
    def from_file(file: str, init_df: bool) -> ELAN_Data:

        # None of this is actually used, might be useful to see if methods/functions return the correct type however.
        if not isinstance(file, (str, Path)):
            raise TypeError("Incorrect type given")

        return ELAN_Data("PLACEHOLDER.eaf")


@pytest.fixture()
def mock_elan() -> Generator:
    """
    Mocks the properties and methods of the ELAN_Data object.
    """

    mock_data = MockElan_Data()

    # Mimic values
    with mock.patch(f"{ELAN_DATA}", spec=True) as MockElan:
        mock_ed = MockElan.return_value
        mock_ed.file = mock_data.file
        mock_ed.audio = mock_data.audio
        mock_ed.tree = mock_data.tree
        mock_ed.tier_names = mock_data.tier_names
        mock_ed.tier_data = mock_data.tier_data

        yield mock_ed


@pytest.fixture()
def eaf() -> Path:
    return Path(EAF)


@pytest.fixture()
def eaf_str() -> str:
    return EAF


@pytest.fixture()
def audio() -> Path:
    return Path(AUDIO)


@pytest.fixture()
def audio_str() -> str:
    return AUDIO


@pytest.fixture()
def rttm() -> Path:
    return Path(RTTM)


@pytest.fixture()
def rttm_str() -> str:
    return RTTM


@pytest.fixture()
def rttm_filtered() -> Path:
    return Path(RTTM_FILTERED)


@pytest.fixture()
def rttm_filtered_str() -> str:
    return RTTM_FILTERED


@pytest.fixture()
def txt() -> Path:
    return Path(TXT)


@pytest.fixture()
def txt_str() -> str:
    return TXT


@pytest.fixture()
def txt_filtered() -> Path:
    return Path(TXT_FILTERED)


@pytest.fixture()
def txt_filtered_str() -> str:
    return TXT_FILTERED


@pytest.fixture()
def created() -> Path:
    """
    Filepath to where created files are stored
    """
    return Path(CREATED)


@pytest.fixture()
def created_str() -> str:
    """
    Filepath to where created files are stored
    """
    return CREATED


if __name__ == "__main__":

    test_mock = MockElan_Data()
    print(test_mock.tier_data)
    print(test_mock.tier_data.info())
