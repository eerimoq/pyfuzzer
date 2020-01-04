all:
	python3 setup.py build_ext --inplace
	python3 -c "import hello_world ; print('tell(\'Hi!\') =', hello_world.tell('Hi!'))"
	PYTHONPATH=../.. python3 -m pyfuzzer clean
	PYTHONPATH=../.. python3 -m pyfuzzer run -l max_total_time=1 hello_world.c
	PYTHONPATH=../.. python3 -m pyfuzzer print_coverage
	PYTHONPATH=../.. python3 -m pyfuzzer print_corpus
