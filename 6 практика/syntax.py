class Syntax:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def get_current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def expect_token(self, token_type, value=None):
        token = self.get_current_token()
        if token and token[0] == token_type and (value is None or token[1] == value):
            self.position += 1
            return token
        raise SyntaxError(f"Expected {token_type} {value}, got {token}")

    def move_to_next_token(self):
        self.position += 1

    def parse_program(self):
        self.expect_token('DELIMITER', '{')
        while self.get_current_token() and self.get_current_token()[1] != '}':
            token = self.get_current_token()
            if token[0] == 'TYPE':
                self.parse_declaration()
            else:
                self.parse_statement()
            self.expect_token('DELIMITER', ';')
        self.expect_token('DELIMITER', '}')

    def parse_declaration(self):
        self.expect_token('TYPE')
        self.parse_identifier_list()

    def parse_identifier_list(self):
        self.expect_token('ID')
        while self.get_current_token() and self.get_current_token()[1] == ',':
            self.expect_token('DELIMITER', ',')
            self.expect_token('ID')

    def parse_if_statement(self):
        self.expect_token('KEYWORD', 'if')
        self.expect_token('DELIMITER', '(')
        self.parse_expression()
        self.expect_token('DELIMITER', ')')
        self.expect_token('KEYWORD', 'then')
        self.parse_statement()
        if self.get_current_token() and self.get_current_token()[1] == 'else':
            self.move_to_next_token()  # Move to 'else'
            self.parse_statement()  # Handle statement after 'else'

    def parse_statement(self):
        token = self.get_current_token()
        if token[0] == 'DELIMITER' and token[1] == '[':
            self.parse_compound_statement()
        elif token[0] == 'ID':
            self.parse_assignment()
        elif token[0] == 'KEYWORD' and token[1] == 'if':
            self.parse_if_statement()
        elif token[0] == 'KEYWORD' and token[1] == 'while':
            self.parse_while_statement()
        elif token[0] == 'KEYWORD' and token[1] == 'for':
            self.parse_for_loop()
        elif token[0] == 'KEYWORD' and token[1] == 'read':
            self.parse_input_statement()
        elif token[0] == 'KEYWORD' and token[1] == 'write':
            self.parse_output_statement()
        elif token[0] == 'KEYWORD' and token[1] == 'else':
            raise SyntaxError(f"Unexpected 'else' statement without matching 'if'")
        else:
            raise SyntaxError(f"Unexpected statement: {token}")

    def parse_compound_statement(self):
        self.expect_token('DELIMITER', '[')
        while self.get_current_token() and self.get_current_token()[1] != ']':
            self.parse_statement()
            if self.get_current_token() and self.get_current_token()[1] in {':', '\n'}:
                self.move_to_next_token()
        self.expect_token('DELIMITER', ']')

    def parse_assignment(self):
        self.expect_token('ID')
        self.expect_token('KEYWORD', 'as')
        self.parse_expression()

    def parse_while_statement(self):
        self.expect_token('KEYWORD', 'while')
        self.parse_expression()
        self.expect_token('KEYWORD', 'do')
        self.parse_statement()

    def parse_for_loop(self):
        self.expect_token('KEYWORD', 'for')
        self.parse_assignment()
        self.expect_token('KEYWORD', 'to')
        self.parse_expression()
        self.expect_token('KEYWORD', 'do')
        self.parse_statement()

    def parse_input_statement(self):
        self.expect_token('KEYWORD', 'read')
        self.expect_token('DELIMITER', '(')
        self.expect_token('ID')
        while self.get_current_token() and self.get_current_token()[1] == ',':
            self.expect_token('DELIMITER', ',')
            self.expect_token('ID')
        self.expect_token('DELIMITER', ')')

    def parse_output_statement(self):
        self.expect_token('KEYWORD', 'write')
        self.expect_token('DELIMITER', '(')
        self.parse_expression()
        while self.get_current_token() and self.get_current_token()[1] == ',':
            self.expect_token('DELIMITER', ',')
            self.parse_expression()
        self.expect_token('DELIMITER', ')')

    def parse_expression(self):
        self.parse_term()
        while self.get_current_token() and self.get_current_token()[1] in {'+', '-', 'or'}:
            self.move_to_next_token()
            self.parse_term()
        while self.get_current_token() and self.get_current_token()[0] == 'REL_OP':  # Handle relational operators
            self.move_to_next_token()
            self.parse_term()

    def parse_term(self):
        self.parse_factor()
        while self.get_current_token() and self.get_current_token()[1] in {'*', '/', 'and'}:
            self.move_to_next_token()
            self.parse_factor()

    def parse_factor(self):
        token = self.get_current_token()
        if token[0] in {'ID', 'STRING'}:
            self.move_to_next_token()
        elif token[0] == 'NUMBER':
            self.parse_number()
        elif token[0] == 'KEYWORD' and token[1] in {'true', 'false'}:
            self.parse_boolean_literal()
        elif token[0] == 'DELIMITER' and token[1] == '(':
            self.move_to_next_token()
            self.parse_expression()
            self.expect_token('DELIMITER', ')')
        elif token[0] == 'KEYWORD' and token[1] == 'not':
            self.move_to_next_token()
            self.parse_factor()
        else:
            raise SyntaxError(f"Unexpected factor: {token}")

    def parse_number(self):
        token = self.get_current_token()
        if self.is_binary_number(token):
            self.move_to_next_token()
        elif self.is_octal_number(token):
            self.move_to_next_token()
        elif self.is_decimal_number(token):
            self.move_to_next_token()
        elif self.is_hexadecimal_number(token):
            self.move_to_next_token()
        elif self.is_real_number(token):
            self.move_to_next_token()
        else:
            raise SyntaxError(f"Unexpected number format: {token}")

    def parse_boolean_literal(self):
        token = self.get_current_token()
        if token[0] == 'KEYWORD' and token[1] in {'true', 'false'}:
            self.move_to_next_token()
        else:
            raise SyntaxError(f"Unexpected boolean literal: {token}")

    def is_binary_number(self, token):
        if token[0] != 'NUMBER':
            return False

        value = token[1]
        if value.startswith(('0b', '0B')):
            return all(c in '01' for c in value[2:])

        return False

    def is_octal_number(self, token):
        if token[0] != 'NUMBER':
            return False

        value = token[1]
        if value.startswith(('0o', '0O')):
            return all(c in '01234567' for c in value[2:])

        return False

    def is_decimal_number(self, token):
        if token[0] != 'NUMBER':
            return False

        value = token[1]
        if value.isdigit():
            return True
        if value.endswith(('d', 'D')):
            return value[:-1].isdigit()
        return False

    def is_hexadecimal_number(self, token):
        if token[0] != 'NUMBER':
            return False

        value = token[1]
        if value.startswith(('0h', '0H')):
            valid_chars = set('0123456789ABCDEFabcdef')
            return all(c in valid_chars for c in value[2:])

        return False

    def is_real_number(self, token):
        if token[0] != 'NUMBER':
            return False

        value = token[1]

        try:
            float(value)
            return True
        except ValueError:
            return False
