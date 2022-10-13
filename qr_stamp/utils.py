import tempfile
from pathlib import Path

import win32com.client as win32

from qr_stamp import config


def generate_pdf_and_read_data(document_path):
    doc_name = get_file_name(document_path, with_extension=False)
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    wb = excel.Workbooks.Open(str(document_path))
    sheet_name = [sh.Name for sh in wb.Sheets][0]
    ws = wb.Worksheets(sheet_name)
    issuer = ws.Range(config.parameters["issuer_cell"]).Value
    vat_num = ws.Range(config.parameters["vat_num_cell"]).Value
    vat_amount = ws.Range(config.parameters["vat_amount_cell"]).Value
    total_amount = ws.Range(config.parameters["total_amount_cell"]).Value
    date_raw = ws.Range(config.parameters["date_cell"]).Value 
    date = "{}-{}-{}".format(date_raw.day, date_raw.month, date_raw.year) 

    tmp_dir = tempfile.gettempdir()
    tmp_file_path = Path(tmp_dir) / "{}.pdf".format(doc_name)
    wb.ExportAsFixedFormat (0, str(tmp_file_path), 0, True, False)
    wb.Close()
    excel.Application.Quit()
    data = {
        "company_name":issuer,
        "vat_number": str(vat_num),
        "vat_amount": str(vat_amount),
        "total_amount": str(total_amount),
        "date": date
    }
    return tmp_file_path, data


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
