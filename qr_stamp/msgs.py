from enum import Enum
from tkinter import messagebox

MsgType = Enum('Type', 'info warning error')


class InfoMsg:
    def __init__(self, title="", body="") -> None:
        self.title = title
        self.body = body
        self.type = MsgType.info

    def popup(self, object_to_append=""):
        text = str(object_to_append)
        if self.type == MsgType.info:
            messagebox.showinfo(self.title, self.body+text)
        elif self.type == MsgType.warning:
            messagebox.showwarning(self.title, self.body+text)
        elif self.type == MsgType.error:
            messagebox.showerror(self.title, self.body+text)


class ErrorMsg(InfoMsg):
    def __init__(self, title="", body=""):
        InfoMsg.__init__(self, title, body)
        self.type = MsgType.error


class WarningMsg(InfoMsg):
    def __init__(self, title="", body=""):
        InfoMsg.__init__(self, title, body)
        self.type = MsgType.warning


class error_msgs:
    NO_FILES = ErrorMsg(title="Documents Error",
                        body="No files to stamp in chosen directory!")
    PREVIEW_FAIL = ErrorMsg(title="Preview Fail",
                            body="Could not preview image!")
    FILE_READ_FAIL = ErrorMsg(title="Documents Error",
                              body="Could not read document: ")
    MKDIR_FAIL = ErrorMsg(title="Output Directory Error",
                          body="Could not create output directory")                         
    CSV_NOT_FOUND = ErrorMsg(
        title="CSV Error", body="Could not find CSV file in chosen directory")
    CSV_OPEN = ErrorMsg(title="CSV Error", body="Could not open CSV file")
    CSV_FORMAT = ErrorMsg(title="CSV Error", body="Wrong format of CSV file")

    Error = ErrorMsg(title="Error")

    KEY_ERROR = ErrorMsg(
        title="No Data Error", body=("No data is found in the CSV file"
                                     " for this file: \n"))
    ENCODE_ERROR = ErrorMsg(title="Data Format Error",
                            body=("Data format in CSV is wrong for the"
                                  " following file: \n"))
    QR_ERROR = ErrorMsg(title="QR Generation Error",
                        body=("Could not generate QR stamp image for the"
                              " following file: \n"))


class warning_msgs:
    FAILED_FILES = WarningMsg(
        title="Skipped some documents", body="")
    CHOOSE_CSV = WarningMsg(
        title="Choose CSV", body=("Please choose an CSV file where"
                                  " the documents to be stamped are placed"
                                  " next to it in the same directory"))
    CHOOSE_DIR = WarningMsg(
        title="Choose Directory", body=("Please choose a directory"))                                  


class info_msgs:
    SUCCESS = InfoMsg(
        title="Done", body=("Successfully stampped all documents and placed"
                            " them inside \"out_docs/\" in the same"
                            " directory as the chosen CSV file."))


def generate_report(skipped_documents, no_skipped, no_docs):
    report = ("Did not stamp all documents!\n"
              "Number of documents that were skipped: {}\n"
              "number of documents "
              "succeeded: {} \n\n").format(no_skipped, no_docs-no_skipped,)
    if len(skipped_documents["key_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["key_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Documents that were skipped because "
                   "no associated data is found in the CSV"
                   " file:\n {} \n\n").format(text)
    if len(skipped_documents["encoding_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["encoding_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Documents that were skipped because the given invoice"
                   " data is not correct (check invoice"
                   " data in the CSV file):\n {}").format(text)
    if len(skipped_documents["qr_generation_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["qr_generation_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Documents that were skipped because of a failure"
                   " in generating the QR image stamp: \n {}").format(text)
    if len(skipped_documents["read_error"]) > 0:
        report += "===========\n"
        text = ""
        for doc in skipped_documents["read_error"]:
            text += "\"{}\"\n________\n".format(doc)
        report += ("Documents that were skipped because of failure"
                   " in reading the invoice file"
                   " (check file format):\n {}").format(text)
    return report
