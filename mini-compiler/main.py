import sys
from lexer import Lexer
from parser import Parser
from code_generator import CodeGenerator

def compile_c(source_code):
    # Create lexer
    lexer = Lexer(source_code)
    
    # Create parser
    parser = Parser(lexer)
    
    # Parse the source code to create AST
    ast = parser.parse()
    
    # Create code generator
    generator = CodeGenerator()
    
    # Generate Python code from AST
    python_code = generator.generate_code(ast)
    
    return python_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    # Read input file
    input_file = sys.argv[1]
    try:
        with open(input_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    try:
        # Compile C code to Python
        python_code = compile_c(source_code)
        
        # Write output to a .py file
        output_file = input_file.rsplit('.', 1)[0] + '.py'
        with open(output_file, 'w') as f:
            f.write(python_code)
        
        print(f"Successfully compiled {input_file} to {output_file}")
        
    except Exception as e:
        print(f"Compilation error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 