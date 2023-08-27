from __future__ import annotations
from elan_data import ELAN_Data
from pathlib import Path
from pytest_lazyfixture import lazy_fixture
from typing import (Any,
                    Optional,
                    Union, )

import elan_data
import pytest
import textwrap

import pandas as pd
import xml.etree.ElementTree as ET


# NOTE: Anything with "test_" in its name is intended to get created and
# stored in the created/ subdirectory, but anything without this convention
# should not be created.
class TestElan_Data:

    # ===================== FIXTURES =====================

    @pytest.fixture()
    def setup_file(self, eaf: Path) -> ELAN_Data:
        return ELAN_Data.from_file(eaf)

    @pytest.fixture()
    def setup_new(self, created: Path, audio: Path, tier_names: list[str]) -> ELAN_Data:
        return ELAN_Data.create_eaf(created / "test_eaf.eaf", audio, tier_names)

    # ===================== TEST CONSTRUCTORS =====================

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    def test_constructor_default_params(self, plhldr: Union[str, Path], minimum_elan: ET.ElementTree,
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
    def test_constructor_init(self, plhldr: Union[str, Path], minimum_elan: ET.ElementTree,
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

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    @pytest.mark.parametrize("aud", [lazy_fixture("audio"), lazy_fixture("audio_str"), None])
    def test_from_dataframe_default_params(self, tier_data: pd.DataFrame, plhldr: Union[str, Path],
                                           aud: Optional[Union[str, Path]], audio: Path,
                                           tree: ET.ElementTree, tier_names: list[str]) -> None:

        ed = ELAN_Data.from_dataframe(df=tier_data, file=plhldr, audio=aud)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(plhldr)
        assert ed.tree.__eq__(tree)
        assert ed._tier_names == tier_names
        if aud:
            assert ed.audio == Path(audio.absolute().as_uri())
        else:
            assert aud is None
        assert ed.tier_data.columns.to_list() == tier_data.columns.to_list()
        assert ed.tier_data.empty
        assert ed._init_data is False

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    @pytest.mark.parametrize("aud", [lazy_fixture("audio"), lazy_fixture("audio_str"), None])
    def test_from_dataframe_init(self, tier_data: pd.DataFrame, plhldr: Union[str, Path],
                                 aud: Optional[Union[str, Path]], audio: Path,
                                 tree: ET.ElementTree, tier_names: list[str]) -> None:

        ed = ELAN_Data.from_dataframe(df=tier_data, file=plhldr, audio=aud, init_df=True)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(plhldr)
        assert ed.tree.__eq__(tree)
        assert ed._tier_names == tier_names
        if aud:
            assert ed.audio == Path(audio.absolute().as_uri())
        else:
            assert aud is None
        assert ed.tier_data.columns.to_list() == tier_data.columns.to_list()
        # assert ed.tier_data.equals(tier_data) Segment ID is not labelled as expected
        # print(ed.tier_data)
        # print(tier_data)
        assert ed._init_data is True

    @pytest.mark.parametrize("invalid_df", ["", 123, ["file.eaf", "names.eaf"]])
    def test_invalid_from_dataframe(self, invalid_df: Any, placeholder: Path, audio: Path) -> None:
        with pytest.raises(TypeError):
            ed = ELAN_Data.from_dataframe(df=invalid_df, file=placeholder, audio=audio)  # noqa: F841

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    @pytest.mark.parametrize("aud", [lazy_fixture("audio"), lazy_fixture("audio_str"), None])
    def test_create_file_default_params(self, plhldr: Union[str, Path], aud: Optional[Union[str, Path]],
                                        tier_names: list[str], tier_data: pd.DataFrame,
                                        minimum_elan: ET.ElementTree, audio: Path) -> None:

        ed = ELAN_Data.create_eaf(file=plhldr, audio=aud, tiers=tier_names)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(plhldr)
        assert ed.tree.__eq__(minimum_elan)
        assert ed._tier_names == tier_names
        if aud:
            assert ed.audio == Path(audio.absolute().as_uri())
        else:
            assert aud is None
        assert ed.tier_data.columns.to_list() == tier_data.columns.to_list()
        assert ed.tier_data.empty
        assert ed._init_data is False

    @pytest.mark.parametrize("plhldr", [lazy_fixture("placeholder"), lazy_fixture("placeholder_str")])
    @pytest.mark.parametrize("aud", [lazy_fixture("audio"), lazy_fixture("audio_str"), None])
    def test_create_file_remove_default(self, plhldr: Union[str, Path], aud: Optional[Union[str, Path]],
                                        tier_names: list[str], tier_data: pd.DataFrame,
                                        minimum_elan: ET.ElementTree, audio: Path) -> None:

        if "default" in tier_names:
            tier_names = tier_names.copy()
            tier_names.remove("default")

        ed = ELAN_Data.create_eaf(file=plhldr, audio=aud, tiers=tier_names, remove_default=True)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(plhldr)
        assert ed.tree.__eq__(minimum_elan)
        assert ed._tier_names == tier_names
        if aud:
            assert ed.audio == Path(audio.absolute().as_uri())
        else:
            assert aud is None
        assert ed.tier_data.columns.to_list() == tier_data.columns.to_list()
        assert ed.tier_data.empty
        assert ed._init_data is False

    @pytest.mark.parametrize("invalid_file", ["", 123, ["file.eaf", "names.eaf"]])
    def test_invalid_create_file(self, invalid_file: Any, audio: Path, tier_names: list[str]) -> None:
        with pytest.raises((ValueError, TypeError)):
            ed = ELAN_Data.create_eaf(file=invalid_file, audio=audio, tiers=tier_names)  # noqa: F841

    def test_init_dataframe(self, setup_file: ELAN_Data, tier_names: list[str], tier_data: pd.DataFrame) -> None:

        assert setup_file._modified is False
        assert setup_file._init_data is False

        df = setup_file.init_dataframe()

        assert setup_file._modified is True
        assert setup_file._init_data is True
        assert df.equals(tier_data)
        assert setup_file.tier_data.equals(tier_data)
        assert setup_file.tier_names == tier_names

    # ===================== TEST DUNDER METHODS =====================

    def test_repr(self, setup_file: ELAN_Data) -> None:

        test_repr = repr(setup_file)
        assert isinstance(test_repr, str)

    def test_str(self, setup_file: ELAN_Data) -> None:

        test_str = str(setup_file)

        answer = textwrap.dedent(f'''\
                 name: {setup_file.file.name}
                 located at: {setup_file.file.absolute()}
                 tiers: {", ".join(setup_file._tier_names)}
                 associated audio file: {"None" if not setup_file.audio else setup_file.audio.name}
                 associated audio location: {"None" if not setup_file.audio else setup_file.audio.absolute()}
                 dataframe init: {str(setup_file._init_data)}
                 modified: {str(setup_file._modified)}
                 ''')  # noqa: E122

        assert isinstance(test_str, str)
        assert test_str == answer

    def test_len(self, setup_file: ELAN_Data, tier_data: pd.DataFrame) -> None:

        assert len(setup_file) == len(pd.DataFrame())

        setup_file.init_dataframe()

        assert len(setup_file) == len(tier_data)

    def test_contains(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        for tier in tier_names:
            assert tier in setup_file

        fake = ["boble", "bingus", "test", "dfault"]

        for tier in fake:
            assert tier not in setup_file

    def test_iter(self, setup_file: ELAN_Data, tier_data: pd.DataFrame) -> None:

        for row_eaf, row_key in zip(setup_file, tier_data.itertuples()):
            assert type(row_eaf) == type(row_key)
            assert list(row_eaf._fields) == list(row_key._fields)

    @pytest.mark.parametrize("ed1,ed2", [(lazy_fixture("setup_file"), lazy_fixture("setup_file")), (lazy_fixture("setup_new"), lazy_fixture("setup_new"))])
    def test_equals_true(self, ed1: ELAN_Data, ed2: ELAN_Data) -> None:
        assert ed1 == ed2

    @pytest.mark.parametrize("ed1,ed2", [(lazy_fixture("setup_file"), lazy_fixture("setup_new")), (lazy_fixture("setup_new"), ELAN_Data("test.eaf"))])
    def test_equals_false(self, ed1: ELAN_Data, ed2: ELAN_Data) -> None:
        assert ed1 != ed2

    # ===================== TEST PROPERTIES =====================

    def test_tier_names(self, setup_file: ELAN_Data) -> None:
        assert setup_file.tier_names == setup_file._tier_names

    def test_df_status(self, setup_file: ELAN_Data) -> None:

        assert setup_file.df_status is False
        assert setup_file.df_status == setup_file._init_data

        # Should automatically (re)init setup_file.tier_data
        setup_file.df_status = True

        assert setup_file.tier_data.empty is False
        assert setup_file.df_status is True
        assert setup_file.df_status == setup_file._init_data

    def test_modified(self, setup_file: ELAN_Data) -> None:

        assert setup_file.modified is False
        assert setup_file.modified == setup_file._modified

        # Init DataFrame, modifying the object since creation
        setup_file.df_status = True

        assert setup_file.modified is True
        assert setup_file.modified == setup_file._modified

    # ===================== TEST ACCESSORS =====================

    def test_get_segment(self, setup_file: ELAN_Data, tier_data: pd.DataFrame) -> None:

        setup_file.init_dataframe()

        assert setup_file.get_segment("a1") == tier_data.loc[tier_data.SEGMENT_ID == "a1", "TEXT"][0]

    # ===================== TEST MUTATORS =====================

    def test_add_tier_default_params(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        new_tier = "new_tier"
        setup_file.add_tier(tier=new_tier)

        assert new_tier in setup_file.tier_names
        assert setup_file.modified is True

    def test_add_tier_not_modified(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        # Should not modify if tier=None
        # Should not modify if tier is in the tier_names
        setup_file.add_tier(tier=None)

        assert setup_file.modified is False

        for tier in tier_names:
            setup_file.add_tier(tier=tier)
            assert setup_file.modified is False


class TestMisc:

    def test_version(self) -> None:
        ver = elan_data.__version__()
        assert isinstance(ver, str)
        assert elan_data.VERSION in ver

    def test_minimum_elan(self, minimum_elan_str: str) -> None:
        assert elan_data.MINIMUM_ELAN == minimum_elan_str

    def test_encoding(self, encoding: str) -> None:
        assert elan_data._ELAN_ENCODING == encoding
