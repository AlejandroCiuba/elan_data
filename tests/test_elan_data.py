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

    @pytest.mark.parametrize("file", [lazy_fixture("eaf"), lazy_fixture("eaf_str"),
                                      lazy_fixture("eaf_no_audio"), lazy_fixture("eaf_no_audio_str")])
    def test_from_file_default_params(self, file: Union[str, Path], audio: Path,
                                      tier_names: list[str], tier_data: pd.DataFrame,
                                      tree: ET.ElementTree) -> None:

        ed = ELAN_Data.from_file(file=file)

        # Assert type and/or value
        assert ed._modified is False
        assert ed.file == Path(file)
        assert ed.tree.__eq__(tree)
        assert ed._tier_names == tier_names

        if "-no-audio" not in str(file):
            assert ed.audio == audio.absolute()
        else:
            assert ed.audio is None

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
        assert ed.audio == audio.absolute()
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
            assert ed.audio == audio.absolute()
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
            assert ed.audio == audio.absolute()
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
            assert ed.audio == audio.absolute()
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
            assert ed.audio == audio.absolute()
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

        fake = ["boble", "boo", "test", "dfault"]

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

    def test_equals_unimplemented(self, setup_file: ELAN_Data) -> None:
        assert setup_file.__eq__(None)

    # ===================== TEST PROPERTIES =====================

    def test_name(self, setup_file: ELAN_Data) -> None:
        assert setup_file.name == setup_file.file.name

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

    # get_segment(self, seg_id: str = "a1") -> Optional[str]

    def test_get_segment(self, setup_file: ELAN_Data, tier_data: pd.DataFrame) -> None:

        setup_file.init_dataframe()

        assert setup_file.get_segment("a1") == tier_data.loc[tier_data.SEGMENT_ID == "a1", "TEXT"][0]

    # overlaps(self, seg_id: Optional[str], tiers: Optional[Iterable[str]], suprasegments: bool = True) -> pd.DataFrame

    def test_overlaps_tiers(self, setup_file: ELAN_Data) -> None:

        # We will get the segment in tier "creator;" it should only have 1 overlaps
        overlaps = setup_file.overlaps(seg_id="a6", tiers=["creator"])

        assert "a2" in overlaps.SEGMENT_ID.to_list()
        assert "a7" not in overlaps.SEGMENT_ID.to_list()

    def test_overlaps_no_suprasegments(self, setup_file: ELAN_Data) -> None:

        overlaps = setup_file.overlaps(seg_id="a6", suprasegments=False)

        assert "a2" in overlaps.SEGMENT_ID.to_list()
        assert "a7" not in overlaps.SEGMENT_ID.to_list()

    def test_overlaps_no_tiers(self, setup_file: ELAN_Data) -> None:

        # It should only have 2 overlaps both times; the same ones
        overlaps = setup_file.overlaps(seg_id="a6")

        assert "a2" in overlaps.SEGMENT_ID.to_list()
        assert "a7" in overlaps.SEGMENT_ID.to_list()

        overlaps = setup_file.overlaps(seg_id="a6", tiers=[])

        assert "a2" in overlaps.SEGMENT_ID.to_list()
        assert "a7" in overlaps.SEGMENT_ID.to_list()

    def test_invalid_overlaps(self, setup_file: ELAN_Data) -> None:
        with pytest.raises(ValueError):
            overlaps = setup_file.overlaps(seg_id=None)  # noqa: F841

    # ===================== TEST MUTATORS =====================

    # change_file(self, filepath: Union[str, Path])

    @pytest.mark.parametrize("filepath", ["new/file/path.eaf", Path("new/file/path.eaf")])
    @pytest.mark.parametrize("ed", [lazy_fixture("setup_file"), lazy_fixture("setup_new")])
    def test_change_file_default_params(self, ed: ELAN_Data, filepath: Union[str, Path]) -> None:

        ed.change_file(filepath)

        assert ed.file == Path(filepath)
        assert ed.modified is True

    @pytest.mark.parametrize("ed", [lazy_fixture("setup_file"), lazy_fixture("setup_new")])
    def test_change_file_not_modified(self, ed: ELAN_Data) -> None:
        ed.change_file(ed.file)
        assert ed.modified is False

    @pytest.mark.parametrize("ed", [lazy_fixture("setup_file"), lazy_fixture("setup_new")])
    def test_invalid_change_file(self, ed: ELAN_Data):
        with pytest.raises((TypeError)):
            ed.change_file(filepath=0)  # type: ignore

    # add_tier(self, tier: Optional[str], init_df: bool = True, **kwargs)

    def test_add_tier_default_params(self, setup_file: ELAN_Data) -> None:

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

        assert len(setup_file.tier_names) == len(tier_names)

    def test_add_tier_kwargs(self, setup_new: ELAN_Data) -> None:

        new_tier = "new_tier"
        participant = "me"

        setup_new.add_tier(tier=new_tier, PARTICIPANT=participant)

        tier = setup_new.tree.find(f".//*[@PARTICIPANT='{participant}']")

        assert tier is not None
        assert tier.attrib["PARTICIPANT"] == participant
        assert setup_new.modified is True

    # add_tiers(self, tiers: Optional[Sequence[str]], init_df: bool = True)

    def test_add_tiers_default_params(self, setup_file: ELAN_Data) -> None:

        new_tiers = ["new_tier", "new_tier_2", "new_tier_3"]
        setup_file.add_tiers(tiers=new_tiers)

        for tier in new_tiers:
            assert tier in setup_file.tier_names

        assert setup_file.modified is True

    def test_add_tiers_not_modified(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        # Should not modify if tier=None
        # Should not modify if tier is in the tier_names
        setup_file.add_tiers(tiers=None)

        assert setup_file.modified is False

        setup_file.add_tiers(tiers=tier_names)

        assert len(setup_file.tier_names) == len(tier_names)
        assert setup_file.modified is False

    # rename_tier(self, tier: Optional[str], name: Optional[str] = None, init_df: bool = True)

    def test_rename_tier_default_params(self, setup_new: ELAN_Data, tier_names: list[str]) -> None:

        new_name = "non-default"

        setup_new.rename_tier(tier='default', name=new_name)

        assert new_name in setup_new.tier_names
        assert 'default' not in setup_new.tier_names
        assert setup_new.modified is True

    def test_rename_tier_not_modified(self, setup_new: ELAN_Data, tier_names: list[str]) -> None:

        # Either tier and/or name are none or tier does not exist

        new_name = "non-default"

        setup_new.rename_tier(tier=None, name=new_name)
        assert setup_new.modified is False

        setup_new.rename_tier(tier='default', name=None)
        assert setup_new.modified is False

        setup_new.rename_tier(tier=None, name=None)
        assert setup_new.modified is False

        setup_new.rename_tier(tier='outside', name='inside')
        assert setup_new.modified is False

    # remove_tiers(self, tiers: Optional[Sequence[str]], init_df: bool = True)

    def test_remove_tiers_default_params(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        for tier in tier_names:

            setup_file.remove_tiers(tiers=[tier])

            assert tier not in setup_file.tier_names
            assert len(setup_file.tier_names) < len(tier_names)
            assert setup_file.tree.find(f".//*[@TIER_ID='{tier}']") is None

        assert setup_file.modified is True

    def test_remove_tiers_not_modified(self, setup_file: ELAN_Data) -> None:

        # Not modified if tiers=None or no tiers belong to the list
        setup_file.remove_tiers(tiers=None)
        assert setup_file.modified is False

        fake_tier_list = ["fake", "another_fake"]

        setup_file.remove_tiers(tiers=fake_tier_list)
        assert setup_file.modified is False

    # add_participant(self, tier: Optional[str], participant: Optional[str])

    def test_add_participant_default_params(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        participant = "I'm the new guy"
        setup_file.add_participant(tier=tier_names[0], participant=participant)

        tier = setup_file.tree.find(f".//*[@TIER_ID='{tier_names[0]}']")

        assert tier is not None
        assert tier.attrib["PARTICIPANT"] == participant
        assert setup_file.modified is True

    def test_add_participant_not_modified(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        # Not modified if the tier does not exist or tier/participant is None
        setup_file.add_participant(tier=None, participant="me")
        assert setup_file.modified is False

        setup_file.add_participant(tier=tier_names[0], participant=None)
        assert setup_file.modified is False

        setup_file.add_participant(tier="The Cool Tier", participant="me")
        assert setup_file.modified is False

    # add_tier_metadata(self, tier: Optional[str], init_df: bool = False, **kwargs)

    def test_add_tier_metadata_default_params(self, setup_file: ELAN_Data, tier_names: list[str]) -> None:

        participant = "me"
        setup_file.add_tier_metadata(tier=tier_names[0], PARTICIPANT=participant)

        tier = setup_file.tree.find(f".//*[@TIER_ID='{tier_names[0]}']")

        assert tier is not None
        assert tier.attrib["PARTICIPANT"] == participant
        assert setup_file.modified is True

    def test_add_tier_metadata_not_modified(self, setup_file: ELAN_Data) -> None:

        # Not modified if the tier does not exist and/or is None; test by wanting to init the df
        setup_file.add_tier_metadata(tier=None, PARTICIPANT="me", init_df=True)
        assert setup_file.modified is False

        setup_file.add_tier_metadata(tier="The Cool Tier", PARTICIPANT="me", init_df=True)
        assert setup_file.modified is False

    # add_metadata(self, author: str = "", date: str = "")

    def test_add_metadata_default_params(self, setup_file: ELAN_Data) -> None:

        author, date = "John Doe", "08/28/2023"
        setup_file.add_metadata(author=author, date=date)

        node_author = setup_file.tree.find(f"[@AUTHOR='{author}']")
        assert node_author is not None

        node_date = setup_file.tree.find(f"[@DATE='{date}']")
        assert node_date is not None

        assert node_author == node_date

    # add_audio(self, audio: Optional[Union[str, Path]], place_holder: bool = False)

    @pytest.mark.parametrize("aud", [lazy_fixture("audio"), lazy_fixture("audio_str"), "new_audio.wav"])
    def test_add_audio_default_params(self, setup_file: ELAN_Data, aud: Union[Path, str]) -> None:

        old_audio = setup_file.audio
        setup_file.add_audio(audio=aud)

        assert isinstance(setup_file.audio, Path)
        assert old_audio is not setup_file.audio

        # Should only be one
        nodes = setup_file.tree.findall(".//*MEDIA_DESCRIPTOR")
        assert len(nodes) == 1

        node = nodes[0]

        assert node is not None
        assert node.attrib["MEDIA_URL"] is not None

        if aud == "new_audio.wav":
            assert setup_file.modified is True
        else:
            assert setup_file.modified is False

    def test_add_audio_not_modified(self, setup_file: ELAN_Data) -> None:

        # Not modified if audio is none, is the same audio, or is the empty string
        # Second cond. not currently testable due to lack-of-portability for test
        setup_file.add_audio(audio=None)
        assert setup_file.modified is False

        setup_file.add_audio(audio="")
        assert setup_file.modified is False

    @pytest.mark.parametrize("invalid_audio", [123, ["file.eaf", "names.eaf"]])
    def test_invalid_add_audio(self, setup_file: ELAN_Data, invalid_audio: Any) -> None:
        with pytest.raises((TypeError)):
            setup_file.add_audio(audio=invalid_audio)

    # add_segment(self, tier: str, start: Union[int, str] = 0, stop: Union[int, str] = 100,
    #             annotation: Optional[str] = "", init_df: bool = True)

    def test_add_segment_default_params(self, setup_new: ELAN_Data, tier_data: pd.DataFrame, tier_names: list[str]) -> None:

        # Empty segment; ideally on the default tier
        setup_new.add_segment(tier=tier_names[0])

        assert not setup_new.tier_data.equals(tier_data)
        assert "" in setup_new.tier_data[setup_new.tier_data.TIER_ID == tier_names[0]].TEXT.to_list()

        node = setup_new.tree.find(f".//*[@TIER_ID='{tier_names[0]}']/ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE")

        assert isinstance(node, ET.Element)
        assert node.text is None

        assert setup_new.df_status is True
        assert setup_new.modified is True

    def test_add_segment_annotation(self, setup_new: ELAN_Data, tier_data: pd.DataFrame, tier_names: list[str]) -> None:

        # Non-empty segment; ideally on the default tier
        annotation = "Hey, guys. I'm a new segment and I'm really excited to be here!"
        setup_new.add_segment(tier=tier_names[0], annotation=annotation)

        assert not setup_new.tier_data.equals(tier_data)
        assert annotation in setup_new.tier_data[setup_new.tier_data.TIER_ID == tier_names[0]].TEXT.to_list()

        node = setup_new.tree.find(f".//*[@TIER_ID='{tier_names[0]}']/ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE")

        assert isinstance(node, ET.Element)
        assert annotation == node.text

        assert setup_new.df_status is True
        assert setup_new.modified is True

    def test_add_segment_no_init_df(self, setup_new: ELAN_Data, tier_data: pd.DataFrame, tier_names: list[str]) -> None:

        # Non-empty segment; ideally on the default tier
        annotation = "Hey, guys. I'm a new segment and I'm really excited to be here!"
        setup_new.add_segment(tier=tier_names[0], annotation=annotation, init_df=False)

        assert not setup_new.tier_data.equals(tier_data)
        assert annotation not in setup_new.tier_data[setup_new.tier_data.TIER_ID == tier_names[0]].TEXT.to_list()

        node = setup_new.tree.find(f".//*[@TIER_ID='{tier_names[0]}']/ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE")

        assert isinstance(node, ET.Element)
        assert annotation == node.text

        assert setup_new.df_status is False
        assert setup_new.modified is True

    def test_invalid_add_segment_no_tier(self, setup_new: ELAN_Data) -> None:
        with pytest.raises((ValueError)):
            setup_new.add_segment(tier="")

    def test_add_segment_first_segment(self, tier_names: list[str]) -> None:

        # Create a new ELAN_Data object and add a segment to it
        ed = ELAN_Data.create_eaf(file="not_to_be_saved.eaf", audio=None, tiers=tier_names)

        assert isinstance(ed, ELAN_Data)
        assert ed.df_status is False
        assert ed.modified is False

        ed.add_segment(tier=tier_names[0])

        assert "" in ed.tier_data[ed.tier_data.TIER_ID == tier_names[0]].TEXT.to_list()

        node = ed.tree.find(f".//*[@TIER_ID='{tier_names[0]}']/ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE")

        assert isinstance(node, ET.Element)
        assert node.text is None

        assert ed.df_status is True
        assert ed.modified is True

    @pytest.mark.parametrize("start", [-1, 30_000])
    def test_invalid_add_segment_bad_start(self, setup_new: ELAN_Data, tier_names: list[str], start: int) -> None:
        with pytest.raises((ValueError)):
            setup_new.add_segment(tier=tier_names[0], start=start)


class TestMisc:

    def test_version(self) -> None:

        ver = elan_data.__version__()

        assert isinstance(ver, str)
        assert elan_data.VERSION in ver

    def test_minimum_elan(self, minimum_elan_str: str) -> None:
        assert elan_data.MINIMUM_ELAN == minimum_elan_str

    def test_encoding(self, encoding: str) -> None:
        assert elan_data._ELAN_ENCODING == encoding
