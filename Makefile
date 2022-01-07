.PHONY: all run clean pip shell help

all: run

run: venv ar_graphql_image_publisher/gui/node_modules
		export PYTHONPATH='.' &&\
		. venv/bin/activate &&\
		python app.py -p 8000


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

icons: 
	inkscape -f docs/logo.svg -e docs/logo.png
	convert docs/logo.png -scale 48 docs/logo.ico


clean:
	rm -rf venv/
	rm -rf build/

help:
	@echo "Available Targets:"
	@echo "... all"
	@echo "... run"
	@echo "... shell"
	@echo "... venv"
	@echo "... pip"
	@echo "... clean"

