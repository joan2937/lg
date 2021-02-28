PYTHON      ?= python3

ifeq ($(DESTDIR),)
  PYINSTALLARGS =
else
  PYINSTALLARGS = --root=$(DESTDIR)
endif

all: build-python

build-python:
	@$(PYTHON) setup.py build

install-python: build-python
	@$(PYTHON) setup.py -q install $(PYINSTALLARGS)

install: install-python
