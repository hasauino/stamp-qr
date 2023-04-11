#!/usr/bin/python3

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter.filedialog import askdirectory, askopenfilename

from ttkthemes import ThemedTk

from qr_stamp.stampper import StampBot

PREVIEW_ASPECT_RATIO = 1.4142
WIDTH = 560
HEGIHT = 310
BG_COLOR = '#fafafa'


class GUI:
    def __init__(self) -> None:
        dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.assets_dir = dir_path / "assets"

        # create tooy
        self.root = ThemedTk(theme="adapta")
        self.root.geometry('{}x{}'.format(WIDTH, HEGIHT))
        self.root.title("QR Stamp Tool")
        self.root.option_add('*Dialog.msg.font', 'Helvetica 11')
        self.root.configure(bg=BG_COLOR)
        self.root.wm_iconbitmap(str(self.assets_dir / 'icon.ico'))

        # create frames
        self.dir_chooser_frame = tk.ttk.Frame(self.root)
        self.dir_chooser_frame.grid(column=0, row=0, padx=10, pady=20)
        # config csv file chooser
        self.config_chooser_frame = tk.ttk.Frame(self.root)
        self.config_chooser_frame.grid(column=0, row=1, padx=10, pady=20)
        # scale
        scale_frame = tk.ttk.Frame(self.root)
        scale_frame.grid(column=0, row=2, padx=10, pady=10)
        # buttons
        self.buttons_frame = tk.ttk.Frame(self.root)
        self.buttons_frame.grid(column=0, row=3, padx=10)

        # populate frames
        self.excel_dir_chooser = PathChooser(frame=self.dir_chooser_frame,
                                             help_text="Choose invoices (Excel files) directory:", side_effect=self.reset_progress)
        # Config CSV file chooser
        self.config_chooser = PathChooser(frame=self.config_chooser_frame,
                                          help_text="Choose Configuration (CSV) file:", side_effect=self.reset_progress, is_directory=False)
        # stamp button
        self.stamp_btn = tk.ttk.Button(self.buttons_frame, text="Run",
                                       command=self.stamp, width=15)
        self.stamp_btn.grid(column=0, row=0, padx=10, pady=10)
        # Generate PDF button
        self.generate_pdf_btn = tk.ttk.Button(self.buttons_frame, text="Generate PDF",
                                              command=self.generate_pdf, width=20)
        self.generate_pdf_btn.grid(column=1, row=0, padx=10, pady=10)
        # scale
        self.scale_label = tk.ttk.Label(scale_frame, text="scale stamp:")
        self.scale_label.grid(column=0, row=0)
        self.scale = tk.ttk.Scale(
            scale_frame, from_=0.05, to=2.0, length=300, command=self.update_scale_value)
        self.scale.set(0.5)
        self.scale.grid(column=1, row=0, padx=10)
        self.scale_value = tk.ttk.Label(scale_frame)
        self.update_scale_value(self.scale.get())
        self.scale_value.grid(column=2, row=0)
        # Stop button
        stop_icon = tk.PhotoImage(file=str(self.assets_dir / "pause.png"))
        self.stop_btn = tk.ttk.Button(
            self.buttons_frame, image=stop_icon, command=self.stop)
        self.stop_btn.grid(column=2, row=0, padx=10, pady=10)
        # progress bar
        self.progress_bar = tk.ttk.Progressbar(
            self.root, orient="horizontal", length=WIDTH, mode='determinate')
        self.progress_bar.grid(column=0, row=4, padx=0, pady=10)

        self.bot = StampBot(gui=self)
        self.stop_pressed = False
        self.root.mainloop()

    def pop_up(self, text, parent=None):
        if parent is None:
            parent = self.root
        window = tk.Toplevel(parent)
        window.geometry("400x200")
        window.configure(bg=BG_COLOR)
        window.title("Message")
        label = tk.ttk.Label(window, text=text)
        label.grid(column=0, row=0, pady=20, padx=20)
        run_btn = tk.ttk.Button(
            window, text="OK", command=window.destroy, width=20)
        run_btn.grid(column=0, row=1, pady=20, padx=20)

    def stamp(self):
        self.reset_progress()
        t1 = threading.Thread(target=self.bot.stamp_all)
        t1.start()

    def generate_pdf(self):
        self.reset_progress()
        t1 = threading.Thread(target=self.bot.generate_pdf)
        t1.start()

    def stop(self):
        self.stop_pressed = True

    def stop_reset(self):
        self.stop_pressed = False

    def is_stopped(self):
        return self.stop_pressed

    def reset_progress(self):
        self.progress_bar["value"] = 0

    def update_scale_value(self, val):
        self.scale_value.config(text="{:.1f} x cell width".format(float(val)))


class PathChooser:
    def __init__(self, frame, help_text, side_effect, width=60, is_directory=True) -> None:
        self.frame = frame
        self.help_text = help_text
        self.width = width
        self.add_to_frame()
        self.side_effect = side_effect
        self.ask = askdirectory if is_directory else askopenfilename

    def add_to_frame(self):
        self.label = tk.ttk.Label(
            self.frame, text=self.help_text)
        self.label.grid(column=0, row=0)
        self.field = tk.ttk.Entry(self.frame, width=self.width)
        self.field.grid(column=0, row=1)
        self.browse = tk.ttk.Button(self.frame, text="Browse",
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
