from __future__ import annotations
from elan_data.tiers import (TierType,
                             Tier,
                             Subtier,
                             Segmentations, 
                             STEREOTYPE,
                             _STEREOTYPE, )
from pathlib import Path
from pytest_lazyfixture import lazy_fixture
from typing import (Any,
                    Optional,
                    Union, )

import pytest
import textwrap

import pandas as pd
import xml.etree.ElementTree as ET

class TestTierType:

    # ===================== FIXTURES =====================

    @pytest.fixture()
    def setup_tiertype(self) -> TierType:
        return TierType()

    @pytest.fixture()
    def setup_tag(self, eaf: Path) -> ET.Element:
        with open(eaf, 'r') as src:
             return ET.parse(src).find('.//LINGUISTIC_TYPE')

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
            tt = TierType(name=invalid_name)

    @pytest.mark.parametrize("invalid_stereotype", ["NONE", "Time Subdivision", 123])
    def test_invalid_stereotype_constructor(self, invalid_stereotype: Any) -> None:
        with pytest.raises(TypeError):
            tt = TierType(stereotype=invalid_stereotype)

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
            tt = TierType.from_xml(bad_tag)

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
             return ET.parse(src).find('.//TIER')

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

    @pytest.mark.parametrize("name,participant,annotator", 
                             [(None, "Alejandro", "Julia"), ("New Tier", None, "Alejandro"), ("", "", 123)])
    def test_constructor_invalid_params(self, name: Any, participant: Any, annotator: Any) -> None:
        with pytest.raises(TypeError):
            tier = Tier(name=name, participant=participant, annotator=annotator)

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
            tier = Tier.from_xml(tag=bad_tag, tier_type=TierType())

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

    # TODO: Add subtiers in the key.eaf ELAN file for testing
    # @pytest.fixture()
    # def setup_tag(self, eaf: Path) -> ET.Element:
    #     with open(eaf, 'r') as src:
    #          return ET.parse(src).find('.//TIER')

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

    @pytest.mark.parametrize("name,participant,annotator", 
                             [(None, "Alejandro", "Julia"), ("New Tier", None, "Alejandro"), ("", "", 123)])
    def test_constructor_invalid_params(self, name: Any, participant: Any, annotator: Any) -> None:
        with pytest.raises(TypeError):
            subtier = Subtier(name=name, participant=participant, annotator=annotator)

    # @pytest.mark.parametrize("tiertype", 
    #                          [TierType(), 
    #                           ET.Element("LINGUISTIC_TYPE", {"TIME_ALIGNABLE": "true", "GRAPHIC_REFERENCES": "false", "LINGUISTIC_TYPE_ID": "default-lt"}), ])
    # def test_from_xml(self, setup_tag: ET.Element, tiertype: Union[TierType, ET.Element]) -> None:

    #     setup_tag.attrib["PARTICIPANT"] = "Alejandro"
    #     setup_tag.attrib["ANNOTATOR"] = "Julia"

    #     tier = Tier.from_xml(tag=setup_tag, tier_type=tiertype)

    #     assert hasattr(tier, "name")
    #     assert hasattr(tier, "participant")
    #     assert hasattr(tier, "annotator")
    #     assert hasattr(tier, "tier_type")

    #     assert tier.name == "default"
    #     assert tier.participant == "Alejandro"
    #     assert tier.annotator == "Julia"
    #     assert tier.tier_type is not None

    # @pytest.mark.parametrize("bad_tag", [ET.Element("bad", {"bad_id": "badbadbad"}),
    #                                      ET.Element("TIER", {"PARENT_REF": "test this"}), ])
    # def test_invalid_from_xml(self, bad_tag: ET.Element) -> None:
    #     with pytest.raises((ValueError, TypeError)):
    #         tier = Tier.from_xml(tag=bad_tag, tier_type=TierType())

    # ===================== TEST DUNDER METHODS =====================

    def test_repr(self, setup_subtier: Tier) -> None:

        test_repr = repr(setup_subtier)
        assert isinstance(test_repr, str)

    def test_str(self, setup_subtier: Tier) -> None:

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
    def test_as_xml(self, setup_subtier: Tier, participant: str, annotator: str) -> None:

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
    pass