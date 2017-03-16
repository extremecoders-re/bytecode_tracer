# bytecode_tracer

Python script to trace execution of bytecode for python 2.7

This works by modifying the CPython virtual machine such that it calls our trace function for each executed instruction rather than line by line of source code.

Visit http://0xec.blogspot.com/2017/03/hacking-cpython-virtual-machine-to.html to know more.

## Known limitations

Tracing of `SETUP_EXTENDED` opcode is not fully supported. However this does not mean tracing will fail or stop. In such case only the `SETUP_EXTENDED` instruction will be written to the trace file AND NOT the following instructions on which this opcode is actually operating on.

For example, if the bytecode looks like

```
SETUP_EXTENDED 0x0001
JUMP_ABSOLUTE 0x1234

0x11234:
POP_TOP
```

The target of the `JUMP_ABSOLUTE` instruction is `0x11234` due to the `SETUP_EXTENDED` before (`(0x0001 << 16) | 0x1234`).
However the trace file will NOT contain the `JUMP_ABSOLUTE` instruction and will contain the following listing.

```
SETUP_EXTENDED 0x0001
POP_TOP
```

This feature is easy to implement. We need to check if the current instruction is `SETUP_EXTENDED`. If so, we need to decode the following instructions on which this is operating as well.

## Command line arguments
```
$ python tracer.py -h
usage: tracer.py [-h] [-t {all,only}] [-n NAME] [-r] pycfile tracefile

positional arguments:
  pycfile               The pyc file to trace.
  tracefile             The file where to write the trace.

optional arguments:
  -h, --help            show this help message and exit
  -t {all,only}, --trace {all,only}
                        Trace all or only those codeobjects with co_name
                        specified by -name.
  -n NAME, --name NAME  co_name of the codeobject that will be traced.
  -r, --resolve         Resolve instruction operand values.
```  

## Usage

1. Trace execution of all code objects in the file *factorial.pyc*; do not resolve arguments

    ```
    $ python tracer.py factorial.pyc trace.txt
    ```

2. Trace code objects having a name of `recur_factorial`; resolve arguments as well

    ```
    $ python tracer.py -t=only -n=recur_factorial -r factorial.pyc trace.txt
    ```
    
