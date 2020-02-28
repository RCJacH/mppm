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


class FileList:
    def __init__(self, folder=None, options=None):
        self._folderpath = folder
        self._options = options or {
            "noBackup": False,
            "backup": {},
            "threshold": 0.00001,
        }
        self._files = []
        # self.filenames = []
        # self.empty_files = []
        # self.mono_files = []
        # self.fake_stereo_files = []
        # self.stereo_files = []
        # self.multichannel_files = []
        if folder and os.path.exists(folder):
            self.search_folder(folder)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del self

    def search_folder(self, folder):
        self._folderpath = folder
        self._files = self.populate(folder)

    def populate(self, folder):
        return [
            AudioFile(os.path.join(folder, f), threshold=self._options["threshold"],)
            for f in self._list_audio_files(folder)
        ]

    def new_options(self, options):
        self._options.update(options)

    def proceed(self):
        if "noBackup" not in self._options or not self._options["noBackup"]:
            if "backup" in self._options:
                self.backup(**self._options["backup"])
            else:
                self.backup()
        for file in self._files:
            file.proceed(options=self._options)
        self._files = self.populate(self._folderpath)

    def backup(self, folder="bak", newFolder=True, replace=False, noAction=False):
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
        path = self._folderpath if (not bakpath or bakpath.isspace) else bakpath
        folderpath = unique(path, bakfolder, new=newFolder)
        if not os.path.exists(folderpath) and not noAction:
            os.makedirs(folderpath)

        for file in self._files:
            filename, ext = os.path.splitext(file._filename)
            newfile = unique(folderpath, filename, new=(not replace), ext=ext)
            if not noAction:
                shutil.copyfile(file._filepath, newfile)

    files = property(lambda self: self._files)

    fileCount = property(lambda self: len(self.files))

    filenames = property(lambda self: [f.filename for f in self.files])

    filepaths = property(lambda self: [f.filepath for f in self.files])

    empty_files = property(lambda self: [f for f in self.files if f.isEmpty])

    fake_stereo_files = property(lambda self: [f for f in self.files if f.isFakeStereo])

    multichannel_files = property(
        lambda self: [f for f in self.files if f.isMultichannel]
    )

    options = property(lambda self: self._options)

    def _list_audio_files(self, folder):
        return [f for f in os.listdir(folder) if self._is_audio_file(f)]

    def _is_audio_file(self, file):
        _, file_extension = os.path.splitext(file)
        return file_extension.upper() in (name.upper() for name in extensions)
