from lexer import Token

class AST:
    
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Compound(AST):
    def __init__(self):
        self.children = []

class If(AST):
    def __init__(self, condition, true_body, false_body=None):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body

class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class FunctionDecl(AST):
    def __init__(self, type_node, name, body):
        self.type_node = type_node
        self.name = name
        self.body = body

class Printf(AST):
    def __init__(self, format_str, args):
        self.format_str = format_str
        self.args = args

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        print(f"Initial token: {self.current_token.type}, {self.current_token.value}")

    def error(self):
        raise Exception(f'Invalid syntax at token: {self.current_token.type}, {self.current_token.value}')

    def eat(self, token_type):
        print(f"Eating token: {self.current_token.type}, {self.current_token.value}, Expected: {token_type}")
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
            print(f"Next token: {self.current_token.type}, {self.current_token.value}")
        else:
            self.error()

    def program(self):
        """program : function_declaration"""
        node = self.function_declaration()
        return node

    def function_declaration(self):
        """function_declaration : type_spec ID LPAREN RPAREN compound_statement"""
        type_node = Type(self.current_token)  # void, int, etc.
        self.eat(self.current_token.type)

        name = self.current_token.value  
        self.eat('ID')

        self.eat('LPAREN')
        self.eat('RPAREN')

        body = self.compound_statement()
        return FunctionDecl(type_node, name, body)

    def compound_statement(self):
        """compound_statement : LBRACE statement_list RBRACE"""
        self.eat('LBRACE')
        nodes = self.statement_list()
        self.eat('RBRACE')

        root = Compound()
        for node in nodes:
            if node is not None:  
                root.children.append(node)

        return root

    def statement_list(self):
        """statement_list : statement
                        | statement SEMICOLON statement_list
        """
        nodes = []
        
        while True:
            if self.current_token.type == 'RBRACE':
                break
                
            node = self.statement()
            if node is not None:  # Skip None nodes
                nodes.append(node)
            
            
            if isinstance(node, (If, While, Compound)):
                continue
                
            if self.current_token.type == 'SEMICOLON':
                self.eat('SEMICOLON')
            elif self.current_token.type == 'RBRACE':
                break
            else:
                self.error()

        return nodes

    def statement(self):
        """statement : compound_statement
                    | assignment_statement
                    | if_statement
                    | while_statement
                    | declaration_statement
                    | printf_statement
                    | empty
        """
        if self.current_token.type == 'LBRACE':
            node = self.compound_statement()
        elif self.current_token.type in ('INT', 'FLOAT', 'VOID'):
            node = self.declaration_statement()
        elif self.current_token.type == 'ID':
            node = self.assignment_statement()
        elif self.current_token.type == 'IF':
            node = self.if_statement()
        elif self.current_token.type == 'WHILE':
            node = self.while_statement()
        elif self.current_token.type == 'PRINTF':
            node = self.printf_statement()
        else:
            node = self.empty()
        return node

    def declaration_statement(self):
        """declaration_statement : type_spec ID"""
        type_node = Type(self.current_token)
        self.eat(self.current_token.type)

        var_node = Var(self.current_token)
        self.eat('ID')

        return VarDecl(var_node, type_node)

    def assignment_statement(self):
        """assignment_statement : variable ASSIGN expr"""
        left = self.variable()
        token = self.current_token
        self.eat('ASSIGN')
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def if_statement(self):
        """if_statement : IF LPAREN condition RPAREN statement
                       | IF LPAREN condition RPAREN statement ELSE statement"""
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.condition()
        self.eat('RPAREN')
        true_body = self.statement()
        
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            false_body = self.statement()
            node = If(condition, true_body, false_body)
        else:
            node = If(condition, true_body)
            
        return node

    def while_statement(self):
        """while_statement : WHILE LPAREN condition RPAREN statement"""
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.condition()
        self.eat('RPAREN')
        body = self.statement()
        return While(condition, body)

    def condition(self):
        """condition : expr (EQUALS | NOT_EQUALS | LT | GT | LTE | GTE) expr"""
        left = self.expr()
        op = self.current_token
        if op.type in ('EQUALS', 'NOT_EQUALS', 'LT', 'GT', 'LTE', 'GTE'):
            self.eat(op.type)
            right = self.expr()
            return BinOp(left, op, right)
        self.error()

    def variable(self):
        """variable : ID"""
        node = Var(self.current_token)
        self.eat('ID')
        return node

    def empty(self):
        """An empty production"""
        return None

    def expr(self):
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
            elif token.type == 'MINUS':
                self.eat('MINUS')

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((MULTIPLY | DIVIDE) factor)*"""
        node = self.factor()

        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            if token.type == 'MULTIPLY':
                self.eat('MULTIPLY')
            elif token.type == 'DIVIDE':
                self.eat('DIVIDE')

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INTEGER_CONST
                  | FLOAT_CONST
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.current_token
        if token.type == 'PLUS':
            self.eat('PLUS')
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == 'MINUS':
            self.eat('MINUS')
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == 'INTEGER_CONST':
            self.eat('INTEGER_CONST')
            return Num(token)
        elif token.type == 'FLOAT_CONST':
            self.eat('FLOAT_CONST')
            return Num(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            node = self.variable()
            return node

    
    def printf_statement(self):
        """printf_statement : PRINTF LPAREN STRING_CONST (COMMA expr)* RPAREN"""
        self.eat('PRINTF')
        self.eat('LPAREN')
        format_str = self.current_token.value
        self.eat('STRING_CONST')
        
        args = []
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            args.append(self.expr())
        
        self.eat('RPAREN')
        return Printf(format_str, args)

    
    def parse(self):
        node = self.program()
        if self.current_token.type != 'EOF':
            self.error()
        return node 
