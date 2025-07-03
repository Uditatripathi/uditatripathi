# Mini C Compiler

A simple C compiler implementation in Python built from scratch. This compiler supports basic C language features including:

- Arithmetic operators (+, -, *, /, %)
- Relational operators (<, >, <=, >=, ==, !=)
- Logical operators (&&, ||, !)
- Variables and assignments
- If-else conditions
- While loops
- Basic I/O operations

## Components

1. `lexer.py` - Tokenizes the input C code
2. `parser.py` - Parses the tokens and creates an Abstract Syntax Tree (AST)
3. `code_generator.py` - Generates Python code from the AST
4. `main.py` - Main entry point of the compiler

## Usage

```bash
python main.py input.c
```

This will compile the C code in `input.c` and generate equivalent Python code. 