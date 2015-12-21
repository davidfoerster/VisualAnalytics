PYUIC = python3 -m PyQt4.uic.pyuic


DEPS = widgetwin_ui.py window_ui.py histogram_ui.py

all: $(DEPS)

%_ui.py: %.ui
	$(PYUIC) -o "$@" "$<"

clean:
	rm -f -- $(DEPS)

.PHONY: all clean
