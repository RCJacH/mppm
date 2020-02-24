import os
import shutil
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
        threshold=0.0001,
        analyze=True,
        action=None,
    ):
        LOGGER.info("Initiating file: %s", filename)
        self._filename = filename
        self._file = None
        self.blocksize = blocksize
        self._channels = None
        self._keepChannel = 0
        self._debug = debug
        self._flag = None
        self._isCorrelated = None
        self._sample = None
        self._samplerate = None
        self.NULL_THRESHOLD = threshold
        if filename is not None:
            try:
                self.file = filename
            except RuntimeError:
                self.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        if self._file is None and self._filename is not None:
            self.file = self._filename
        return self

    def __exit__(self, *args):
        self.close()

    def __str__(self):
        empty = self.isEmpty and "Empty" or ""
        fake = self.isFakeStereo and "FakeStereo" or ""
        info = "\t".join(["{0.filename}", "Channels: {0.channels}", empty, fake])
        return info.format(self)

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def read(self, *args, **kwargs):
        if self._file:
            yield self._file.read(*args, **kwargs)
            self._file.seek(0)

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = sf(file)
        self._channels = self._file.channels
        self._samplerate = self._file.samplerate
        if not self.blocksize:
            self.blocksize = self._samplerate
        self.analyze()
        # LOGGER.info('Finished Analyzing channel properties: channel == %s; empty == %s; fake == %s;', self.channel, self.isEmpty, self.isFakeStereo)
        self._file.seek(0)

    filename = property(lambda self: self._filename)

    validChannel = property(lambda self: self._validChannel)

    countValidChannel = property(lambda self: bin(self.validChannel).count("1"))

    channels = property(
        lambda self: self._file.channels if self._file else self._channels
    )

    flag = property(lambda self: self._flag)

    isCorrelated = property(lambda self: self._isCorrelated)

    sample = property(lambda self: self._sample)

    samplerate = property(lambda self: self._samplerate)

    isEmpty = property(lambda self: self.validChannel == 0 or self.channels == 0)

    isMono = property(
        lambda self: (self.isCorrelated or self.countValidChannel == 1)
        and not self.isEmpty
    )

    isFakeStereo = property(lambda self: self.isMono and self.channels == 2)

    isMultichannel = property(
        lambda self: self.channels > 2
        and self.countValidChannel > 2
        and not self.isCorrelated
    )

    def analyze(self):
        if self.file:
            info = self._analyze_blocks()
            if info is not None:
                self._flag = info.flag
                self._isCorrelated = info.isCorrelated
                self._sample = info.sample
            self._validChannel = self._analyze_valid_channels(
                self.flag, self.isCorrelated, self.sample
            )

    def _analyze_valid_channels(self, flag=0, isCorrelated=False, sample=[]):
        """ Analyze which channels to keep
        """
        if flag == None or flag == 0:
            return 0  # Empty File
        if self.channels == 1 and flag:
            return 1  # Single Channel -> Mono
        if not isCorrelated and "0" not in bin(flag)[2:]:
            return flag  # True Multichannel
        if isCorrelated:
            try:
                return sample.index(max(sample, key=abs)) + 1
            except IndexError:
                raise Exception("Sample argument must have at least length of 1.")
        else:
            return flag

    def _analyze_blocks(self):
        info = SampleblockChannelInfo(
            flag=None, isCorrelated=None, sample=None, threshold=self.NULL_THRESHOLD
        )
        for sampleblock in self.file.blocks(blocksize=self.blocksize, always_2d=True):
            info.set_info(sampleblock)
        return info

    def backup(self, folder="bak", newfolder=True, replace=False, noAction=False):
        def join(*args, inc="", ext=""):
            return (
                os.path.join(*args).rstrip("\\")
                + (inc if inc != "0" else "")
                + ("." + ext if ext else "")
            )

        def unique(*args, new=False, **kwargs):
            if not new:
                return join(*args, **kwargs)
            name = ""
            i = 0
            while os.path.exists(name := join(*args, inc=str(i), **kwargs)):
                i += 1
            return name

        oldpath, filename = os.path.split(self._filename)
        bakpath, bakfolder = os.path.split(folder)
        path = bakpath if bakpath != "" else oldpath

        foldername = unique(path, bakfolder, new=newfolder)
        if not os.path.exists(foldername) and not noAction:
            os.makedirs(foldername)

        filename, ext = filename.split('.')
        newfile = unique(foldername, filename, new=(not replace), ext=ext)
        if not noAction:
            shutil.copyfile(self._filename, newfile)
        return newfile

    def monolize(self, channel=None):
        if self.file and (channel or self.isFakeStereo):
            channel = channel or self._validChannel
            data = [x[channel] for x in self.file.read()]
            self.file.close()
            st = self.file.subtype
            ed = self.file.endian
            fm = self.file.format
            with sf(self._filename, "w", self._samplerate, 1, st, ed, fm, True) as f:
                f.write(data)
            self.file = self.filename

    def remove(self, forced=False):
        if self.file and (forced or self.isEmpty):
            self.close()
            os.remove(self._filename)
            del self

    def split(self):
        if self.file and self.channels == 2:
            path, ext = os.path.splitext(self._filename)
            for i, ch in enumerate([".L", ".R"]):
                self.file.seek(0)
                data = self.file.read()[i]
                st = self.file.subtype
                ed = self.file.endian
                fm = self.file.format
                with sf(path+ch+ext, "w", self._samplerate, 1, st, ed, fm, True) as f:
                    f.write(data)
            self.remove(forced=True)