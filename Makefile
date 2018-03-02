init:
	pip install -r requirements.txt

test:
	pip install -r requirements-dev.txt
	tox

.PHONY: init test
