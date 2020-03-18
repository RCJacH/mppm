import os
import shutil
from music_production_project_manager.audio_file_handler import AudioFile


extensions = [".wav", ".wave"]
"""
Potential additions supported by PySoundFile library
{'AIFF': 'AIFF (Apple/SGI)',
 'AU': 'AU (Sun/NeXT)',
 'AVR': 'AVR (Audio Visual Research)',
 'CAF': 'CAF (Apple Core Audio File)',
 'FLAC': 'FLAC (FLAC Lossless Audio Codec)',
 'HTK': 'HTK (HMM Tool Kit)',
 'IRCAM': 'SF (Berkeley/IRCAM/CARL)',
 'MAT4': 'MAT4 (GNU Octave 2.0 / Matlab 4.2)',
 'MAT5': 'MAT5 (GNU Octave 2.1 / Matlab 5.0)',
 'MPC2K': 'MPC (Akai MPC 2k)',
 'NIST': 'WAV (NIST Sphere)',
 'OGG': 'OGG (OGG Container format)',
 'PAF': 'PAF (Ensoniq PARIS)',
 'PVF': 'PVF (Portable Voice Format)',
 'RAW': 'RAW (header-less)',
 'RF64': 'RF64 (RIFF 64)',
 'SD2': 'SD2 (Sound Designer II)',
 'SDS': 'SDS (Midi Sample Dump Standard)',
 'SVX': 'IFF (Amiga IFF/SVX8/SV16)',
 'VOC': 'VOC (Creative Labs)',
 'W64': 'W64 (SoundFoundry WAVE 64)',
 'WAV': 'WAV (Microsoft)',
 'WAVEX': 'WAVEX (Microsoft)',
 'WVE': 'WVE (Psion Series 3)',
 'XI': 'XI (FastTracker 2)'}
"""


def _iterate_files(folder):
    return (os.path.join(folder, f) for f in _list_audio_files(folder))


def _create_analysis(filepath, options):
    return AudioFile(
        filepath,
        null_threshold=options["null_threshold"],
        empty_threshold=options["empty_threshold"],
    )


def _list_audio_files(folder):
    return (f for f in os.listdir(folder) if _is_audio_file(f))


def _is_audio_file(file):
    _, file_extension = os.path.splitext(file)
    return file_extension.upper() in (name.upper() for name in extensions)


class FileList:
    def __init__(self, folder=None, options=None):
        self._options = options or {
            "noBackup": False,
            "backup": {"folder": "bak"},
            "null_threshold": -100,
            "empty_threshold": -100,
        }
        self._files = []
        self._folderpath = ""
        self.folderpath = folder

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

    files = property(lambda self: self._files)

    fileCount = property(lambda self: len(self.files))

    filenames = property(lambda self: [f.filename for f in self.files])

    filepaths = property(lambda self: [f.filepath for f in self.files])

    empty_files = property(lambda self: [f for f in self.files if f.isEmpty])

    fake_stereo_files = property(lambda self: [f for f in self.files if f.isFakeStereo])

    multichannel_files = property(
        lambda self: [f for f in self.files if f.isMultichannel]
    )

    options = property(lambda self: dict(self._options))

    @property
    def folderpath(self):
        return self._folderpath

    @folderpath.setter
    def folderpath(self, folder):
        if folder and os.path.exists(folder):
            self._files = []
            self._folderpath = folder
            for file in self.search_folder(folder):
                pass

    def update_options(self, options={}):
        self._options.update(options)

    def search_folder(self, folder, populate=True, func=None):
        for f in _iterate_files(folder):
            af = _create_analysis(f, self._options)
            if populate:
                self._files.append(af)
            yield af

    def proceed(self):
        if not self.options.pop("noBackup", False):
            self.backup(**self.options.pop("backup", {}))
        for file in self._files:
            file.proceed(options=self.options)
        self.folderpath = self.folderpath

    def backup(self, folder="bak", newFolder=True, read_only=False):
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

        def backup(file):
            filename, ext = os.path.splitext(file._filename)
            newfile = unique(folderpath, filename, new=False, ext=ext)
            return file.backup(newfile, read_only=read_only)

        bakpath, bakfolder = os.path.split(folder)
        path = self.folderpath if (not bakpath or bakpath.isspace) else bakpath
        folderpath = unique(path, bakfolder, new=newFolder)

        return [backup(f) for f in self._files]
