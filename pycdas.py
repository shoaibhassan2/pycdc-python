import sys
import os
from typing import TextIO

# Imports from converted modules
from pyc_module import PycModule
from pyc_code import PycCode
from pyc_object import PycObject, PycObjectType
from pyc_numeric import PycInt, PycLong, PycFloat, PycComplex, PycCFloat, PycCComplex
from pyc_string import PycString
from pyc_sequence import PycTuple, PycList, PycDict, PycSet
import bytecode

# Flag names for Code Objects
FLAG_NAMES = [
    "CO_OPTIMIZED", "CO_NEWLOCALS", "CO_VARARGS", "CO_VARKEYWORDS",
    "CO_NESTED", "CO_GENERATOR", "CO_NOFREE", "CO_COROUTINE",
    "CO_ITERABLE_COROUTINE", "CO_ASYNC_GENERATOR", "<0x400>", "<0x800>",
    "CO_GENERATOR_ALLOWED", "<0x2000>", "<0x4000>", "<0x8000>",
    "<0x10000>", "CO_FUTURE_DIVISION", "CO_FUTURE_ABSOLUTE_IMPORT", "CO_FUTURE_WITH_STATEMENT",
    "CO_FUTURE_PRINT_FUNCTION", "CO_FUTURE_UNICODE_LITERALS", "CO_FUTURE_BARRY_AS_BDFL",
    "CO_FUTURE_GENERATOR_STOP",
    "CO_FUTURE_ANNOTATIONS", "CO_NO_MONITORING_EVENTS", "<0x4000000>", "<0x8000000>",
    "<0x10000000>", "<0x20000000>", "<0x40000000>", "<0x80000000>"
]

def print_coflags(flags: int, stream: TextIO):
    if flags == 0:
        stream.write("\n")
        return

    stream.write(" (")
    f = 1
    k = 0
    first = True
    while k < 32:
        if (flags & f) != 0:
            if not first:
                stream.write(" | ")
            stream.write(FLAG_NAMES[k])
            first = False
        k += 1
        f <<= 1
    stream.write(")\n")

def iputs(stream: TextIO, indent: int, text: str):
    stream.write("    " * indent + text)

def iprintf(stream: TextIO, indent: int, fmt: str, *args):
    stream.write("    " * indent)
    stream.write(fmt % args)

def output_object(obj: PycObject, mod: PycModule, indent: int, flags: int, stream: TextIO):
    if obj is None:
        iputs(stream, indent, "<NULL>\n")
        return

    obj_type = obj.type
    
    if obj_type in (PycObjectType.TYPE_CODE, PycObjectType.TYPE_CODE2):
        code_obj = obj # Assuming obj is PycCode instance
        iputs(stream, indent, "[Code]\n")
        iprintf(stream, indent + 1, "File Name: %s\n", code_obj.fileName.value.decode('utf-8', 'replace'))
        iprintf(stream, indent + 1, "Object Name: %s\n", code_obj.name.value.decode('utf-8', 'replace'))
        
        if mod.ver_compare(3, 11) >= 0:
            iprintf(stream, indent + 1, "Qualified Name: %s\n", code_obj.qualName.value.decode('utf-8', 'replace'))
            
        iprintf(stream, indent + 1, "Arg Count: %d\n", code_obj.argCount)
        
        if mod.ver_compare(3, 8) >= 0:
            iprintf(stream, indent + 1, "Pos Only Arg Count: %d\n", code_obj.posOnlyArgCount)
            
        if mod.major_ver >= 3:
            iprintf(stream, indent + 1, "KW Only Arg Count: %d\n", code_obj.kwOnlyArgCount)
            
        if mod.ver_compare(3, 11) < 0:
            iprintf(stream, indent + 1, "Locals: %d\n", code_obj.numLocals)
            
        if mod.ver_compare(1, 5) >= 0:
            iprintf(stream, indent + 1, "Stack Size: %d\n", code_obj.stackSize)
            
        if mod.ver_compare(1, 3) >= 0:
            orig_flags = code_obj.flags
            if mod.ver_compare(3, 8) < 0:
                # Remap flags logic from C++
                orig_flags = (orig_flags & 0xFFFF) | ((orig_flags & 0xFFF00000) >> 4)
            
            # Format hex string
            iprintf(stream, indent + 1, "Flags: 0x%08X", orig_flags)
            print_coflags(code_obj.flags, stream)

        # FIXED: Removed .size() calls, using .size property instead
        iputs(stream, indent + 1, "[Names]\n")
        for i in range(code_obj.names.size):
            output_object(code_obj.names.get(i), mod, indent + 2, flags, stream)

        if mod.ver_compare(1, 3) >= 0:
            if mod.ver_compare(3, 11) >= 0:
                iputs(stream, indent + 1, "[Locals+Names]\n")
            else:
                iputs(stream, indent + 1, "[Var Names]\n")
            for i in range(code_obj.localNames.size):
                output_object(code_obj.localNames.get(i), mod, indent + 2, flags, stream)

        if mod.ver_compare(3, 11) >= 0 and (flags & bytecode.DISASM_PYCODE_VERBOSE) != 0:
            iputs(stream, indent + 1, "[Locals+Kinds]\n")
            output_object(code_obj.localKinds, mod, indent + 2, flags, stream)

        if mod.ver_compare(2, 1) >= 0 and mod.ver_compare(3, 11) < 0:
            iputs(stream, indent + 1, "[Free Vars]\n")
            for i in range(code_obj.freeVars.size):
                output_object(code_obj.freeVars.get(i), mod, indent + 2, flags, stream)

            iputs(stream, indent + 1, "[Cell Vars]\n")
            for i in range(code_obj.cellVars.size):
                output_object(code_obj.cellVars.get(i), mod, indent + 2, flags, stream)

        iputs(stream, indent + 1, "[Constants]\n")
        for i in range(code_obj.consts.size):
            output_object(code_obj.consts.get(i), mod, indent + 2, flags, stream)

        iputs(stream, indent + 1, "[Disassembly]\n")
        bytecode.bc_disasm(stream, code_obj, mod, indent + 2, flags)

        if mod.ver_compare(1, 5) >= 0 and (flags & bytecode.DISASM_PYCODE_VERBOSE) != 0:
            iprintf(stream, indent + 1, "First Line: %d\n", code_obj.firstLine)
            iputs(stream, indent + 1, "[Line Number Table]\n")
            output_object(code_obj.lnTable, mod, indent + 2, flags, stream)

        if mod.ver_compare(3, 11) >= 0 and (flags & bytecode.DISASM_PYCODE_VERBOSE) != 0:
            iputs(stream, indent + 1, "[Exception Table]\n")
            output_object(code_obj.exceptTable, mod, indent + 2, flags, stream)

    elif obj_type in (PycObjectType.TYPE_STRING, PycObjectType.TYPE_UNICODE, 
                      PycObjectType.TYPE_INTERNED, PycObjectType.TYPE_ASCII,
                      PycObjectType.TYPE_ASCII_INTERNED, PycObjectType.TYPE_SHORT_ASCII,
                      PycObjectType.TYPE_SHORT_ASCII_INTERNED):
        iputs(stream, indent, "")
        obj.print(stream, mod)
        stream.write("\n")

    elif obj_type in (PycObjectType.TYPE_TUPLE, PycObjectType.TYPE_SMALL_TUPLE):
        iputs(stream, indent, "(\n")
        for val in obj.values:
            output_object(val, mod, indent + 1, flags, stream)
        iputs(stream, indent, ")\n")

    elif obj_type == PycObjectType.TYPE_LIST:
        iputs(stream, indent, "[\n")
        for val in obj.values:
            output_object(val, mod, indent + 1, flags, stream)
        iputs(stream, indent, "]\n")

    elif obj_type == PycObjectType.TYPE_DICT:
        iputs(stream, indent, "{\n")
        for key, val in obj.values:
            output_object(key, mod, indent + 1, flags, stream)
            output_object(val, mod, indent + 2, flags, stream)
        iputs(stream, indent, "}\n")

    elif obj_type == PycObjectType.TYPE_SET:
        iputs(stream, indent, "{\n")
        for val in obj.values:
            output_object(val, mod, indent + 1, flags, stream)
        iputs(stream, indent, "}\n")

    elif obj_type == PycObjectType.TYPE_FROZENSET:
        iputs(stream, indent, "frozenset({\n")
        for val in obj.values:
            output_object(val, mod, indent + 1, flags, stream)
        iputs(stream, indent, "})\n")

    elif obj_type == PycObjectType.TYPE_NONE:
        iputs(stream, indent, "None\n")
    elif obj_type == PycObjectType.TYPE_FALSE:
        iputs(stream, indent, "False\n")
    elif obj_type == PycObjectType.TYPE_TRUE:
        iputs(stream, indent, "True\n")
    elif obj_type == PycObjectType.TYPE_ELLIPSIS:
        iputs(stream, indent, "...\n")
    elif obj_type == PycObjectType.TYPE_INT:
        iprintf(stream, indent, "%d\n", obj.value)
    elif obj_type == PycObjectType.TYPE_LONG:
        iprintf(stream, indent, "%s\n", obj.repr(mod))
    elif obj_type == PycObjectType.TYPE_FLOAT:
        iprintf(stream, indent, "%s\n", obj.value)
    elif obj_type == PycObjectType.TYPE_COMPLEX:
        iprintf(stream, indent, "(%s+%sj)\n", obj.value, obj.imag)
    elif obj_type == PycObjectType.TYPE_BINARY_FLOAT:
        iprintf(stream, indent, "%g\n", obj.value)
    elif obj_type == PycObjectType.TYPE_BINARY_COMPLEX:
        iprintf(stream, indent, "(%g+%gj)\n", obj.value, obj.imag)
    else:
        iprintf(stream, indent, "<TYPE: %d>\n", obj.type)

def main():
    args = sys.argv[1:]
    infile = None
    marshalled = False
    version = None
    disasm_flags = 0
    pyc_output = sys.stdout
    out_file = None

    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        
        if arg == "-o":
            if i + 1 < len(args):
                filename = args[i+1]
                try:
                    out_file = open(filename, "w", encoding="utf-8")
                    pyc_output = out_file
                    skip_next = True
                except OSError:
                    sys.stderr.write(f"Error opening file '{filename}' for writing\n")
                    return 1
            else:
                sys.stderr.write("Option '-o' requires a filename\n")
                return 1
        elif arg == "-c":
            marshalled = True
        elif arg == "-v":
            if i + 1 < len(args):
                version = args[i+1]
                skip_next = True
            else:
                sys.stderr.write("Option '-v' requires a version\n")
                return 1
        elif arg == "--pycode-extra":
            disasm_flags |= bytecode.DISASM_PYCODE_VERBOSE
        elif arg == "--show-caches":
            disasm_flags |= bytecode.DISASM_SHOW_CACHES
        elif arg in ("--help", "-h"):
            print(f"Usage:  {sys.argv[0]} [options] input.pyc\n")
            print("Options:")
            print("  -o <filename>  Write output to <filename> (default: stdout)")
            print("  -c             Specify loading a compiled code object. Requires the version to be set")
            print("  -v <x.y>       Specify a Python version for loading a compiled code object")
            print("  --pycode-extra Show extra fields in PyCode object dumps")
            print("  --show-caches  Don't suprress CACHE instructions in Python 3.11+ disassembly")
            print("  --help         Show this help text and then exit")
            return 0
        elif arg.startswith('-'):
            sys.stderr.write(f"Error: Unrecognized argument {arg}\n")
            return 1
        else:
            infile = arg

    if not infile:
        sys.stderr.write("No input file specified\n")
        return 1

    mod = PycModule()
    
    if not marshalled:
        try:
            mod.load_from_file(infile)
        except Exception as ex:
            sys.stderr.write(f"Error disassembling {infile}: {ex}\n")
            return 1
    else:
        if not version:
            sys.stderr.write("Opening raw code objects requires a version to be specified\n")
            return 1
        
        try:
            parts = version.split('.')
            if len(parts) != 2:
                raise ValueError
            major = int(parts[0])
            minor = int(parts[1])
        except ValueError:
            sys.stderr.write("Unable to parse version string (use the format x.y)\n")
            return 1
            
        mod.load_from_marshalled_file(infile, major, minor)

    dispname = os.path.basename(infile)
    unicode_str = " -U" if (mod.major_ver < 3 and mod.is_unicode()) else ""
    pyc_output.write(f"{dispname} (Python {mod.major_ver}.{mod.minor_ver}{unicode_str})\n")
    
    try:
        output_object(mod.code, mod, 0, disasm_flags, pyc_output)
    except Exception as ex:
        sys.stderr.write(f"Error disassembling {infile}: {ex}\n")
        # import traceback
        # traceback.print_exc() # Uncomment for debugging
        return 1
    
    if out_file:
        out_file.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())