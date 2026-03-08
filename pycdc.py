import sys
import os
from pyc_module import PycModule
from astree import decompyle
import traceback

def main():
    # Argument variables
    infile = None
    marshalled = False
    version = None
    output_file = None
    
    # Parse arguments
    # [cite: 731-744]
    args = sys.argv[1:]
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        if arg == "-o":
            if i + 1 < len(args):
                output_file = args[i+1]
                skip_next = True
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
        elif arg in ("--help", "-h"):
            print(f"Usage:  {sys.argv[0]} [options] input.pyc\n")
            print("Options:")
            print("  -o <filename>  Write output to <filename> (default: stdout)")
            print("  -c             Specify loading a compiled code object. Requires the version to be set")
            print("  -v <x.y>       Specify a Python version for loading a compiled code object")
            print("  --help         Show this help text and then exit")
            return 0
        else:
            infile = arg

    if not infile:
        sys.stderr.write("No input file specified\n")
        return 1

    # Setup output stream
    if output_file:
        try:
            pyc_output = open(output_file, "w", encoding="utf-8")
        except OSError:
            sys.stderr.write(f"Error opening file '{output_file}' for writing\n")
            return 1
    else:
        pyc_output = sys.stdout

    mod = PycModule()

    if not marshalled:
        try:
            mod.load_from_file(infile)
        except Exception as ex:
            sys.stderr.write(f"Error loading file {infile}: {ex}\n")
            return 1
    else:
        if not version:
            sys.stderr.write("Opening raw code objects requires a version to be specified\n")
            return 1
        
        # [cite: 748-750]
        try:
            parts = version.split('.')
            if len(parts) != 2:
                raise ValueError
            major = int(parts[0])
            minor = int(parts[1])
        except ValueError:
            sys.stderr.write("Unable to parse version string (use the format x.y)\n")
            return 1
            
        # [cite: 751-752]
        # Note: strict adherence to provided source, which restricts minor < 12
        if minor < 12:
            return 1
            
        mod.load_from_marshalled_file(infile, major, minor)

    if not mod.is_valid():
        sys.stderr.write(f"Could not load file {infile}\n")
        return 1

    # Header printing
    # [cite: 754-757]
    dispname = os.path.basename(infile)
    pyc_output.write("# Source Generated with Decompyle++\n")
    
    # [cite: 756] 
    # Note: strict adherence to provided source check
    if mod.minor_ver < 12:
        return 1
        
    unicode_str = " Unicode" if (mod.major_ver < 3 and mod.is_unicode()) else ""
    pyc_output.write(f"# File: {dispname} (Python {mod.major_ver}.{mod.minor_ver}{unicode_str})\n\n")

    try:
        decompyle(mod.code, mod, pyc_output)
    except Exception:
        print("\n" + "="*70)
        print(f"Error decompyling {infile}: ")
        print("="*70)
        traceback.print_exc()  # This prints the EXACT line number
        print("="*70 + "\n")
        return 1

    if output_file:
        pyc_output.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())