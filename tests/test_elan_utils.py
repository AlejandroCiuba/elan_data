# Tests the various functions found in elan_data.elan_utils
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from elan_data import ELAN_Data
from elan_data.elan_utils import (audio_loader,
                                  eaf_to_rttm, )  # eaf_to_text, sound_wave
from pathlib import Path
from pytest_lazyfixture import lazy_fixture
from typing import (Any,
                    Union, )
from unittest import mock

import pytest
import wave

import numpy as np


class TestAudioLoader:

    @pytest.mark.parametrize("aud", [lazy_fixture("audio"), lazy_fixture("audio_str")])
    def test_default_args(self, aud: Union[str, Path]) -> None:
        with audio_loader(audio=aud) as src:
            assert isinstance(src, wave.Wave_read)

    def test_default_args_str_abs(self, audio: Path) -> None:
        with audio_loader(audio=str(audio.absolute())) as src:
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

    @pytest.mark.parametrize("src", [lazy_fixture("mock_elan"), lazy_fixture("eaf"), lazy_fixture("eaf_str")])
    @pytest.mark.parametrize("dst", [lazy_fixture("created"), lazy_fixture("created_str")])
    def test_default_args(self, src: Union[ELAN_Data, str, Path], dst: Union[str, Path], rttm: Path) -> None:

        save_name = "test_dst.rttm"

        if isinstance(dst, str):
            dst = dst + "/" + save_name
        elif isinstance(dst, Path):
            dst = dst / save_name
        else:
            raise TypeError("Unsupported dst type")

        eaf_to_rttm(src=src, dst=dst)
        assert TestEAFToRTTM.compare_to_key(dst, rttm)

    @pytest.mark.parametrize("invalid_src", [np.array([1, 2, 3]), "fake_destination/place.rttm", "invalid.rttm"])
    def test_invalid_src(self, invalid_src: Any, created: Path) -> None:

        save_name = "should-not-exist.rttm"
        dst = created / save_name

        # We don't care how ELAN_Data.from_file() functions as long as it returns a FileNotFoundError when the file dne
        # We are specifically testing to make sure no dst files get written if the src file dne and that we raise a TypeError
        # on incorrect data types for src
        with mock.patch("elan_data.ELAN_Data.from_file", side_effect=FileNotFoundError("mocked file dne")):
            with pytest.raises((TypeError, FileNotFoundError)):
                eaf_to_rttm(src=invalid_src, dst=dst)

        assert not dst.exists()

    @pytest.mark.parametrize("invalid_dst", [np.array([1, 2, 3]), "fake_destination/place.rttm"])
    def test_invalid_dst(self, mock_elan: ELAN_Data, invalid_dst: Any) -> None:
        with pytest.raises((TypeError, FileNotFoundError)):
            eaf_to_rttm(src=mock_elan, dst=invalid_dst)

    def test_valid_filter(self, mock_elan: ELAN_Data, created: Path, rttm_filtered: Path) -> None:

        # Specifically removing "THE FINAL TIER"
        save_name = "test_dst_filter.rttm"
        dst = created / save_name

        eaf_to_rttm(mock_elan, dst, filter=["THE FINAL TIER"])
        assert TestEAFToRTTM.compare_to_key(dst, rttm_filtered)

    def test_invalid_filter(self, mock_elan: ELAN_Data, created: Path, rttm: Path) -> None:

        # Should be the same as if no filter existed
        save_name = "test_dst_filter.rttm"
        dst = created / save_name

        eaf_to_rttm(mock_elan, dst, filter=["dffault"])
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
