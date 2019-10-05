About
=====

!!! UNDER CONSTRUCTION - DO NOT USE !!!

Use `libFuzzer`_ to fuzzy-test Python C extension modules.

Ideas
=====

- Use type annotations for less type errors.

- Add support to fuzzy test pure Python modules by generating C code
  from them using Cython.

Installation
============

.. code-block:: text

   $ apt install clang
   $ pip install pyfuzzer

Example Usage
=============

Use the default generic mutator when testing the module hello_world.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer hello_world.c
   ...

Use a custom mutator when testing the module hello_world.

Testing with a custom mutator is often more efficient then using a
generic.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer -m mutator.py hello_world.c
   ...

.. _libFuzzer: https://llvm.org/docs/LibFuzzer.html
