import base64
import os
import re
from os import mkdir
from pathlib import Path
from random import randint

import cv2
import numpy as np
import qrcode
from pdf2image import convert_from_path
from PIL import Image, ImageTk

from qr_stamp.msgs import WarningMsg
from qr_stamp.msgs import error_msgs as err
from qr_stamp.msgs import generate_report
from qr_stamp.msgs import info_msgs as info
from qr_stamp.msgs import warning_msgs as warn
from qr_stamp.utils import generate_pdf_and_read_data, get_file_name


class EncodingError(Exception):
    pass


class QRGenerationError(Exception):
    pass


class StampBot:
    def __init__(self, gui, step_ratio=0.1):
        self.gui = gui
        self.step_ratio = step_ratio
        xlsx_re = r'[\w\d]+.*\.xlsx'
        self.xlsx_pattern = re.compile(xlsx_re, re.I)
        self.print = self.gui.pop_up

    def stamp_all(self, dir_path, stamp_ratio):
        skipped_total = 0
        skipped_documents = {
            "key_error": [],
            "encoding_error": [],
            "qr_generation_error": [],
            "read_error": [],
        }
        self.gui.progress_bar['value'] = 5
        documents = self.check_directory(dir_path)
        if documents is None:
            return None
        out_dir = Path(dir_path) / "out_docs"
        if not out_dir.exists():
            try:
                mkdir(out_dir)
            except:
                err.MKDIR_FAIL.popup()
                return None
        for i, excel_document_path in enumerate(documents):
            document_abs_path, data = generate_pdf_and_read_data(
                excel_document_path)
            document_name = get_file_name(
                document_abs_path, with_extension=False)
            document_name_with_xlsx = "{}.xlsx".format(document_name)
            try:
                qr_stamp = self.generate_qr(data)
            except EncodingError:
                skipped_documents["encoding_error"].append(
                    document_name_with_xlsx)
                skipped_total += 1
                continue
            except QRGenerationError:
                skipped_documents["qr_generation_error"].append(
                    document_name_with_xlsx)
                skipped_total += 1
                continue
            try:
                pages = convert_from_path(document_abs_path, dpi=400)
            except Image.DecompressionBombError:
                pages = convert_from_path(document_abs_path)
            except Exception as e:
                skipped_documents["read_error"].append(document_name_with_xlsx)
                skipped_total += 1
                continue
            # stamp only first page
            doc = np.array(pages[0])
            doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
            doc = self.add_stamp(
                doc, qr_stamp, stamp_ratio=stamp_ratio, step_ratio=self.step_ratio)
            doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
            stamped_page = Image.fromarray(doc)
            output_path = out_dir / "{}.pdf".format(document_name)
            stamped_page.save(output_path,
                              save_all=True,
                              append_images=pages[1:])
            self.gui.progress_bar['value'] = (i+1.0)/len(documents)*100.0
        if skipped_total > 0:
            report = generate_report(
                skipped_documents, skipped_total, len(documents))
            error = WarningMsg(title="Skipped some documents", body=report)
            error.popup()
        else:
            info.SUCCESS.popup()

    def preview(self, dir_path, stamp_ratio, size):
        documents = self.check_directory(dir_path)
        if documents is None:
            return None
        rand_index = randint(0, len(documents)-1)
        excel_document_path = documents[rand_index]
        document_abs_path, data = generate_pdf_and_read_data(
            excel_document_path)
        try:
            qr_stamp = self.generate_qr(data)
        except EncodingError:
            err.ENCODE_ERROR.popup(get_file_name(excel_document_path))
            return None
        except QRGenerationError:
            err.QR_ERROR.popup(get_file_name(excel_document_path))
            return None
        try:
            pages = convert_from_path(document_abs_path, dpi=400)
        except Image.DecompressionBombError:
            pages = convert_from_path(document_abs_path)
        except:
            err.READ_ERROR.popup(excel_document_path)
            return None
        # stamp only first page
        doc = np.array(pages[0])
        doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
        doc = self.add_stamp(
            doc, qr_stamp, stamp_ratio=stamp_ratio, step_ratio=self.step_ratio)
        doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
        ratio = doc.shape[1]/doc.shape[0]
        page = Image.fromarray(doc)
        page = page.resize((int(size*ratio), size))
        img = ImageTk.PhotoImage(page)
        if img:
            return img
        else:
            return None

    @staticmethod
    def add_stamp():
        pass

    @staticmethod
    def generate_qr(data):
        try:
            qr_raw_text = StampBot.get_invocie_text(data)
            qr_encoded_text = StampBot.encode(qr_raw_text)
        except:
            raise EncodingError
        try:
            qr_pil_img = qrcode.make(qr_encoded_text)
            gray_qr = np.uint8(np.array(qr_pil_img) * 255)
            qr = cv2.cvtColor(gray_qr, cv2.COLOR_GRAY2RGB)
        except:
            raise QRGenerationError
        return qr

    @staticmethod
    def get_invocie_text(invoice_dict):
        company_name = invoice_dict["company_name"]
        vat_number = invoice_dict["vat_number"].split(".")[0]
        vat_amount = StampBot.format_number(invoice_dict["vat_amount"])
        total = StampBot.format_number(invoice_dict["total_amount"])
        day, month, year = invoice_dict["date"].split("-")
        date = "{yyyy}-{mm}-{dd}".format(yyyy=year,
                                         mm=month, dd=day)
        time = "12:00:00.000"
        return b''.join([
            b'\x01',
            int.to_bytes(len(company_name), 1, 'big'),
            company_name.encode(),
            b'\x02',
            int.to_bytes(len(vat_number), 1, 'big'),
            vat_number.encode(),
            b'\x03',
            int.to_bytes(len(date+time+'TZ'), 1, 'big'),
            date.encode(),
            b'T',
            time.encode(),
            b'Z',
            b'\x05',
            int.to_bytes(len(vat_amount), 1, 'big'),
            vat_amount.encode(),
            b'\x04',
            int.to_bytes(len(total), 1, 'big'),
            total.encode(),
        ])

    @staticmethod
    def encode(message_bytes):
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        return base64_message

    def is_valid_invocie(self, document_abs_path):
        document_name = get_file_name(document_abs_path)
        if self.xlsx_pattern.match(document_name):
            return True
        return False

    def check_directory(self, dir_path):
        documents = list()
        if dir_path is None or len(dir_path) == 0:
            warn.CHOOSE_DIR.popup()
            return None
        try:
            for document in os.listdir(dir_path):
                document_abs_path = Path(dir_path) / document
                if self.is_valid_invocie(document_abs_path):
                    documents.append(document_abs_path)
        except FileNotFoundError as e:
            err.Error.popup(e)
            return None
        if len(documents) == 0:
            err.NO_FILES.popup()
            return None
        return documents

    @staticmethod
    def format_number(num_string):
        return "{:.2f}".format(float(num_string))
