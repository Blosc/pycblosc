init:
	pip install -r requirements.txt

test:
	pip install -r requirements-dev.txt
	py.test tests

.PHONY: init test
