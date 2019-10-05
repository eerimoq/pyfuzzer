test:
	cd examples/hello_world && \
	    PYTHONPATH=../.. \
	        python3 -m pyfuzzer hello_world hello_world.c
	cd examples/hello_world_custom_mutator && \
	    PYTHONPATH=.:../.. \
	        python3 -m pyfuzzer -m hello_world_mutator.py hello_world hello_world.c

release-to-pypi:
	python setup.py sdist
	twine upload dist/*
