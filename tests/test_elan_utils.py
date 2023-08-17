# Tests the various functions found in elan_data.elan_utils
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from elan_data import ELAN_Data
from elan_data.elan_utils import (audio_loader,
                                  eaf_to_rttm, )  # eaf_to_text, sound_wave
from pathlib import Path
from typing import (Any,
                    Union, )

import pytest
import wave

import numpy as np


class TestAudioLoader:

    def test_default_args_path(self, audio: Path) -> None:
        with audio_loader(audio=audio) as src:
            assert isinstance(src, wave.Wave_read)

    def test_default_args_str_abs(self, audio: Path) -> None:
        with audio_loader(audio=str(audio.absolute())) as src:
            assert isinstance(src, wave.Wave_read)

    def test_default_args_str_local(self, audio_str: str) -> None:
        with audio_loader(audio=audio_str) as src:
            assert isinstance(src, wave.Wave_read)

    @pytest.mark.parametrize("invalid_audio", [np.array([1, 2, 3]), "fake_destination/place.wav", "invalid.wav"])
    def test_invalid_audio(self, invalid_audio: Any) -> None:
        with pytest.raises((TypeError, FileNotFoundError)):
            with audio_loader(audio=invalid_audio) as src:  # noqa: F841
                pass

    @pytest.mark.parametrize("mode", ["rb", "wb", "r", "w"])
    def test_valid_mode_wave(self, audio: Path, created: Path, mode: str) -> None:
        if "r" in mode:
            with audio_loader(audio, mode=mode) as src:
                assert isinstance(src, wave.Wave_read)
        elif "w" in mode:
            # The wave module is annoying and expects us to always write when opening a writable file
            # It will also automatically erase *all* contents of any wave file that already exists...
            with pytest.raises(wave.Error):
                with audio_loader(created / "test_writing.wav", mode=mode) as src:
                    assert isinstance(src, wave.Wave_write)
        else:
            raise TypeError("mode type not implemented")

    @pytest.mark.parametrize("mode", ["r+", "w+", "w*", "bingus"])
    def test_invalid_mode_wave(self, audio: Path, created: Path, mode: str) -> None:
        with pytest.raises(wave.Error):
            # Safety in case any ".*w.*" will overwrite
            if "w" not in mode:
                with audio_loader(audio, mode) as src:  # noqa: F841
                    pass
            else:
                with audio_loader(created / "test_writing.wav", mode=mode) as src:  # noqa: F841
                    pass

    # Originally, you could return multiple types from audio_loader, I might bring this back later
    # def test_valid_mode_ndarray(self, audio: Path) -> None:
    #     with audio_loader(audio, "rb", ret_type="ndarray") as src:
    #         assert isinstance(src, tuple)
    #         assert isinstance(src[0], np.ndarray)
    #         assert isinstance(src[1], int)
    #         assert src[1] == 2


class TestEAFToRTTM:

    def test_default_args_elan(self, mock_elan: ELAN_Data, created: Path, rttm: Path) -> None:
        dst = created / "test_dst.rttm"
        eaf_to_rttm(mock_elan, dst)
        assert TestEAFToRTTM.compare_to_key(dst, rttm)

    @staticmethod
    def compare_to_key(src: Union[str, Path], rttm: Path) -> bool:
        """
        Compare the created file to the key.rttm file.
        """
        with open(src, "r", encoding="UTF-8") as ans:
            with open(rttm, "r", encoding="UTF-8") as key:
                return not len(set(ans.readlines(-1)) & set(key.readlines(-1)))


class TestEAFToText:
    pass


class TestSoundWave:
    pass
