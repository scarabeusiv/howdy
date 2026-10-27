from pathlib import PurePath
import grp
import os
import stat

import paths

models = [
    "shape_predictor_5_face_landmarks.dat",
    "mmod_human_face_detector.dat",
    "dlib_face_recognition_resnet_model_v1.dat",
]


def dlib_data_dir_path() -> str:
    return str(paths.dlib_data_dir)


def shape_predictor_5_face_landmarks_path() -> str:
    return str(paths.dlib_data_dir / models[0])


def mmod_human_face_detector_path() -> str:
    return str(paths.dlib_data_dir / models[1])


def dlib_face_recognition_resnet_model_v1_path() -> str:
    return str(paths.dlib_data_dir / models[2])


def user_model_path(user: str) -> str:
    return str(paths.user_models_dir / f"{user}.dat")


def config_file_path() -> str:
    return str(paths.config_dir / "config.ini")


def snapshots_dir_path() -> PurePath:
    return paths.log_path / "snapshots"


def snapshot_path(snapshot: str) -> str:
    return str(snapshots_dir_path() / snapshot)


def user_models_dir_path() -> PurePath:
    return paths.user_models_dir


def restrict_model_file(enc_file: str) -> None:
    """Apply the models directory's permission shape to a model file.

    The default shape is owner-only: mode 0600. Where the models directory
    opts into sharing -- it carries the setgid bit or its group is named
    "howdy" -- the file takes the directory's group and mode 0640 instead,
    so a PAM stack running in the owning user's context can read it. The
    directory's own mode still gates traversal, so a group-owned directory
    at mode 0700 grants no access by itself.
    """
    dir_stat = os.stat(os.path.dirname(enc_file))
    shared = bool(dir_stat.st_mode & stat.S_ISGID)
    if not shared:
        try:
            shared = grp.getgrgid(dir_stat.st_gid).gr_name == "howdy"
        except KeyError:
            shared = False
    if shared:
        os.chown(enc_file, -1, dir_stat.st_gid)
        os.chmod(enc_file, 0o640)
    else:
        os.chmod(enc_file, 0o600)


def gtk_binary_path() -> str:
    return str(paths.bin_dir / "howdy-gtk")


def logo_path() -> str:
    return str(paths.data_dir / "logo.png")
