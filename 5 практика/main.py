import re

letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
digits = set('0123456789')

def create_automaton():
    states = {0, 1, 2, 3}  # Состояния
    initial_state = 0  # Начальное состояние
    final_states = {1, 2, 3}  # Конечные состояния

    # Узлы состояний
    transition_function = {
        (0, 'letter'): 1,
        (1, 'letter'): 1,
        (1, 'digit'): 2,
        (1, '_'): 3,
        (2, 'digit'): 2,
        (2, 'letter'): 1,
        (2, '_'): 3,
        (3, '_'): 3,
        (3, 'letter'): 1,
        (3, 'digit'): 2
    }
    return states, initial_state, final_states, transition_function

def process_input(input_string, states, initial_state, final_states, transition_function):
    current_state = initial_state
    for char in input_string:
        # Определяем тип символа: буква, цифра или подчеркивание
        if char in letters:
            char_type = 'letter'
        elif char in digits:
            char_type = 'digit'
        elif char == '_':
            char_type = '_'
        else:
            return False  # Если символ не подходит, сразу возвращаем False

        # Переход к новому состоянию
        if (current_state, char_type) in transition_function:
            current_state = transition_function[(current_state, char_type)]
        else:
            return False
    return current_state in final_states

if __name__ == "__main__":
    states, initial_state, final_states, transition_function = create_automaton()
    input_string = input("Введите строку для анализа: ")
    if process_input(input_string, states, initial_state, final_states, transition_function):
        print("Строка принята")
    else:
        print("Строка не принята")