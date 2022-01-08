.PHONY: all run clean pip shell help

all: run


run: venv
		export PYTHONPATH='.' &&\
		. venv/bin/activate &&\
		python qr_stamp/main.py


shell: venv
		export PYTHONPATH='.' &&\
		. venv/bin/activate &&\
		ipython		

venv: 
		pip3 install virtualenv
		python3 -m virtualenv venv
		. venv/bin/activate &&\
			pip install --upgrade pip &&\
			pip install -r dev-requirements.txt

pip: venv
		. venv/bin/activate &&\
			pip install --upgrade pip &&\
			pip install -r dev-requirements.txt

dist_linux: venv
		export PYTHONPATH='.' &&\
		. venv/bin/activate &&\
		pyinstaller --name StampQR --icon=qr_stamp/icon.ico qr_stamp/main.py --hidden-import='pkg_resources.py2_warn' --hidden-import='PIL._tkinter_finder'

clean:
	rm -rf venv/
	rm -rf build/
	rm -rf dist/
	rm *.spec

help:
	@echo "Available Targets:"
	@echo "... all"
	@echo "... run"
	@echo "... shell"
	@echo "... venv"
	@echo "... pip"
	@echo "... clean"

