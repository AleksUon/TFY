from enum import Enum


class Lexer:
    # Состояния автомата
    class LexerState(Enum):
        H = "H"  # Начальное состояние
        ID = "ID"  # Идентификаторы
        NUM = "NUM"  # Числа
        COM = "COM"  # Комментарии
        ALE = "ALE"  # Операции отношения
        NEQ = "NEQ"  # Неравенство
        DELIM = "DELIM"  # Разделители
        STR = "STR"  # Строковые литералы
        ERROR = "ERROR"  # Состояние ошибки
        END = "END"  # Конечное состояние

    # Ключевые слова и типы данных
    TW = [
        "if", "then", "else", "while", "do", "for", "to", "read", "write",
        "true", "false", "as", "not", "or", "and"
    ]

    # Типы данных
    TYPES = [
        "%", "!", "$"
    ]

    # Разделители и операторы
    TD = [
        "{", "}", "[", "]", "(", ")", ",", ";", ":", "<>", "=", "<", "<=", ">", ">=", "+", "-", "*", "/", "or", "and"
    ]

    def __init__(self, input_text):
        self.text = input_text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
        self.tokens = []
        self.state = self.LexerState.H  # Начальное состояние

    # Обработка ввода и переход к следующему символу
    def advance_position(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def append_token(self, token_type, value):
        self.tokens.append((token_type, value))

    def skip_whitespace(self):
        while self.current_char and self.current_char in ' \n\r\t':
            self.advance_position()
    # Переходы между состояниями
    def process_state(self):
        if self.state == self.LexerState.H:
            self.skip_whitespace()
            if not self.current_char:
                self.state = self.LexerState.END  # Завершаем анализ
                return
            if self.current_char in self.TYPES:
                self.state = self.LexerState.ALE
            elif self.current_char.isalpha():
                self.state = self.LexerState.ID
            elif self.current_char.isdigit():
                self.state = self.LexerState.NUM
            elif self.current_char == "'":
                self.state = self.LexerState.STR
            elif self.current_char == '/' and self.text[self.pos + 1:self.pos + 2] == '*':
                self.state = self.LexerState.COM
            elif self.current_char in self.TD:
                self.state = self.LexerState.DELIM
            else:
                self.state = self.LexerState.ERROR  # Ошибка при неправильном символе
                self.append_token('ERROR', f"Unexpected character: {self.current_char}")
                self.advance_position()

        elif self.state == self.LexerState.ID:
            self.handle_identifier_or_keyword()
            self.state = self.LexerState.H

        elif self.state == self.LexerState.NUM:
            self.handle_number()
            self.state = self.LexerState.H

        elif self.state == self.LexerState.STR:
            self.handle_string()
            self.state = self.LexerState.H

        elif self.state == self.LexerState.COM:
            self.handle_comment()
            self.state = self.LexerState.H

        elif self.state == self.LexerState.ALE:
            self.handle_type_symbol()
            self.state = self.LexerState.H

        elif self.state == self.LexerState.DELIM:
            self.handle_delimiter_or_operator()
            self.state = self.LexerState.H

        elif self.state == self.LexerState.ERROR:
            # Ошибка в состоянии, можно добавить обработку или выход из цикла
            self.append_token('ERROR', f"Unexpected character: {self.current_char}")
            self.state = self.LexerState.H  # Переход к началу после ошибки
            self.advance_position()
    def handle_identifier_or_keyword(self):
        start = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            self.advance_position()
        text = self.text[start:self.pos]
        if text in self.TYPES:
            self.append_token('TYPE', text)
        elif text in self.TW:
            self.append_token('KEYWORD', text)
        else:
            self.append_token('ID', text)

    def handle_number(self):
        start = self.pos
        if self.current_char == '0':  # Возможные специальные форматы
            self.advance_position()
            if self.current_char in 'Bb':  # Двоичное число
                self.advance_position()
                while self.current_char and self.current_char in '01':
                    self.advance_position()
                self.append_token('NUMBER', self.text[start:self.pos])
                return
            elif self.current_char in 'Oo':  # Восьмеричное число
                self.advance_position()
                while self.current_char and self.current_char in '01234567':
                    self.advance_position()
                self.append_token('NUMBER', self.text[start:self.pos])
                return
            elif self.current_char in 'Hh':  # Шестнадцатеричное число
                self.advance_position()
                while self.current_char and (self.current_char.isdigit() or self.current_char in 'ABCDEFabcdef'):
                    self.advance_position()
                self.append_token('NUMBER', self.text[start:self.pos])
                return

        is_real = False
        while self.current_char and self.current_char.isdigit():
            self.advance_position()
        if self.current_char == '.':  # Возможное действительное число
            is_real = True
            self.advance_position()
            while self.current_char and self.current_char.isdigit():
                self.advance_position()
        if self.current_char in 'Ee':  # Порядок
            is_real = True
            self.advance_position()
            if self.current_char in '+-':
                self.advance_position()
            while self.current_char and self.current_char.isdigit():
                self.advance_position()
        if is_real:
            self.append_token('NUMBER', self.text[start:self.pos])
            return
        if self.current_char in 'Dd':  # Десятичное число с суффиксом
            self.advance_position()
            self.append_token('NUMBER', self.text[start:self.pos])
            return

        self.append_token('NUMBER', self.text[start:self.pos])

    def handle_comment(self):
        self.advance_position()  # Спускаемся с /*
        while self.current_char and not (self.current_char == '*' and self.text[self.pos + 1:self.pos + 2] == '/'):
            self.advance_position()
        self.advance_position()  # Спускаемся на *
        self.advance_position()  # И на /

    def handle_delimiter_or_operator(self):
        start = self.pos
        self.advance_position()
        while self.current_char and (self.text[start:self.pos + 1] in self.TD):
            self.advance_position()
        text = self.text[start:self.pos]
        if text in ["<>", "=", "<", "<=", ">", ">="]:
            self.append_token('REL_OP', text)
        elif text in ["+", "-", "or"]:
            self.append_token('ADD_OP', text)
        elif text in ["*", "/", "and"]:
            self.append_token('MUL_OP', text)
        elif text in self.TD:
            self.append_token('DELIMITER', text)
        else:
            self.append_token('UNKNOWN', text)

    def handle_type_symbol(self):
        if self.current_char in self.TYPES:
            self.append_token('TYPE', self.current_char)
            self.advance_position()

    def handle_string(self):
        self.advance_position()
        start = self.pos
        while self.current_char and self.current_char != "'":
            self.advance_position()
        text = self.text[start:self.pos]
        self.append_token('STRING', f"'{text}'")
        self.advance_position()

    # Циклическая обработка входной строки
    def tokenize(self):
        while self.state != self.LexerState.END:
            self.process_state()

        # Если есть ошибка, токены ошибки тоже добавляются
        if self.state == self.LexerState.ERROR:
            self.append_token('ERROR', "Unexpected end of input")

        return self.tokens
