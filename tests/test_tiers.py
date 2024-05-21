from __future__ import annotations
from elan_data.tiers import (TierType,  # noqa F401
                             Tier,
                             Subtier,
                             Segmentations,
                             STEREOTYPE,
                             _STEREOTYPE, )
from pathlib import Path
from pytest_lazyfixture import lazy_fixture  # noqa F401
from typing import (Any,
                    Union, )

import pytest
import textwrap
import typing

import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET


class TestTierType:

    # ===================== FIXTURES =====================

    @pytest.fixture()
    def setup_tiertype(self) -> TierType:
        return TierType()

    @pytest.fixture()
    def setup_tag(self, eaf: Path) -> ET.Element:
        with open(eaf, 'r') as src:
            return typing.cast(ET.Element, ET.parse(src).find('.//LINGUISTIC_TYPE'))

    # ===================== TEST CONSTRUCTORS =====================

    def test_constructor_default_params(self) -> None:

        tt = TierType()

        assert hasattr(tt, "name")
        assert hasattr(tt, "stereotype")

        assert tt.name == "default-lt"
        assert tt.stereotype == "None"

    @pytest.mark.parametrize("stereotype", ["None", "Time_Subdivision", "Symbolic_Subdivision", "Symbolic_Association", "Included_In"])
    def test_constructor_init(self, stereotype: STEREOTYPE, name: str = "new-type") -> None:

        tt = TierType(name=name, stereotype=stereotype)

        assert hasattr(tt, "name")
        assert hasattr(tt, "stereotype")

        assert tt.name == name
        assert tt.stereotype == stereotype

    @pytest.mark.parametrize("invalid_name", [Path("test"), 123])
    def test_invalid_name_constructor(self, invalid_name: Any) -> None:
        with pytest.raises(TypeError):
            tt = TierType(name=invalid_name)  # noqa: F841

    @pytest.mark.parametrize("invalid_stereotype", ["NONE", "Time Subdivision", 123])
    def test_invalid_stereotype_constructor(self, invalid_stereotype: Any) -> None:
        with pytest.raises(TypeError):
            tt = TierType(stereotype=invalid_stereotype)  # noqa: F841

    @pytest.mark.parametrize("stereotype", ["None", "Time_Subdivision"])
    def test_from_xml(self, setup_tag: ET.Element, stereotype: STEREOTYPE) -> None:

        if stereotype != "None":
            setup_tag.attrib["CONSTRAINTS"] = stereotype

        tt = TierType.from_xml(setup_tag)

        assert hasattr(tt, "name")
        assert hasattr(tt, "stereotype")

        assert tt.name == "default-lt"
        assert tt.stereotype == stereotype

    def test_invalid_from_xml(self) -> None:

        bad_tag = ET.Element("bad", {"bad_id": "badbadbad"})

        with pytest.raises(ValueError):
            tt = TierType.from_xml(bad_tag)  # noqa: F841

    # ===================== TEST DUNDER METHODS =====================

    def test_repr(self, setup_tiertype: TierType) -> None:

        test_repr = repr(setup_tiertype)
        assert isinstance(test_repr, str)

    def test_str(self, setup_tiertype: TierType) -> None:

        test_str = str(setup_tiertype)

        answer = textwrap.dedent(f'''\
                 name: {setup_tiertype.name}
                 stereotype: {setup_tiertype.stereotype}
                 ''')  # noqa: E122

        assert isinstance(test_str, str)
        assert test_str == answer

    def test_hash(self, setup_tiertype: TierType) -> None:
        assert hash(setup_tiertype.name) == hash(setup_tiertype)

    # ===================== TEST PROPERTIES =====================

    def test_name(self, setup_tiertype: TierType) -> None:
        assert setup_tiertype.name == "default-lt"

    def test_stereotype(self, setup_tiertype: TierType) -> None:
        assert setup_tiertype.stereotype == "None"

    # ===================== OTHER METHODS =====================

    # as_xml(self)

    @pytest.mark.parametrize("stereotype", _STEREOTYPE)
    def test_as_xml(self, setup_tiertype: TierType, stereotype: STEREOTYPE) -> None:

        setup_tiertype.stereotype = stereotype
        tag = setup_tiertype.as_xml()

        assert hasattr(tag, "tag")
        assert hasattr(tag, "attrib")

        assert tag.attrib["LINGUISTIC_TYPE_ID"] == setup_tiertype.name
        assert tag.attrib["GRAPHIC_REFERENCES"] == "false"

        if stereotype == "None":

            assert tag.attrib["TIME_ALIGNABLE"] == "true"
            assert "CONSTRAINTS" not in tag.attrib.keys()

        elif stereotype == "Time_Subdivision":

            assert tag.attrib["TIME_ALIGNABLE"] == "true"
            assert tag.attrib["CONSTRAINTS"] == stereotype

        else:

            assert tag.attrib["TIME_ALIGNABLE"] == "false"
            assert tag.attrib["CONSTRAINTS"] == stereotype


class TestTier:

    # ===================== FIXTURES =====================

    @pytest.fixture()
    def setup_tier(self) -> Tier:
        return Tier(tier_type=TierType())

    @pytest.fixture()
    def setup_tag(self, eaf: Path) -> ET.Element:
        with open(eaf, 'r') as src:
            return typing.cast(ET.Element, ET.parse(src).find('.//TIER'))

    # ===================== TEST CONSTRUCTORS =====================

    def test_constructor_default_params(self) -> None:

        tier = Tier()

        assert hasattr(tier, "name")
        assert hasattr(tier, "participant")
        assert hasattr(tier, "annotator")
        assert hasattr(tier, "tier_type")

        assert tier.name == "default"
        assert tier.participant == ""
        assert tier.annotator == ""
        assert isinstance(tier.tier_type, TierType)

    @pytest.mark.parametrize("name,participant,annotator",
                             [("Default", "Alejandro", "Julia"), ("New Tier", "Alejandro", "Alejandro"), ("", "", "")])
    def test_constructor_init(self, name: str, participant: str, annotator: str) -> None:

        tier = Tier(name=name, participant=participant, annotator=annotator)

        assert hasattr(tier, "name")
        assert hasattr(tier, "participant")
        assert hasattr(tier, "annotator")
        assert hasattr(tier, "tier_type")

        assert tier.name == name
        assert tier.participant == participant
        assert tier.annotator == annotator
        assert isinstance(tier.tier_type, TierType)

    @pytest.mark.parametrize("name,participant,annotator,tier_type",
                             [(None, "Alejandro", "Julia", TierType()), ("New Tier", None, "Alejandro", TierType()), ("", "", 123, TierType()), ("1", "2", "3", None)])
    def test_constructor_invalid_params(self, name: Any, participant: Any, annotator: Any, tier_type: Any) -> None:
        with pytest.raises(TypeError):
            tier = Tier(name=name, participant=participant, annotator=annotator, tier_type=tier_type)  # noqa: F841

    @pytest.mark.parametrize("tiertype",
                             [TierType(),
                              ET.Element("LINGUISTIC_TYPE", {"TIME_ALIGNABLE": "true", "GRAPHIC_REFERENCES": "false", "LINGUISTIC_TYPE_ID": "default-lt"}), ])
    def test_from_xml(self, setup_tag: ET.Element, tiertype: Union[TierType, ET.Element]) -> None:

        setup_tag.attrib["PARTICIPANT"] = "Alejandro"
        setup_tag.attrib["ANNOTATOR"] = "Julia"

        tier = Tier.from_xml(tag=setup_tag, tier_type=tiertype)

        assert hasattr(tier, "name")
        assert hasattr(tier, "participant")
        assert hasattr(tier, "annotator")
        assert hasattr(tier, "tier_type")

        assert tier.name == "default"
        assert tier.participant == "Alejandro"
        assert tier.annotator == "Julia"
        assert isinstance(tier.tier_type, TierType)

    @pytest.mark.parametrize("bad_tag", [ET.Element("bad", {"bad_id": "badbadbad"}),
                                         ET.Element("TIER", {"PARENT_REF": "test this"}), ])
    def test_invalid_from_xml(self, bad_tag: ET.Element) -> None:
        with pytest.raises((ValueError, TypeError)):
            tier = Tier.from_xml(tag=bad_tag, tier_type=TierType())  # noqa: F841

    # ===================== TEST DUNDER METHODS =====================

    def test_repr(self, setup_tier: Tier) -> None:

        test_repr = repr(setup_tier)
        assert isinstance(test_repr, str)

    def test_str(self, setup_tier: Tier) -> None:

        test_str = str(setup_tier)

        answer = textwrap.dedent(f'''\
                name: {setup_tier.name}
                participant: {setup_tier.participant}
                annotator: {setup_tier.annotator}
                tier type: {setup_tier.tier_type.name}
                ''')  # noqa: E122

        assert isinstance(test_str, str)
        assert test_str == answer

    def test_hash(self, setup_tier: Tier) -> None:
        assert hash(setup_tier.name) == hash(setup_tier)

    # ===================== OTHER METHODS =====================

    # as_xml(self)

    @pytest.mark.parametrize("participant,annotator", [("", ""), ("Alejandro", "Julia")])
    def test_as_xml(self, setup_tier: Tier, participant: str, annotator: str) -> None:

        setup_tier.participant = participant
        setup_tier.annotator = annotator

        tag = setup_tier.as_xml()

        assert hasattr(tag, "attrib")

        assert tag.tag == "TIER"
        assert tag.attrib["TIER_ID"] == setup_tier.name
        assert tag.attrib["LINGUISTIC_TYPE_REF"] == setup_tier.tier_type.name

        if participant == "":
            assert "PARTICIPANT" not in tag.attrib.keys()
        else:
            assert tag.attrib["PARTICIPANT"] == participant

        if annotator == "":
            assert "ANNOTATOR" not in tag.attrib.keys()
        else:
            assert tag.attrib["ANNOTATOR"] == annotator


class TestSubtier:

    # ===================== FIXTURES =====================

    # TODO: Mock objects are not working at all for this, I don't know why.
    @pytest.fixture()
    def setup_subtier(self) -> Subtier:
        return Subtier(tier_type=TierType(), parent=Tier())

    @pytest.fixture()
    def setup_tags(self, eaf_sub: Path) -> tuple[ET.Element, ET.Element]:

        with open(eaf_sub, 'r') as src:
            subtier = ET.parse(src).find(".//*[@TIER_ID='Subtier']")

        with open(eaf_sub, 'r') as src:
            tier = ET.parse(src).find(".//*[@TIER_ID='Alejandro']")

        return (tier, subtier)

    # ===================== TEST CONSTRUCTORS =====================

    def test_constructor_default_params(self) -> None:

        subtier = Subtier()

        assert hasattr(subtier, "name")
        assert hasattr(subtier, "participant")
        assert hasattr(subtier, "annotator")
        assert hasattr(subtier, "tier_type")
        assert hasattr(subtier, "parent")

        assert subtier.name == "default"
        assert subtier.participant == ""
        assert subtier.annotator == ""
        assert isinstance(subtier.tier_type, TierType)
        assert isinstance(subtier.parent, (Tier, Subtier))

    @pytest.mark.parametrize("name,participant,annotator",
                             [("Default", "Alejandro", "Julia"), ("New Tier", "Alejandro", "Alejandro"), ("", "", "")])
    def test_constructor_init(self, name: str, participant: str, annotator: str) -> None:

        subtier = Subtier(name=name, participant=participant, annotator=annotator)

        assert hasattr(subtier, "name")
        assert hasattr(subtier, "participant")
        assert hasattr(subtier, "annotator")
        assert hasattr(subtier, "tier_type")
        assert hasattr(subtier, "parent")

        assert subtier.name == name
        assert subtier.participant == participant
        assert subtier.annotator == annotator
        assert isinstance(subtier.tier_type, TierType)
        assert isinstance(subtier.parent, (Tier, Subtier))

    @pytest.mark.parametrize("name,participant,annotator,parent",
                             [(None, "Alejandro", "Julia", Tier()), ("New Tier", None, "Alejandro", Subtier()), ("", "", 123, Tier()), ("", "", "", None)])
    def test_constructor_invalid_params(self, name: Any, participant: Any, annotator: Any, parent: Any) -> None:
        with pytest.raises(TypeError):
            subtier = Subtier(name=name, participant=participant, annotator=annotator, parent=parent)  # noqa: F841

    def test_from_xml(self, setup_tags: ET.Element) -> None:

        setup_tags[1].attrib["PARTICIPANT"] = "Alejandro"
        setup_tags[1].attrib["ANNOTATOR"] = "Julia"

        subtier = Subtier.from_xml(tag=setup_tags[1], tier_type=TierType(), parent=Tier(setup_tags[0].attrib['TIER_ID']))

        assert hasattr(subtier, "name")
        assert hasattr(subtier, "participant")
        assert hasattr(subtier, "annotator")
        assert hasattr(subtier, "tier_type")
        assert hasattr(subtier, "parent")

        assert subtier.name == "Subtier"
        assert subtier.participant == "Alejandro"
        assert subtier.annotator == "Julia"
        assert isinstance(subtier.tier_type, TierType)

    @pytest.mark.parametrize("bad_tag", [ET.Element("bad", {"bad_id": "badbadbad"}),
                                         ET.Element("TIER", {"PARENT_REF": "test this"}),
                                         ET.Element("TIER", {"bad_id": "badbadbad"})])
    def test_invalid_from_xml(self, bad_tag: ET.Element) -> None:
        with pytest.raises((ValueError, TypeError)):
            tier = Subtier.from_xml(tag=bad_tag, tier_type=TierType(), parent=Tier())

    # ===================== TEST DUNDER METHODS =====================

    def test_repr(self, setup_subtier: Subtier) -> None:

        test_repr = repr(setup_subtier)
        assert isinstance(test_repr, str)

    def test_str(self, setup_subtier: Subtier) -> None:

        test_str = str(setup_subtier)

        answer = textwrap.dedent(f'''\
                name: {setup_subtier.name}
                parent: {setup_subtier.parent.name}
                participant: {setup_subtier.participant}
                annotator: {setup_subtier.annotator}
                tier type: {setup_subtier.tier_type.name}
                ''')  # noqa: E122

        assert isinstance(test_str, str)
        assert test_str == answer

    # ===================== OTHER METHODS =====================

    # as_xml(self)

    @pytest.mark.parametrize("participant,annotator", [("", ""), ("Alejandro", "Julia")])
    def test_as_xml(self, setup_subtier: Subtier, participant: str, annotator: str) -> None:

        setup_subtier.participant = participant
        setup_subtier.annotator = annotator

        tag = setup_subtier.as_xml()

        assert hasattr(tag, "attrib")

        assert tag.tag == "TIER"
        assert tag.attrib["TIER_ID"] == setup_subtier.name
        assert tag.attrib["LINGUISTIC_TYPE_REF"] == setup_subtier.tier_type.name

        assert "PARENT_REF" in tag.attrib.keys()
        assert tag.attrib["PARENT_REF"] == setup_subtier.parent.name

        if participant == "":
            assert "PARTICIPANT" not in tag.attrib.keys()
        else:
            assert tag.attrib["PARTICIPANT"] == participant

        if annotator == "":
            assert "ANNOTATOR" not in tag.attrib.keys()
        else:
            assert tag.attrib["ANNOTATOR"] == annotator


class TestSegmentations:

    # ===================== FIXTURES =====================

    TYPES: dict[str, type] = {'TIER':     object,
                              'START':    np.int32,
                              'END':      np.int32,
                              'TEXT':     object,
                              'ID':       object,
                              'DURATION': np.int32, }

    @pytest.fixture()
    def setup_dictionary(self) -> dict:
        return {'TIER':     ['TEST_TIER'],
                'START':    [0],
                'END':      [5],
                'TEXT':     ['TEST TEXT'],
                'ID':       ['a3'],
                'DURATION': [5], }

    @pytest.fixture()
    def setup_dataframe(self, setup_dictionary: dict) -> pd.DataFrame:
        return pd.DataFrame(setup_dictionary)

    # ===================== TEST CONSTRUCTORS =====================

    def test_constructor_default_params(self) -> None:

        seg = Segmentations()

        assert hasattr(seg, "COLUMNS")
        assert hasattr(seg, "_ID")
        assert hasattr(seg, "segments")

        for column in seg.segments.columns:
            assert column in seg.COLUMNS

        for column in seg.COLUMNS:
            assert seg.segments[column].empty

        for column in self.TYPES:
            assert seg.segments[column].dtype == self.TYPES[column]

    @pytest.mark.parametrize("data", [lazy_fixture("setup_dictionary"), lazy_fixture("setup_dataframe")])
    def test_constructor_init(self, data: Any) -> None:

        seg = Segmentations(data=data)

        assert hasattr(seg, "COLUMNS")
        assert hasattr(seg, "_ID")
        assert hasattr(seg, "segments")

        for column in seg.segments.columns:
            assert column in seg.COLUMNS

        for column in seg.COLUMNS:
            if isinstance(data, dict):
                assert seg.segments[column].tolist() == data[column]
            else:
                assert seg.segments[column].eq(data[column]).all()

    def test_constructor_invalid_params(self) -> None:
        with pytest.raises(TypeError):
            seg = Segmentations(data=12)  # noqa: F841