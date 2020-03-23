import math
import os
import shutil
import re

import numpy as np
from soundfile import SoundFile as sf
from soundfile import SEEK_END

from .analyze import SampleblockChannelInfo
from .utils import lazy_property

import logging

# logging.basicConfig(
# handlers=[logging.FileHandler('build_json_list.log', 'w', 'utf-8')],
# level=logging.INFO,
# format="%(levelname)s:%(asctime)s:%(message)s"
# )
LOGGER = logging.getLogger(__name__)


def _dB_to_float(v):
    return 10 ** (v / 20)


class AudioFile:
    """An Audio file.

    For more documentation see the __init__() docstring.

    """
    def __init__(
        self, filepath=None, blocksize=None, analyze=True, options=None,
    ):
        """Open an audio file.

        Parameters
        ----------
        filepath: str, optional
            The complete path to an audio file.
        blocksize: {str, int}, optional
            The size of sampleblock to be used for analysis.
        analyze: bool
            Whether to analyze the audio file, may be turned off for
            faster debugging of file info.
        options: dict, optional
            Options for working with the audio file. Possible Keys:
            delimiter: The string or character in the filename that
                separates root with its channel info. For example a
                filename called sin_R.wav has delimiter of underscore
                '_', with 'sin' as root, and R as it's channel.
            null_threshold: A decibels number to determine the maximum
                allowed differences between two channels for them to be
                considered different.
            empty_threshold: A decibels number to determine the lowest
                value before a sample is considered noise.

        """

        LOGGER.debug(
            f"Initiating file: {self.__class__.__name__}, with filepath: {filepath}"
        )
        self._filepath = filepath
        self._file = None
        self._location = None
        self.blocksize = None if str(blocksize) == "None" else int(blocksize)
        self._channels = None
        self._validChannel = 0
        self._flag = None
        self._isCorrelated = None
        self._sample = None
        self._samplerate = None
        self._action = "N"
        self._options = options or {"delimiter": "."}
        self.join_files = []
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

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        try:
            self._file = sf(file)
        except RuntimeError:
            self.close()
        else:
            self._channels = self._file.channels
            self._samplerate = self._file.samplerate
            if not self.blocksize:
                self.blocksize = self._file.frames
            self.analyze()
            self._file.seek(0)

    @property
    def action(self):
        """The action to take for the proceed method.

        Returns
        -------
        str
            The name of method to use, or 'None' to skip any action.
        """
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

    @lazy_property
    def location(self):
        """Information regarding the location of the audio file.

        Returns
        -------
        dict
            List of file location related information.
        """
        dirname, basename = os.path.split(self._filepath)
        root, ext = os.path.splitext(self._filepath)
        filename = basename[: -len(ext)]
        try:
            filebase, ch = filename.rsplit(self.delimiter, 1)
            ch = "1" if ch == "L" else "2" if ch == "R" else ch
            if ch.isdigit():
                channelnum = ch
            else:
                raise ValueError
        except ValueError:
            filebase = filename
            channelnum = ""
        self._location = {
            "dirname": dirname,
            "basename": basename,
            "filename": filename,
            "extension": ext,
            "root": root,
            "filebase": filebase,
            "channelnum": channelnum,
        }
        return self._location

    filepath = property(lambda self: self._filepath)
    """The absolute location of the file."""
    dirname = property(lambda self: self.location["dirname"])
    """The complete path to where the file is located."""
    basename = property(lambda self: self.location["basename"])
    """The filename with extension."""
    filename = property(lambda self: self.location["filename"])
    """The filename without extension."""
    extension = property(lambda self: self.location["extension"])
    """The extension of the file."""
    root = property(lambda self: self.location["root"])
    """The complete location to the file without the extension."""
    filebase = property(lambda self: self.location["filebase"])
    """The filename without the channel number, if there is any."""
    channelnum = property(lambda self: self.location["channelnum"])
    """The channel number in filename, such as 'L', 'R', or numerals."""

    options = property(lambda self: dict(self._options))
    null_threshold = property(
        lambda self: _dB_to_float(self.options.get("null_threshold", -100))
    )
    empty_threshold = property(
        lambda self: _dB_to_float(self.options.get("empty_threshold", -100))
    )
    delimiter = property(lambda self: self.options.get("delimiter", "."))

    validChannel = property(lambda self: self._validChannel)

    countValidChannel = property(lambda self: bin(self.validChannel).count("1"))

    channels = property(
        lambda self: self._file.channels if self._file else self._channels
    )

    frames = property(lambda self: self._file.frames)

    flag = property(lambda self: self._flag)

    isCorrelated = property(lambda self: self._isCorrelated)

    sample = property(lambda self: self._sample)

    samplerate = property(lambda self: self._samplerate)

    isEmpty = property(lambda self: self.validChannel == 0 or self.channels == 0)
    """File is pure noise or noisefloor."""
    isMono = property(lambda self: self.channels == 1 and not self.isEmpty)
    """File has 1 channel and not empty."""
    isFakeStereo = property(
        lambda self: (self.isCorrelated or self.countValidChannel == 1)
        and self.channels == 2
        and not self.isEmpty
    )
    """File has 2 channels with identical value."""
    isStereo = property(
        lambda self: self.channels == 2
        and self.countValidChannel == 2
        and not self.isCorrelated
    )
    """File has 2 channels with different values."""

    isMultichannel = property(
        lambda self: self.channels > 2
        and self.countValidChannel > 2
        and not self.isCorrelated
    )
    """File has more than 2 channels"""

    def update_options(self, options):
        self._options.update(options)

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def read(self, *args, **kwargs):
        if self._file:
            yield self._file.read(*args, **kwargs)
            self._file.seek(0)

    def analyze(self):
        """Analyze the audio file for channel information."""
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
        """Determine which channels have meaningful values."""
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
        """Determine the default action to take.

        Parameters
        ----------
        options : {str}, optional
            List of actions availlable.

        Returns
        -------
        str
            The action code to be used for action.setter.
        """
        m = options.get("monoize", True)
        r = options.get("remove", True)
        j = options.get("join", True)
        if self.isEmpty and r:
            return "R"
        if self.isFakeStereo and m:
            return "M"
        if self.join_files and j:
            return "J"
        return "N"

    def proceed(self, options={}):
        """Carry out the set action of the file.

        Parameters
        ----------
        options : dict, optional
            keyword arguments for the selected action method.
        """
        if options.get("read_only", False):
            return self.action

        if self._action == "M":
            return self.monoize(**options.get("monoize_options", {}))
        if self._action == "R":
            return self.remove(forced=True)
        if self._action == "S":
            return self.split(**options.get("split_options", {}))
        if self._action == "J":
            return self.join(**options.get("join_options", {}))

    def backup(self, filepath, read_only=False):
        """Make a identical copy of the file to a desinated filepath.

        Parameters
        ----------
        filepath : str
            The location of the new file, accepts both absolute and
            relative location string.
        read_only : bool, optional
            Display the result filepath for debugging.

        Returns
        -------
        str
            The location of the new file.
        """
        try:
            if not read_only:
                shutil.copy2(self._filepath, filepath)
            return filepath
        except FileNotFoundError:
            path = os.path.split(filepath)[0]
            os.makedirs(path)
            return self.backup(filepath)

    def monoize(self, channel=None):
        """Convert a non-mono audio file to single-channel one.

        Parameters
        ----------
        channel : int, optional
            The channel to keep manually. If no valid input received,
            the channel with the highest amplitude is selected, if the
            file is a fake stereo one.
        """
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
        """Remove the file from the system.

        Parameters
        ----------
        forced : bool, optional
            Remove even when the file is not empty.
        """
        if self.file and (forced or self.isEmpty):
            self.close()
            os.remove(self._filepath)

    def split(self, remove=True):
        """Split a non-single channeled file into mono files.

        Create a new mono audio file for each channel of the original
        one, mainly used for DAWs that distinguish between stereo audio
        files from mono ones.

        Parameters
        ----------
        remove : bool, optional
            Remove the original file from system, default to True.
        """
        if self.file and self.channels > 1:
            channelnums = ("L", "R") if self.channels == 2 else range(self.channels)
            for i, ch in enumerate(channelnums):
                self.file.seek(0)
                data = self.file.read()[i]
                st = self.file.subtype
                ed = self.file.endian
                fm = self.file.format
                with sf(
                    self.root + self.delimiter + ch + self.extension,
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

    def join(self, others=None, remove=True, forced=False, newfile=None):
        """Join several files together into a new one.

        Used for joining audio file of the same source but with different
        channels (multi-mic recordings) into a single multi-channeled or
        stereo file.

        Parameters
        ----------
        others : [str, AudioFile], optional
            List of other files to join, abort action if no other files
            are received.
        remove : bool, optional
            Whether to delete the original files after joining, by
            default True.
        forced : bool, optional
            Whether to join files even when they have different length,
            by default False.
        newfile : str, optional
            The absolute location of the new file, if no input, use path
            + filebase of self.

        Returns
        -------
        str
            The absolute location of the new file.

        Raises
        ------
        FileNotFoundError
            Any file not found in others will raise this error.
        """
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
            (self.root[-pos] == self.delimiter and self.root[:-pos] + self.extension)
            if (not newfile and self.delimiter)
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
