import os
import re
from os import mkdir
from pathlib import Path
from random import randint

import cv2
import numpy as np
import win32com.client as win32
from pdf2image import convert_from_path
from PIL import Image, ImageTk

from exceptions import EncodingError, QRGenerationError
from invoice import Invoice, get_invoices_data
from qr_stamp.msgs import ErrorMsg, WarningMsg
from qr_stamp.msgs import error_msgs as err
from qr_stamp.msgs import generate_report
from qr_stamp.msgs import info_msgs as info
from qr_stamp.msgs import warning_msgs as warn
from qr_stamp.utils import generate_pdf_and_read_data, get_file_name


class StampBot:
    def __init__(self, gui, step_ratio=0.1):
        self.gui = gui
        self.step_ratio = step_ratio
        xlsx_re = r'[\w\d]+.*\.xlsx?'
        self.xlsx_pattern = re.compile(xlsx_re, re.I)
        self.print = self.gui.pop_up

    def stamp_all(self):
        dir_path = self.gui.excel_dir_chooser.get()
        config_path = self.gui.config_chooser.get()
        skipped_total = 0
        skipped_documents = {
            "key_error": [],
            "encoding_error": [],
            "qr_generation_error": [],
            "read_error": [],
        }
        self.gui.progress_bar['value'] = 5
        documents = self.check_directory(dir_path)
        invoices_data = get_invoices_data(config_path)
        if documents is None:
            return None
        if invoices_data is None:
            return None
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        for i, excel_document_path in enumerate(documents):
            document_name = get_file_name(
                excel_document_path, with_extension=False)
            try:
                invoice = Invoice(invoices_data[document_name])
                invoice.insert_to_excel_file(excel, excel_document_path)
            except EncodingError:
                skipped_documents["encoding_error"].append(excel_document_path)
                skipped_total += 1
                continue
            except QRGenerationError:
                skipped_documents["qr_generation_error"].append(
                    excel_document_path)
                skipped_total += 1
                continue
            self.gui.progress_bar['value'] = (i+1.0)/len(documents)*100.0

    def preview(self, dir_path, size):
        return
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

    def is_valid_invoice(self, document_abs_path):
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
                if self.is_valid_invoice(document_abs_path):
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
