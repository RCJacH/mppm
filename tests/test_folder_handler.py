import os
import shutil
import pytest
from music_production_project_manager.folder_handler import FileList


def get_audio_path(filename=""):
    return os.path.join("tests", "audio_files", filename)


audio_files = [
    "0-m",
    "0-s",
    "empty",
    "sin-l50",
    "sin-m",
    "sin-r25",
    "sin-r100",
    "sin-s",
    "sin+tri",
]


class TestFileList:
    @pytest.mark.parametrize(
        "options, result",
        [
            ({}, {"_folderpath": get_audio_path(),}),
            (
                {},
                {
                    "basenames": [x + ".wav" for x in audio_files],
                    "filepaths": [
                        get_audio_path(filename=x + ".wav") for x in audio_files
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

    def test_folderpath(self):
        with FileList() as obj:
            assert len(obj) == 0
            obj.folderpath = get_audio_path()
            assert obj.folderpath == get_audio_path()
            assert len(obj) == len(audio_files)
            assert set(x.filepath for x in obj) == set(
                get_audio_path(x + ".wav") for x in audio_files
            )

    def test_update_options(self):
        options = {"a": "aa", "b": "bb"}
        with FileList(options=options) as obj:
            obj.update_options({"c": "cc"})
            assert obj.options == {"a": "aa", "b": "bb", "c": "cc"}
            obj.update_options({"a": "ab"})
            assert obj.options == {"a": "ab", "b": "bb", "c": "cc"}
            assert obj.options.pop("a") == "ab"
            assert obj.options == {"a": "ab", "b": "bb", "c": "cc"}

    def test_proceed(self, mocker):
        with FileList(get_audio_path()) as obj:
            obj.backup = mocker.Mock()
            obj.update_options({"read_only": True})
            assert "read_only" in obj.options
            obj.proceed()
            obj.backup.assert_called()

    @pytest.mark.parametrize(
        "params",
        [
            pytest.param({}, id="default"),
            pytest.param({"folderExists": True}, id="inc-foldername"),
            pytest.param({"fileExists": True, "newFolder": False}, id="inc-filename"),
        ],
    )
    def test_backup(self, tmp_path, params):
        def ignore_py(folder, content):
            return [f for f in content if os.path.splitext(f)[1] == ".py"]

        path = get_audio_path()
        shutil.copytree(
            path, tmp_path, dirs_exist_ok=True, ignore=ignore_py,
        )

        bakpath = os.path.join(tmp_path, "bak")

        if params.pop("folderExists", False):
            os.makedirs(bakpath)
            bakpath += "1"

        if params.pop("fileExists", False):
            shutil.copytree(
                tmp_path, bakpath, dirs_exist_ok=True,
            )

        with FileList(tmp_path) as obj:
            f = obj.backup(**params)
            assert os.path.exists(bakpath)
            assert set(os.listdir(bakpath)) == set(f + ".wav" for f in audio_files)
