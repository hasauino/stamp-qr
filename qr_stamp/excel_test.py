import win32com.client as win32
excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(r"C:\Users\Yasmeen\Documents\in.xls")


sheet_name = [sh.Name for sh in wb.Sheets][0]
ws = wb.Worksheets(sheet_name)

cell = ws.Range('E47')
picture = ws.Pictures().Insert(r"C:\Users\Yasmeen\Documents\stamp.png")
cell_width = cell.Width
aspect = picture.Width / picture.Height
picture_width = cell_width / 2
picture_height = int(picture_width/aspect)
picture.Width = picture_width
picture.Height = picture_height

picture.Left = cell.Left + (cell_width - picture_width) / 2
picture.Top = cell.Top

wb.Save()
wb.Close()
excel.Application.Quit()
