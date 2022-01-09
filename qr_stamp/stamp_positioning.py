from tempfile import template
import cv2
from numpy.core.numeric import ones_like
from pdf2image import convert_from_path
from PIL import Image
import qrcode
import numpy as np


class PDF2ImageConversionError(Exception):
    pass


def get_gradient_2d(start, stop, width, height, is_horizontal):
    if is_horizontal:
        return np.tile(np.linspace(start, stop, width), (height, 1))
    else:
        return np.tile(np.linspace(start, stop, height), (width, 1)).T


def pdf2img(abs_path):
    try:
        pages = convert_from_path(abs_path, dpi=400)
    except Image.DecompressionBombError:
        pages = convert_from_path(abs_path)
    except Exception:
        raise PDF2ImageConversionError
    return pages


def resize(img, scale):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


doc_path = "/home/hassan/Desktop/dev/qr-stamp/test/docs/01.pdf"

# getting inputs: document image + stamp image
doc = np.array(pdf2img(doc_path)[0])
graydoc = cv2.cvtColor(doc, cv2.COLOR_RGB2GRAY)

scale = 0.3
# resize image
graydoc = resize(graydoc, scale)

_qr_pil_img = qrcode.make("jnpoiniopniobiopbio")
grayqr = np.uint8(np.array(_qr_pil_img) * 255)  # grayscale qr
grayqr = resize(grayqr, scale)


# 1: blur document
doc_blured = cv2.GaussianBlur(graydoc, (301, 301), 0)

height, width = graydoc.shape


template_margin = 0.05
d = round(width*template_margin)
area_width = width - 2*d
area_height = height - 2*d
area_mid_y = round(area_height*2/3)
area_mid_x = round(area_width/2)


area = np.zeros([area_height, area_width])*255

area[0:area_mid_y, :] = get_gradient_2d(0, 1, area_width, area_mid_y, False)

template = np.zeros_like(graydoc)
template[d:d+area_height, d:d +
         area_width] = np.ones([area_height, area_width]) * 255


cv2.namedWindow("window", cv2.WINDOW_NORMAL)
cv2.imshow("window", area)
cv2.resizeWindow("window", 600, 900)
cv2.waitKey(0)
cv2.destroyAllWindows()
