# This file contains all test fixtures
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from pathlib import Path
from typing import (Optional,
                    Union, )

import pytest

import pandas as pd
import xml.etree.ElementTree as ET

AUDIO = "./tests/test_recording.wav"
EAF = "./tests/test.eaf"
TIER_NAMES = ["default", "creator", "test_2", "THE FINAL TIER"]
TIER_DATA = pd.DataFrame({'TIER_ID':       ["creator",
                                            "creator",
                                            "creator",
                                            "creator",
                                            "test_2",
                                            "THE FINAL TIER", ],
                          'START':         [829,
                                            2263,
                                            4379,
                                            6406,
                                            2130,
                                            340, ],
                          'STOP':          [1329,
                                            4224,
                                            6193,
                                            6950,
                                            4330,
                                            7050, ],
                          'DURATION':      [1329 - 829,
                                            4224 - 2263,
                                            6193 - 4379,
                                            6950 - 6406,
                                            4330 - 2130,
                                            77050 - 340, ],
                          'TEXT':          ["Hello .",
                                            "This is a test recording .",
                                            "for the ELAN Data Object .",
                                            "",
                                            "This is a test recording",
                                            "This segment spans over everything - Extraneous text and symbols too! (!@*()#$UV#)*ÑÑÑñññóÓö^**++]})", ],
                          'SEGMENT_ID':    ["a1",
                                            "a2",
                                            "a3",
                                            "a5",
                                            "a6",
                                            "a7", ]})


class MockElanData:
    """
    Basic Mock object of Elan_Data providing the absolute basics for testing elan_utils.

    Assumptions
    ---

    - `pd.DataFrame` and all its respective functions work as expected.
    - Likewise with `xml.etree.ElementTree` (and its `ElementTree` object), `pathlib.Path`, and the built-in `list`.
    """

    def __init__(self, file: Union[str, Path], init_df: bool = True) -> None:

        # None of this is actually used, might be useful to see if methods/functions return the correct type however.
        if not isinstance(file, (str, Path)):
            raise TypeError("Incorrect type given")

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

    def from_file(file: Union[str, Path], init_df: bool) -> MockElanData:
        return MockElanData(file, init_df)


@pytest.fixture()
def mockelan() -> MockElanData:
    return MockElanData(EAF)


@pytest.fixture()
def mockelan_noinit() -> MockElanData:
    return MockElanData(EAF, init_df=False)


@pytest.fixture()
def audio() -> Path:
    return Path(AUDIO)


if __name__ == "__main__":

    test_mock = MockElanData(EAF)
    print(test_mock.tree)
