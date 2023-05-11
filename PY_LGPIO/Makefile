SWIG         = swig
PYTHON      ?= python3

ifeq ($(DESTDIR),)
  PYBUILDARGS =
  PYINSTALLARGS =
else
  PYBUILDARGS = --include-dirs=$(DESTDIR)$(includedir) --library-dirs=$(DESTDIR)$(libdir)
  PYINSTALLARGS = --root=$(DESTDIR)
endif

all: build-python

build-python: lgpio.i
	@if type -p $(SWIG) >&/dev/null; then \
		$(SWIG) -python lgpio.i && \
		$(PYTHON) setup.py build_ext $(PYBUILDARGS); \
	else \
		echo "*** need swig package to install lgpio.py ***"; \
	fi

lgpio_wrap.c: build-python

install-python:
	@if type -p $(SWIG) >&/dev/null; then \
		$(PYTHON) setup.py -q install $(PYINSTALLARGS); \
	fi

install: install-python

clean:
	rm -f lgpio_wrap.c
