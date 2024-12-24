import re

def infix_to_postfix(expression):
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output = []
    operators = []
    tokens = re.findall(r'\d+\.?\d*|[()+*/-]', expression) # Нужно для деления на типо список из '10', '+', ... (я устал это прописывать)

    for token in tokens:
        if token.isdigit() or '.' in token: # Если это число
            output.append(token)
        elif token in precedence: # Если это оператор
            while (operators and operators[-1] in precedence and
                   precedence[token] <= precedence[operators[-1]]):
                output.append(operators.pop())
            operators.append(token)
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.pop() # Удаление '(' ато почему-то багалось

    while operators:
        output.append(operators.pop())
    return ' '.join(output)


def evaluate_postfix(expression):
    stack = []
    tokens = expression.split()
    for token in tokens:
        if token.isdigit() or '.' in token: # Если это число
            stack.append(float(token))
        else: # Если это оператор
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                stack.append(a / b)
    return stack[0] # По итогу возвращаем первый элемент в стеке, он же и ответ


expression = "10 + 3 * (2 - 1/2)"
print(f"Дано: {expression}")
postfix_expression = infix_to_postfix(expression)
print(f"Полиз: {postfix_expression}")
result = evaluate_postfix(postfix_expression)
print(f"Результат: {result}")
