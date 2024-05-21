# Object for extracting audio of a specific speaker from ELAN tiers
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from pathlib import Path
from elan_data.tiers import (Tier,
                             TierType,
                             Subtier,
                             Segmentations)
from typing import (Any,
                    Iterable,
                    Iterator,
                    Optional,
                    Sequence,
                    Union, )

import copy
import pickle
import textwrap
import typing

import pandas as pd
import xml.etree.ElementTree as ET

# TODO: Explain that changing referred attributes in the tiers objects might be undefined
# ===================== GLOBAL VARIABLES =====================
VERSION = "2.0.0"

_ELAN_ENCODING = "UTF-8"

# Minimum amount needed for an ELAN_Data file
MINIMUM_ELAN = \
'''
<?xml version="1.0" encoding="UTF-8"?>
<ANNOTATION_DOCUMENT AUTHOR="" DATE=""
    FORMAT="3.0" VERSION="3.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv3.0.xsd">
    <HEADER MEDIA_FILE="" TIME_UNITS="milliseconds">
    </HEADER>
    <TIME_ORDER/>
    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="default"/>
    <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
        LINGUISTIC_TYPE_ID="default-lt" TIME_ALIGNABLE="true"/>
    <CONSTRAINT
        DESCRIPTION="Time subdivision of parent annotation's time interval, no time gaps allowed within this interval" STEREOTYPE="Time_Subdivision"/>
    <CONSTRAINT
        DESCRIPTION="Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered" STEREOTYPE="Symbolic_Subdivision"/>
    <CONSTRAINT DESCRIPTION="1-1 association with a parent annotation" STEREOTYPE="Symbolic_Association"/>
    <CONSTRAINT
        DESCRIPTION="Time alignable annotations within the parent annotation's time interval, gaps are allowed" STEREOTYPE="Included_In"/>
</ANNOTATION_DOCUMENT>
'''  # noqa: E122

# ===================== ELAN_Data Class =====================


class ELAN_Data:
    '''
    Object used to create, edit, and parse `eaf` files used by ELAN software.

    Notes
    ---

    - Any method with `init_df` will only (re)initialize the DataFrame if no errors were raised or it didn't exit early (if applicable).
    '''

    file: Path
    audio: Optional[Path]
    tree: ET.ElementTree
    tiers: set[Tier]
    tier_types: set[TierType]
    subtiers: set[Subtier]
    names: set[str]  # All tier names
    segmentations: Segmentations

# ===================== INITIALIZATION METHODS =====================

    def __init__(self, file: Union[str, Path]):
        '''
        Default constructor for an ELAN_Data object.

        Parameters
        ---

        file : `str` or `pathlib.Path`
            Path of file and filename to be created; use `ELAN_Data.from_file` to parse an existing `.eaf` file.

        Raises
        ---

        - `ValueError`: If no file was given (either `None` or an empty string).
        - `TypeError`: If an invalid file type was given.
        '''

        if isinstance(file, str):
            if file == "":
                raise ValueError("No file given")
            file = Path(file)
        elif not isinstance(file, Path):
            raise TypeError("Invalid file type given")

        self.file = file

        # Parse the XML
        self.tree = ET.ElementTree(ET.fromstring(MINIMUM_ELAN.strip()))

        self.tiers, self.subtiers, self.tier_types, self.names = self._extract_tiers(tree=self.tree)  # This is getting called twice if from_file is used :(

        # Audio file path
        self.audio: Optional[Path] = None

        # Tier segmentations
        self.segmentations: Segmentations = Segmentations()
        self._modified: bool = False

    @classmethod
    def from_file(cls, file: Union[str, Path]) -> ELAN_Data:
        '''
        Initialize an ELAN_Data object from an existing `.eaf` file, storing all its information.

        Parameters
        ---

        file : `str` or `pathlib.Path`
            Filepath to the `.eaf` file.

        init_df : `bool`
            Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `False`.

        Returns
        ---

        - `ELAN_Data` instance.

        Raises
        ---

        - Any error from `open()` or `xml.etree.ElementTree.parse()`.
        '''

        ed_obj = cls(file)

        # Parse the XML
        with open(ed_obj.file, 'r', encoding=_ELAN_ENCODING) as src:
            ed_obj.tree = ET.parse(src)

        # Extract all tier names
        ed_obj.tiers, ed_obj.subtiers, ed_obj.tier_types, ed_obj.names = ed_obj._extract_tiers(tree=ed_obj.tree)

        # Separate the audio loading process, assumes local storage
        descriptor = ed_obj.tree.find(".//*[@MIME_TYPE]")

        if isinstance(descriptor, ET.Element):
            ed_obj.audio = Path(descriptor.attrib["MEDIA_URL"].replace("file:", ""))
        else:
            ed_obj.audio = None

        ed_obj._modified = False

        return ed_obj

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, file: Union[str, Path], audio: Optional[Union[str, Path]] = None, init_df: bool = False) -> ELAN_Data:
        '''
        Initialize an ELAN_Data object based on a dataframe structured like a tiers dataframe (`ELAN_Data.tiers_data`).

        Parameters
        ---

        df : `pandas.DataFrame`
            DataFrame used to create `.eaf` file.

        file : `str` or `pathlib.Path`
            Filename for the `.eaf` file.

        audio : `str` or `pathlib.Path`
            Audio associated with this `.eaf` file.

        init_df : `bool` DEPRECATED; TIHS METHOD WILL ALWAYS INITIALIZE THE DATAFRAME UNTIL FURTHER NOTICE
            Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `False`.

        Returns
        ---

        - `ELAN_Data` instance.

        Raises
        ---

        - `ValueError`: From `ELAN_Data.__init__()` method.

        Notes
        ---

        - Only supports tiers (no subtiers) with the `default-lt` linguistic reference type
        '''

        if not isinstance(df, pd.DataFrame):
            raise TypeError("DataFrame not given")

        ed_obj = cls(file)

        ed_obj.add_audio(audio)

        # Add all the tiers
        tier_names: set[str] = set()
        for row in df.itertuples(index=False):
            tier_names.add(row.TIER_ID)
            ed_obj.add_segment(row.TIER_ID, row.START, row.STOP, row.TEXT, init_df=False)

        ed_obj.tiers.update([Tier(name=name) for name in tier_names])
        ed_obj.names = tier_names

        # Reset the modified variable
        ed_obj._modified = False

        return ed_obj

    # TODO: ADD KWARGS TO FUNCTIONS THAT NEED IT TO CUSTOMIZE TIERS; ALSO ADD SUBTIERS
    @classmethod
    def create_eaf(cls, file: Union[str, Path], audio: Optional[Union[str, Path]],
                   tiers: list[str], remove_default: bool = False) -> ELAN_Data:
        '''
        Creates an ELAN_Data object to work with via Python.

        Parameters
        ---

        file : `str` or `pathlib.Path`
            What will be created when the `ELAN_Data` instance is saved.

        audio : `str` or `pathlib.Path`
            File path to the associated audio file.

        tiers : `list[str]`
            List of strings containing all

        remove_default : `bool`
            No default tier upon creation; defaults to False.

        Returns
        ---

        - `ELAN_Data` instance.

        Raises
        ---

        - `ValueError`: From `ELAN_Data.__init__()` method.
        '''

        ed_obj = cls(file)

        if remove_default:
            ed_obj.remove_tiers(['default'])

        if tiers:
            ed_obj.add_tiers(tiers, False)

        if audio:
            ed_obj.add_audio(audio)

        ed_obj._modified = False

        return ed_obj

# ===================== PRIVATE METHODS =====================

    def _extract_tiers(self, tree: ET.ElementTree) -> tuple[set[Tier], set[Subtier], set[TierType], set[str]]:
        '''
        Extract all tier information from an ELAN-based element tree.

        Parameters
        ---

        tree: `ET.ElementTree`
            The tree to parse

        Returns
        ---

        - `tuple[tiers, subtiers, tier types, all tier names]`
        '''

        tier_list: set[Tier] = set()
        tier_names: dict[str, Tier] = {}
        tier_types: set[TierType] = set()
        type_check: dict[str, TierType] = {}
        subtier_eles: list[ET.Element] = []
        subtiers: set[Subtier] = set()
        # tier names; default might still be there
        # 1. Find all tiers, ignoring subtiers
        # 2. Get their Linguistic Ref
        # 3. Create objects for each
        # 4. Insert into tiers
        for element in self.tree.findall(".//TIER"):

            type_name = element.attrib['LINGUISTIC_TYPE_REF']

            if type_name not in type_check:

                tier_type_ele = self.tree.find(f".//*[@LINGUISTIC_TYPE_ID='{type_name}']")

                if isinstance(tier_type_ele, ET.Element):

                    tier_type = TierType.from_xml(tag=tier_type_ele)
                    tier_types.add(tier_type)
                    type_check[type_name] = tier_type

                    # Skip and save for later if it is a subtier
                    if "PARENT_REF" not in element.attrib:

                        tier = Tier.from_xml(tag=element, tier_type=tier_type)
                        tier_names[element.attrib['TIER_ID']] = tier
                        tier_list.add(tier)

                    else:
                        subtier_eles.append(element)

                else:
                    raise ValueError(f"{element.attrib['TIER_ID']} has unknown Linguistic Type Reference {type_name}")

        if not subtier_eles:
            return tier_list, subtiers, tier_types, set(tier_names.keys())

        # All information should be ready to collect
        for element in subtier_eles:

            tier_type = type_check[element.attrib['LINGUISTIC_TYPE_REF']]
            parent = tier_names[element.attrib['PARENT_REF']]
            subtier = Subtier.from_xml(tag=element, tier_type=tier_type, parent=parent)
            subtiers.add(subtier)
            tier_names[element.attrib['TIER_ID']] = subtier

        return tier_list, subtiers, tier_types, set(tier_names.keys())

# ===================== DUNDER METHODS =====================

    def __repr__(self) -> str:
        return \
        textwrap.dedent(f'''\
        {type(self).__name__}({self.tree!r}, {self.tiers!r}, {self.subtiers!r}, {self.names!r}, {self.tier_types!r}, {self.file!r}, {self.segmentations!r}, {self.audio!r}, {self._modified!r})
        ''')  # noqa: E122

    def __str__(self) -> str:
        return \
        textwrap.dedent(f'''\
        name: {self.file.name}
        located at: {self.file.absolute()}
        tiers: {", ".join(self.names)}
        associated audio file: {"None" if not self.audio else self.audio.name}
        associated audio location: {"None" if not self.audio else self.audio.absolute()}
        modified: {str(self._modified)}
        ''')  # noqa: E122

    def __len__(self) -> int:
        return len(self.segmentations)

    def __contains__(self, item: Union[str, Tier, Subtier, TierType]) -> bool:
        return item in self.names or item in self.tiers or item in self.subtiers or item in self.tier_types

    def __iter__(self) -> Iterator[Any]:
        return self.segmentations.segments.itertuples()

    # TODO: Not a perfect equals -- FIX THIS!!!
    @typing.no_type_check
    def __eq__(self, other: object) -> bool:

        if type(self).__name__ != type(other).__name__:
            return NotImplemented

        return self.file == other.file and self.audio == other.audio \
            and self.names == other.names and self.segmentations.segments.equals(other.segmentations.segments) \
            and self._modified == other.modified  # Trees is a redundant check and not guaranteed

# ===================== FIELDS =====================

    @property
    def filename(self) -> str:
        return str(self.file.name)

    @property
    def modified(self) -> bool:
        '''
        Has this ELAN_Data object been altered since it was first created?
        '''
        return self._modified

# ===================== ACCESSORS =====================

    def get_segment(self, id: str = "a1") -> Optional[str]:
        '''
        Find the given segment based on the segment ID.

        Parameters
        ---

        id : `str`
            The segment's ID; in the form `a\\d{1,}`

        Returns
        ---

        - Text inside the segment or `None` if no segment was found.
        '''  # noqa: W605

        row = self.segmentations.get_segment(id=id, deep=True, named_tuple=True)
        return row.TEXT if row else row

#     def overlaps(self, seg_id: Optional[str] = None, tiers: Optional[Iterable[str]] = None, suprasegments: bool = True) -> pd.DataFrame:
#         '''
#         Find all segments on different tiers which overlap with the given segment.

#         Parameters
#         ---

#         seg_id : `str`
#             Segment ID; usually `a\\d{1,}`.

#         tiers : `Sequence[str]`
#             Which tiers to check for overlapped segments (excludes tier current segment is on).

#         suprasegments : `bool`
#             If segments whose start and ends completely encompass the start and end of the `seg_id` segment should be included; defaults to True.

#         Returns
#         ---

#         - A sub-dataframe (slice/view) containing all segments on different tiers which overlap the given segment.

#         Raises
#         ---

#         - `ValueError`: If no segment matches the given `seg_id`.

#         Notes
#         ---

#         - This method will always reinitialize the DataFrame.
#         '''  # noqa: W605

#         if not tiers or not any(tiers):
#             # We can remove the segment itself in the mask
#             # Assumes no tier has self-overlapping segments
#             tiers = self.tier_names

#         df = self.init_dataframe()

#         # Check for the segment based on its ID
#         segment = self.tier_data[self.tier_data.SEGMENT_ID == seg_id]

#         if segment.empty or len(segment) > 1:
#             raise ValueError(f"No segment matches the given seg_id value {seg_id}")

#         start, stop, tier = int(segment.START.values[0]), int(segment.STOP.values[0]), str(segment.TIER_ID.values[0])

#         # Tier mask; automatically exclude the segment's own tier
#         t = ((df.TIER_ID.isin(tiers)) & (df.TIER_ID != tier))

#         # There are four types of overlaps
#         # 1. End overlaps
#         # 2. Start overlaps
#         # 3. Start and End are in the segment's bounds
#         # 4. Suprasegment (segment within the bounds of another segment)
#         o1_3 = ((df.START >= start) & (df.START < stop)) | ((df.STOP > start) & (df.STOP <= stop))

#         if suprasegments:

#             o4 = (df.START < start) & (df.STOP > stop)

#             return df[t & (o1_3 | o4)]

#         else:
#             return df[t & o1_3]

# # ===================== MUTATORS =====================

#     def change_file(self, filepath: Union[str, Path]):
#         '''
#         Change the filepath associated with this information. Does
#         not overwrite the actual file's name. This is useful for
#         making copies or saving changes made to the data in a
#         separate file.

#         Parameters
#         ---

#         filepath : `str or pathlib.Path`
#             New filepath destination.
#         '''

#         if isinstance(filepath, (str, Path)):

#             if self.file != Path(filepath):
#                 self.file = Path(filepath)
#                 self._modified = True

#             return

#         else:
#             raise TypeError("Incorrect type passed into change_filepath")

    def add_tier(self, tier: Optional[str], init_df: bool = True, **kwargs):
        '''
        Add a single tier at the bottom of the tier list.

        Parameters
        ---

        tier : `str`
            `TIER_ID`; defaults to `"default"`.

        init_df : `bool`
            Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `True`.

        **kwargs :
            Any metadata that should be included with the tier.
        '''

        if not tier or tier in self.names:
            return

        self.names.add(tier)
        self.tiers.add(Tier(name=tier))

        self._modified = True

    def add_tiers(self, tiers: Optional[Sequence[str]], init_df: bool = True):
        '''
        Add a list of

        Parameters
        ---

        tiers : `Sequence[str]`
            List of tiers to add.
        '''

        if not tiers or not any(tiers):
            return

        for tier in tiers:

            self.names.add(tier)
            self.tiers.add(Tier(name=tier))

        self._modified = True

#     def rename_tier(self, tier: Optional[str], name: Optional[str] = None, init_df: bool = True):
#         '''
#         Rename a tier.

#         Parameters
#         ---

#         tier : `str`
#             Current tier ID.

#         name : `str`
#            New tier name

#         init_df : `bool`
#             Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `True`.
#         '''

#         if not (tier and name and tier in self._tier_names):
#             return

#         t = self.tree.getroot().find(f".//*[@TIER_ID='{tier}']")
#         assert isinstance(t, ET.Element)

#         t.attrib['TIER_ID'] = name

#         self._tier_names.remove(tier)
#         self._tier_names.append(name)

#         self._modified = True
#         self.df_status = init_df

    # TODO: Make this more efficient
    def remove_tiers(self, tiers: Optional[Sequence[str]]):
        '''
        Remove a list of tiers from the `ELAN_Data` instance.

        Parameters
        ---

        tiers : `Sequence[str]`
            List of tiers to remove.
        '''

        if not tiers:
            return

        for name in tiers:

            if name in self.names:

                self.names.remove(name)

                for tier in self.tiers:

                    if tier.name == name:

                        self.tiers.remove(tier)
                        return

                for subtier in self.subtiers:

                    if subtier.name == name:

                        self.subtiers.remove(subtier)
                        return

#     def add_participant(self, tier: Optional[str], participant: Optional[str]):
#         '''
#         Add participant metadata for a particular tier.

#         Parameters
#         ---

#         tier : `str`
#             Name of the tier.

#         participant : `str`
#             Name of the participant.
#         '''

#         if not tier or not participant:
#             return

#         if tier not in self._tier_names:
#             return

#         t = self.tree.getroot().find(f".//*[@TIER_ID='{tier}']")

#         assert isinstance(t, ET.Element)

#         t.attrib["PARTICIPANT"] = participant

#         self._modified = True

#     def add_tier_metadata(self, tier: Optional[str], init_df: bool = False, **kwargs):
#         '''
#         Add/replace any acceptable metadata for the tier.

#         Parameters
#         ---

#         tier : `str`
#             Tier to have metadata added/replaced; does nothing if tier does not exist.

#         init_df : `bool`
#             Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `False`.

#         **kwargs:
#             Attribute name(s) and value(s); all strings.
#         '''

#         if not tier or tier not in self._tier_names:
#             return

#         t = self.tree.getroot().find(f".//*[@TIER_ID='{tier}']")
#         assert isinstance(t, ET.Element)

#         t.attrib = {**(t.attrib), **kwargs}

#         self._modified = True
#         self.df_status = init_df

#     def add_metadata(self, author: str = "", date: str = ""):
#         '''
#         Add metadata to the fileheader.

#         Parameters
#         ---

#         author : `str`
#             Author name; defaults to the empty string.

#         date : `str`
#             Date information.

#         Notes
#         ---

#         - I don't know if the date needs to be formatted a specific way, so try to keep things DD/MM/YYYY.
#         '''

#         root = self.tree.getroot()
#         root.attrib["AUTHOR"] = author
#         root.attrib["DATE"] = date

    def add_audio(self, audio: Optional[Union[str, Path]]):
        '''
        Add/replace audio associated with this `ELAN_Data` instance.

        Parameters
        ---

        audio : `str` or `pathlib.Path`
            Audio file path.

        Note
        ---
        - Giving a placeholder filepath is useful when the audio is not available on the current computer.
        '''

        if not audio:
            return

        if isinstance(audio, str):
            self.audio = Path(Path(audio).absolute())
        elif isinstance(audio, Path):
            self.audio = Path(audio.absolute())
        else:
            raise TypeError("audio is not a Path or a string")

        a = ET.Element('MEDIA_DESCRIPTOR')

        a.attrib["MEDIA_URL"] = self.audio.absolute().as_uri()
        a.attrib["RELATIVE_MEDIA_URL"] = ""  # Remove completely, ELAN will figure it out
        a.attrib["MIME_TYPE"] = "audio/x-wav"

        parent = self.tree.find("./HEADER")

        assert isinstance(parent, ET.Element)

        old_audio = parent.find("./MEDIA_DESCRIPTOR")

        # Duplicate MEDIA_URL does not modify the object
        if isinstance(old_audio, ET.Element):
            if old_audio.attrib["MEDIA_URL"] == a.attrib["MEDIA_URL"]:
                return
            parent.remove(old_audio)

        parent.insert(0, a)

        self._modified = True

    def add_segment(self, tier: str, start: Union[int, str] = 0, end: Union[int, str] = 100,
                    annotation: Optional[str] = "", init_df: bool = True):
        '''
        Adds an annotation segment to a given tier.

        Parameters
        ---

        tier : `str`
            Name of the tier. Will make new tier if no match found.

        start : `int` or `str`
            Where to begin the segment (ms).

        end : `int` or `str`
            Where to end the segment (ms).

        annotation : `str`
            What to put as the annotation.

        init_df : `bool`
            Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `True`.

        Raises
        ---

        - `ValueError`: If no tier is specified.
        - `ValueError`: If start less than 0 or start is greater than stop, this will throw an error.

        Notes
        ---

        - If the tier does not exist, this will automatically make it.
        '''

        if not tier:
            raise ValueError("No tier given")

        if int(start) < 0 or int(start) > int(end):
            raise ValueError("Start must be 0 or greater and less than stop")

        if tier not in self.names:
            self.add_tier(tier, False)

        self.segmentations.add_segment(tier=tier, start=start, end=end, annotation=annotation)

#     def split_segment(self, splits: Optional[list[int]], seg_id: str):
#         '''
#         Split a segment at the points specified.

#         Parameters
#         ---

#         splits : `list[int]`
#             Where to do the splits (ms); bounds: `(start, stop)`.

#         seg_id : `str`
#             Segment ID; usually `a\\d{1,}`.

#         Raises
#         ---

#         - `ValueError`: If no segment matches the given `seg_id`.

#         Notes
#         ---

#         - This method will remove all items from the given splits list; make a copy if you wish to use it afterwards.
#         - This method will always reinitialize the DataFrame. `.TEXT` remains the same across all splits.
#         '''  # noqa: W605

#         # Check to see if everything is correctly initialized
#         if not splits:
#             return

#         # Reinit the dataframe
#         self.init_dataframe()

#         # Check for the segment based on its ID
#         segment = self.tier_data[self.tier_data.SEGMENT_ID == seg_id]

#         if segment.empty or len(segment) > 1:
#             raise ValueError("No segment matches the given seg_id value")

#         start, stop, text, tier = int(segment.START.values[0]), int(segment.STOP.values[0]), segment.TEXT.values[0], segment.TIER_ID.values[0]

#         # Remove the old segment
#         self.remove_segment(seg_id=seg_id, init_df=False)

#         # Sort the time splits to make it easier and loop through them, creating the new splits
#         splits.sort(reverse=True)

#         if start >= splits[-1] or stop <= splits[0]:
#             raise ValueError("Split list times are out of bounds for the specified segment")

#         # Do the start
#         start = splits.pop(-1)
#         self.add_segment(tier, start, start, text, False)

#         while len(splits) >= 1:
#             start = splits.pop(-1)
#             self.add_segment(tier, start, start, text, False)

#         self.add_segment(tier, start, stop, text, True)

#     def merge_segments(self, tier: Optional[str], seg_ids: Optional[list[str]], init_df: bool = True):
#         '''
#         Merge consecutive segments together.

#         Parameters
#         ---

#         tier : `str`
#             Name of the tier; optional. Let's users ignore segment IDs on other

#         seg_ids : `list[str]`
#             List of segment IDs to merge, MUST be consecutive to prevent weird `.eaf` file errors.

#         init_df : `bool`
#             Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `True`.

#         Notes
#         ---

#         - Segments contain all annotations concatonated together, separated by spaces (equivalent to `' '.join(texts)`).
#         - Up to you to make sure the segments are consecutive; assumes up-to-date DataFrame.
#         '''

#         if not tier:
#             return
#         elif tier not in self._tier_names:
#             return

#         if not seg_ids:
#             return

#         # Get relevant start and stop times and text information
#         seg_mask = (self.tier_data.SEGMENT_ID.isin(seg_ids)) & (self.tier_data.TIER_ID == tier)
#         segs_df = self.tier_data[seg_mask]

#         if segs_df.empty:
#             return

#         start, stop = segs_df.START.min(), \
#             segs_df.STOP.max()

#         text = ' '.join(segs_df.TEXT.to_list())
#         tier = segs_df.TIER_ID.iloc[0]  # Assumes they are all in the same tier!!!

#         for seg_id in seg_ids:
#             self.remove_segment(seg_id, False)

#         # Will also update self._modified
#         # Guaranteed to be str due to earlier guard
#         self.add_segment(typing.cast(str, tier), start, stop, text, init_df)

#     def remove_segment(self, seg_id: Optional[str], init_df: bool = True):
#         '''
#         Remove the given audio segment.

#         Parameters
#         ---

#         seg_id : `str`
#             The ID of the segment to remove; usually "a\\d{1,}"

#         init_df : `bool`
#             Initialize a `pandas.DataFrame` containing information related to this file. Defaults to `True`.
#         '''  # noqa: W605

#         # NOTE: I don't remove a segment's associated TIME_SLOT values because
#         # multiple segments could use the same TIME_SLOT value.

#         # Get root and then ALIGNABLE_ANNOTATION tag's parent, ANNOTATION
#         rem = self.tree.getroot().find(f".//*[@ANNOTATION_ID='{seg_id}']/..")

#         if not rem:
#             return

#         typing.cast(ET.Element, self.tree.getroot().find(f".//*[@ANNOTATION_ID='{seg_id}']/../..")).remove(rem)

#         self._modified = True
#         self.df_status = init_df

# # ===================== OTHER METHODS =====================

#     def copy(self) -> ELAN_Data:
#         '''
#         Create a deep copy of this `ELAN_Data` object.

#         Notes
#         ---

#         - `df_status` will be `True
#         - `modified` will be `False`
#         '''

#         eaf = copy.deepcopy(self)
#         eaf._modified = False

#         return eaf

#     def to_pickle(self, file: Union[str, Path] = ""):
#         '''
#         Pickles the object.

#         Parameters
#         ---

#         file : `str` or `pathlib.Path`
#             Name of file to pickle to; will default to `FILEPATH/FILENAME.pkl` if none is provided.
#         '''

#         if file == "":
#             file = self.file.parent / (self.file.name[:-4] + ".pkl")

#         with open(file, 'wb+') as dst:
#             pickle.dump(self, dst, -1)

#     @staticmethod
#     def from_pickle(file: Union[str, Path]) -> ELAN_Data:
#         '''
#         Creates `ELAN_Data` instance from pickled object.

#         Parameters
#         ---

#         file : `str` or `pathlib.Path`
#             Location of the pickled object.

#         Returns
#         ---

#         - Unpickled `ELAN_Data` instance.

#         Raises:
#         ---

#         - `FileNotFoundError`: If no filepath is provided.
#         - Any errors thrown by `open()` or `pickle.load()`.
#         '''

#         if not file or str(file) == "":
#             raise FileNotFoundError("No filepath provided")

#         with open(file, 'rb') as src:
#             return pickle.load(src)

#     def save_ELAN(self, rename: Optional[Union[str, Path]] = None,
#                   raise_error_if_unmodified: bool = True):
#         '''
#         Save as an `.eaf` file.

#         Parameters
#         ---

#         rename: `str`, `pathlib.Path` or `None
#             If you want the file to have a different name; good for saving modified copies.
#             **NOTE:** Requires there to be a full, absolute path.

#         raise_error_if_unmodified: `bool`
#             To prevent overwriting already existing `.eaf` files, this option will raise a
#             `FileExistsError` if enabled; defaults to `True`.

#         Raises
#         ---
#         - `FileNotFoundError` if the associated `ELAN_Data` instance has no `.file` attribute.
#         - `FileExistsError` if raise_error_if_unmodified is set to `True` and the associated
#         `.eaf` file already exists.
#         '''

#         if not self.file and not (rename or rename == ""):
#             raise FileNotFoundError(f"{self.file.absolute()} is not a valid file path")

#         if rename:
#             self.file = Path(rename)

#         if self.file.exists() and raise_error_if_unmodified:
#             raise FileExistsError(f"{self.file.absolute()} already exists!!! You would be overwriting it.")

#         # Only works in Python 3.9+
#         # ET.indent(self.tree)
#         # Shamelessly ripped from https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file
#         def _pretty_print(current, parent=None, index=-1, depth=0):
#             for i, node in enumerate(current):
#                 _pretty_print(node, current, i, depth + 1)
#             if parent:
#                 if index == 0:
#                     parent.text = '\n' + ('\t' * depth)
#                 else:
#                     parent[index - 1].tail = '\n' + ('\t' * depth)
#                 if index == len(parent) - 1:
#                     current.tail = '\n' + ('\t' * (depth - 1))

#         _pretty_print(self.tree.getroot())

#         self.tree.write(str(self.file.absolute()), encoding=_ELAN_ENCODING, xml_declaration=True)


# def __version__() -> str:
#     return f"version {VERSION}"
