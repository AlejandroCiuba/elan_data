# Object to store tier information for the elan_data object
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from dataclasses import dataclass
from elan_data import _ELAN_ENCODING
from pathlib import Path
from typing import (Any,
                    Optional,
                    Union, )

import sys
import textwrap
import typing

import pandas as pd
import numpy as np
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


class Segmentations:
    '''
    Object used to store segmentation information.
    '''

    COLUMNS: set[str] = {'TIER', 'START', 'END', 'TEXT', 'ID', 'DURATION'}

    def __init__(self, data: Optional[Union[dict[str, list[Any]], pd.DataFrame]]):
        '''
        Default constructor.

        Parameters
        ---

        data : `dict` or `pd.DataFrame`
            Data to start the Segmentations object with.

        Notes
        ---

        - This constructor assumes all columns (Segmentation.COLUMNS) are provided.
        - This constructor makes a deep copy of any passed DataFrame; additional columns are dropped.
        - This object enforces strict column types:
            - `TIER` as `str`
            - `START` as `np.int32`
            - `END` as `np.int32`
            - `TEXT` as `str`
            - `ID` as `str`
            - `DURATION as `np.int32`
        - This constructore will automatically cast the provided data to these types.
        - Note that casting `TIER` to a `'category'` type is encouraged; only exception.
        '''

        if data is not None:
            if isinstance(data, dict):
                self.segments: pd.DataFrame = pd.DataFrame({'TIER':     data['TIER'],
                                                            'START':    data['START'],
                                                            'END':      data['END'],
                                                            'TEXT':     data['TEXT'],
                                                            'ID':       data['ID'],
                                                            'DURATION': data['DURATION'], })
            elif isinstance(data, pd.DataFrame):
                self.segments = data.copy(deep=True).drop(columns=set(data.columns).difference(self.COLUMNS))

            # Reinforce column types
            self.segments = self.segments.astype({'TIER':     str,
                                                  'START':    np.int32,
                                                  'END':      np.int32,
                                                  'TEXT':     str,
                                                  'ID':       str,
                                                  'DURATION': np.int32, })

        else:
            self.segments = pd.DataFrame.astype({'TIER':     str,
                                                 'START':    np.int32,
                                                 'END':      np.int32,
                                                 'TEXT':     str,
                                                 'ID':       str,
                                                 'DURATION': np.int32, })

    @typing.no_type_check  # Avoid unnecessary casting to clean-up code
    @classmethod
    def from_file(cls, file: Union[str, Path]) -> Segmentations:
        '''
        Extracts the segment information from an `.eaf` file.

        Returns
        ---

        - A `Segmentation` object.
        '''

        data = {'TIER':  [],
                'START': [],
                'END':   [],
                'TEXT':  [],
                'ID':    [], }

        with open(file, 'r', encoding=_ELAN_ENCODING) as src:
            tree = ET.parse(src)

        # 1. Get tier information
        for e in tree.findall(".//TIER"):

            tier = e.attrib["TIER_ID"]

            # Search for the information we'll need to extract time info from the XML tree
            search = f".//*[@TIER_ID='{tier}']//ALIGNABLE_ANNOTATION"
            aligns = [element.attrib for element in tree.findall(search)]

            data['TIER'].extend([tier] * len(aligns))

            # Get segmentation IDs
            data['ID'].extend([element['ANNOTATION_ID'] for element in aligns])

            # Get start and end times for all segments
            starts = [int(tree.find(f".//*[@TIME_SLOT_ID='{element['TIME_SLOT_REF1']}']").attrib['TIME_VALUE']) for element in aligns]
            data['START'].extend(starts)

            ends = [int(tree.find(f".//*[@TIME_SLOT_ID='{element['TIME_SLOT_REF2']}']").attrib['TIME_VALUE']) for element in aligns]
            data['END'].extend(ends)

            # Calculate durations
            data['DURATION'].extend([int(start - end) for start, end in zip(starts, ends)])

            # Get segmentation text values
            texts = []
            for text in [tree.find(f".//*[@TIER_ID='{tier}']//*[@ANNOTATION_ID='{element['ANNOTATION_ID']}']/ANNOTATION_VALUE").text for element in aligns]:
                texts.append(text if text is not None else "")

            data['TEXT'].extend(texts)

        # 2. Create the Segmentations object
        seg = cls(data=data)

        return seg

# ===================== DUNDER METHODS =====================

    def __repr__(self) -> str:
        return \
        textwrap.dedent(f'''\
        {type(self).__name__}({self.segments!r})
        ''')  # noqa: E122
