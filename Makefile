test:
	cd examples/hello_world && \
	    PYTHONPATH=../.. python3 -m pyfuzzer hello_world.c

release-to-pypi:
	python setup.py sdist
	twine upload dist/*
