import win32com.client as win32
excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(r"C:\Users\Yasmeen\Documents\in.xlsx")


#wb.ExportAsFixedFormat (0, r"C:\Users\Yasmeen\Documents\invoice.pdf", 0, True, False)

sheet_names = [sh.Name for sh in wb.Sheets]

ws = wb.Worksheets(sheet_names[0])

issuer = ws.Range("E3").Value
vat_num = ws.Range("E10").Value
vat_amount = ws.Range("I41").Value
total_amount = ws.Range("I24").Value
date = ws.Range("I16").Value



wb.ExportAsFixedFormat (0, r"C:\Users\Yasmeen\Documents\invoice.pdf", 0, True, False)
wb.Close()
excel.Application.Quit()
