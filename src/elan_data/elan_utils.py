# Convert .eaf files to the Rich Transcription Time Marked (RTTM) format
from __future__ import annotations
from elan_data import ELAN_Data
from pathlib import Path
from typing import (Callable,
                    Iterator,
                    Optional,
                    Union, )

import contextlib
import matplotlib.figure
import matplotlib.axes
import sys
import wave

import matplotlib.pyplot as plt
import numpy as np

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

MODE = Literal["rb", "wb", "w", "r"]
RETURN = Literal["wave", "ndarray"]


def eaf_to_rttm(src: Union[str, Path, ELAN_Data], dst: Union[str, Path],
                filter: list = [], encoding: str = "UTF-8"):
    """
    Convert a .eaf file to the RTTM format.

    Parameters
    ---

    file : `str` or `pathlib.Path`
        Filepath to the .eaf file.

    dst : `str` or `pathlib.Path`
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
    elif not isinstance(src, (ELAN_Data)):
        raise TypeError("Incorrect type given")
    else:
        eaf = src

    eaf.df_status = True

    with open(dst, "w+", encoding=encoding) as rttm:

        name = eaf.file.name[:-4]

        for row in eaf.tier_data.itertuples():
            if row.TIER_ID not in filter:
                fields = [
                    "SPEAKER",
                    name,
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


def eaf_to_text(src: Union[str, Path, ELAN_Data], dst: Union[str, Path],
                filter: list = [], encoding: str = "UTF-8", formatter: Optional[Callable[..., str]] = None):
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

    formatter = default if not formatter else formatter

    # Create the Elan_Data object from the file
    if isinstance(src, (str, Path)):
        eaf = ELAN_Data.from_file(src)
    elif not isinstance(src, (ELAN_Data)):
        raise TypeError("Incorrect type given")
    else:
        eaf = src

    eaf.df_status = True

    with open(dst, "w+", encoding=encoding) as txt:
        for row in eaf.tier_data.itertuples():
            if row.TIER_ID not in filter:
                line = formatter(row)
                txt.write(line)
                txt.write("\n")


@contextlib.contextmanager
def audio_loader(audio: Union[str, Path], mode: Union[MODE, str] = "rb") -> Iterator[Union[wave.Wave_read, wave.Wave_write]]:
    """
    Context manageable function that loads in audio. Closes file upon end.

    Parameters
    ---

    audio : `str` or `Path`
        Filepath to the audio.

    mode : `'rb'` or `'wb'`
        Defaults to `'rb'` (read-binary).

    Yields
    ---

    - `wave` file from the `wave` library.

    Raises
    ---

    - `TypeError`: If the given audio isn't a string or Path.

    Notes
    ---

    - Essentially just a wrapper around `wave.open` to allow Paths. There might be more functionality in future iterations.
    """

    # Error handling
    if not isinstance(audio, Path):
        if isinstance(audio, str):
            audio = Path(audio)
        else:
            raise TypeError("audio is not a string or Path")

    wav = wave.open(str(audio.absolute()), mode)

    try:
        yield wav
    finally:
        wav.close()


def sound_wave(audio: Union[str, Path], start: float = 0, stop: float = -1,
               name: str = "Soundwave", **kwargs) -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plots the audio's amplitude for each channel.

    Parameters
    ---

    audio : `str` or `Path`
        Filepath to the audio.

    start : `float`
        Start of the sound wave (in seconds).

    stop : `float`
        End of the sound wave (in seconds); use `-1` to capture the until the end.

    name : `str`
        Title to use for the graph.

    **kwargs : `dict[str : int]`
        Any colors (`str`) and their corresponding channels (`int`)

        (e.g. `sound_wave(eaf, start=10, blue=1, gold=2)`)

    Returns
    ---

    - A figure from `matplotlib` with the soundwave(s).

    Raises
    ---

    - `TypeError`: If the given audio isn't a string or Path.
    - `ValueError`: If the start time is greater than the stop time (excluding -1).
    - `ValueError`: If the start time is greater than the audio duration.
    """
    # Error handling
    if start < 0:
        raise ValueError("Start time cannot be negative")
    elif start >= stop and stop != -1:
        raise ValueError("Start time cannot be greater than stop time")

    # Get audio information
    with audio_loader(audio) as src:

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

    ax.set_title(f"Soundwave of {name}")
    ax.set_xlabel("Time (Seconds)")
    ax.set_ylabel("Amplitude")
    ax.legend()

    return (fig, ax)
