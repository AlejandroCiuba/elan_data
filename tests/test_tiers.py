from __future__ import annotations
from elan_data.tiers import (TierType,
                             Tier,
                             Subtier,
                             Segmentations, 
                             STEREOTYPE)
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

    def test_from_xml(self, setup_tag: ET.ElementTree) -> None:

        tt = TierType.from_xml(setup_tag)

        assert hasattr(tt, "name")
        assert hasattr(tt, "stereotype")

        assert tt.name == "default-lt"
        assert tt.stereotype == "None"

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

    def test_as_xml(self, setup_tiertype: TierType) -> None:

        tag = setup_tiertype.as_xml()

        assert hasattr(tag, "tag")
        assert hasattr(tag, "attrib")

        assert tag.attrib["LINGUISTIC_TYPE_ID"] == setup_tiertype.name
        assert tag.attrib["GRAPHIC_REFERENCES"] == "false"
        assert tag.attrib["TIME_ALIGNABLE"] == "true"


class TestTier:
    pass


class TestSubtier:
    pass


class TestSegmentations:
    pass