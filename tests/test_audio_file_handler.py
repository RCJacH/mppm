"""
Tests for 'analyze' module
"""
import pytest
import os
import numpy as np
from music_production_project_manager.audio_file_handler import AudioFile
from soundfile import SoundFile as sf


class AudioInfo(object):
    def __init__(self, shape):
        self.filename = os.path.join("tests", "audio_files", shape + ".wav")
        self.src = AudioFile(self.filename)
        self.isEmpty = True if shape[0] == "0" else False
        self.isMono = False if (self.isEmpty or "+" in shape) else True
        self.channels = 1 if "-m" in shape else 2
        self.keepChannel = None
        self.flag = (
            0
            if self.isEmpty
            else 1
            if "-m" in shape
            else 2
            if "-r100" in shape
            else 3
        )
        self.isFakeStereo = self.isMono and self.channels == 2

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self.src


@pytest.fixture(
    params=["sin-m", "sin-s", "0-m", "0-s", "sin+tri", "sin-l50", "sin-r25", "sin-r100"]
)
def audioinfo(request):
    with AudioInfo(request.param) as info:
        yield info


class TestAudioFile:
    @pytest.fixture(
        params=[
            "flag",
            # "keepChannel",
            "channels",
            # "isCorrelated",
            # "sample",
            "isMono",
            "isEmpty",
            # "isFakeStereo",
            # "isMultichannel",
        ]
    )
    def each_attribute(self, request, audioinfo):
        yield [getattr(x, request.param) for x in (audioinfo.src, audioinfo)]

    def test_analyze(self, each_attribute):
        assert each_attribute[0] == each_attribute[1]
        # assert audioinfo.src.flag == audioinfo.flag
        # assert audioinfo.src.isMono == audioinfo.isMono
