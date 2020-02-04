"""
Tests for 'analyze' module
"""
import pytest
import os
import numpy as np
from music_production_project_manager.analyze import SampleblockChannelInfo
from soundfile import read


class Test_SampleblockChannelInfo(object):
    @pytest.fixture
    def obj(self):
        return SampleblockChannelInfo()

    def test_set_channels(self, obj):
        obj.channelblock = [[0.1], [0.2]]
        assert obj.set_channels() == 2
        obj.channelblock = [[0.1, 0.2]]
        assert obj.set_channels() == 1
        obj.channelblock = [[0.6721, 0.0391, -0.518], [-0.6968, -0.644, 0.0526]]
        assert obj.set_channels() == 2

    def test_flag_on_from_sample(self, obj):
        obj.flag = 0
        obj.set_channelblock([[0, 0.5]])
        assert obj.set_flag() == 2
        obj.flag = 0
        obj.set_channelblock([[-0.25, 0]])
        assert obj.set_flag() == 1
        obj.flag = 0
        obj.set_channelblock([[0.0, 0.0]])
        assert obj.set_flag() == 0

    def test_flag_on(self, obj):
        obj.flag = 0
        assert obj.flag == 0
        assert obj.flag_on(1) == 1
        assert obj.flag_on(1) == 1
        assert obj.flag_on(2) == 3
        obj.flag = 0

    def test_transpose(self, obj):
        assert (
            obj._transpose([[0.1, 0.2], [0.3, 0.6], [0.15, 0.3]])
            == [[0.1, 0.3, 0.15], [0.2, 0.6, 0.3]]
        ).all()

    def test_get_ratio(self, obj):
        assert obj._get_ratio([0.5, 0.5]) == 1
        assert obj._get_ratio([0.22900572, 0.11450286]) == 0.5
        assert obj._get_ratio([0.0, 0.0]) == 0

    def test_is_ratio_correlated(self, obj):
        assert obj._is_ratio_correlated([[1], [1]]) == True
        assert (
            obj._is_ratio_correlated(
                [
                    [0.99990839, 0.99987785, 0.99987783, 0.99984727],
                    [0.998004, 0.99800001, 0.99799599, 0.99799196],
                ]
            )
            == False
        )
        assert (
            obj._is_ratio_correlated(
                [
                    [1.0148026, 1.01443943, 1.01423377],
                    [1.0148026, 1.01443943, 1.01423382],
                ]
            )
            == True
        )
        assert obj._is_ratio_correlated([[1.0, 1.0], [1.0, 1.000009],]) == True
        assert obj._is_ratio_correlated([[1, 2], [1, 2.00001]]) == False

    def test_is_sampleblock_correlated(self, obj):
        assert obj._is_sampleblock_correlated([[0.5, 0.5, 0.5]] * 2) == True
        assert (
            obj._is_sampleblock_correlated(
                [[0.00308228, 0.00613403], [0.00308228, 0.00613403],]
            )
            == True
        )
        assert (
            obj._is_sampleblock_correlated(
                [
                    [0.22900572, 0.2323956, 0.23575126, 0.23910689],
                    [0.11450286, 0.1161978, 0.11787563, 0.11955345],
                ]
            )
            == True
        )
        assert (
            obj._is_sampleblock_correlated(
                [
                    [0.99996948, 0.99996948, 0.99996948],
                    [0.99996948, 0.99804688, 0.99609375],
                ]
            )
            == False
        )
        assert obj._is_sampleblock_correlated([[0.0, 0.0, 0.0]] * 2) == True

    def test_get_sample_from_sampleblock(self, obj):
        obj.reset_sample()
        assert obj.sample == []
        assert obj._get_sample_from_sampleblock([[0.0, 0.0]] * 3) == []
        assert obj._get_sample_from_sampleblock(
            [[0.00308228, 0.00308228], [0.00613403, 0.00613403]]
        ) == [0.00308228, 0.00308228]
        assert obj._get_sample_from_sampleblock(
            [[0.99996948, 0.0], [0.99996948, 0.99804688], [0.99996948, 0.99609375]]
        ) == [0.99996948, 0.99804688]
        obj.sample = [0.1, 0.2]
        assert obj._get_sample_from_sampleblock([[0.2, 0.5,]]) == [0.1, 0.2]
        obj.sample = [0.1, 0.1]
        assert obj._get_sample_from_sampleblock([[0.2, 0.5,]]) == [0.2, 0.5]
        assert obj._get_sample_from_sampleblock([[]]) == [0.1, 0.1]
        obj.reset_sample()

    def test_is_sample_stereo(self, obj):
        assert obj._is_sample_stereo([0.5, 0.3]) == True
        assert obj._is_sample_stereo([0.5]) == False
        assert obj._is_sample_stereo([0.5, 0.5]) == False
        assert obj._is_sample_stereo([0, 0]) == False

    # def test_get_noisefloor_from_channelblock(self, obj):
    #     assert (
    #         obj._get_noisefloor_from_channelblock([[0.2, 1], [0.1, 0]]) == [0.2, 0]
    #     ).all()
    #     assert (obj._get_noisefloor_from_channelblock([[0, 0], [0, 0]]) == [0, 0]).all()
    #     assert (
    #         obj._get_noisefloor_from_channelblock([[-1, -0.001], [0.01, -0.02]])
    #         == [0.001, 0.01,]
    #     ).all()

    # def test_set_noisefloor(self, obj):
    #     obj.channels = 2
    #     obj.noisefloor = [0.1, 0.2]
    #     assert (
    #         obj.set_noisefloor([[-0.3751, 0.0575], [0.4578, 0.5397]]) == [0.0575, 0.2,]
    #     ).all()


# class AudioInfo:
#     def __init__(self, shape):
#         self.src = Monolizer()
#         self.src.file = "tests//" + shape + ".wav"
#         if shape == "sin":
#             self.channel = 0
#             self.channels = 1
#             self.isMono = True
#             self.isEmpty = False
#             self.isFakeStereo = False
#         if shape == "sins":
#             self.channel = 0
#             self.channels = 2
#             self.isMono = True
#             self.isEmpty = False
#             self.isFakeStereo = True
#         if shape == "empty":
#             self.channel = self.src.EMPTY
#             self.channels = 1
#             self.isMono = False
#             self.isEmpty = True
#             self.isFakeStereo = False
#         if shape == "sin_tri":
#             self.channel = self.src.STEREO
#             self.channels = 2
#             self.isMono = False
#             self.isEmpty = False
#             self.isFakeStereo = False
#         if shape == "sin_l50":
#             self.channel = 0
#             self.channels = 2
#             self.isMono = True
#             self.isEmpty = False
#             self.isFakeStereo = True
#         if shape == "sin_r25":
#             self.channel = 1
#             self.channels = 2
#             self.isMono = True
#             self.isEmpty = False
#             self.isFakeStereo = True
#         if shape == "sin_r100":
#             self.channel = 1
#             self.channels = 2
#             self.isMono = True
#             self.isEmpty = False
#             self.isFakeStereo = True

#     def __enter__(self):
#         return self

#     def __exit__(self, *args):
#         del self.src

# @pytest.fixture(params=["sin", "sins", "empty", "sin_tri", "sin_l50", "sin_r25", "sin_r100"])
# def audioinfo(request):
#     with AudioInfo(request.param) as info:
#         yield info
