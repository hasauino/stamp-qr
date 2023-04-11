from pathlib import Path

import cv2


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


def generate_pdf(excel, document_path, out_dir):
    doc_name = get_file_name(document_path, with_extension=False)
    wb = excel.Workbooks.Open(str(document_path))
    file_path = out_dir / "{}.pdf".format(doc_name)
    wb.ExportAsFixedFormat (0, str(file_path), 0, True, False)
    wb.Close()
