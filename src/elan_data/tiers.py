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
_STEREOTYPE = ["None", "Time_Subdivision", "Symbolic_Subdivision", "Symbolic_Association", "Included_In"]


# ===================== TierType Class =====================


@dataclass(init=False)
class TierType:
    '''
    Object used to store tier type information.
    '''

    name: str = "default-lt"  # LINGUISTIC_TYPE_ID
    stereotype: STEREOTYPE = "None"  # CONSTRAINTS (and TIME_ALIGNABLE)
    time_alignable: bool = True

    def __init__(self, name: str = "default-lt", stereotype: STEREOTYPE = "None"):

        if not isinstance(name, str):
            raise TypeError("name attribute is not of the correct type, str")

        if stereotype not in _STEREOTYPE:
            raise TypeError("stereotype attribute is not in STEREOTYPE")

        self.name = name
        self.stereotype = stereotype

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

        if tag.tag != "LINGUISTIC_TYPE":
            raise ValueError("Incorrect tag type, not LINGUISTIC_TYPE")

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

    def __post_init__(self):
        """
        Type checking for dataclass fields.
        """

        if not isinstance(self.name, str):
            raise TypeError("name is not of type str")

        if not isinstance(self.participant, str):
            raise TypeError("participant is not of type str")

        if not isinstance(self.annotator, str):
            raise TypeError("annotator is not of type str")

        if not isinstance(self.tier_type, TierType):
            raise TypeError("tier_type is not of type TierType")

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

        if tag.tag != "TIER":
            raise ValueError("Incorrect tag type, not TIER")

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
        participant: {self.participant}
        annotator: {self.annotator}
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

        if self.participant != "":
            element.attrib["PARTICIPANT"] = self.participant

        if self.annotator != "":
            element.attrib["ANNOTATOR"] = self.annotator

        return element

# ===================== Subtier Class =====================


@dataclass
class Subtier(Tier):
    '''
    Object used to store and edit tier attributes for a subtier.
    '''

    parent: Union[Tier, Subtier] = Tier()

    def __post_init__(self):
        """
        Type checking for dataclass fields.
        """

        super().__post_init__()

        if not isinstance(self.parent, (Tier, Subtier)):
            raise TypeError("parent is not of type Tier or Subtier")

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
        if tag.tag != "TIER":
            raise ValueError("Incorrect tag type, not TIER")

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
        parent: {self.parent.name}
        participant: {self.participant}
        annotator: {self.annotator}
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
    _ID: int = 1  # Update segments to the "best" ID for the XML

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
            self._reinforce()

            # Establish the "best" next ID
            self._ID = self.segments.ID.max()

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

    def __str__(self) -> str:
        return \
        textwrap.dedent(f'''\
        Tiers: {self.segments.Tier.unique()}
        Segments: {len(self.segments)}
        Maximum ID: a{self._ID}
        ''')  # noqa: E122

    def __len__(self) -> int:
        return len(self.segments)

    def __contains__(self, item: str) -> bool:
        return not self.segments[self.segments.Tier == item].empty

# ===================== ACCESSORS =====================

    def get_segment(self, id: Union[str, int], deep: bool = False, named_tuple: bool = False) -> Optional[Any]:
        '''
        Find the given segment based on the segment ID.

        Parameters
        ---

        id : `str` or `int`
            The segment's ID; in the form `a\\d{1,}`, or an integer.

        named_tuple: `bool`
            Return a `pd.DataFrame` or a `namedtuple`; defaults to False.

        deep: `bool`
            Return a deep copy of the row; defaults to False.

        Returns
        ---

        - The `pd.DataFrame` row for the segment, `nametuple` if `named_tuple=True` or `None` if no segment was found.
        '''

        form = f"a{id}" if isinstance(id, int) else id

        query = self.segments[self.segments.ID == form]

        if len(query) == 0:
            return None

        if deep:
            return query.copy()

        return query if not named_tuple else query.itertuples()

# ===================== MUTATORS METHODS =====================

    def split_segment(self, id: Union[str, int], split: Union[int, float] = 0.5):
        '''
        Split a segment at the given timestamp or ratio.

        Parameters
        ---

        id: `str` or `int`
            The segment's ID; in the form `a\\d{1,}`, or an integer.

        split: `int` or `float`
            Either the specific timestamp (ms) to split at (`int`) or the ratio of segments after splitting (`float` between [0, 1]); defaults to 0.75 (75%).
        '''

        form = f"a{id}" if isinstance(id, int) else id

        query = self.segments.loc[0, self.segments.ID == form]

        if query.END < split or (isinstance(split, float) and split > 1.0):
            raise ValueError(f"Timestamp split {split} is too late for end time {query.END}")

        # Add the segments
        self.add_segment(tier=query.TIER, start=query.START, end=split if isinstance(split, int) else query.START + ((query.START - query.END) * split), annotation=query.TEXT)
        self.add_segment(tier=query.TIER, start=split if isinstance(split, int) else query.START + ((query.START - query.END) * split), end=query.END, annotation=query.TEXT)

        # Remove the original segment
        self.remove_segment(id=query.ID)

    def add_segment(self, tier: str, start: Union[int, str] = 0, end: Union[int, str] = 100,
                    annotation: Optional[str] = ""):
        '''
        Adds an annotation segment to a given tier.

        Parameters
        ---

        tier : `str`
            Name of the tier.

        start : `int` or `str`
            Where the segment begins (ms).

        end : `int` or `str`
            Where the segment ends (ms).

        annotation : `str`
            Annotation for the segment.

        Notes
        ---

        - Does not matter if the tier actually exists; `ELAN_Data` should handle that.
        '''

        if int(start) < 0 or int(end) <= int(start):
            raise ValueError("Start time is less than 0 or greater than the end time")

        # I need to manually cast them to the correct type because
        # Python's "strict typing" is a fake friend...
        start, end = str(int(start)), str(int(end))

        # Insert it into the DataFrame
        self.segments = pd.concat([self.segments, pd.DataFrame([tier, start, end, annotation, f"a{self._ID}"], columns=self.segments.columns)],
                                  ignore_index=True)

        # Update ID
        self._ID += 1

    def remove_segment(self, id: Union[str, int]):
        '''
        Remove the given audio segment.

        Parameters
        ---

        id : `str` or `int`
            The ID of the segment to remove; usually "a\\d{1,}", or an integer.
        '''

        # There should be either one or no indices returned
        form = f"a{id}" if isinstance(id, int) else id
        query = self.segments[self.segments.id == form]

        if not query.empty and len(query) == 1:

            index = self.segments[self.segments.id == form].idxmax
            self.segments.drop(index=index, inplace=True)

        else:
            raise Exception("Multiple segments with the same ID")

# ===================== OTHER METHODS =====================

    def _reinforce(self):
        '''
        Reinforce column types; casts columns to correct types.

        Notes
        ---

        - `Segmentations.segments` must already exist.
        '''
        self.segments = self.segments.astype({'TIER':     str,
                                              'START':    np.int32,
                                              'END':      np.int32,
                                              'TEXT':     str,
                                              'ID':       str,
                                              'DURATION': np.int32, })
