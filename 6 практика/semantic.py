class Semantic:
    def __init__(self, tokens=None):
        self.symbol_table = {}
        self.current_position = 0
        self.tokens = tokens

    def get_current_token(self):
        return self.tokens[self.current_position] if self.current_position < len(self.tokens) else None

    def advance_token(self):
        self.current_position += 1

    def analyze_tokens(self):
        try:
            while self.current_position < len(self.tokens):
                token = self.get_current_token()

                # Обработка объявления переменных
                if token[0] == 'TYPE':
                    self.handle_variable_declaration()

                # Обработка операторов (например, присваивания)
                elif token[0] == 'ID' and self.peek_next_token() and self.peek_next_token()[0] == 'KEYWORD' and self.peek_next_token()[1] == 'as':
                    self.handle_assignment()

                # Логическое значение (true/false)
                elif token[0] == 'KEYWORD' and token[1] in ['true', 'false']:
                    self.advance_token()
                    return '$'

                # Обработка условного оператора if
                elif token[0] == 'KEYWORD' and token[1] == 'if':
                    self.handle_if_statement()

                # Обработка цикла for
                elif token[0] == 'KEYWORD' and token[1] == 'for':
                    self.handle_for_loop()

                # Обработка цикла while
                elif token[0] == 'KEYWORD' and token[1] == 'while':
                    self.handle_while_loop()

                # Игнорирование остальных токенов (например, ';', '{', '}')
                elif token[0] in {'DELIMITER', 'COMMENT'}:
                    self.advance_token()

                else:
                    raise Exception(f"Неожиданный токен: {token}")

            return "Семантический анализ завершён успешно"

        except Exception as e:
            return f"Семантическая ошибка: {e}"

    def handle_integer(self):
        token = self.get_current_token()
        if not token or token[0] != 'NUMBER':
            raise Exception(f"Ожидалось целое число, но найдено: {token}")

        number = token[1]

        if self.is_binary_number(number):
            self.advance_token()
            return '%'
        elif self.is_octal_number(number):
            self.advance_token()
            return '%'
        elif self.is_decimal_number(number):
            self.advance_token()
            return '%'
        elif self.is_hexadecimal_number(number):
            self.advance_token()
            return '%'
        else:
            raise Exception(f"Недопустимый формат числа: {number}")

    def is_binary_number(self, number):
        return number[:-1].isdigit() and all(c in '01' for c in number[:-1]) and number[-1] in 'Bb'

    def is_octal_number(self, number):
        return number[:-1].isdigit() and all(c in '01234567' for c in number[:-1]) and number[-1] in 'Oo'

    def is_decimal_number(self, number):
        return number[:-1].isdigit() and number[-1] in 'Dd' or number.isdigit()

    def is_hexadecimal_number(self, number):
        prefix = number[:-1]
        return all(c in '0123456789ABCDEFabcdef' for c in prefix) and number[-1] in 'Hh'

    def handle_real_number(self):
        token = self.get_current_token()
        if not token or token[0] != 'REAL':
            raise Exception(f"Ожидалось действительное число, но найдено: {token}")

        number = token[1]

        if self.is_real_format(number):
            self.advance_token()
            return '%'
        else:
            raise Exception(f"Недопустимый формат действительного числа: {number}")

    def is_real_format(self, number):
        if '.' in number:
            parts = number.split('.')
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                return False
            return True
        elif 'E' in number or 'e' in number:
            parts = number.split('E' if 'E' in number else 'e')
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].lstrip('+-').isdigit():
                return False
            return True
        return False

    def handle_program(self):
        self.expect_token('DELIMITER', '{')
        while self.get_current_token() and self.get_current_token()[1] != '}':
            if self.get_current_token()[0] in {'KEYWORD', 'ID'}:
                self.handle_statement()
                self.expect_token('DELIMITER', ';')
            else:
                raise Exception(f"Неожиданный токен: {self.get_current_token()}")
        self.expect_token('DELIMITER', '}')

    def handle_statement(self):
        token = self.get_current_token()
        if token[0] == 'KEYWORD':
            if token[1] == 'if':
                self.handle_if_statement()
            elif token[1] == 'for':
                self.handle_for_loop()
            elif token[1] == 'while':
                self.handle_while_loop()
            elif token[1] == 'read':
                self.handle_input()
            elif token[1] == 'write':
                self.handle_output()
            else:
                raise Exception(f"Неизвестная ключевая команда: {token[1]}")
        elif token[0] == 'ID':
            self.handle_assignment()
        else:
            raise Exception(f"Неподдерживаемый оператор: {token}")

    # Парсинг декларации переменных. Например: % a, b, c;
    def handle_variable_declaration(self):
        token = self.get_current_token()
        if token[0] != 'TYPE':
            raise Exception(f"Ожидался токен TYPE, но найден: {token}")

        var_type = token[1]  # Сохраняем тип переменной: %, ! или $
        self.advance_token()  # Пропускаем токен TYPE

        start_position = self.current_position

        # Собираем идентификаторы до конца строки (;)
        while self.get_current_token()[0] != 'DELIMITER' or self.get_current_token()[1] != ';':
            self.advance_token()

        end_position = self.current_position
        identifiers = self.collect_identifiers(start_position, end_position)

        # Проверяем на наличие повторных идентификаторов
        for identifier in identifiers:
            if identifier in self.symbol_table:
                raise Exception(f"Повторное объявление идентификатора: {identifier}")
            # Добавляем идентификатор в таблицу символов
            self.symbol_table[identifier] = {'type': var_type}

        self.advance_token()  # Пропускаем токен ';'

    # Собирает идентификаторы (ID) из токенов в заданном диапазоне
    def collect_identifiers(self, start_index, end_index):
        identifiers = []
        for i in range(start_index, end_index):
            token = self.tokens[i]
            if token[0] == 'ID':  # Проверяем тип токена
                identifiers.append(token[1])  # Добавляем имя идентификатора
        return identifiers

    # Возвращает следующий токен без изменения текущей позиции.
    def peek_next_token(self):
        if self.current_position + 1 < len(self.tokens):
            return self.tokens[self.current_position + 1]
        return None  # Возвращаем None, если следующий токен отсутствует

    def handle_assignment(self):
        variable = self.expect_token('ID')
        if variable[1] not in self.symbol_table:
            raise Exception(f"Переменная '{variable[1]}' не была объявлена.")
        self.expect_token('KEYWORD', 'as')
        expr_type = self.handle_expression()
        var_type = self.symbol_table[variable[1]]['type']
        if expr_type != var_type:
            raise Exception(
                f"Несоответствие типов: переменная '{variable[1]}' имеет тип {var_type}, но ей присваивается значение типа {expr_type}"
            )

    # Анализирует выражение и возвращает его тип.
    def handle_expression(self):
        token = self.get_current_token()
        if not token:
            raise Exception("Ожидалось выражение, но токены закончились.")

        # Логические значения true/false
        if token[0] == 'KEYWORD' and token[1] in ['true', 'false']:
            self.advance_token()
            return '$'  # Логические значения имеют тип $

        # Числовой литерал
        if token[0] == 'NUMBER':
            self.advance_token()
            left_type = '%'

        # Строковый литерал
        elif token[0] == 'STRING':
            self.advance_token()
            left_type = 'STRING'

        # Переменная
        elif token[0] == 'ID':
            var_name = token[1]
            if var_name not in self.symbol_table:
                raise Exception(f"Переменная '{var_name}' не была объявлена.")
            left_type = self.symbol_table[var_name]['type']
            self.advance_token()

            # Проверяем на наличие оператора REL_OP (сравнительного)
            if self.get_current_token() and self.get_current_token()[0] == 'REL_OP':
                operator = self.get_current_token()
                self.advance_token()
                right_type = self.handle_expression()  # Обрабатываем правый операнд
                if left_type != '%' or right_type != '%':
                    raise Exception(
                        f"Операторы сравнения применимы только к числовым значениям, найдено: {left_type} и {right_type}"
                    )
                return '$'  # Логическое выражение возвращает тип '$'

        # Скобки
        elif token[0] == 'DELIMITER' and token[1] == '(':
            self.advance_token()
            left_type = self.handle_expression()
            self.expect_token('DELIMITER', ')')

        else:
            raise Exception(f"Неподдерживаемый токен в выражении: {token}")

        # Обработка бинарных операций
        while self.get_current_token() and self.get_current_token()[0] in ['ADD_OP', 'MUL_OP']:
            op_token = self.get_current_token()
            self.advance_token()
            right_type = self.handle_expression()  # Рекурсивный вызов для правого операнда
            if left_type != '%' or right_type != '%':
                raise Exception(
                    f"Операторы {op_token[1]} применимы только к числовым значениям, найдено: {left_type} и {right_type}"
                )
            left_type = '%'  # Результат бинарной операции — всегда числовой тип

        return left_type

    def handle_if_statement(self):
        self.expect_token('KEYWORD', 'if')
        self.expect_token('DELIMITER', '(')
        condition_type = self.handle_expression()
        if condition_type != '$':
            raise Exception("Условие должно быть логическим выражением.")
        self.expect_token('DELIMITER', ')')
        self.expect_token('KEYWORD', 'then')
        self.handle_statement()
        if self.get_current_token() and self.get_current_token()[0] == 'KEYWORD' and self.get_current_token()[1] == 'else':
            self.advance_token()
            self.handle_statement()

    def handle_for_loop(self):
        self.expect_token('KEYWORD', 'for')
        self.handle_assignment()
        self.expect_token('KEYWORD', 'to')
        expr_type = self.handle_expression()
        if expr_type != '%':
            raise Exception("Выражение в операторе for должно быть числовым.")
        self.expect_token('KEYWORD', 'do')
        self.handle_statement()

    def handle_while_loop(self):
        self.expect_token('KEYWORD', 'while')
        self.expect_token('DELIMITER', '(')
        condition_type = self.handle_expression()
        if condition_type != '$':
            raise Exception("Условие должно быть логическим выражением.")
        self.expect_token('DELIMITER', ')')
        self.expect_token('KEYWORD', 'do')
        self.handle_statement()

    # Обработка инструкции read(<переменные>).
    def handle_input(self):
        self.expect_token('KEYWORD', 'read')  # Проверяем наличие ключевого слова read
        self.expect_token('DELIMITER', '(')  # Открывающая скобка

        while True:
            token = self.get_current_token()
            if not token or token[0] != 'ID':  # Проверяем, что токен — идентификатор
                raise Exception(f"Ожидалась переменная в read(), но найдено: {token}")

            var_name = token[1]
            if var_name not in self.symbol_table:  # Проверяем, что переменная объявлена
                raise Exception(f"Переменная '{var_name}' не была объявлена до вызова read().")

            self.advance_token()  # Переход к следующему токену

            # Проверяем на запятые между переменными
            if self.get_current_token() and self.get_current_token()[0] == 'DELIMITER' and self.get_current_token()[1] == ',':
                self.advance_token()  # Пропускаем запятую и продолжаем
            else:
                break  # Если запятых больше нет, выходим из цикла

        self.expect_token('DELIMITER', ')')  # Закрывающая скобка

    def handle_output(self):
        self.expect_token('KEYWORD', 'write')
        self.expect_token('DELIMITER', '(')
        while self.get_current_token() and self.get_current_token()[0] in {'ID', 'NUMBER', 'STRING'}:
            self.handle_expression()
            if self.get_current_token() and self.get_current_token()[0] == 'DELIMITER' and self.get_current_token()[1] == ',':
                self.advance_token()
            else:
                break
        self.expect_token('DELIMITER', ')')

    def expect_token(self, token_type, value=None):
        token = self.get_current_token()
        if token and token[0] == token_type and (value is None or token[1] == value):
            self.advance_token()
            return token
        raise Exception(f"Ожидалось {token_type} '{value}', но найдено {token}")

    # Преобразует токены выражения в строку обратной польской нотации (ОПН).
    def to_rpn_expression(self, expression_tokens):
        output = []  # Выходной список (постфиксная запись)
        stack = []  # Стек для операторов и скобок

        # Приоритеты операторов
        precedence = {
            '+': 1, '-': 1,
            '*': 2, '/': 2
        }

        # Проход по каждому токену выражения
        for token in expression_tokens:
            token_type, token_value = token

            # Если токен - операнд (число или переменная)
            if token_type in {'NUMBER', 'ID'}:
                output.append(token_value)  # Добавляем операнд в выходной список

            # Если токен - открывающая скобка
            elif token_type == 'DELIMITER' and token_value == '(':
                stack.append(token_value)

            # Если токен - закрывающая скобка
            elif token_type == 'DELIMITER' and token_value == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack or stack[-1] != '(':
                    raise Exception("Несогласованные скобки")
                stack.pop()  # Удаляем '(' из стека

            # Если токен - оператор
            elif token_type in {'ADD_OP', 'MUL_OP'}:
                while (stack and stack[-1] in precedence and
                       precedence[token_value] <= precedence[stack[-1]]):
                    output.append(stack.pop())
                stack.append(token_value)

            # Неизвестный токен
            else:
                raise Exception(f"Неподдерживаемый токен в выражении: {token}")

        # Перемещаем все оставшиеся операторы из стека в выходной список
        while stack:
            if stack[-1] in {'(', ')'}:
                raise Exception("Несогласованные скобки в выражении")
            output.append(stack.pop())

        # Собираем и возвращаем строку ОПН
        return ''.join(output)
