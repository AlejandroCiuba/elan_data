# Object to store tier information for the elan_data object
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from dataclasses import dataclass
from typing import Union

import sys
import textwrap

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

@dataclass
class Tier:
    '''
    Object used to store and edit tier attribute and segmentation information.
    '''

    name: str = "default"
    tier_type: TierType = TierType()  # Calling with no args is the default-lt type

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

        element = ET.Element("TIER")

        element.attrib["LINGUISTIC_TYPE_REF"] = self.tier_type.name
        element.attrib["TIER_ID"] = self.name
        element.attrib["PARENT_REF"] = self.parent.name

        return element
