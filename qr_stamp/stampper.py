from tkinter.constants import N
import cv2
import numpy as np
import os
import csv
import base64
import qrcode
from pdf2image import convert_from_path
from os import listdir
from PIL import Image, ImageTk
from os import mkdir, path
import re
from qr_stamp.msgs import error_msgs as err
from random import randint
from qr_stamp.msgs import warning_msgs as warn
from qr_stamp.msgs import info_msgs as info


class StampBot:
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar
        self.stamp_ratio = 0.2
        self.step_ratio = 0.1
        self.preview_size = 600
        self.stamp_path = None
        self.stamp = None
        self.ready = False
        pdf_re = r'.*\.pdf'
        img_re = r'.*\.(bmp|dib|jpeg|jpg|jpe|jp2|png|webp|pbm|pgm|ppm|pxm|pnm|pfm|sr|ras|tiff|tif|exr|hdr|pic)'
        self.pdf_pattern = re.compile(pdf_re, re.I)
        self.img_pattern = re.compile(img_re, re.I)
        self.invoice_pattern = re.compile("MENA\d+")
        self.file_pattern = re.compile("(%s|%s)" % (pdf_re, img_re))
        self.dir_path = None
        self._csv_path = None
        self.csv_file_name = None

    @property
    def csv_path(self):
        return self._csv_path

    @csv_path.setter
    def csv_path(self, path):
        self._csv_path = path
        self.csv_file_name = self._csv_path.split("/")[-1]
        self.dir_path = self._csv_path[:-len(self.csv_file_name)]

    @staticmethod
    def add_stamp(doc, stamp, stamp_ratio=0.2, step_ratio=0.1):
        doc_rows, doc_col, _ = doc.shape
        stamp_rows, stamp_cols, _ = stamp.shape
        k = stamp_rows/stamp_cols
        r = np.sqrt((doc_rows)**2 + (doc_col)**2)*stamp_ratio
        new_col = np.sqrt(r**2 / (k**2 + 1))
        new_row = k*new_col
        new_size = (int(new_col), int(new_row))
        stamp = cv2.resize(stamp, new_size, cv2.INTER_AREA)
        stamp_rows, stamp_cols, _ = stamp.shape
        gray = cv2.cvtColor(stamp, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)
        graydoc = cv2.cvtColor(doc, cv2.COLOR_BGR2GRAY)
        step_check = int(step_ratio*doc_col)
        centers = []
        white_values = []
        center = [doc_rows, doc_col]
        while (center[1] > int(doc_col*0.5)):
            while (center[0] > int(doc_rows*0.5)):
                centers.append(np.copy(center))
                white_values.append(graydoc[center[0]-int(stamp_rows*2):center[0],
                                            center[1]-int(stamp_rows*2):center[1]].mean())
                center[0] -= step_check
            center[1] -= step_check
            center[0] = doc_rows
        centers = centers[::-1]
        white_values = white_values[::-1]
        location = centers[np.argmax(white_values)]
        pos_x = location[0] - stamp_rows
        pos_y = location[1] - stamp_cols
        roi = doc[pos_x:pos_x+stamp_rows, pos_y:pos_y+stamp_cols]
        mask_inv = cv2.bitwise_not(mask)
        anded = cv2.bitwise_and(roi, roi, mask=mask_inv)
        stamp = cv2.bitwise_and(stamp, stamp, mask=mask)
        dst = cv2.add(anded, stamp)
        doc[pos_x:pos_x+stamp_rows, pos_y:pos_y+stamp_cols] = dst
        return doc

    @staticmethod
    def format_number(num_string):
        return "{:,.2f}".format(float(num_string))

    @staticmethod
    def get_invocie_text(invoice_dict):
        company_name = invoice_dict["company_name"]
        vat_number = invoice_dict["vat_number"]
        vat_amount = "{:.2f}".format(float(invoice_dict["vat_amount"]))
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

    def generate_qr(self, document_name, data):
        indx_start, indx_end = self.invoice_pattern.match(
            document_name).span()
        document_key = document_name[indx_start:indx_end]
        qr_raw_text = self.get_invocie_text(data[document_key])
        qr_encoded_text = self.encode(qr_raw_text)
        qr_pil_img = qrcode.make(qr_encoded_text)
        gray_qr = np.uint8(np.array(qr_pil_img) * 255)
        qr = cv2.cvtColor(gray_qr, cv2.COLOR_GRAY2RGB)
        return qr

    def stamp_all(self):
        self.progress_bar['value'] = 5
        documents, data = self._check_directory()
        if data is None or documents is None:
            return None
        out_dir = self.dir_path + "out_docs"
        if not path.exists(out_dir):
            try:
                mkdir(out_dir)
            except:
                err.MKDIR_FAIL.popup()
                return None

        failed_documents = []
        for i, document in enumerate(documents):
            document_name = document.split("/")[-1]
            qr_stamp = self.generate_qr(document_name, data)
            # if document is a PDF file (could have multiple pages)
            if self.pdf_pattern.match(document_name):
                try:
                    pages = convert_from_path(document, dpi=400)
                except Image.DecompressionBombError:
                    pages = convert_from_path(document)
                except:
                    failed_documents.append(document_name)
                    continue
                # stamp only first page
                doc = np.array(pages[0])
                doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
                doc = self.add_stamp(doc, qr_stamp,
                                     stamp_ratio=self.stamp_ratio)
                doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
                stamped_page = Image.fromarray(doc)
                stamped_page.save(out_dir+"/"+document_name[:-4]+".pdf",
                                  save_all=True,
                                  append_images=pages[1:])
            else:
                doc = cv2.imread(document)
                if doc is None:
                    failed_documents.append(document_name)
                    continue
                doc = self.add_stamp(
                    doc, qr_stamp, stamp_ratio=self.stamp_ratio)
                cv2.imwrite(out_dir+"/"+document_name, doc)

            self.progress_bar['value'] = (i+1.0)/len(documents)*100.0
        if len(failed_documents) > 0:
            failed_docs_text = ("number of documents failed: {}\n.""numbe of documents succeeded: {}. \n\n").format(
                len(failed_documents), len(documents)-len(failed_documents))
            for doc in failed_documents:
                failed_docs_text = "".join(
                    [failed_docs_text, "\"{}\"".format(doc)+"\n________\n"])
            warn.FAILED_FILES.popup(failed_docs_text)
        else:
            info.SUCCESS.popup()

    def preview(self, size):
        documents, data = self._check_directory()
        if data is None or documents is None:
            return None
        rand_index = randint(0, len(documents)-1)
        document = documents[rand_index]
        document_name = document.split("/")[-1]
        qr_stamp = self.generate_qr(document_name, data)
        if self.pdf_pattern.match(document_name):
            try:
                page = convert_from_path(document, dpi=400)[0]
            except Image.DecompressionBombError:
                page = convert_from_path(document)[0]
            except:
                err.FILE_READ_FAIL.popup(document_name)
                return None
            doc = np.array(page)
            doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
        else:
            doc = cv2.imread(document)
            if doc is None:
                err.FILE_READ_FAIL.popup(document_name)
                return None

        ratio = doc.shape[1]/doc.shape[0]
        doc = self.add_stamp(
            doc, qr_stamp, stamp_ratio=self.stamp_ratio)
        doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
        page = Image.fromarray(doc)
        page = page.resize((int(size*ratio), size))
        img = ImageTk.PhotoImage(page)
        if img:
            return img
        else:
            return None

    def is_valid_invocie(self, document_abs_path):
        document_name = document_abs_path.split("/")[-1]
        if self.file_pattern.match(document_name) and self.invoice_pattern.match(document_name):
            return True
        return False

    def _check_directory(self):
        documents = list()
        if self.dir_path is None or len(self.dir_path) == 0:
            warn.CHOOSE_CSV.popup()
            return None, None
        try:
            for document in os.listdir(self.dir_path):
                document_abs_path = os.path.join(self.dir_path, document)
                if self.is_valid_invocie(document_abs_path):
                    documents.append(document_abs_path)
        except FileNotFoundError as e:
            err.Error.popup(e)
            return None, None
        if len(documents) == 0:
            err.NO_FILES.popup()
            return None, None

        if not path.exists(self.csv_path):
            err.CSV_NOT_FOUND.popup()
            return None, None

        data = dict()
        try:
            with open(self.csv_path, newline='') as csvfile:
                file_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in file_reader:
                    if self.invoice_pattern.match(row[-1]) is not None:
                        data[row[-1]] = {"company_name": row[0],
                                         "vat_number": row[1],
                                         "date": row[2],
                                         "total_amount": row[3],
                                         "vat_amount": row[4]
                                         }
        # TODO: print warning if length of row is < documents

        except FileNotFoundError:
            err.CSV_OPEN.popup()
            return None, None

        except IndexError:
            err.CSV_FORMAT.popup()
            return None, None

        except Exception as e:
            err.Error.popup(e)
            return None, None

        return documents, data
