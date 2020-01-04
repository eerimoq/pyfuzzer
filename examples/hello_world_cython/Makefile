all:
	python3 setup.py build_ext --inplace
	python3 -c "import hello_world ; hello_world.tell()"
	PYTHONPATH=../.. python3 -m pyfuzzer clean
	PYTHONPATH=../.. python3 -m pyfuzzer run -l max_total_time=1 hello_world.c
	PYTHONPATH=../.. python3 -m pyfuzzer print_coverage
