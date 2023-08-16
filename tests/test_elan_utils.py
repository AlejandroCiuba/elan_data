from __future__ import annotations
from elan_data.elan_utils import audio_loader, eaf_to_rttm, sound_wave
from pathlib import Path

import pytest
import wave


class TestAudioLoader:

    def test_default_args(self, audio: Path) -> None:
        with audio_loader(audio) as src:
            assert isinstance(src, wave.Wave_read)

    @pytest.mark.parametrize("mode", ["rb", "wb"])
    def test_mode_wave(self, audio: Path, mode: str) -> None:
        if mode == "rb":
            with audio_loader(audio, mode) as src:
                assert isinstance(src, wave.Wave_read)
        elif mode == "wb":
            # The wave module is annoying and expects us to always write when opening a writable file
            # It will also automatically delete any wave file that already exists...
            with pytest.raises(wave.Error):
                with audio_loader("test_writing.wav", mode) as src:
                    assert isinstance(src, wave.Wave_write)
        else:    
            raise TypeError("mode type not implemented")
