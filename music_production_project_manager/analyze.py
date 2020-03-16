import numpy as np

np.seterr(divide="ignore", invalid="ignore")
from soundfile import SoundFile as sf
from soundfile import SEEK_END


class SampleblockChannelInfo:
    def __init__(
        self,
        null_threshold=0.00001,  # -100dB
        empty_threshold=0.00001,  # -100dB
        flag=0,
        isCorrelated=None,
        sample=None,
        sampleblock=None,
        noisefloor=0,
    ):
        """Analyze audio information in a single sampleblock

        Keyword Arguments:
            null_threshold {float} -- Ratios below this value are ignored. (default: {0.00001})
            empty_threshold {float} -- Sample value below this value are considered silent. (default: {0.00001})
            flag {int} -- Indicate which channel has valid sounding sample. (default: {0})
            isCorrelated {[float]} -- The panning if both channels have fixed ratio. (default: {None})
            sample {list} -- A valid sample of each channel of the same position. (default: {[]})
            sampleblock {[float]} -- Sampleblock to analyze. (default: {None})
            noisefloor {int} -- The lowest bit that contains information. (default: {0})
        """

        self.flag = flag
        self.isCorrelated = isCorrelated
        self.sample = [] if sample is None else sample
        self.null_threshold = null_threshold
        self.empty_threshold = empty_threshold
        self.noisefloor = noisefloor
        self.set_info(sampleblock)

    def set_info(self, sampleblock):
        """Analyze the sampleblock."""
        if type(sampleblock) is np.ndarray and sampleblock.size:
            self.set_channelblock(sampleblock)
            self.set_channels()
            self.set_flag(sampleblock)
            self.set_correlation(self.channelblock)
            self.set_sample(sampleblock)
        # self.set_noisefloor(sampleblock)

    def set_channelblock(self, sampleblock):
        """Channelblock is a transposed sampleblock."""
        self.channelblock = self._transpose(sampleblock)

    def _transpose(self, sampleblock):
        """Exchange the x and y dimensions of sampleblock."""
        return np.array(sampleblock).transpose(1, 0)

    def set_channels(self):
        """Number of channels of a sampleblock."""
        self.channels = len(self.channelblock)
        return self.channels

    def set_flag(self, sampleblock):
        """Flag on for each channel that contains a sample above empty threshold."""
        if self.flag is None:
            self.flag = 0
        a = np.any(np.absolute(sampleblock) >= self.empty_threshold, axis=0).astype(int)
        [self.flag_on(i + 1) for i, v in enumerate(a) if v]
        return self.flag

    def flag_on(self, n):
        """Turn a channel flag on, or reset all channel flags."""
        if type(n) is int:
            self.flag |= 1 << (n - 1)
        else:
            self.flag = 0
        return self.flag

    def set_correlation(self, channelblock):
        """Check whether audio is panned mono."""
        if self.isCorrelated is not False:
            self.isCorrelated = self.channels < 2 or self._is_channelblock_correlated(
                channelblock
            )

    def _is_channelblock_correlated(self, channelblock):
        """Analyze whether the sample-to-sample ratios of all channels are correlated."""
        ratios = [self._get_ratio(samples) for samples in channelblock]
        return self._is_ratio_correlated(ratios)

    def _get_ratio(self, samples):
        """Calculate the sample-to-sample ratio of all channels."""
        a = np.array(samples[:-1])
        b = np.array(samples[1:])
        return np.nan_to_num(np.divide(b, a, dtype="float")).tolist()

    def _is_ratio_correlated(self, ratios):
        """Check if the difference of ratios of all channels are below null threshold."""
        return (
            np.absolute(np.diff(np.array(ratios), axis=0)).flat < self.null_threshold
        ).all()

    def set_sample(self, sampleblock):
        """A valid sample of all channels with the same position."""
        self.sample = self._get_sample_from_sampleblock(sampleblock)

    def reset_sample(self):
        """Empty a sample of all channels."""
        self.sample = []

    def _get_sample_from_sampleblock(self, sampleblock):
        """Take a sample of all channels with the same position."""
        if self.sample:
            sampleblock = np.append([self.sample], sampleblock, axis=0)
        sampleblock = np.array(sampleblock)
        return self._get_valid_sample(sampleblock[np.all(sampleblock, axis=1), :])

    def _is_sample_identical(self, sample):
        """Check whether all channels of a sample have the same value."""
        return len(set(sample)) == 1

    def _get_valid_sample(self, sampleblock):
        """Check whether the sample has the highest absolute single-sample amplitude."""
        try:
            a = sampleblock[np.all(sampleblock != 0, axis=1), :]
            maxindex = np.unravel_index(np.argmax(np.absolute(a)), a.shape)
            return a[maxindex[0]].tolist()
        except ValueError:
            return self.sample

    # Noisefloor algorithm needs reconsideration for three reasons:
    # 1. Noisefloor should be above digital noisefloor value of 0 (float)
    # 2. Audio clip could contain fade in/outs that results in values lower than normal noisefloor
    # 3. Stem tracks combining several takes may have different noisefloor level due to bad
    #    gain-staging during recording
    # def set_noisefloor(self, channelblock):
    #     """Noisefloor is the lowest sample value"""
    #     newnoisefloor = np.concatenate(
    #             (
    #                 [self.noisefloor],
    #                 [self._get_noisefloor_from_channelblock(channelblock)],
    #             ),
    #             axis=0,
    #         ),
    #     self.noisefloor = np.amin(newnoisefloor, 1)
    #     return self.noisefloor

    # def _get_noisefloor_from_channelblock(self, channelblock):
    #     return np.amin(np.abs(channelblock), 1).flatten()
