About
=====

Fuzzy-test the ``hello_world`` module which will cause a fatal error.

.. code-block:: text

   $ pyfuzzer run hello_world hello_world.c
   clang -fprofile-instr-generate -fcoverage-mapping -g -fsanitize=fuzzer -fsanitize=signed-integer-overflow -fno-sanitize-recover=all -I/usr/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer.c -Wl,-Bsymbolic-functions -Wl,-z,relro -lpython3.7m -o pyfuzzer
   clang -I/usr/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer_print_corpus.c -Wl,-Bsymbolic-functions -Wl,-z,relro -lpython3.7m -o pyfuzzer_print_corpus
   rm -f pyfuzzer.profraw
   ./pyfuzzer corpus
   INFO: Seed: 71862278
   INFO: Loaded 1 modules   (23 inline 8-bit counters): 23 [0x47444d, 0x474464),
   INFO: Loaded 1 PC tables (23 PCs): 23 [0x461770,0x4618e0),
   INFO:        0 files found in corpus
   Importing module under test... done.
   Importing custom mutator... failed.
   ModuleNotFoundError: No module named 'mutator'
   Importing mutator 'pyfuzzer.mutators.random'... done.
   Finding function 'test_one_input' in mutator... done.
   INFO: A corpus is not provided, starting from an empty corpus
   #2	INITED cov: 4 ft: 5 corp: 1/1b lim: 4 exec/s: 0 rss: 44Mb
        NEW_FUNC[1/1]: 0x450c80 in m_tell /home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/hello_world.c:10
   #774	NEW    cov: 6 ft: 8 corp: 2/12b lim: 11 exec/s: 0 rss: 46Mb L: 11/11 MS: 2 CMP-CopyPart- DE: "\x01\x00\x00\x00\x00\x00\x00\x00"-
   #785	REDUCE cov: 6 ft: 8 corp: 2/11b lim: 11 exec/s: 0 rss: 46Mb L: 10/10 MS: 1 EraseBytes-
   #817	REDUCE cov: 6 ft: 8 corp: 2/7b lim: 11 exec/s: 0 rss: 46Mb L: 6/6 MS: 2 ShuffleBytes-EraseBytes-
   #848	REDUCE cov: 6 ft: 8 corp: 2/5b lim: 11 exec/s: 0 rss: 46Mb L: 4/4 MS: 1 EraseBytes-
   #1219	REDUCE cov: 10 ft: 12 corp: 3/9b lim: 14 exec/s: 0 rss: 46Mb L: 4/4 MS: 1 ChangeBit-
   #1265	NEW    cov: 11 ft: 13 corp: 4/17b lim: 14 exec/s: 0 rss: 46Mb L: 8/8 MS: 1 CopyPart-
   #1402	NEW    cov: 12 ft: 14 corp: 5/23b lim: 14 exec/s: 0 rss: 46Mb L: 6/8 MS: 2 ShuffleBytes-CopyPart-
   #1428	NEW    cov: 13 ft: 15 corp: 6/29b lim: 14 exec/s: 0 rss: 46Mb L: 6/8 MS: 1 ShuffleBytes-
   #1834	REDUCE cov: 13 ft: 15 corp: 6/28b lim: 17 exec/s: 0 rss: 46Mb L: 5/8 MS: 1 EraseBytes-
   #2824	REDUCE cov: 13 ft: 15 corp: 6/27b lim: 25 exec/s: 0 rss: 46Mb L: 7/7 MS: 5 CopyPart-ChangeBit-InsertRepeatedBytes-ShuffleBytes-EraseBytes-
   #28771	REDUCE cov: 13 ft: 15 corp: 6/26b lim: 277 exec/s: 0 rss: 46Mb L: 3/7 MS: 2 EraseBytes-ChangeBinInt-
   Fatal Python error: deallocating None

   Current thread 0x00007fe5e9392780 (most recent call first):
     File "/home/erik/workspace/pyfuzzer/pyfuzzer/mutators/random.py", line 84 in test_one_input
   ==13442== ERROR: libFuzzer: deadly signal
       #0 0x4509bf in __sanitizer_print_stack_trace (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x4509bf)
       #1 0x43070b in fuzzer::PrintStackTrace() (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x43070b)
       #2 0x4157b8 in fuzzer::Fuzzer::CrashCallback() (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x4157b8)
       #3 0x41577f in fuzzer::Fuzzer::StaticCrashSignalCallback() (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x41577f)
       #4 0x7fe5e976ef3f  (/lib/x86_64-linux-gnu/libpthread.so.0+0x13f3f)
       #5 0x7fe5e9438ed6 in gsignal (/lib/x86_64-linux-gnu/libc.so.6+0x43ed6)
       #6 0x7fe5e941a534 in abort (/lib/x86_64-linux-gnu/libc.so.6+0x25534)
       #7 0x7fe5e97ead77 in initgroups (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x6ed77)
       #8 0x7fe5e98f0e72 in Py_FatalError (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x174e72)
       #9 0x7fe5e99a766f  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x22b66f)
       #10 0x7fe5e986a8b9  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0xee8b9)
       #11 0x7fe5e986df0a  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0xf1f0a)
       #12 0x7fe5e99f100b in _PyMethodDef_RawFastCallDict (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x27500b)
       #13 0x7fe5e99f1a44 in _PyCFunction_FastCallDict (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x275a44)
       #14 0x7fe5e99f36ad in _PyObject_CallMethodId_SizeT (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x2776ad)
       #15 0x7fe5e99f100b in _PyMethodDef_RawFastCallDict (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x27500b)
       #16 0x7fe5e99f1a44 in _PyCFunction_FastCallDict (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x275a44)
       #17 0x7fe5e99f39bd in _PyObject_CallMethodId (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x2779bd)
       #18 0x7fe5e98f0b27  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x174b27)
       #19 0x7fe5e98f0df8  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x174df8)
       #20 0x7fe5e98f0e72 in Py_FatalError (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x174e72)
       #21 0x7fe5e99a766f  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x22b66f)
       #22 0x7fe5e97f0008 in _PyEval_EvalFrameDefault (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x74008)
       #23 0x7fe5e97f54d2  (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x794d2)
       #24 0x7fe5e99f1541 in _PyFunction_FastCallDict (/lib/x86_64-linux-gnu/libpython3.7m.so.1.0+0x275541)
       #25 0x451092 in LLVMFuzzerTestOneInput /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer.c:90:13
       #26 0x416ada in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x416ada)
       #27 0x4162d5 in fuzzer::Fuzzer::RunOne(unsigned char const*, unsigned long, bool, fuzzer::InputInfo*, bool*) (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x4162d5)
       #28 0x418289 in fuzzer::Fuzzer::MutateAndTestOne() (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x418289)
       #29 0x418f55 in fuzzer::Fuzzer::Loop(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, fuzzer::fuzzer_allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&) (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x418f55)
       #30 0x40eb50 in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x40eb50)
       #31 0x430ec2 in main (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x430ec2)
       #32 0x7fe5e941bb6a in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x26b6a)
       #33 0x407cf9 in _start (/home/erik/workspace/pyfuzzer/examples/hello_world_fatal_error/pyfuzzer+0x407cf9)

   NOTE: libFuzzer has rudimentary signal handlers.
         Combine libFuzzer with AddressSanitizer or similar for better crash reports.
   SUMMARY: libFuzzer: deadly signal
   MS: 2 InsertRepeatedBytes-ChangeBinInt-; base unit: 4be627e5af73c3215e0d70084aba695045d1a512
   0xa,0x1,0x3,0xdf,0xdf,0xe5,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0xdf,0x0,
   \x0a\x01\x03\xdf\xdf\xe5\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\x00
   artifact_prefix='./'; Test unit written to ./crash-bd22a93daac0260bdb6f6a8f10ac852eae5dd77c
   Base64: CgED39/l39/f39/f39/f39/f39/f39/f39/f39/f39/f3wA=
   error: Command '['./pyfuzzer', 'corpus', '-max_total_time=1', '-max_len=4096']' returned non-zero exit status 77.

Print the function call that caused the crash.

.. code-block:: text

   $ pyfuzzer print_crashes
   tell(b'\xdf\xe5\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\xdf\x00') = None
