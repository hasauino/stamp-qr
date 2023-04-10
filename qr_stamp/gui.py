#!/usr/bin/python3

import os
import threading
import tkinter as tk
from pathlib import Path
from sys import platform
from tkinter import ttk
from tkinter.filedialog import askdirectory

from ttkthemes import ThemedTk

from qr_stamp.stampper import StampBot

PREVIEW_ASPECT_RATIO = 1.4142
WIDTH = 560
HEGIHT = 310
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
        # scale bar
        self.scale_frame = ttk.Frame(self.main)
        self.scale_frame.grid(column=0, row=2, padx=10, pady=10)
        # buttons
        self.buttons_frame = ttk.Frame(self.main)
        self.buttons_frame.grid(column=0, row=3, padx=10)

    def populate_frames(self):
        # populat frames
        self.add_path_chooser(
            self.dir_chooser_frame, "Choose invoices (Excel files) directory:", self.dir_chooser_event)
        self.add_path_chooser(self.config_chooser_frame,
                              "Choose invoices (Excel files) directory:", self.dir_chooser_event)
        # scale
        self.scale_label = ttk.Label(self.scale_frame, text="scale stamp:")
        self.scale_label.grid(column=0, row=0)
        self.scale = ttk.Scale(
            self.scale_frame, from_=0.05, to=0.2, length=300)
        self.scale.set(0.15)
        self.scale.grid(column=1, row=0, padx=10)
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

    def add_path_chooser(self, frame, help_text, callback, width=40):
        self.dir_label = ttk.Label(
            frame, text=help_text)
        self.dir_label.grid(column=0, row=0)
        self.path_field = ttk.Entry(frame, width=width)
        self.path_field.grid(column=0, row=1)
        self.dir_browse = ttk.Button(frame, text="Browse",
                                     command=callback)
        self.dir_browse.grid(column=1, row=1, padx=10)

    def dir_chooser_event(self):
        text = self.path_field.get()
        selected = askdirectory()
        if not len(selected) == 0:
            self.path_field.delete(first=0, last=len(text))
            self.path_field.insert(0, Path(selected))
            self.progress_bar["value"] = 0

    def run(self):
        self.progress_bar["value"] = 0
        t1 = threading.Thread(target=self.bot.stamp_all, args=[
            self.path_field.get(), float(self.scale.get()),])
        t1.start()

    def preview(self):
        width = self.root.winfo_screenwidth()*0.3
        height = width*PREVIEW_ASPECT_RATIO
        self.progress_bar["value"] = 0
        img = self.bot.preview(size=int(height), dir_path=self.path_field.get(),
                               stamp_ratio=float(self.scale.get()))
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
