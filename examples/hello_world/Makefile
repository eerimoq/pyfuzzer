CFLAGS = \
	-fprofile-instr-generate \
	-fcoverage-mapping \
	-I/usr/include/python3.7m \
	-g \
	-fsanitize=fuzzer \
	-fsanitize=signed-integer-overflow \
	-fno-sanitize-recover=all

all: hello_world.c
	clang \
	    $(CFLAGS) \
	    hello_world.c \
	    ../../pyfuzzer.c \
	    -lpython3.7m \
	    -o hello_world_fuzzer
	rm -f hello_world_fuzzer.profraw
	PYTHONPATH=. \
	LLVM_PROFILE_FILE=hello_world_fuzzer.profraw \
	    ./hello_world_fuzzer \
	        -max_total_time=5 \
	        -max_len=1024
	llvm-profdata merge \
	    -sparse hello_world_fuzzer.profraw \
	    -o hello_world_fuzzer.profdata
	llvm-cov show ./hello_world_fuzzer \
	    -instr-profile=hello_world_fuzzer.profdata

hello_world.c: hello_world.py
	python3 -m cython -3 hello_world.py
