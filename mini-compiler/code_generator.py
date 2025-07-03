from parser import FunctionDecl, If, While, Compound, Printf

class CodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def write(self, text):
        self.code.append('    ' * self.indent_level + text)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_map = {
            'PLUS': '+',
            'MINUS': '-',
            'MULTIPLY': '*',
            'DIVIDE': '/',
            'EQUALS': '==',
            'NOT_EQUALS': '!=',
            'LT': '<',
            'GT': '>',
            'LTE': '<=',
            'GTE': '>='
        }
        op = op_map[node.op.type]
        return f'({left} {op} {right})'

    def visit_UnaryOp(self, node):
        op = '+' if node.op.type == 'PLUS' else '-'
        expr = self.visit(node.expr)
        return f'{op}{expr}'

    def visit_Num(self, node):
        return str(node.value)

    def visit_Var(self, node):
        return node.value

    def visit_Assign(self, node):
        var_name = self.visit(node.left)
        expr = self.visit(node.right)
        self.write(f'{var_name} = {expr}')

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_If(self, node):
        condition = self.visit(node.condition)
        self.write(f'if {condition}:')
        self.indent()
        self.visit(node.true_body)
        self.dedent()
        
        if node.false_body:
            self.write('else:')
            self.indent()
            self.visit(node.false_body)
            self.dedent()

    def visit_While(self, node):
        condition = self.visit(node.condition)
        self.write(f'while {condition}:')
        self.indent()
        self.visit(node.body)
        self.dedent()

    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        # In Python we don't need explicit type declarations
        self.write(f'{var_name} = None')

    def visit_Printf(self, node):
        # Replace newlines with explicit \n
        format_str = node.format_str.replace('\n', '\\n')
        args = [self.visit(arg) for arg in node.args]
        args_str = ', '.join(args)
        if args:
            self.write(f'print("{format_str}" % ({args_str}))')
        else:
            self.write(f'print("{format_str}")')

    def visit_FunctionDecl(self, node):
        self.write(f'def {node.name}():')
        self.indent()
        self.visit(node.body)
        self.dedent()

    def generate_code(self, node):
        # Add standard imports and setup
        self.write('# Generated Python code')
        self.write('import sys')
        self.write('')
        
        # Visit the AST
        self.visit(node)
        
        # Add main function call
        if isinstance(node, FunctionDecl) and node.name == 'main':
            self.write('')
            self.write('if __name__ == "__main__":')
            self.indent()
            self.write('main()')
            self.dedent()
        
        # Return the generated code as a string
        return '\n'.join(self.code) 
