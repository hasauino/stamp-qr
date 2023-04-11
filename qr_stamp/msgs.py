from enum import Enum
from tkinter import messagebox

MsgType = Enum('Type', 'info warning error')


def error(title="Error", body=""):
    messagebox.showerror(title, body)


def warn(title="Warning", body=""):
    messagebox.showwarning(title, body)


def info(title="Information", body=""):
    messagebox.showinfo(title, body)


def generate_report(skipped_documents, no_skipped, no_docs):
    report = ("Did not stamp all Invoices!\n"
              "Number of Invoices that were skipped: {}\n"
              "number of Invoices "
              "succeeded: {} \n\n").format(no_skipped, no_docs-no_skipped,)
    if len(skipped_documents["key_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["key_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Invoices that were skipped because "
                   "no associated data is found in the CSV"
                   " file:\n {} \n\n").format(text)
    if len(skipped_documents["encoding_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["encoding_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Invoices that were skipped because the given invoice"
                   " data is not correct (check invoice"
                   " data in the CSV file):\n {}").format(text)
    if len(skipped_documents["qr_generation_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["qr_generation_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Invoices that were skipped because of a failure"
                   " in generating the QR image stamp: \n {}").format(text)
    if len(skipped_documents["invoice_open_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["invoice_open_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Invoices that were skipped because of a failure"
                   " in opening them: \n {}").format(text)
    if len(skipped_documents["read_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["read_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Invoices that were skipped because of failure"
                   " in reading invoice file"
                   " (check file format):\n {}").format(text)
    return report
