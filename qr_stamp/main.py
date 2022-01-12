#!/usr/bin/python3

import os
import threading
import tkinter as tk
from sys import platform
from tkinter import ttk
from tkinter.filedialog import askdirectory

from ttkthemes import ThemedTk

from qr_stamp.stampper import StampBot


PREVIEW_ASPECT_RATIO = 1.4142
WIDTH = 560
HEGIHT = 215
BG_COLOR = '#fafafa'

def dir_chooser_event():
    text = path_field.get()
    selected = askdirectory()
    if not len(selected) == 0:
        path_field.delete(first=0, last=len(text))
        path_field.insert(0, selected)
        progress_bar["value"] = 0


def run():
    progress_bar["value"] = 0
    bot.stamp_ratio = float(scale.get())
    bot.dir_path = path_field.get()
    bot.print = pop_up
    t1 = threading.Thread(target=bot.stamp_all, args=[])
    t1.start()


def preview():
    width = root.winfo_screenwidth()*0.3
    height = width*PREVIEW_ASPECT_RATIO
    progress_bar["value"] = 0
    bot.stamp_ratio = float(scale.get())
    bot.csv_path = path_field.get()
    bot.print = pop_up
    img = bot.preview(size=int(height))
    if img is None:
        return
    preview_window = tk.Toplevel(root)
    preview_window.title("Preview")
    # sets the geometry of toplevel
    width = root.winfo_screenwidth()*0.3
    height = width*PREVIEW_ASPECT_RATIO
    if not height < root.winfo_screenheight():
        pass
    preview_window.geometry("{}x{}".format(int(width), int(height)))
    preview_window.configure(bg=BG_COLOR)
    panel = ttk.Label(preview_window, text="")
    panel.pack(side="bottom", fill="both", expand="yes")
    panel.configure(image=img)
    panel.image = img


def pop_up(text, parent=None):
    if parent is None:
        parent = root
    window = tk.Toplevel(parent)
    window.geometry("400x200")
    window.configure(bg=BG_COLOR)
    window.title("Message")
    label = ttk.Label(window, text=text)
    label.grid(column=0, row=0, pady=20, padx=20)
    run_btn = ttk.Button(window, text="OK", command=window.destroy, width=20)
    run_btn.grid(column=0, row=1, pady=20, padx=20)


if __name__ == '__main__':
    root = ThemedTk(theme="adapta")
    root.geometry('{}x{}'.format(WIDTH, HEGIHT))
    root.title("QR Stamp Tool")
    root.option_add('*Dialog.msg.font', 'Helvetica 11')
    root.configure(bg=BG_COLOR)
    if platform == "win32":
        dir_path = os.path.dirname(os.path.realpath(__file__))
        root.wm_iconbitmap(dir_path+'/icon.ico')
    left = ttk.Frame(root)
    left.grid(column=0, row=0)
    fileschooser_frame = ttk.Frame(left)
    fileschooser_frame.grid(column=0, row=0, padx=10)
    dir_chooser_frame = ttk.Frame(fileschooser_frame)
    dir_chooser_frame.grid(column=0, row=0, padx=10, pady=20)
    scale_frame = ttk.Frame(left)
    scale_frame.grid(column=0, row=1, padx=10, pady=10)
    buttons_frame = ttk.Frame(left)
    buttons_frame.grid(column=0, row=2, padx=10)
    # stamp details
    dir_label = ttk.Label(dir_chooser_frame, text="Choose invoices (Excel files) directory:")
    dir_label.grid(column=0, row=0)
    path_field = ttk.Entry(dir_chooser_frame, width=40)
    path_field.grid(column=0, row=1)
    dir_browse = ttk.Button(dir_chooser_frame, text="Browse",
                            command=dir_chooser_event)
    dir_browse.grid(column=1, row=1, padx=10)
    # scale
    scale_label = ttk.Label(scale_frame, text="scale stamp:")
    scale_label.grid(column=0, row=0)
    scale = ttk.Scale(scale_frame, from_=0.05, to=0.2, length=300)
    scale.set(0.15)
    scale.grid(column=1, row=0, padx=10)
    # run
    run_btn = ttk.Button(buttons_frame, text="Run",
                         command=run, width=20)
    run_btn.grid(column=0, row=0, padx=10, pady=10)
    # preview
    preview_btn = ttk.Button(buttons_frame, text="Preview",
                             command=preview, width=20)
    preview_btn.grid(column=1, row=0, padx=10, pady=10)
    # progress bar
    progress_bar = ttk.Progressbar(
        left, orient="horizontal", length=WIDTH, mode='determinate')
    progress_bar.grid(column=0, row=4, padx=0, pady=10)
    bot = StampBot(progress_bar=progress_bar)
    root.mainloop()
