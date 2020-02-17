from soundfile import SoundFile as sf
from soundfile import SEEK_END
from music_production_project_manager.analyze import SampleblockChannelInfo

import logging

logging.basicConfig(
    # handlers=[logging.FileHandler('build_json_list.log', 'w', 'utf-8')],
    # level=logging.INFO,
    format="%(levelname)s:%(asctime)s:%(message)s"
)
LOGGER = logging.getLogger(__name__)


class AudioFile:
    def __init__(
        self,
        filename=None,
        blocksize=None,
        debug=False,
        threshold=0,
        analyze=True,
        action=None,
    ):
        LOGGER.info("Initiating file: %s", filename)
        self._filename = filename
        self._file = None
        self.blocksize = blocksize
        self._keepChannel = 0
        self._debug = debug
        self._flag = None
        self._isCorrelated = None
        self._sample = None
        self.NULL_THRESHOLD = threshold
        if filename is not None:
            try:
                self.file = filename
            except RuntimeError:
                self.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __str__(self):
        empty = self.isEmpty and "Empty" or ""
        fake = self.isFakeStereo and "FakeStereo" or ""
        info = "\t".join(["{0.filename}", "Channels: {0.channels}", empty, fake])
        return info.format(self)

    def close(self):
        if self.file:
            self.file.close()
            self._file = None
            self._channel = None

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = sf(file)
        if not self.blocksize:
            self.blocksize = self._file.samplerate
            self._keepChannel = self.analyze()
            # LOGGER.info('Finished Analyzing channel properties: channel == %s; empty == %s; fake == %s;', self.channel, self.isEmpty, self.isFakeStereo)
            self._file.seek(0)

    filename = property(lambda self: self._filename)

    keepChannel = property(lambda self: self._keepChannel)

    validChannels = property(lambda self: bin(self.keepChannel).count("1"))

    channels = property(lambda self: self._file.channels if self._file else 0)

    flag = property(lambda self: self._flag)

    isCorrelated = property(lambda self: self._isCorrelated)

    sample = property(lambda self: self._sample)

    isMono = property(lambda self: self.validChannels == 1)

    isEmpty = property(lambda self: self.keepChannel == 0 or self.channels == 0)

    isFakeStereo = property(lambda self: self.isMono and self.channels == 2)

    isMultichannel = property(lambda self: self.validChannels > 2 and self.channels > 2)

    def _identify_valid_channels(
        self, flag=0, isCorrelated=False, sample=[], eof=False
    ):
        """ Analyze which channels to keep

        Possibility for channels
        L == 0; # Empty
        L != 0;
        L == R == 0; # Empty
        L != 0; R == 0; # Channel 0
        L == 0; R != 0; # Channel 1
        L * ratio == R; # Channel = R if ratio > 1 else L
        L * ratio != R; # Stereo
        """
        LOGGER.debug(
            "Analyzing channel info: flag=%s; correlated=%s; sample=%s",
            str(flag),
            str(isCorrelated),
            str(sample),
        )
        if self.channels == 1 and flag:
            return 1  # Single Channel -> Mono
        if not isCorrelated and "0" not in bin(flag)[2:]:
            return flag  # True Multichannel
        if eof:
            if not flag or flag == 0:
                return 0  # Empty File
            if isCorrelated:
                try:
                    return sample.index(max(sample, key=abs))
                except IndexError:
                    raise Exception("Sample argument must have at least length of 1.")
            else:
                return flag
        return None

    def _get_channel_info_from_sampleblock(self, sampleblock, info=None):
        if info is None:
            info = {
                "flag": None,
                "isCorrelated": None,
                "sample": None,
                "threshold": self.NULL_THRESHOLD,
            }
        info["sampleblock"] = sampleblock
        return SampleblockChannelInfo(**info)

    def _analyze_blocks(self):
        info = None
        for sampleblock in self.file.blocks(blocksize=self.blocksize, always_2d=True):
            info = self._get_channel_info_from_sampleblock(sampleblock, info)
        return info

    def analyze(self):
        if self.file:
            info = self._analyze_blocks()
            # flag = correlated = sample = None
            # for sampleblock in self.file.blocks(
            #     blocksize=self.blocksize, always_2d=True
            # ):
            #     info = SampleblockChannelInfo(
            #         sampleblock=sampleblock,
            #         flag=flag,
            #         isCorrelated=correlated,
            #         sample=sample,
            #         threshold=self.NULL_THRESHOLD,
            #     )
            #     flag = info.flag
            #     correlated = info.isCorrelated
            #     sample = info.sample
            # channel = self._identify_valid_channels(flag, correlated, sample)
            self._flag = info.flag
            self._isCorrelated = info.isCorrelated
            self._sample = info.sample
            print(self.flag, self.isCorrelated, self.sample)
            return self._identify_valid_channels(
                self.flag, self.isCorrelated, self.sample, eof=True
            )
        else:
            return None
