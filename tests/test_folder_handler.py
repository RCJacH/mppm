import os
import shutil
import pytest
from music_production_project_manager.folder_handler import FileList
from music_production_project_manager.audio_file_handler import AudioFile


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
            assert len(obj[1:3]) == 2

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

    @pytest.mark.parametrize(
        "files, result",
        [
            pytest.param(["sin"], {}, id="single-NoAction"),
            pytest.param(("san", "sin.L", "tri.L"), {}, id="no-pair"),
            pytest.param(
                ("sin.L", "sin.R"), {"sin": ("sin.L", "sin.R")}, id="one-pair"
            ),
            pytest.param(
                ("san", "sin.L", "sin.R", "tri"),
                {"sin": ("sin.L", "sin.R")},
                id="one-pair-with-other",
            ),
            pytest.param(
                ("san", "sin.L", "sin.R", "tri.L", "tri.R"),
                {"sin": ("sin.L", "sin.R"), "tri": ("tri.L", "tri.R")},
                id="two-pairs-with-other",
            ),
            pytest.param(
                ("san", "sin.L", "sin.R", "tri.L", "tri.R"),
                {"sin": ("sin.L", "sin.R"), "tri": ("tri.L", "tri.R")},
                id="two-pairs-with-other",
            ),
            pytest.param(
                ("sin.1", "sin.2", "sin.3"),
                {"sin": ("sin.1", "sin.2", "sin.3")},
                id="multichannel",
            ),
            pytest.param(("san", "sin.2", "sin.R"), {}, id="ignore-same-channel"),
            pytest.param(
                (
                    "san",
                    "sin.1",
                    "sin.2",
                    "sin.3",
                    "tri.L",
                    "tri.R",
                    "tri.3",
                    "saw.2",
                    "saw.R",
                    "saw.wave",
                ),
                {
                    "sin": ["sin.1", "sin.2", "sin.3"],
                    "tri": ["tri.L", "tri.R", "tri.3"],
                },
                id="mixed",
            ),
        ],
    )
    def test__search_for_join(self, tmp_path, files, result):
        filepath = get_audio_path("sin-m.wav")
        ext = ".wav"
        files = [os.path.join(tmp_path, x + ext) for x in files]
        for f in files:
            shutil.copyfile(filepath, f)

        with FileList(tmp_path) as obj:
            assert {
                k: [x.filepath for x in v] for k, v in obj._search_for_join().items()
            } == {
                k: [os.path.join(tmp_path, x + ext) for x in v]
                for k, v in result.items()
            }

    @pytest.mark.parametrize(
        "lists, filename, result",
        [
            pytest.param(
                {"sin": ["sin.L", "sin.R"]},
                "sin.L",
                {"first": True, "others": ["sin.R"], "newfile": "sin"},
                id="first",
            ),
            pytest.param(
                {"sin": ["sin.L", "sin.R"]}, "sin.R", {"first": False}, id="second"
            ),
        ],
    )
    def test__get_join_options(self, tmp_path, mocker, lists, filename, result):
        ext = ".wav"
        lists = {
            k: [os.path.join(tmp_path, x + ext) for x in v] for k, v in lists.items()
        }
        filepath = os.path.join(tmp_path, filename + ext)
        if "others" in result:
            result.update(
                {"others": [(os.path.join(tmp_path, x + ext)) for x in result["others"]]}
            )
        f = AudioFile(filepath, analyze=False)
        with FileList() as fl:
            fl.joinlists = mocker.Mock(return_value=lists).return_value
            assert fl._get_join_options(f) == result
