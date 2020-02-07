import numpy as np

np.seterr(divide="ignore", invalid="ignore")
from soundfile import SoundFile as sf
from soundfile import SEEK_END


class SampleblockChannelInfo:
    def __init__(
        self,
        threshold=0.00001,  # -100dB
        flag=0,
        isCorrelated=None,
        sample=[],
        sampleblock=None,
        noisefloor=0,
    ):
        """Analyze audio information in a single sampleblock

        Keyword Arguments:
            threshold {float} -- Ignore all samples below this value (default: {0.00001})
            flag {int} -- Previous channel flag info (default: {0})
            isCorrelated {[type]} -- Previous channel panning info (default: {None})
            sample {list} -- Previous sample value (default: {[]})
            sampleblock {[type]} -- sampleblock to analyze (default: {None})
            noisefloor {int} -- Previous noisefloor info (default: {0})

        Returns:
        flag -- Indicate which channel has valid sounding sample
        isCorrelated -- The panning if both channels have fixed ratio
        sample -- A valid sample of each channel of the same position
        noisefloor -- The lowest bit that contains information
        channels -- number of audio channels
        """
        self.flag = flag != None and flag
        self.isCorrelated = isCorrelated
        self.sample = sample != None and sample
        self.NULL_THRESHOLD = threshold
        self.noisefloor = noisefloor
        if sampleblock:
            self.set_info(sampleblock)

    def set_info(self, sampleblock):
        self.set_channelblock(sampleblock)
        self.set_channels()
        self.set_flag()
        self.set_correlation(self.channelblock)
        self.set_sample(sampleblock)
        # self.set_noisefloor(sampleblock)

    def set_channelblock(self, sampleblock):
        """Channelblock is a transposed sampleblock"""
        self.channelblock = self._transpose(sampleblock)

    def _transpose(self, sampleblock):
        return np.array(sampleblock).transpose(1, 0)

    def set_channels(self):
        self.channels = len(self.channelblock)
        return self.channels

    def set_flag(self):
        """Flag on for each channel that contains a sounding sample"""
        [
            self.flag_on(i + 1)
            for i, v in enumerate(self.channelblock)
            if any(x != 0 for x in v)
        ]
        return self.flag

    def flag_on(self, n):
        if type(n) is int:
            self.flag |= 1 << (n - 1)
        else:
            self.flag = 0
        return self.flag

    def set_correlation(self, channelblock):
        """Check whether audio is panned mono"""
        if self.isCorrelated is not False:
            self.isCorrelated = (
                True
                if self.channels == 1
                else self._is_channelblock_correlated(channelblock)
            )

    def _is_channelblock_correlated(self, channelblock):
        ratios = [self._get_ratio(samples) for samples in channelblock]
        return self._is_ratio_correlated(ratios)

    def _get_ratio(self, samples):
        a = np.array(samples[:-1])
        b = np.array(samples[1:])
        return np.nan_to_num(np.divide(b, a, dtype="float")).tolist()

    def _is_ratio_correlated(self, ratios):
        return (
            np.absolute(np.diff(np.array(ratios), axis=0)).flat < self.NULL_THRESHOLD
        ).all()

    def set_sample(self, sampleblock):
        """A valid sample of all channels with the same position"""
        self.sample = self._get_sample_from_sampleblock(sampleblock)

    def reset_sample(self):
        self.sample = []

    def _get_sample_from_sampleblock(self, sampleblock):
        if self.sample:
            sampleblock = np.append([self.sample], sampleblock, axis=0)
        sampleblock = np.array(sampleblock)
        return self._get_valid_sample(sampleblock[np.all(sampleblock, axis=1), :])

    def _is_sample_identical(self, sample):
        return len(set(sample)) == 1

    def _get_valid_sample(self, sampleblock):
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
