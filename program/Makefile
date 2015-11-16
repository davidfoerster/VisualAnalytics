DEPS = widgetwin_ui.py window_ui.py

all: $(DEPS)

%_ui.py: %.ui
	pyuic4 -o "$@" "$<"

clean:
	rm -f -- $(DEPS)

.PHONY: all clean
