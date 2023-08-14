# Convert .eaf files to the Rich Transcription Time Marked (RTTM) format
from __future__ import annotations
from elan_data.elan_data import ELAN_Data
from pathlib import Path
from typing import Callable, Iterator, TYPE_CHECKING, Union

import contextlib
import matplotlib.figure
import matplotlib.axes
import wave

import matplotlib.pyplot as plt
import numpy as np

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

MODE = Literal["rb", "wb"]
RETURN = Literal["wave", "ndarray"]


def eaf_to_rttm(
    src: Union[str, Path, ELAN_Data],
    dst: Union[str, Path],
    filter: list = [],
    encoding: str = "UTF-8",
):
    """
    Convert a .eaf file to the RTTM format.

    Parameters
    ---

    file : `str` or `pathlib.Path`
        Filepath to the .eaf file.

    save_as : `str`
        Name and location of the created .rttm file.

    filter : `list[str]`
        Names of tiers which will not appear in the .rttm file (such as Noise or Comments).

    Notes
    ---

    - For Speaker Names, spaces in the tier name of the .eaf file are replaced with underscores in the .rttm file.
    - `utf-8` encoding.
    """

    # Create the Elan_Data object from the file
    if isinstance(src, (str, Path)):
        eaf = ELAN_Data.from_file(src)

    eaf.df_status = True

    with open(dst, "w+", encoding=encoding) as rttm:
        for row in eaf.tier_data.itertuples():
            if row.TIER_ID not in filter:
                fields = [
                    "SPEAKER",
                    eaf.file.name[:-4],
                    "1",
                    f"{row.START * 10**-3:.6f}",
                    f"{row.DURATION * 10**-3:.6f}",
                    "<NA>",
                    "<NA>",
                    row.TIER_ID.strip().replace(" ", "_"),
                    "<NA>",
                    "<NA>",
                ]

                line = " ".join(fields)
                rttm.write(line)
                rttm.write("\n")


def eaf_to_text(src: Union[str, Path, ELAN_Data], dst: Union[str, Path], filter: list = [], 
                encoding: str = "UTF-8", formatter: Union[Callable[..., str], None] = None):
    """
    Takes the text of an `.eaf` file and outputs it to a text file.

    Parameters
    ---

    src : `str` or `pathlib.Path`
        Filepath to the .eaf file.

    dst : `str`
        Name and location of the created .rttm file.

    filter : `list[str]`
        Names of tiers which will not appear in the .rttm file (such as Noise or Comments).

    formatter : `func(row in eaf.tier_data.itertuples()) -> str` or `None`
        Custom function with which to format each line; `\n` always appended automatically.

    Notes
    ---

    - Default Format: `TIER_ID START-STOP: TEXT`.
    - `utf-8` encoding.
    """

    def default(row) -> str:
        return f"{row.TIER_ID} {row.START}-{row.STOP}: {row.TEXT.strip()}"

    formatter = default if formatter is None else formatter

    # Create the Elan_Data object from the file
    if isinstance(src, (str, Path)):
        eaf = ELAN_Data.from_file(src)

    eaf.df_status = True

    with open(dst, "w+", encoding=encoding) as txt:
        for row in eaf.tier_data.itertuples():
            if row.TIER_ID not in filter:
                line = formatter(row)
                txt.write(line)
                txt.write("\n")


@contextlib.contextmanager
def audio_loader(eaf: ELAN_Data = None, mode: MODE = "rb", ret_type: RETURN = "wave") -> Iterator[Union[wave.Wave_read, wave.Wave_write, tuple[np.ndarray, int]]]:
    """
    Context manageable function that loads in the audio associated with the `.eaf` file. File must be in directory stated in XML. Closes file upon end.

    Parameters
    ---

    ed : `ELAN_Data`
        Correct audio filepath must be established.

    mode : `'rb'` or `'wb'`
        Defaults to `'rb'` (read-binary).

    ret_type : `"wave"` or `"ndarray"`
        What to yield, either a `wave` file object (from the `wave` library) or a tuple of an `ndarray` from `numpy` and the audio's sample width.

    Yields
    ---

    - `wave` file from the `wave` library.
    - A tuple of an `ndarray` from `numpy` and the audio's sample width.

    Raises
    ---

    - `ValueError`: If no `ELAN_Data` instance is provided.
    - `ValueError`: If the `ELAN_Data` instance has no associated audio file.
    - `TypeError`: If `ret_type` is not `"wave"` or `"ndarray"`.
    """

    if eaf is None:
        raise ValueError("No ELAN_Data object provided")

    if ret_type not in ("wave", "ndarray"):
        raise TypeError(f"{ret_type} not an option")

    try:
        if eaf.audio is None:
            raise ValueError("ELAN_Data object has no associated audio file")

        audio = wave.open(str(eaf.audio.absolute()), mode)

        if ret_type == "ndarray":
            samp_width = audio.getsampwidth()
            dtype = np.int16

            yield (np.frombuffer(audio.readframes(-1), dtype=dtype), samp_width)

        else:
            yield audio

    finally:
        audio.close()


def sound_wave(eaf: ELAN_Data = None, start: float = 0, stop: float = -1, **kwargs) -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plots the audio's amplitude for each channel.

    Parameters
    ---

    ed : `ELAN_Data`
        Contains filepath to audio.

    start : `float`
        Start of the sound wave (in seconds).

    stop : `float`
        End of the sound wave (in seconds); use `-1` to capture the until the end.

    **kwargs : `dict[str : int]`
        Any colors (`str`) and their corresponding channels (`int`)

        (e.g. `sound_wave(eaf, start=10, blue=1, gold=2)`)

    Returns
    ---

    - A figure from `matplotlib` with the soundwave(s).

    Raises
    ---

    - `ValueError`: If no `ELAN_Data` instance is provided.
    - `ValueError`: If the `ELAN_Data` instance has no associated audio file.
    - `ValueError`: If the start time is greater than the stop time (excluding -1).
    - `ValueError`: If the start time is greater than the audio duration.
    """

    # Error handling
    if eaf is None:
        raise ValueError("No ELAN_Data object provided")

    if eaf.audio is None:
        raise ValueError("ELAN_Data has no associated audio file")

    if start >= stop and stop != -1:
        raise ValueError("Start time cannot be greater than stop time")

    # Get audio information

    with audio_loader(eaf) as src:
        # So mypy won't be absolutely stupid
        assert isinstance(src, (wave.Wave_read))

        total_channels = src.getnchannels()
        frames = src.getnframes()
        hertz = src.getframerate()
        duration = frames / hertz
        signals = []

        if start > duration:
            raise ValueError("Start time is greater than audio duration")

        if stop > duration:
            stop = -1

        # Get the sample width and calculate dtype for np.frombuffer
        sample_width = src.getsampwidth()

        # Only accomodates 1, 2, or 4 bytes per sample
        d_type: type[np.signedinteger] = np.int16

        if sample_width == 1:
            d_type = np.int8
        elif sample_width == 4:
            d_type = np.int32

        raw_signal = np.frombuffer(src.readframes(-1), dtype=d_type)

        # Separate signal into its channels
        for i in range(total_channels):
            signals.append(raw_signal[i::total_channels].copy())

    # Get and trim timespace
    start, stop = int(start * hertz), int(stop * hertz)
    timespace = np.linspace(0, duration, num=frames)[start:stop]

    # Plot it all
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

    for color, chan in kwargs.items():
        ind = chan - 1
        if ind < total_channels:
            ax.plot(
                timespace,
                signals[ind][start:stop],
                label=f"Channel {chan}",
                color=color,
                alpha=1 - ((ind) * (1 / len(kwargs))),
            )

    ax.set_title(f"Soundwave of {eaf.audio.name}")
    ax.set_xlabel("Time (Seconds)")
    ax.set_ylabel("Amplitude")
    ax.legend()

    return (fig, ax)
