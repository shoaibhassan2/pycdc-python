# Decompyle++ (Python Edition)
***A Python Byte-code Disassembler / Decompiler implemented in Python***

⚠️ **Project Status:**  
This project is **still under active development**. Features may be incomplete and some Python bytecode versions may not yet be fully supported.  
Contributions, suggestions, bug reports, and improvements are welcome.

---

# Overview

**Decompyle++ (Python Edition)** aims to translate compiled Python byte-code back into valid and human-readable Python source code.

This project is a **Python translation of the original C++ project pycdc (Decompyle++)**.  
The core logic and architecture were translated from the original implementation while adapting it to a pure Python environment.

It focuses on providing a portable and easy-to-use byte-code decompiler written entirely in Python.

Like the original project, this implementation attempts to support **multiple Python byte-code versions** and reconstruct readable source code from compiled `.pyc` files.

---

# Features

- Python byte-code **disassembler**
- Python byte-code **decompiler**
- Supports `.pyc` files
- Supports **marshalled Python code objects**
- Pure **Python implementation**
- Portable across platforms

---

# Tools Included

### `pycdas`
A **byte-code disassembler** that prints readable Python byte-code instructions.

### `pycdc`
A **byte-code decompiler** that attempts to reconstruct Python source code from compiled byte-code.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/shoaibhassan2/pycdc-python
cd pycdc-python
```