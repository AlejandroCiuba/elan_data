# Tests the various functions found in elan_data.elan_utils
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from elan_data import ELAN_Data
from elan_data.elan_utils import (audio_loader, 
                                  eaf_to_rttm, )  # eaf_to_text, sound_wave
from pathlib import Path
from pytest import MonkeyPatch

import pytest
import wave

import numpy as np


class TestAudioLoader:

    def test_default_args_path(self, audio: Path) -> None:
        with audio_loader(audio) as src:
            assert isinstance(src, wave.Wave_read)

    def test_default_args_str_abs(self, audio: Path) -> None:
        with audio_loader(audio=str(audio.absolute())) as src:
            assert isinstance(src, wave.Wave_read)

    def test_default_args_str_lcl(self) -> None:
        with audio_loader(audio=str("./tests/test_recording.wav")) as src:
            assert isinstance(src, wave.Wave_read)

    def test_invalid_audio(self) -> None:
        with pytest.raises(TypeError):
            with audio_loader(np.array([1, 2, 3])) as src:  # noqa: F841
                pass

    @pytest.mark.parametrize("mode", ["rb", "wb", "r", "w"])
    def test_valid_mode_wave(self, audio: Path, mode: str) -> None:
        if "r" in mode:
            with audio_loader(audio, mode) as src:
                assert isinstance(src, wave.Wave_read)
        elif "w" in mode:
            # The wave module is annoying and expects us to always write when opening a writable file
            # It will also automatically erase *all* contents of any wave file that already exists...
            with pytest.raises(wave.Error):
                with audio_loader("tests/test_writing.wav", mode) as src:
                    assert isinstance(src, wave.Wave_write)
        else:
            raise TypeError("mode type not implemented")

    @pytest.mark.parametrize("mode", ["r+", "w+", "bingus"])
    def test_invalid_mode_wave(self, audio: Path, mode: str) -> None:
        with pytest.raises(wave.Error):
            with audio_loader(audio, mode) as src:  # noqa: F841
                pass

    # Originally, you could return multiple types from audio_loader, I might bring this back later
    # def test_valid_mode_ndarray(self, audio: Path) -> None:
    #     with audio_loader(audio, "rb", ret_type="ndarray") as src:
    #         assert isinstance(src, tuple)
    #         assert isinstance(src[0], np.ndarray)
    #         assert isinstance(src[1], int)
    #         assert src[1] == 2


class TestEAFToRTTM:
    
    @pytest.fixture(scope="class")
    def setup(mockelan) -> None:
        """
        Setup all the monkeypatches
        """
        MonkeyPatch.setattr(ELAN_Data, "from_file", mockelan.from_file)
        MonkeyPatch.setattr(ELAN_Data, "df_status", mockelan.df_status)
        MonkeyPatch.setattr(ELAN_Data, "file", mockelan.file)
        MonkeyPatch.setattr(ELAN_Data, "tier_data", mockelan.tier_data)

    def test_default_args_elan(setup, mockelan) -> None:
        eaf_to_rttm(mockelan, "test_dst.rttm")

class TestEAFToText:
    pass


class TestSoundWave:
    pass
