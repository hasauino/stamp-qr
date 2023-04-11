import os
import re
from pathlib import Path

import win32com.client as win32

from qr_stamp.exceptions import EncodingError, QRGenerationError, OpenInvoiceError
from qr_stamp.invoice import Invoice, get_invoices_data
from qr_stamp.msgs import error, generate_report, info, warn
from qr_stamp.utils import get_file_name, generate_pdf


class StampBot:
    def __init__(self, gui, step_ratio=0.1):
        self.gui = gui
        self.step_ratio = step_ratio
        xlsx_re = r'[\w\d]+.*\.xlsx?'
        self.xlsx_pattern = re.compile(xlsx_re, re.I)
        self.print = self.gui.pop_up

    def stamp_all(self):
        self.gui.stop_reset()
        dir_path = self.gui.excel_dir_chooser.get()
        config_path = self.gui.config_chooser.get()
        succeeded = 0
        skipped_documents = {
            "key_error": [],
            "encoding_error": [],
            "qr_generation_error": [],
            "read_error": [],
            "invoice_open_error": []
        }
        self.gui.progress_bar['value'] = 5
        documents = self.check_directory(dir_path)
        invoices_data = get_invoices_data(config_path)
        if documents is None:
            return None
        if invoices_data is None:
            return None
        try:
            excel = win32.gencache.EnsureDispatch('Excel.Application')
        except Exception:
            error("Excel Application Error",
                  ("Could not open Excel application. "
                   "Possible reasons:\n"
                   "- Excel is not installed on your machine\n"
                   "- Excel is already running. Please close all excel workbooks before running the stamper"))

        for i, excel_document_path in enumerate(documents):
            if self.gui.is_stopped():
                break
            document_name = get_file_name(
                excel_document_path, with_extension=False)
            try:
                invoice = Invoice(invoices_data[document_name])
            except KeyError:
                skipped_documents["key_error"].append(
                    excel_document_path)
                continue
            except EncodingError:
                skipped_documents["encoding_error"].append(excel_document_path)
                continue
            try:
                invoice.insert_to_excel_file(excel, excel_document_path, self.gui.scale.get())
            except QRGenerationError:
                skipped_documents["qr_generation_error"].append(
                    excel_document_path)
                continue
            except OpenInvoiceError:
                skipped_documents["invoice_open_error"].append(
                    excel_document_path)
                continue
            self.gui.progress_bar['value'] = (i+1.0)/len(documents)*100.0
            succeeded += 1
        skipped_total = len(documents) - succeeded
        if skipped_total == 0:
            info(title="Done", body=("Successfully stamped all Excel files in place"))
            return
        report = generate_report(
            skipped_documents, skipped_total, len(documents))
        warn(title="Skipped Some Documents", body=report)

    def generate_pdf(self):
        self.gui.stop_reset()
        dir_path = self.gui.excel_dir_chooser.get()
        succeeded = 0
        skipped_documents = []
        self.gui.progress_bar['value'] = 5
        documents = self.check_directory(dir_path)
        if documents is None:
            return None
        try:
            excel = win32.gencache.EnsureDispatch('Excel.Application')
        except Exception:
            error("Excel Application Error",
                  ("Could not open Excel application. "
                   "Possible reasons:\n"
                   "- Excel is not installed on your machine\n"
                   "- Excel is already running. Please close all excel workbooks before running the stamper"))
        out_dir = Path(documents[0]).parent / "out"
        if not out_dir.exists():
            try:
                os.mkdir(out_dir)
            except:
                error(title="Output Directory Error",
                      body="Could not create output directory")
                return None
        for i, excel_document_path in enumerate(documents):
            if self.gui.is_stopped():
                break
            try:
                generate_pdf(excel, excel_document_path, out_dir)
            except:
                skipped_documents.append(excel_document_path)
                continue

            self.gui.progress_bar['value'] = (i+1.0)/len(documents)*100.0
            succeeded += 1
        skipped_total = len(documents) - succeeded
        if skipped_total == 0:
            info(title="Done", body=(
                f"Successfully generated all PDF files to:\n {Path(excel_document_path).parent}"))
            return
        failed_list = "\n".join([path.name for path in skipped_documents])
        report = f"Failed to export {skipped_total}/{len(documents)} of Excel files to PDF. Files that failed:\n{failed_list}"

        warn(title="Skipped Some Documents", body=report)

    def is_valid_invoice(self, document_abs_path):
        document_name = get_file_name(document_abs_path)
        if self.xlsx_pattern.match(document_name):
            return True
        return False

    def check_directory(self, dir_path):
        documents = list()
        if dir_path is None or len(dir_path) == 0:
            warn(title="Choose Directory", body="Please choose a directory")
            return None
        try:
            for document in os.listdir(dir_path):
                document_abs_path = Path(dir_path) / document
                if self.is_valid_invoice(document_abs_path):
                    documents.append(document_abs_path)
        except FileNotFoundError as e:
            error(title="File Not Found",
                  body=f"File {document} was not found in {document_abs_path}")
            return None
        if len(documents) == 0:
            error(title="Documents Error",
                        body="No files to stamp in chosen directory!")
            return None
        return documents

    @ staticmethod
    def format_number(num_string):
        return "{:.2f}".format(float(num_string))
