import os
from music_production_project_manager.audio_file_handler import AudioFile





extensions = [".wav", ".wave"]
'''
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
'''
class FileList:

    def __init__(self, folder=None, options=None):
        self._folderpath = folder
        self._options = options or {}
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
        self._files = self.populate(folder)

    def populate(self, folder):
        return [AudioFile(os.path.join(folder, f),
                        **self._options,
                        ) for f in self._list_audio_files(folder)]

    def new_options(self, options):
        self._options = options

    files = property(lambda self: self._files)

    fileCount = property(lambda self: len(self.files))

    filenames = property(lambda self: [f.filename for f in self.files])

    filepaths = property(lambda self: [f.filepath for f in self.files])

    empty_files = property(lambda self: [f for f in self.files if f.isEmpty])

    fake_stereo_files = property(lambda self: [f for f in self.files if f.isFakeStereo])

    multichannel_files = property(lambda self: [f for f in self.files if f.isMultichannel])

    def _list_audio_files(self, folder):
        return [f for f in os.listdir(folder) if self._is_audio_file(f)]

    def _is_audio_file(self, file):
        _, file_extension = os.path.splitext(file)
        return file_extension.upper() in (name.upper() for name in extensions)
