from __future__ import annotations
from elan_data import ELAN_Data
from pathlib import Path
from pytest_lazyfixture import lazy_fixture
from typing import (Any,
                    Union, )

import elan_data
import pytest

import pandas as pd
import xml.etree.ElementTree as ET


# NOTE: Anything with "test_" in its name is intended to get created and
# stored in the created/ subdirectory, but anything without this convention
# should not be created.
class TestElan_Data:

    @pytest.fixture()
    def setup_file(self, eaf: Path) -> ELAN_Data:
        return ELAN_Data.from_file(eaf)

    @pytest.fixture()
    def setup_new(self, created: Path, audio: Path, tier_names: list[str]) -> ELAN_Data:
        return ELAN_Data.create_eaf(created / "test_eaf.eaf", audio, tier_names)

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    def test_valid_constructor_default_params(self, plhldr: Union[str, Path], minimum_elan: ET.ElementTree,
                                              default_tier_list: list[str], default_tier_data: pd.DataFrame) -> None:

        ed = ELAN_Data(file=plhldr, init_df=False)

        # Assert existence of necessary attributes
        assert hasattr(ed, "_modified")
        assert hasattr(ed, "file")
        assert hasattr(ed, "tree")
        assert hasattr(ed, "_tier_names")
        assert hasattr(ed, "audio")
        assert hasattr(ed, "tier_data")
        assert hasattr(ed, "_init_data")

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(plhldr)
        assert ed.tree.__eq__(minimum_elan)
        assert ed._tier_names == default_tier_list
        assert ed.audio is None
        assert ed.tier_data.columns.to_list() == default_tier_data.columns.to_list()
        assert ed.tier_data.empty
        assert ed._init_data is False

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    def test_valid_constructor_init(self, plhldr: Union[str, Path], minimum_elan: ET.ElementTree,
                                    default_tier_list: list[str], default_tier_data: pd.DataFrame) -> None:
        ed = ELAN_Data(file=plhldr, init_df=True)

        # Assert existence of necessary attributes
        assert hasattr(ed, "_modified")
        assert hasattr(ed, "file")
        assert hasattr(ed, "tree")
        assert hasattr(ed, "_tier_names")
        assert hasattr(ed, "audio")
        assert hasattr(ed, "tier_data")
        assert hasattr(ed, "_init_data")

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(plhldr)
        assert ed.tree.__eq__(minimum_elan)
        assert ed._tier_names == default_tier_list
        assert ed.audio is None
        assert ed.tier_data.columns.to_list() == default_tier_data.columns.to_list()
        assert ed.tier_data.empty
        assert ed._init_data is True

    @pytest.mark.parametrize("invalid_file", ["", 123, ["file.eaf", "names.eaf"]])
    def test_invalid_constructor(self, invalid_file: Any) -> None:
        with pytest.raises((ValueError, TypeError)):
            ed = ELAN_Data(invalid_file)  # noqa: F841

    @pytest.mark.parametrize("file", [lazy_fixture("eaf"), lazy_fixture("eaf_str")])
    def test_from_file_default_params(self, file: Union[str, Path], audio: Path,
                                      tier_names: list[str], tier_data: pd.DataFrame,
                                      tree: ET.ElementTree) -> None:
        ed = ELAN_Data.from_file(file=file)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(file)
        assert ed.tree.__eq__(tree)
        assert ed._tier_names == tier_names
        assert ed.audio == Path(audio.absolute().as_uri())
        assert ed.tier_data.columns.to_list() == tier_data.columns.to_list()
        assert ed.tier_data.empty
        assert ed._init_data is False

    @pytest.mark.parametrize("file", [lazy_fixture("eaf"), lazy_fixture("eaf_str")])
    def test_from_file_init(self, file: Union[str, Path], audio: Path,
                            tier_names: list[str], tier_data: pd.DataFrame,
                            tree: ET.ElementTree) -> None:
        ed = ELAN_Data.from_file(file=file, init_df=True)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(file)
        assert ed.tree.__eq__(tree)
        assert ed._tier_names == tier_names
        assert ed.audio == Path(audio.absolute().as_uri())
        assert ed.tier_data.columns.to_list() == tier_data.columns.to_list()
        assert ed.tier_data.equals(tier_data)
        assert ed._init_data is True

    @pytest.mark.parametrize("invalid_file", ["", 123, ["file.eaf", "names.eaf"]])
    def test_invalid_from_file(self, invalid_file: Any) -> None:
        with pytest.raises((ValueError, TypeError)):
            ed = ELAN_Data.from_file(invalid_file)  # noqa: F841


class TestMisc:

    def test_version(self) -> None:
        ver = elan_data.__version__()
        assert isinstance(ver, str)
        assert elan_data.VERSION in ver

    def test_minimum_elan(self, minimum_elan_str: str) -> None:
        assert elan_data.MINIMUM_ELAN == minimum_elan_str

    def test_encoding(self, encoding: str) -> None:
        assert elan_data._ELAN_ENCODING == encoding
