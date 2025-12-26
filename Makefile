# Define the Python interpreter to use
PYTHON ?= python3

# Define the location of the main script
MAIN_SCRIPT = HexViewer.py

# A phony target to prevent conflicts with potential files named "run"
.PHONY: run

# The 'run' target
run:
	@echo "Running $(MAIN_SCRIPT)..."
	$(PYTHON) $(MAIN_SCRIPT)
