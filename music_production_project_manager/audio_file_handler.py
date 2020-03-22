import math
import os
import shutil
import re

import numpy as np
from soundfile import SoundFile as sf
from soundfile import SEEK_END

from music_production_project_manager.analyze import SampleblockChannelInfo
from music_production_project_manager.utils import lazy_property

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
        options=None,
    ):
        LOGGER.debug(
            f"Initiating file: {self.__class__.__name__}, with filepath: {filepath}"
        )
        self._filepath = filepath
        self._file = None
        self._location = None
        self.blocksize = None if str(blocksize) == "None" else int(blocksize)
        self._channels = None
        self._validChannel = 0
        self._debug = debug
        self._flag = None
        self._isCorrelated = None
        self._sample = None
        self._samplerate = None
        self._action = "D"
        self.null_threshold = 10 ** (null_threshold / 20)
        self.empty_threshold = 10 ** (empty_threshold / 20)
        self._options = options or {"delimiter": "."}
        if filepath is not None and analyze:
            self.file = filepath

    def __del__(self):
        self.close()

    def __enter__(self):
        if self._file is None and self._filepath is not None:
            self.file = self._filepath
        return self

    def __exit__(self, *args):
        self.close()

    def __eq__(self, other):
        return isinstance(other, AudioFile) and self._filepath == other._filepath

    @lazy_property
    def location(self):
        dirname, basename = os.path.split(self._filepath)
        root, ext = os.path.splitext(self._filepath)
        filename = basename[: -len(ext)]
        try:
            filebase, ch = filename.rsplit(self.options.get("delimiter", "."), 1)
            channelname = "1" if ch == "L" else "2" if ch == "R" else ch
        except ValueError:
            filebase = filename
            channelname = ""
        self._location = {
            "dirname": dirname,
            "basename": basename,
            "filename": filename,
            "extension": ext,
            "root": root,
            "filebase": filebase,
            "channelname": channelname,
        }
        return self._location

    filepath = property(lambda self: self._filepath)
    dirname = property(lambda self: self.location["dirname"])
    basename = property(lambda self: self.location["basename"])
    filename = property(lambda self: self.location["filename"])
    extension = property(lambda self: self.location["extension"])
    root = property(lambda self: self.location["root"])
    filebase = property(lambda self: self.location["filebase"])
    channelname = property(lambda self: self.location["channelname"])

    validChannel = property(lambda self: self._validChannel)

    countValidChannel = property(lambda self: bin(self.validChannel).count("1"))

    channels = property(
        lambda self: self._file.channels if self._file else self._channels
    )

    flag = property(lambda self: self._flag)

    frames = property(lambda self: self._file.frames)

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

    options = property(lambda self: dict(self._options))

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
            "N": "None",
        }[self._action]

    @action.setter
    def action(self, v):
        if v in "DMRSJN" or v.lower() in (
            "default",
            "monoize",
            "remove",
            "split",
            "join",
            "none",
        ):
            self._action = v

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

    def default_action(self, options={}):
        m = options.pop("monoize", True)
        r = options.pop("remove", True)
        j = options.pop("join", True)
        if self.isEmpty and r:
            return "R"
        if self.isFakeStereo and m:
            return "M"
        if options.pop("join_file", False) and j:
            return "J"
        return "N"

    def proceed(self, options={}):
        if options.pop("read_only", False):
            return self.action

        if self._action == "M":
            return self.monoize(**options.pop("monoize_options", {}))
        if self._action == "R":
            return self.remove(forced=True)
        if self._action == "S":
            return self.split(**options.pop("split_options", {}))
        if self._action == "J":
            return self.join(**options.pop("join_options", {}))

    def backup(self, filepath, read_only=False):
        try:
            if not read_only:
                shutil.copy2(self._filepath, filepath)
            return filepath
        except FileNotFoundError:
            path = os.path.split(filepath)[0]
            os.makedirs(path)
            return self.backup(filepath)

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

    def split(self, delimiter=".", remove=True):
        if self.file and self.channels > 1:
            channelnames = ("L", "R") if self.channels == 2 else range(self.channels)
            for i, ch in enumerate(channelnames):
                self.file.seek(0)
                data = self.file.read()[i]
                st = self.file.subtype
                ed = self.file.endian
                fm = self.file.format
                with sf(
                    self.root + delimiter + ch + self.extension,
                    "w",
                    self._samplerate,
                    1,
                    st,
                    ed,
                    fm,
                    True,
                ) as f:
                    f.write(data)
            if remove:
                self.remove(forced=True)

    def join_old(self, other=None, remove=True):
        s = re.match(r"(.+)([^\a])([lL]|[rR])$", self.root)
        if s:
            base, delimiter, ch = s.groups()
            chs = ["L", "R"]
            chnum = chs.index(ch)
            data = self.file.read(always_2d=True)
            chs.remove(ch)
            newfile = base + delimiter + chs[0] + self.extension
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
            with sf(
                base + self.extension, "w", self._samplerate, 2, st, ed, fm, True,
            ) as f:
                f.write(data)
            if remove:
                self.close()
                os.remove(self._filepath)

    def join(self, others=None, remove=True, forced=False, newfile=None, delimiter="."):
        if not others:
            return

        if not isinstance(others, list):
            others = [others]

        data = None
        a = [self]
        max_frames = self.frames
        for each in others:
            if not isinstance(each, AudioFile):
                if not os.path.exists(each):
                    raise FileNotFoundError
                each = AudioFile(each)
            a.append(each)
            max_frames = max(max_frames, each.frames)

        pos = len(others) // 10 + 2
        newfile = (
            (self.root[-pos] == delimiter and self.root[:-pos] + self.extension)
            if (not newfile and delimiter)
            else newfile
            if newfile
            else self.filepath
        )

        st = self.file.subtype
        ed = self.file.endian
        fm = self.file.format

        for each in a:
            if each.frames != self.frames and not forced:
                return
            d = each.file.read(always_2d=True)
            if each.frames < max_frames and forced:
                np.pad(d, (0, max_frames - each.frames), "constant")
            data = d if data is None else np.concatenate((data, d), axis=1)

        with sf(newfile, "w", self._samplerate, 1 + len(others), st, ed, fm, True) as f:
            f.write(data)
        if remove:
            for each in a:
                each.remove(forced=True)
        return newfile
