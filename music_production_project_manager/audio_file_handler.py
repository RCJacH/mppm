import math
import os
import shutil
import re
import numpy as np

from soundfile import SoundFile as sf
from soundfile import SEEK_END

from music_production_project_manager.analyze import SampleblockChannelInfo

import logging

# logging.basicConfig(
# handlers=[logging.FileHandler('build_json_list.log', 'w', 'utf-8')],
# level=logging.INFO,
# format="%(levelname)s:%(asctime)s:%(message)s"
# )
LOGGER = logging.getLogger(__name__)


class AudioFile:
    def __init__(
        self,
        filepath=None,
        blocksize=None,
        debug=False,
        null_threshold=-100,
        empty_threshold=-100,
        analyze=True,
    ):
        LOGGER.debug(
            f"Initiating file: {self.__class__.__name__}, with filepath: {filepath}"
        )
        self._filepath = filepath
        self._file = None
        self.blocksize = blocksize
        self._channels = None
        self._keepChannel = 0
        self._debug = debug
        self._flag = None
        self._isCorrelated = None
        self._sample = None
        self._samplerate = None
        self._action = "D"
        self.null_threshold = 10 ** (null_threshold / 20)
        self.empty_threshold = 10 ** (empty_threshold / 20)
        if filepath is not None and analyze:
            self._path, self._filename = os.path.split(filepath)
            self.file = filepath

    def __del__(self):
        self.close()

    def __enter__(self):
        if self._file is None and self._filepath is not None:
            self.file = self._filepath
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
        try:
            self._file = sf(file)
            self._channels = self._file.channels
            self._samplerate = self._file.samplerate
            if not self.blocksize:
                self.blocksize = self._samplerate
            self.analyze()
            self._file.seek(0)
        except RuntimeError:
            self.close()

    @property
    def action(self):
        return {
            "D": "Default",
            "M": "Monoize",
            "R": "Remove",
            "S": "Split",
            "J": "Join",
        }[self._action]

    @action.setter
    def action(self, v):
        if v in ("DMRSJ"):
            self._action = v

    def proceed(self, options={}):
        noM = "skipMonoize" in options and options["skipMonoize"]
        noR = "skipRemove" in options and options["skipRemove"]
        if self._action == "D":
            if self.isFakeStereo and not noM:
                self.monoize()
            elif self.isEmpty and not noR:
                self.remove()
        if self._action == "M" and not noM:
            self.monoize(
                channel=options.pop("channel") if "channel" in options else None
            )
        if self._action == "R" and not noR:
            self.remove(forced=True)
        if self._action == "S":
            if "delimiter" in options:
                self.split(delimiter=options.pop("delimiter"))
            else:
                self.split()
        if self._action == "J":
            self.join()

    filepath = property(lambda self: self._filepath)

    path = property(lambda self: self._path)

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

    isMono = property(lambda self: self.channels == 1 and not self.isEmpty)

    isFakeStereo = property(
        lambda self: (self.isCorrelated or self.countValidChannel == 1)
        and self.channels == 2
        and not self.isEmpty
    )

    isStereo = property(
        lambda self: self.channels == 2
        and self.countValidChannel == 2
        and not self.isCorrelated
    )

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
            return sample.index(max(sample, key=abs)) + 1
        else:
            return flag

    def _analyze_blocks(self):
        info = SampleblockChannelInfo(
            flag=None,
            isCorrelated=None,
            sample=None,
            null_threshold=self.null_threshold,
            empty_threshold=self.empty_threshold,
        )
        for sampleblock in self.file.blocks(blocksize=self.blocksize, always_2d=True):
            info.set_info(sampleblock)
        return info

    def backup(self, folder="bak", newfolder=True, replace=False, noAction=False):
        def join(*args, inc="", ext=""):
            return (
                os.path.join(*args).rstrip("\\")
                + (inc if inc != "0" else "")
                + (ext if ext else "")
            )

        def unique(*args, new=False, **kwargs):
            if not new:
                return join(*args, **kwargs)
            name = ""
            i = 0
            while os.path.exists(name := join(*args, inc=str(i), **kwargs)):
                i += 1
            return name

        bakpath, bakfolder = os.path.split(folder)
        path = bakpath if bakpath != "" else self.path

        foldername = unique(path, bakfolder, new=newfolder)
        if not os.path.exists(foldername) and not noAction:
            os.makedirs(foldername)

        filename, ext = os.path.splitext(self._filename)
        newfile = unique(foldername, filename, new=(not replace), ext=ext)
        if not noAction:
            shutil.copyfile(self._filepath, newfile)
        return newfile

    def monoize(self, channel=None):
        if self.file and (channel or self.isFakeStereo):
            channel = channel or self._validChannel - 1
            data = [x[channel] for x in self.file.read()]
            self.file.close()
            st = self.file.subtype
            ed = self.file.endian
            fm = self.file.format
            with sf(self._filepath, "w", self._samplerate, 1, st, ed, fm, True) as f:
                f.write(data)
            self.file = self._filepath

    def remove(self, forced=False):
        if self.file and (forced or self.isEmpty):
            self.close()
            os.remove(self._filepath)

    def split(self, delimiter="."):
        if self.file and self.channels == 2:
            path, ext = os.path.splitext(self._filepath)
            for i, ch in enumerate(["L", "R"]):
                self.file.seek(0)
                data = self.file.read()[i]
                st = self.file.subtype
                ed = self.file.endian
                fm = self.file.format
                with sf(
                    path + delimiter + ch + ext,
                    "w",
                    self._samplerate,
                    1,
                    st,
                    ed,
                    fm,
                    True,
                ) as f:
                    f.write(data)
            self.remove(forced=True)

    def join(self, other=None, remove=True):
        path, ext = os.path.splitext(self._filepath)
        s = re.match(r"(.+)([^\a])([lL]|[rR])$", path)
        if s:
            base, delimiter, ch = s.groups()
            chs = ["L", "R"]
            chnum = chs.index(ch)
            data = self.file.read(always_2d=True)
            chs.remove(ch)
            newfile = base + delimiter + chs[0] + ext
            if not os.path.exists(newfile):
                return
            with AudioFile(newfile) as f:
                if chnum:
                    data = np.concatenate((f.file.read(always_2d=True), data), axis=1)
                else:
                    data = np.concatenate((data, f.file.read(always_2d=True)), axis=1)
                if remove:
                    f.remove()
            st = self.file.subtype
            ed = self.file.endian
            fm = self.file.format
            with sf(base + ext, "w", self._samplerate, 2, st, ed, fm, True) as f:
                f.write(data)
            if remove:
                self.close()
                os.remove(self._filepath)
