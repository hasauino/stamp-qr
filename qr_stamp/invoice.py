import base64
import csv
import tempfile
from pathlib import Path

import cv2
import numpy as np
import qrcode

from qr_stamp.exceptions import EncodingError, QRGenerationError, OpenInvoiceError
from qr_stamp.msgs import error, warn
from qr_stamp.utils import resize_to_width


def get_invoices_data(csv_path):
    if len(csv_path) == 0:
        warn(title="Choose CSV",
             body=f"Please choose a configuration CSV file")
        return None
    if not Path(csv_path).exists():
        error(title="File Not Found",
              body=f"Config CSV file not found in:\n{csv_path}")
        return None
    header_expected = ['COMPANY', 'VAT NUM',
                       'DATE', 'VAT', 'TOTAL', 'INV', 'QR']
    data = {}
    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = [label.lower().strip() for label in next(reader)]
        if len(header) != len(header_expected):
            error(title="Wrong CSV Config format",
                  body=f"CSV Configuration file should have {len(header_expected)} columns")
            return None
        if not header == [label.lower() for label in header_expected]:
            error(title="Wrong CSV Config format",
                  body=f"Header Columns should be: {header_expected}")
            return None
        for i, row in enumerate(reader):
            if len(row) != len(header_expected):
                error(title="File Not Found",
                      body=f"CSV Configuration file row number {i+2} should have {len(header_expected)} columns")
                return None
            data[row[5]] = row
    return data


class Invoice:
    header_expected = ['company', 'vat num',
                       'date', 'vat', 'total', 'inv', 'qr']

    def __init__(self, data) -> None:
        self.data = data
        self.parse()
        try:
            self.generate_text()
            self.encode()
        except Exception:
            raise EncodingError

    def insert_to_excel_file(self, excel, abs_path, scale):
        # generate image and save it to a tmp path
        tmp_dir = tempfile.gettempdir()
        tmp_img_path = Path(tmp_dir) / "stamp.png"
        qr_img = self.generate_qr()
        cv2.imwrite(str(tmp_img_path), qr_img)
        try:
            wb = excel.Workbooks.Open(abs_path)
        except:
            raise OpenInvoiceError
        sheet_name = [sh.Name for sh in wb.Sheets][0]  # could raise IndexError
        ws = wb.Worksheets(sheet_name)
        cell = ws.Range(self.qr_cell)
        picture = ws.Pictures().Insert(tmp_img_path)
        cell_width = cell.Width
        aspect = picture.Width / picture.Height
        picture_width = cell_width * scale
        picture_height = int(picture_width/aspect)
        picture.Width = picture_width
        picture.Height = picture_height
        picture.Left = cell.Left + (cell_width - picture_width) / 2
        picture.Top = cell.Top
        wb.Save()
        wb.Close()

    def generate_qr(self, width=None):
        try:
            qr_pil_img = qrcode.make(self.encoded_text)
            gray_qr = np.uint8(np.array(qr_pil_img) * 255)
            qr = cv2.cvtColor(gray_qr, cv2.COLOR_GRAY2RGB)
        except:
            raise QRGenerationError
        if width is None:
            return qr
        return resize_to_width(qr)

    def parse(self):
        (self.company, vat_number, date, vat_amount,
         total, self.file_name, self.qr_cell) = self.data
        self.vat_number = str(int(float(vat_number)))
        self.vat_amount = self.format_number(vat_amount)
        self.total = self.format_number(total)
        day, month, year = date.split("-")
        self.date = "{yyyy}-{mm}-{dd}".format(yyyy=year,
                                              mm=month, dd=day)
        self.time = "12:00:00.000"

    def encode(self):
        base64_bytes = base64.b64encode(self.bytes)
        self.encoded_text = base64_bytes.decode('ascii')

    def generate_text(self):
        self.bytes = b''.join([
            b'\x01',
            int.to_bytes(len(self.company), 1, 'big'),
            self.company.encode(),
            b'\x02',
            int.to_bytes(len(self.vat_number), 1, 'big'),
            self.vat_number.encode(),
            b'\x03',
            int.to_bytes(len(self.date+self.time+'TZ'), 1, 'big'),
            self.date.encode(),
            b'T',
            self.time.encode(),
            b'Z',
            b'\x05',
            int.to_bytes(len(self.vat_amount), 1, 'big'),
            self.vat_amount.encode(),
            b'\x04',
            int.to_bytes(len(self.total), 1, 'big'),
            self.total.encode(),
        ])

    @staticmethod
    def format_number(num_string):
        return "{:.2f}".format(float(num_string.replace(",", "")))
