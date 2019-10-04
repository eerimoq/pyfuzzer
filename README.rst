About
=====

!!! UNDER CONSTRUCTION - DO NOT USE !!!

Use `libFuzzer`_ to fuzzy-test Python 3 modules.

Installation
============

.. code-block:: text

   $ pip install pyfuzzer

Example Usage
=============

Use the default mutator when testing the module hello_world. Cython is
used to generate C code from Python code.

Testing with the default mutator is often very inefficient as Python
is such a dynamic language. A custom mutator is often needed for
efficient testing.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer hello_world
   ...

Use a custom mutator when testing the module hello_world.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer -f mutator hello_world
   ...

.. _libFuzzer: https://llvm.org/docs/LibFuzzer.html
