# This file contains all test fixtures
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from dataclasses import dataclass
from elan_data import ELAN_Data
from pathlib import Path
from typing import (Optional,
                    Generator, )
from unittest import mock

import pytest

import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

# Package directories and mocking
ELAN_DATA = "elan_data.ELAN_Data"
ELAN_UTILS = "elan_data.elan_utils"
ELAN_TIERS = "elan_data.tiers.TierType"

# Test directories
TEST_DIR = "./tests"
KEYS = f"{TEST_DIR}/keys"
CREATED = f"{TEST_DIR}/created"

# Keys
AUDIO = f"{KEYS}/key.wav"
EAF = f"{KEYS}/key.eaf"
EAF_NO_AUDIO = f"{KEYS}/key-no-audio.eaf"
EAF_SUB = f"{KEYS}/outside_APLS.eaf"
RTTM = f"{KEYS}/key.rttm"
RTTM_FILTERED = f"{KEYS}/key-filtered.rttm"
TXT = f"{KEYS}/key.txt"
TXT_FILTERED = f"{KEYS}/key-filtered.txt"
TXT_FORMATTED = f"{KEYS}/key-formatted.txt"

# Keys - Mock data setup
TIER_NAMES = ["default", "creator", "test_2", "THE FINAL TIER"]
TIER_DATA = pd.read_csv(f"{KEYS}/key.csv", keep_default_na=False).astype({'START': np.int32,
                                                                          'END': np.int32,
                                                                          'ID': str,
                                                                          'TIER': 'category',
                                                                          'TEXT': str,
                                                                          'DURATION': np.int32, })

# Proper default encoding
ELAN_ENCODING = "UTF-8"

# Minimum amount needed for an ELAN_Data file
MINIMUM_ELAN = \
'''
<?xml version="1.0" encoding="UTF-8"?>
<ANNOTATION_DOCUMENT AUTHOR="" DATE=""
    FORMAT="3.0" VERSION="3.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv3.0.xsd">
    <HEADER MEDIA_FILE="" TIME_UNITS="milliseconds">
    </HEADER>
    <TIME_ORDER/>
    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="default"/>
    <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
        LINGUISTIC_TYPE_ID="default-lt" TIME_ALIGNABLE="true"/>
    <CONSTRAINT
        DESCRIPTION="Time subdivision of parent annotation's time interval, no time gaps allowed within this interval" STEREOTYPE="Time_Subdivision"/>
    <CONSTRAINT
        DESCRIPTION="Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered" STEREOTYPE="Symbolic_Subdivision"/>
    <CONSTRAINT DESCRIPTION="1-1 association with a parent annotation" STEREOTYPE="Symbolic_Association"/>
    <CONSTRAINT
        DESCRIPTION="Time alignable annotations within the parent annotation's time interval, gaps are allowed" STEREOTYPE="Included_In"/>
</ANNOTATION_DOCUMENT>
'''  # noqa: E122

# Placeholder name for certain tests
NEW_EAF = "new.eaf"
DEFAULT_TIER_LIST = ["default"]
DEFAULT_TIER_DATA = pd.DataFrame({'TIER_ID':       [],
                                  'START':         [],
                                  'STOP':          [],
                                  'TEXT':          [],
                                  'SEGMENT_ID':    [],
                                  'DURATION':      [], })


# class MockElan_Data:
#     """
#     Basic Mock object of Elan_Data providing the absolute basics for testing elan_utils.

#     Assumptions
#     ---

#     - `pd.DataFrame` and all its respective functions work as expected.
#     - Likewise with `xml.etree.ElementTree` (and its `ElementTree` object), `pathlib.Path`, and the built-in `list`.
#     """

#     def __init__(self, init_df: bool = True) -> None:

#         with open(EAF, "r", encoding="UTF-8") as src:
#             text = "\n".join(src.readlines(-1))
#             self.tree = ET.ElementTree(ET.fromstring(text))

#         self.file: Path = Path(EAF)
#         self.audio: Optional[Path] = Path(AUDIO)
#         self.tier_names: list[str] = TIER_NAMES

#         if init_df:
#             self.tier_data = TIER_DATA
#             self.df_status = True
#         else:
#             self.tier_data = pd.DataFrame()
#             self.df_status = False

#     @staticmethod
#     def from_file(file: str, init_df: bool) -> ELAN_Data:

#         # None of this is actually used, might be useful to see if methods/functions return the correct type however.
#         if not isinstance(file, (str, Path)):
#             raise TypeError("Incorrect type given")

#         return ELAN_Data("PLACEHOLDER.eaf")


# @dataclass
# class MockTierType:
#     """
#     Basic Mock object of TierType providing the absolute basics for testing the tiers.py classes.

#     Assumptions
#     ---

#     - The attributes `name`, `stereotype` and `time_alignable` are all present.
#     - The `stereotype` attribute is among those found in `_STEREOTYPE`.
#     """

#     name: str = "default-lt"  # LINGUISTIC_TYPE_ID
#     stereotype: str = "None"  # CONSTRAINTS (and TIME_ALIGNABLE)
#     time_alignable: bool = True


# @pytest.fixture()
# def mock_elan() -> Generator:
#     """
#     Mocks the properties and methods of the ELAN_Data object.
#     """

#     mock_data = MockElan_Data()

#     # Mimic values
#     with mock.patch(f"{ELAN_DATA}", spec=True) as MockElan:
#         mock_ed = MockElan.return_value
#         mock_ed.file = mock_data.file
#         mock_ed.audio = mock_data.audio
#         mock_ed.tree = mock_data.tree
#         mock_ed.tier_names = mock_data.tier_names
#         mock_ed.tier_data = mock_data.tier_data

#         yield mock_ed


# @pytest.fixture()
# def mock_tiertype() -> Generator:
#     """
#     Mock the properties of the TierType object.
#     """

#     mock_type = MockTierType()

#     with mock.patch(f"{ELAN_TIERS}", spec=True) as MockType:

#         mock_tt = MockType.return_value
#         mock_tt.name = mock_type.name
#         mock_tt.stereotype = mock_type.stereotype
#         mock_tt.time_alignable = mock_type.time_alignable

#         yield mock_tt


# @pytest.fixture()
# def mock_data() -> MockElan_Data:
#     return MockElan_Data()


# @pytest.fixture()
# def mock_type() -> MockTierType:
#     return MockTierType()


@pytest.fixture()
def tree() -> ET.ElementTree:

    with open(EAF, "r", encoding="UTF-8") as src:

        text = "\n".join(src.readlines(-1))
        return ET.ElementTree(ET.fromstring(text))


@pytest.fixture()
def eaf() -> Path:
    return Path(EAF)


@pytest.fixture()
def eaf_str() -> str:
    return EAF


@pytest.fixture()
def eaf_no_audio() -> Path:
    return Path(EAF_NO_AUDIO)


@pytest.fixture()
def eaf_no_audio_str() -> str:
    return EAF_NO_AUDIO


@pytest.fixture()
def eaf_sub() -> Path:
    return Path(EAF_SUB)


@pytest.fixture()
def eaf_sub_str() -> str:
    return EAF_SUB


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
def txt_formatted() -> Path:
    return Path(TXT_FORMATTED)


@pytest.fixture()
def txt_formatted_str() -> str:
    return TXT_FORMATTED


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


@pytest.fixture()
def tier_names() -> list[str]:
    return TIER_NAMES


@pytest.fixture()
def tier_data() -> pd.DataFrame:
    return TIER_DATA


@pytest.fixture()
def encoding() -> str:
    return ELAN_ENCODING


@pytest.fixture()
def minimum_elan_str() -> str:
    return MINIMUM_ELAN


@pytest.fixture()
def minimum_elan() -> ET.ElementTree:
    return ET.ElementTree(ET.fromstring(MINIMUM_ELAN.strip()))


@pytest.fixture()
def placeholder() -> Path:
    return Path(NEW_EAF)


@pytest.fixture()
def placeholder_str() -> str:
    return NEW_EAF


@pytest.fixture()
def default_tier_list() -> list[str]:
    return DEFAULT_TIER_LIST


@pytest.fixture()
def default_tier_data() -> pd.DataFrame:
    return DEFAULT_TIER_DATA


if __name__ == "__main__":
    pass
