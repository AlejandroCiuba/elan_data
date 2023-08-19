# Tests the various functions found in elan_data.elan_utils
# Created by Alejandro Ciuba, alc307@pitt.edu
from __future__ import annotations
from elan_data import ELAN_Data
from elan_data.elan_utils import (audio_loader,
                                  eaf_to_rttm,
                                  eaf_to_text,
                                  sound_wave, )
from pathlib import Path
from pytest_lazyfixture import lazy_fixture
from typing import (Any,
                    Callable,
                    Generator,
                    Union, )
from unittest import mock

import matplotlib.figure
import matplotlib.axes
import pytest
import wave

import tests.helper as helper
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
        assert helper.compare_to_key(dst, rttm)

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
        assert helper.compare_to_key(dst, rttm_filtered)

    def test_invalid_filter(self, mock_elan: ELAN_Data, created: Path, rttm: Path) -> None:

        # Should be the same as if no filter existed
        save_name = "test_dst_invalid_filter.rttm"
        dst = created / save_name

        eaf_to_rttm(mock_elan, dst, filter=["dffault"])
        assert helper.compare_to_key(dst, rttm)


class TestEAFToText:

    @pytest.mark.parametrize("src", [lazy_fixture("mock_elan"), lazy_fixture("eaf"), lazy_fixture("eaf_str")])
    @pytest.mark.parametrize("dst", [lazy_fixture("created"), lazy_fixture("created_str")])
    def test_default_args(self, src: Union[ELAN_Data, str, Path], dst: Union[str, Path], txt: Path) -> None:

        save_name = "test_dst.txt"

        if isinstance(dst, str):
            dst = dst + "/" + save_name
        elif isinstance(dst, Path):
            dst = dst / save_name
        else:
            raise TypeError("Unsupported dst type")

        eaf_to_text(src=src, dst=dst)
        assert helper.compare_to_key(dst, txt)

    @pytest.mark.parametrize("invalid_src", [np.array([1, 2, 3]), "fake_destination/place.txt", "invalid.txt"])
    def test_invalid_src(self, invalid_src: Any, created: Path) -> None:

        save_name = "should-not-exist.txt"
        dst = created / save_name

        # We don't care how ELAN_Data.from_file() functions as long as it returns a FileNotFoundError when the file dne
        # We are specifically testing to make sure no dst files get written if the src file dne and that we raise a TypeError
        # on incorrect data types for src
        with mock.patch("elan_data.ELAN_Data.from_file", side_effect=FileNotFoundError("mocked file dne")):
            with pytest.raises((TypeError, FileNotFoundError)):
                eaf_to_text(src=invalid_src, dst=dst)

        assert not dst.exists()

    @pytest.mark.parametrize("invalid_dst", [np.array([1, 2, 3]), "fake_destination/place.rttm"])
    def test_invalid_dst(self, mock_elan: ELAN_Data, invalid_dst: Any) -> None:
        with pytest.raises((TypeError, FileNotFoundError)):
            eaf_to_text(src=mock_elan, dst=invalid_dst)

    def test_valid_filter(self, mock_elan: ELAN_Data, created: Path, txt_filtered: Path) -> None:

        # Specifically removing "THE FINAL TIER"
        save_name = "test_dst_filter.txt"
        dst = created / save_name

        eaf_to_text(mock_elan, dst, filter=["THE FINAL TIER"])
        assert helper.compare_to_key(dst, txt_filtered)

    def test_invalid_filter(self, mock_elan: ELAN_Data, created: Path, txt: Path) -> None:

        # Should be the same as if no filter existed
        save_name = "test_dst_invalid_filter.txt"
        dst = created / save_name

        eaf_to_text(mock_elan, dst, filter=["dffault"])
        assert helper.compare_to_key(dst, txt)

    def test_valid_formatter(self, mock_elan: ELAN_Data, created: Path, txt_formatted: Path) -> None:

        # Test if making new valid formatting functions works
        # Valid formatters take in a row from pd.DataFrame.itertuples() and return a string
        def new_formatter(row: Any) -> str:
            if row.TEXT.strip() != "":
                return f"{row.TIER_ID} {row.DURATION}: {row.TEXT.strip()}"
            else:
                return f"{row.TIER_ID} {row.DURATION}: *Silence.*"

        save_name = "test_dst_valid_formatter.txt"
        dst = created / save_name

        eaf_to_text(mock_elan, dst, formatter=new_formatter)
        assert helper.compare_to_key(dst, txt_formatted)


class TestSoundWave:

    # Keep audio_loader testing separate completely
    @pytest.fixture()
    def setup(self, audio_str: str) -> Generator:
        with mock.patch("elan_data.elan_utils.audio_loader", spec=True) as mock_loader:
            mock_loader.return_value = wave.open(audio_str, "rb")
            yield mock_loader

    def test_default_args(self, setup: Callable[..., Any], audio: Path) -> None:
        result = sound_wave(audio=audio)
        assert isinstance(result, tuple)
        assert isinstance(result[0], matplotlib.figure.Figure)
        assert isinstance(result[1], matplotlib.axes.Axes)

    # Audio duration: 7.12s
    @pytest.mark.parametrize("start,stop", [(-200, 10), (10, 5), (-1, -1), (8, 10)])
    def test_invalid_times(self, setup: Callable[..., Any], audio: Path, start: float, stop: float) -> None:
        with pytest.raises(ValueError):
            sound_wave(audio, start=start, stop=stop)

    # Audio duration: 7.12s
    @pytest.mark.parametrize("start,stop", [(0, 7.12), (2, 5), (0, -1), (3, 10_000)])
    def test_valid_times(self, setup: Callable[..., Any], audio: Path, start: float, stop: float) -> None:
        result = sound_wave(audio=audio, start=start, stop=stop)
        assert isinstance(result, tuple)
        assert isinstance(result[0], matplotlib.figure.Figure)
        assert isinstance(result[1], matplotlib.axes.Axes)

    def test_valid_kwargs(self, setup: Callable[..., Any], audio: Path) -> None:
        result = sound_wave(audio=audio, red=1)
        assert isinstance(result, tuple)
        assert isinstance(result[0], matplotlib.figure.Figure)
        assert isinstance(result[1], matplotlib.axes.Axes)

    def test_invalid_kwargs(self, setup: Callable[..., Any], audio: Path) -> None:
        # Same as if it was valid, but the color information doesn't apply
        result = sound_wave(audio=audio, red=2)
        assert isinstance(result, tuple)
        assert isinstance(result[0], matplotlib.figure.Figure)
        assert isinstance(result[1], matplotlib.axes.Axes)
