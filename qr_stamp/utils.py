import win32com.client as win32
import tempfile
import os


def generate_pdf_and_read_data(document_path):
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    wb = excel.Workbooks.Open(document_path)
    sheet_name = [sh.Name for sh in wb.Sheets][0]
    ws = wb.Worksheets(sheet_name)
    issuer = ws.Range("E3").Value
    vat_num = ws.Range("E10").Value
    vat_amount = ws.Range("I41").Value
    total_amount = ws.Range("I24").Value
    date_raw = ws.Range("I16").Value 
    date = "{}-{}-{}".format(date_raw.day, date_raw.month, date_raw.year) 

    tmp_dir = tempfile.gettempdir()
    tmp_file_path = os.path.join(tmp_dir, "invoice_tmp_pdf.pdf")
    wb.ExportAsFixedFormat (0, tmp_file_path, 0, True, False)
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