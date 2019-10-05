CFLAGS = \
	-fprofile-instr-generate \
	-fcoverage-mapping \
	-I/usr/include/python3.5m \
	-g \
	-fsanitize=fuzzer \
	-fsanitize=signed-integer-overflow \
	-fno-sanitize-recover=all

all: lib
	clang \
	    $(CFLAGS) \
	    ../../pyfuzzer.c \
	    -lpython3.5m \
	    -o hello_world_fuzzer
	$(MAKE) run

run:
	rm -f hello_world_fuzzer.profraw
	PYTHONPATH=. \
	LLVM_PROFILE_FILE=hello_world_fuzzer.profraw \
	    ./hello_world_fuzzer \
	        -max_total_time=5 \
	        -max_len=1024
	llvm-profdata-6.0 merge \
	    -sparse hello_world_fuzzer.profraw \
	    -o hello_world_fuzzer.profdata
	llvm-cov-6.0 show ./hello_world_fuzzer \
	    -instr-profile=hello_world_fuzzer.profdata

lib:
	rm -rf *.so build
	CC=clang-6.0 \
	CFLAGS="--coverage -g -fsanitize=signed-integer-overflow" \
	python3 setup.py build_ext --inplace

hello_world.c: hello_world.py
	python3 -m cython -3 hello_world.py
