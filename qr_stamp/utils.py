import cv2
from pathlib import Path


def get_file_name(path, with_extension=True):
    if issubclass(type(path), Path):
        if with_extension:
            return path.name
        else:
            return path.stem
    else:
        if with_extension:
            return Path(str(path)).name
        else:
            return Path(str(path)).stem


def resize_to_width(img, width):
    h, w = img.shape[:2]
    new_h = int(h * width / w)
    return cv2.resize(img, (width, new_h))
