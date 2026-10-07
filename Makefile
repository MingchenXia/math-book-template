PYTHON ?= python3
FLOW = $(PYTHON) scripts/bookflow.py
.PHONY: setup sync check test build review edit finish doctor watch
setup:
	bash scripts/setup.sh
sync:
	$(FLOW) sync
check:
	$(FLOW) sync --check
	$(FLOW) audit
test:
	$(PYTHON) -m unittest discover -s tests -v
build:
	$(FLOW) build
review:
	$(FLOW) agent review
edit:
	$(FLOW) agent edit
finish:
	$(FLOW) finish
doctor:
	bash scripts/doctor.sh
watch:
	$(PYTHON) scripts/watch.py
