class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {self.value})'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the position pointer and set the current_char"""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()

    def string(self):
        """Return a string token"""
        result = ''
        self.advance()  # Skip the opening quote
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                else:
                    result += self.current_char
            else:
                result += self.current_char
            self.advance()
        
        if self.current_char == '"':
            self.advance()  # Skip the closing quote
            return Token('STRING_CONST', result)
        else:
            self.error()

    def number(self):
        """Return a number consumed from the input"""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token('FLOAT_CONST', float(result))
        
        return Token('INTEGER_CONST', int(result))

    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        token_type = {
            'if': 'IF',
            'else': 'ELSE',
            'while': 'WHILE',
            'int': 'INT',
            'float': 'FLOAT',
            'void': 'VOID',
            'return': 'RETURN',
            'printf': 'PRINTF',
            'scanf': 'SCANF'
        }.get(result, 'ID')
        
        return Token(token_type, result)

    def get_next_token(self):
        """Lexical analyzer (tokenizer)"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '/':
                self.advance()  # Skip first /
                self.advance()  # Skip second /
                self.skip_comment()
                continue

            if self.current_char == '"':
                return self.string()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            # Single-character tokens
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return Token('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE', '/')
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            if self.current_char == '{':
                self.advance()
                return Token('LBRACE', '{')
            if self.current_char == '}':
                self.advance()
                return Token('RBRACE', '}')
            if self.current_char == ';':
                self.advance()
                return Token('SEMICOLON', ';')
            if self.current_char == ',':
                self.advance()
                return Token('COMMA', ',')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('EQUALS', '==')
                return Token('ASSIGN', '=')
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('LTE', '<=')
                return Token('LT', '<')
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('GTE', '>=')
                return Token('GT', '>')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('NOT_EQUALS', '!=')
                return Token('NOT', '!')
            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token('AND', '&&')
            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token('OR', '||')

            self.error()

        return Token('EOF', None) 
