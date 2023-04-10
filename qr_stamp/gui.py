#!/usr/bin/python3

import os
import threading
import tkinter as tk
from pathlib import Path
from sys import platform
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

from ttkthemes import ThemedTk

from qr_stamp.stampper import StampBot

PREVIEW_ASPECT_RATIO = 1.4142
WIDTH = 560
HEGIHT = 270
BG_COLOR = '#fafafa'


class GUI:
    def __init__(self) -> None:
        self.create_root()
        self.create_frames()
        self.populate_frames()
        self.bot = StampBot(gui=self)

    def spin(self):
        self.root.mainloop()

    def create_root(self):
        self.root = ThemedTk(theme="adapta")
        self.root.geometry('{}x{}'.format(WIDTH, HEGIHT))
        self.root.title("QR Stamp Tool")
        self.root.option_add('*Dialog.msg.font', 'Helvetica 11')
        self.root.configure(bg=BG_COLOR)
        if platform == "win32":
            dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
            self.root.wm_iconbitmap(str(dir_path / 'icon.ico'))
        self.main = ttk.Frame(self.root)
        self.main.grid(column=0, row=0)

    def create_frames(self):
        # Dir chooser
        self.dir_chooser_frame = ttk.Frame(self.main)
        self.dir_chooser_frame.grid(column=0, row=0, padx=10, pady=20)
        # config csv file chooser
        self.config_chooser_frame = ttk.Frame(self.main)
        self.config_chooser_frame.grid(column=0, row=1, padx=10, pady=20)
        # buttons
        self.buttons_frame = ttk.Frame(self.main)
        self.buttons_frame.grid(column=0, row=2, padx=10)

    def populate_frames(self):
        # Excel Dir chooser
        self.excel_dir_chooser = PathChooser(frame=self.dir_chooser_frame,
                                             help_text="Choose invoices (Excel files) directory:", side_effect=self.reset_progress)
        # Config CSV file chooser
        self.config_chooser = PathChooser(frame=self.config_chooser_frame,
                                          help_text="Choose Configuration (CSV) file:", side_effect=self.reset_progress, is_directory=False)
        # run
        self.run_btn = ttk.Button(self.buttons_frame, text="Run",
                                  command=self.run, width=20)
        self.run_btn.grid(column=0, row=0, padx=10, pady=10)
        # preview
        self.preview_btn = ttk.Button(self.buttons_frame, text="Preview",
                                      command=self.preview, width=20)
        self.preview_btn.grid(column=1, row=0, padx=10, pady=10)
        # progress bar
        self.progress_bar = ttk.Progressbar(
            self.main, orient="horizontal", length=WIDTH, mode='determinate')
        self.progress_bar.grid(column=0, row=4, padx=0, pady=10)

    def pop_up(self, text, parent=None):
        if parent is None:
            parent = self.root
        window = tk.Toplevel(parent)
        window.geometry("400x200")
        window.configure(bg=BG_COLOR)
        window.title("Message")
        label = ttk.Label(window, text=text)
        label.grid(column=0, row=0, pady=20, padx=20)
        run_btn = ttk.Button(
            window, text="OK", command=window.destroy, width=20)
        run_btn.grid(column=0, row=1, pady=20, padx=20)

    def run(self):
        self.reset_progress()
        t1 = threading.Thread(target=self.bot.stamp_all)
        t1.start()

    def preview(self):
        width = self.root.winfo_screenwidth()*0.3
        height = width*PREVIEW_ASPECT_RATIO
        self.reset_progress()
        img = self.bot.preview(
            size=int(height), dir_path=self.path_field.get())
        if img is None:
            return
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview")
        # sets the geometry of toplevel
        width = self.root.winfo_screenwidth()*0.3
        height = width*PREVIEW_ASPECT_RATIO
        if not height < self.root.winfo_screenheight():
            pass
        preview_window.geometry("{}x{}".format(int(width), int(height)))
        preview_window.configure(bg=BG_COLOR)
        panel = ttk.Label(preview_window, text="")
        panel.pack(side="bottom", fill="both", expand="yes")
        panel.configure(image=img)
        panel.image = img

    def reset_progress(self):
        self.progress_bar["value"] = 0


class PathChooser:
    def __init__(self, frame, help_text, side_effect, width=40, is_directory=True) -> None:
        self.frame = frame
        self.help_text = help_text
        self.width = width
        self.add_to_frame()
        self.side_effect = side_effect
        self.ask = askdirectory if is_directory else askopenfilename

    def add_to_frame(self):
        self.label = ttk.Label(
            self.frame, text=self.help_text)
        self.label.grid(column=0, row=0)
        self.field = ttk.Entry(self.frame, width=self.width)
        self.field.grid(column=0, row=1)
        self.browse = ttk.Button(self.frame, text="Browse",
                                 command=self.callback)
        self.browse.grid(column=1, row=1, padx=10)

    def callback(self):
        text = self.field.get()
        selected = self.ask()
        if len(selected) > 0:
            self.field.delete(first=0, last=len(text))
            self.field.insert(0, Path(selected))
            self.side_effect()

    def get(self):
        return self.field.get()
