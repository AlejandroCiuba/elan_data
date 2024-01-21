# Object to store tier information for the elan_data object
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from dataclasses import dataclass
from elan_data import _ELAN_ENCODING
from pathlib import Path
from typing import Union

import sys
import textwrap
import typing

import pandas as pd
import xml.etree.ElementTree as ET

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

STEREOTYPE = Literal["None", "Time_Subdivision", "Symbolic_Subdivision", "Symbolic_Association", "Included_In"]


# ===================== TierType Class =====================

@dataclass
class TierType:
    '''
    Object used to store tier type information.
    '''

    name: str = "default-lt"  # LINGUISTIC_TYPE_ID
    stereotype: STEREOTYPE = "None"  # CONSTRAINTS (and TIME_ALIGNABLE)

    @classmethod
    def from_xml(cls, tag: ET.Element) -> TierType:
        '''
        Create a `TierType` object from a `LINGUISTIC_TYPE` tag.

        Parameters
        ---

        tag : `ET.Element`
            `LINGUISTIC_TYPE` tag.

        Returns
        ---

        - A `TierType` with the information from the `LINGUISTIC_TYPE` XML tag.
        '''

        type_obj = TierType(tag.attrib['LINGUISTIC_TYPE_ID'])

        if "CONSTRAINTS" in tag.attrib:
            type_obj.stereotype = typing.cast(STEREOTYPE, tag.attrib["CONSTRAINTS"])

        return type_obj

    def __str__(self) -> str:
        return \
        textwrap.dedent(f'''\
        name: {self.name}
        stereotype: {self.stereotype}
        ''')  # noqa: E122

    def as_xml(self) -> ET.Element:
        '''
        Takes the information of the tier type as a LINGUISTIC_TYPE XML tag.

        Returns
        ---

        - An XML tag as defined by `xml.etree.ElementTree.Element`.
        '''

        element = ET.Element("LINGUISTIC_TYPE")

        element.attrib["GRAPHIC_REFERENCES"] = "false"  # No support for graphic references yet
        element.attrib["LINGUISTIC_TYPE_ID"] = self.name

        if self.stereotype == "None":
            element.attrib["TIME_ALIGNABLE"] = "true"

        elif self.stereotype == "Time_Subdivision":

            element.attrib["TIME_ALIGNABLE"] = "true"
            element.attrib["CONSTRAINTS"] = self.stereotype

        else:

            element.attrib["TIME_ALIGNABLE"] = "false"
            element.attrib["CONSTRAINTS"] = self.stereotype

        return element


# ===================== Tier Class =====================

@dataclass()
class Tier:
    '''
    Object used to store and edit tier attribute and segmentation information.
    '''

    name: str = "default"
    participant: str = ""
    annotator: str = ""
    tier_type: TierType = TierType()  # Calling with no args is the default-lt type

    @classmethod
    def from_xml(cls, tag: ET.Element, tier_type: Union[ET.Element, TierType], **kwargs):
        '''
        Create a `Tier` object from a `TIER` tag.

        Parameters
        ---

        tag : `ET.Element`
            `TIER` tag.

        type : `ET.Element` or `TierType`
            Either a `LINGUISTIC_TYPE` XMl tag or `TierType` object for settings information.

        Returns
        ---

        - A `Tier` with the information from the `TIER` XML tag.

        Notes
        ---

        - `**kwargs` does nothing, see `Subtier.from_xml()` notes for more information.
        '''

        if "PARENT_REF" in tag.attrib:
            raise TypeError("Tried to create a Tier object from a subtier tag. Please use Subtier if there is a PARENT_ID attribute.")

        tier_type = tier_type if isinstance(tier_type, TierType) else TierType.from_xml(tier_type)
        tier = cls(name=tag.attrib['TIER_ID'], tier_type=tier_type)

        if "PARTICIPANT" in tag.attrib:
            tier.participant = tag.attrib['PARTICIPANT']

        if "ANNOTATOR" in tag.attrib:
            tier.annotator = tag.attrib['ANNOTATOR']

        return tier

    def __str__(self) -> str:
        return \
        textwrap.dedent(f'''\
        name: {self.name}
        tier type: {self.tier_type.name}
        ''')  # noqa: E122

    def as_xml(self) -> ET.Element:
        '''
        Takes the information of the tier type as a LINGUISTIC_TYPE XML tag.

        Returns
        ---

        - An XML tag as defined by `xml.etree.ElementTree.Element`.
        '''

        element = ET.Element("TIER")

        element.attrib["LINGUISTIC_TYPE_REF"] = self.tier_type.name
        element.attrib["TIER_ID"] = self.name

        return element


# ===================== Subtier Class =====================

@dataclass
class Subtier(Tier):
    '''
    Object used to store and edit tier attributes for a subtier.
    '''

    parent: Union[Tier, Subtier] = Tier()

    @classmethod
    def from_xml(cls, tag: ET.Element, tier_type: Union[ET.Element, TierType], **kwargs):
        '''
        Create a `Subtier` object from a `TIER` tag.

        Parameters
        ---

        tag : `ET.Element`
            `TIER` tag.

        type : `ET.Element` or `TierType`
            Either a `LINGUISTIC_TYPE` XMl tag or `TierType` object for settings information.

        **kwargs : name as `parent` which is either `ET.Element` `Tier` or `Subtier`
            Either a `Tier` or `Subtier` instance. Required.

        Returns
        ---

        - A `Subtier` with the information from the `TIER` XML tag.

        Notes
        ---

        - The reason the `parent` attribute is stored in the `**kwargs` catch-all argument is so
        this class' `from_xml` method's signature matches that of its parent class `Tier.from_xml()`.

        - The reason we cannot accept an `ET.Element` tag for the parent is because that parent's
        setting information would be stored in a separate tag that we would need to somehow search for.
        '''

        # Cannot take a TIER tag for the parent because its TierType settings would be
        # in a different tag. Therefore, recursively making the parents is impossible.

        if "PARENT_REF" not in tag.attrib:
            raise TypeError("Tried to create a Subtier object from a tier tag. Please use Tier if there is no PARENT_ID attribute.")

        tier_type = tier_type if isinstance(tier_type, TierType) else TierType.from_xml(tier_type)
        subtier = cls(name=tag.attrib['TIER_ID'], tier_type=tier_type, parent=kwargs['parent'])

        if "PARTICIPANT" in tag.attrib:
            subtier.participant = tag.attrib['PARTICIPANT']

        if "ANNOTATOR" in tag.attrib:
            subtier.annotator = tag.attrib['ANNOTATOR']

        return subtier

    def __str__(self) -> str:
        return \
        textwrap.dedent(f'''\
        name: {self.name}
        paret: {self.parent.name}
        tier type: {self.tier_type.name}
        ''')  # noqa: E122

    def as_xml(self) -> ET.Element:
        '''
        Takes the information of the tier type as a LINGUISTIC_TYPE XML tag.

        Returns
        ---

        - An XML tag as defined by `xml.etree.ElementTree.Element`.
        '''

        element = super().as_xml()
        element.attrib["PARENT_REF"] = self.parent.name

        return element


# ===================== Segmentation Class =====================
    
# TODO: Decide if I want the tier and subtier information here too

class Segmentations:
    '''
    Object used to store segmentation information.
    '''

    def __init__(self):
        '''
        Default constructor.
        '''

        self.segments: pd.DataFrame = pd.DataFrame({'TIER_ID':       [],
                                                    'START':         [],
                                                    'STOP':          [],
                                                    'TEXT':          [],
                                                    'SEGMENT_ID':    [],
                                                    'DURATION':      [], })

        # Keeps track of the unique tiers and subtiers for segments
        self.tiers: set[Tier] = set()
        self.subtiers: set[Subtier] = set()
        self.tier_types: set[TierType] = set()

    @classmethod
    def from_file(cls, file: Union[str, Path]) -> Segmentations:
        '''
        Extracts the segment and tier information from an `.eaf` file.

        Returns
        ---

        - A `Segmentation` object.
        '''

        seg = cls()

        with open(file, 'r', encoding=_ELAN_ENCODING) as src:
            tree = ET.parse(src)

        # 1. get tier information
        # Making subtiers requires making the parent tiers first
        for e in tree.findall(".//TIER"):

            if "PARENT_REF" not in e.attrib:

                tier_type = tree.find(f".//[@LINGUISTIC_TYPE_ID='{e.attrib['LINGUISTIC_TYPE_REF']}']")

                if tier_type is None:
                    raise TypeError("No tier type information found.")

                tier = Tier.from_xml(tag=e, tier_type=tier_type)
                seg.tiers.add(tier)
                seg.tier_types.add(tier.tier_type)

        return seg
