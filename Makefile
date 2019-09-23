checkfiles = tortoise/ examples/ tests/ setup.py conftest.py
black_opts = -l 100 -t py36
py_warn = PYTHONWARNINGS=default PYTHONASYNCIODEBUG=1 PYTHONDEBUG=x PYTHONDEVMODE=dev

help:
	@echo  "Tortoise ORM development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    up          Updates dev/test dependencies"
	@echo  "    deps        Ensure dev/test dependencies are installed"
	@echo  "    check	Checks that build is sane"
	@echo  "    lint	Reports all linter violations"
	@echo  "    test	Runs all tests"
	@echo  "    docs 	Builds the documentation"
	@echo  "    style       Auto-formats the code"

up:
	cd tests && CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements-pypy.txt requirements-pypy.in -U
	cd tests && CUSTOM_COMPILE_COMMAND="make up" pip-compile -o requirements.txt requirements.in -U
	cat tests/extra_requirements.txt >> tests/requirements-pypy.txt
	cat tests/extra_requirements.txt >> tests/requirements.txt
	sed -i "s/^-e .*/-e ./" tests/requirements.txt

deps:
	@which pip-sync || pip install -q pip-tools
	@pip-sync tests/requirements.txt

check: deps
ifneq ($(shell which black),)
	black --check $(black_opts) $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
endif
	flake8 $(checkfiles)
	mypy $(checkfiles)
	pylint -E $(checkfiles)
	bandit -r $(checkfiles)
	python setup.py check -mrs

lint: deps
ifneq ($(shell which black),)
	black --check $(black_opts) $(checkfiles) || (echo "Please run 'make style' to auto-fix style issues" && false)
endif
	flake8 $(checkfiles)
	mypy $(checkfiles)
	pylint $(checkfiles)
	bandit -r $(checkfiles)
	python setup.py check -mrs

test: deps
	-$(py_warn) TORTOISE_TEST_DB=sqlite://:memory: py.test -q

_testall:
	-$(py_warn) TORTOISE_TEST_DB=sqlite://:memory: py.test -q --cov-report=
	-python -V | grep PyPy || $(py_warn) TORTOISE_TEST_DB=postgres://postgres:@127.0.0.1:5432/test_\{\} py.test -q --cov-append --cov-report=
	-$(py_warn) TORTOISE_TEST_DB="mysql://root:@127.0.0.1:3306/test_\{\}" py.test -q --cov-append

testall: deps _testall

ci: check testall

docs: deps
	python setup.py build_sphinx -E

style: deps
	isort -rc $(checkfiles)
	black $(black_opts) $(checkfiles)

publish: deps
	rm -fR dist/
	python setup.py sdist
	twine upload dist/*
