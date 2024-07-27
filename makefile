install:
	pip install -e .

build:
	python -m build

upload:
	python -m twine upload --repository testpypi dist/*

clean:
	rm -rf dist

install-from-testpypi:
	python3 -m pip install --index-url https://test.pypi.org/simple/ bandamon