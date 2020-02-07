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
        assert obj.flag_on("") == 0
        obj.flag = 0

    def test_transpose(self, obj):
        assert (
            obj._transpose([[0.1, 0.2], [0.3, 0.6], [0.15, 0.3]])
            == [[0.1, 0.3, 0.15], [0.2, 0.6, 0.3]]
        ).all()

    @pytest.mark.parametrize(
        "sample, ratio",
        [
            pytest.param([0.5, 0.5], [1], id="Identical"),
            pytest.param([0.22900572, 0.11450286], [0.5], id="Float"),
            pytest.param([0.0, 0.0], [0], id="Zeroes"),
            pytest.param([1, 2, 3, -6], [2, 1.5, -2], id="Multichannel"),
        ],
    )
    def test_get_ratio(self, obj, sample, ratio):
        assert obj._get_ratio(sample) == ratio

    @pytest.mark.parametrize(
        "ratios, isCorrelated",
        [
            pytest.param([[1, 0.5], [1, 0.5]], True, id="FakeStereo"),
            pytest.param(
                [
                    [0.99990839, 0.99987785, 0.99987783],
                    [0.998004, 0.99800001, 0.99799599],
                ],
                False,
                id="FloatStereo",
            ),
            pytest.param(
                [[1.0148026, 1.01443943, 1.01423377]] * 2, True, id="FloatFakeStereo",
            ),
            pytest.param(
                [[1, 2, 3], [1, 2, 4], [1, 3, 2]], False, id="TrueMultichannel",
            ),
            pytest.param(
                [[1, 2, 3], [1, 2, 3], [1, 2, 4]], False, id="PartialMultichannel",
            ),
            pytest.param(
                [[1, 2, 3], [1, 2, 3], [1, 2, 3]], True, id="FakeMultichannel",
            ),
            pytest.param([[1.0, 1.0], [1.0, 1.000009],], True, id="BelowThreshold"),
            pytest.param([[1, 2], [1, 2.00001]], False, id="AboveThreshold"),
            pytest.param(
                [[0.5, 1, 2.000009], [0.5, 1, 2], [0.5, 1, 1.999991]],
                True,
                id="MultichannelBelowThreshold",
            ),
            pytest.param(
                [[0.5, 1, 2], [0.5, 1, 2.00001], [0.5, 1, 2]],
                False,
                id="MultichannelAboveThreshold",
            ),
        ],
    )
    def test_is_ratio_correlated(self, obj, ratios, isCorrelated):
        assert obj._is_ratio_correlated(ratios) == isCorrelated

    @pytest.mark.parametrize(
        "channelblock, isCorrelated",
        [
            pytest.param([[0.5, 0.5, 0.5]] * 2, True, id="FakeStereo"),
            pytest.param([[0.00308228, 0.00613403]] * 2, True, id="FakeStereoFloat"),
            pytest.param(
                [
                    [0.22900572, 0.2323956, 0.23575126, 0.23910689],
                    [0.11450286, 0.1161978, 0.11787563, 0.11955345],
                ],
                True,
                id="PannedMono",
            ),
            pytest.param(
                [
                    [0.99996948, 0.99996948, 0.99996948],
                    [0.99996948, 0.99804688, 0.99609375],
                ],
                False,
                id="TrueStereo",
            ),
            pytest.param([[0.0, 0.0, 0.0]] * 2, True, id="Empty"),
            pytest.param(
                [[0, 1, 2], [0, 1, 2], [0, -1, -1.5]], False, id="Multichannel"
            ),
        ],
    )
    def test_is_channelblock_correlated(self, obj, channelblock, isCorrelated):
        assert obj._is_channelblock_correlated(channelblock) == isCorrelated

    def test_get_sample_from_sampleblock(self, obj):
        obj.reset_sample()
        assert obj.sample == []
        assert obj._get_sample_from_sampleblock(
            [[0.00308228, 0.00308228], [0.00613403, 0.00613403]]
        ) == [0.00613403, 0.00613403]
        assert obj._get_sample_from_sampleblock(
            [[0.99996948, 0.0], [0.99996948, 0.99804688], [0.99996948, 0.99609375]]
        ) == [0.99996948, 0.99804688]
        obj.sample = [0.1, 0.2]
        assert obj._get_sample_from_sampleblock([[0.2, 0.5,]]) == [0.2, 0.5]
        obj.sample = [0.8, 0.8]
        assert obj._get_sample_from_sampleblock([[0.2, 0.5,]]) == [0.8, 0.8]
        assert obj._get_sample_from_sampleblock([[]]) == [0.8, 0.8]
        obj.reset_sample()

    @pytest.mark.parametrize(
        "sample, result",
        [
            pytest.param([0.5, 0.3], False, id="Stereo"),
            pytest.param([0.5], True, id="Mono"),
            pytest.param([0.5, 0.5], True, id="FakeStereo"),
            pytest.param([0, 0], True, id="Zero"),
            pytest.param([0, 1, -1], False, id="TrueMultichannel"),
            pytest.param([0.5]*4, True, id="FakeMultichannel"),
        ]
    )
    def test_is_sample_identical(self, obj, sample, result):
        assert obj._is_sample_identical(sample) == result

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
