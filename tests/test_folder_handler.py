import os
import pytest
from music_production_project_manager.folder_handler import FileList


def get_audio_path(filename=""):
    return os.path.join("tests", "audio_files", filename)


class TestFileList:
    @pytest.mark.parametrize(
        "options, result",
        [
            ({}, {"_folderpath": get_audio_path(),}),
            (
                {},
                {
                    "fileCount": 9,
                    "filenames": [
                        get_audio_path(filename=x + ".wav")
                        for x in (
                            "0-m",
                            "0-s",
                            "empty",
                            "sin-l50",
                            "sin-m",
                            "sin-r25",
                            "sin-r100",
                            "sin-s",
                            "sin+tri",
                        )
                    ],
                },
            ),
        ],
    )
    def test__init__(self, options, result):
        with FileList(folder=get_audio_path(), options=options) as obj:
            for item in result:
                if isinstance(result[item], list):
                    L1 = getattr(obj, item)
                    L2 = result[item]
                    assert len(L1) == len(L2) and sorted(L1) == sorted(L2)
                else:
                    assert getattr(obj, item) == result[item]
