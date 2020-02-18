"""
Tests for 'analyze' module
"""
import pytest
import os
import numpy as np
from music_production_project_manager.audio_file_handler import AudioFile
from soundfile import SoundFile as sf

def get_audio_path(name):
    return os.path.join("tests", "audio_files", name + ".wav")

class AudioInfo(object):
    def __init__(self, shape):
        self.filename = get_audio_path(shape)
        self.src = AudioFile(self.filename)
        self.isCorrelated = False if ("+" in shape or "100" in shape) else True
        self.isEmpty = shape[0] == "0"
        self.isMono = False if (self.isEmpty or "+" in shape) else True
        self.channels = 1 if "-m" in shape else 2
        self.validChannel = (
            0
            if "0-" in shape
            else 3
            if "+" in shape
            else 2
            if "r" in shape
            else 1
        )
        self.flag = (
            0 if self.isEmpty else 1 if "-m" in shape else 2 if "-r100" in shape else 3
        )
        self.isFakeStereo = self.isMono and self.channels == 2
        self.isMultichannel = shape[-1] == "n" or shape.count("+") > 1

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
            "isCorrelated",
            "validChannel",
            "channels",
            "isMono",
            "isEmpty",
            "isFakeStereo",
            "isMultichannel",
        ]
    )
    def each_attribute(self, request, audioinfo):
        yield [getattr(x, request.param) for x in (audioinfo.src, audioinfo)]

    def test_analyze(self, each_attribute):
        assert each_attribute[0] == each_attribute[1]

    def test_empty_file(self):
        with AudioFile(get_audio_path("empty")) as src:
            assert src.flag == None
            assert src.isCorrelated == None
            assert src.isMono == False
            assert src.isFakeStereo == False
            assert src.isMultichannel == False

    def test__enter__exit(self):
        with AudioFile(get_audio_path("empty")) as src:
            assert src.file is not None
        assert src.file is None