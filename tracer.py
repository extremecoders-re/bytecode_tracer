"""
Python bytecode execution tracer to be used with a modified version of python
supporting bytecode tracing.

Author: ExtremeCoders (0xec)

Example usage:

1. Trace execution of all code objects, do not resolve arguments
$ python tracer.py factorial.pyc trace.txt

2. Trace code objects having a name of `recur_factorial`, resolve arguments as well
$ python tracer.py -t=only -n=recur_factorial -r factorial.pyc trace.txt

Visit http://0xec.blogspot.com/2017/03/hacking-cpython-virtual-machine-to.html
"""

import sys
import dis
import marshal
import argparse

tracefile = None
options = None

# List of valid python opcodes
valid_opcodes = dis.opmap.values()

def trace(frame, event, arg):
    global tracefile, valid_opcodes, options
    if event == 'line':
        # Get the code object
        co_object = frame.f_code

        # Retrieve the name of the associated code object
        co_name = co_object.co_name

        if options.name is None or co_name == options.name:
            # Get the code bytes
            co_bytes = co_object.co_code

            # f_lasti is the offset of the last bytecode instruction executed
            # w.r.t the current code object
            # For the very first instruction this is set to -1
            ins_offs = frame.f_lasti

            if ins_offs >= 0:
                opcode = ord(co_bytes[ins_offs])

                # Check if it is a valid opcode
                if opcode in valid_opcodes:
                    if opcode >= dis.HAVE_ARGUMENT:
                        # Fetch the operand
                        operand = arg = ord(co_bytes[ins_offs+1]) | (ord(co_bytes[ins_offs+2]) << 8)

                        # Resolve instriction arguments if specified
                        if options.resolve:
                            try:
                                if opcode in dis.hasconst:
                                    operand = co_object.co_consts[arg]
                                elif opcode in dis.hasname:
                                    operand = co_object.co_names[arg]
                                elif opcode in dis.haslocal:
                                    operand = co_object.co_varnames[arg]
                                elif opcode in dis.hascompare:
                                    operand = dis.cmp_op[arg]
                                elif opcode in dis.hasjabs:
                                    operand = arg
                                elif opcode in dis.hasjrel:
                                    operand = arg + ins_offs + 3
                                else:
                                    operand = arg
                            except:
                                operand = None

                        tracefile.write('{}> {} {} ({})\n'.format(co_name, ins_offs, dis.opname[opcode], operand))

                    # No operands
                    else:
                        tracefile.write('{}> {} {}\n'.format(co_name, ins_offs, dis.opname[opcode]))

                # Invalid opcode
                else:
                    tracefile.write('{}> {} {} **********INVALID**********\n'.format(co_name, ins_offs, opcode))

    return trace

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pycfile', help='The pyc file to trace.')
    parser.add_argument('tracefile', help='The file where to write the trace.')
    parser.add_argument('-t', '--trace', choices=['all', 'only'], default='all', help='Trace all or only those codeobjects with the co_name.')
    parser.add_argument('-n', '--name', help='co_name of the codeobject that will be traced.')
    parser.add_argument('-r', '--resolve', action='store_true', help='Resolve instruction operand values.')
    args = parser.parse_args()

    if args.trace == 'only' and args.name is None:
        parser.error('--trace=only requires specifying --name')

    f = open(args.pycfile, 'rb')

    # Check pyc header
    if f.read(4) != '\x03\xf3\x0d\x0a':
        raise Exception('[*] Not a pyc file. Header mismatch')

    # Go to beginning of code object at offset of 8 from start
    f.seek(8)

    # Unmarshal file
    co = marshal.load(f)

    f.close()
    tracefile = open(args.tracefile, 'w')
    options = args

    # Set the trace function
    sys.settrace(trace)

    # Go, go
    eval(co)
