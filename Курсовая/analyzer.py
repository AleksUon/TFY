import tkinter as tk
from tkinter import scrolledtext, messagebox
from lex import Lexer
from syntax import Syntax
from semantic import Semantic
from prettytable import PrettyTable

# Исходный код
code = '''
{
% a;
! a;
$ flag;
[
    a as 5  /* Это комментарий */
    flag = true
];
}
'''

def run_lexical_analysis():
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        table = PrettyTable()
        table.field_names = ["Тип токена", "Токен"]
        for token in tokens:
            table.add_row(token)

        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Токены:\n")
        output_text.insert(tk.END, str(table))
        output_text.insert(tk.END, "\nЛексический анализ - OK\n")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка лексического анализа: {e}")

def run_syntax_analysis():
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        parser = Syntax(tokens)
        parser.parse_program()

        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Синтаксический анализ - OK\n")
    except SyntaxError as e:
        messagebox.showerror("Ошибка", f"Ошибка синтаксического анализа: {e}")

def run_semantic_analysis():
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        analyzer = Semantic(tokens)
        result = analyzer.analyze_tokens()

        # Выводим результаты семантического анализа
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Результаты семантического анализа:\n")
        output_text.insert(tk.END, result)

        # Преобразование выражений в ОПН
        # Пример: собираем токены для одного выражения
        expression_tokens = [
            ('ID', 'sum'), ('ADD_OP', '+'), ('ID', 'i'),
        ]

        # Получаем строку ОПН
        rpn = analyzer.to_rpn_expression(expression_tokens)

        # Добавляем ОПН в текстовый блок
        output_text.insert(tk.END, "\nОбратная польская нотация (ОПН):\n")
        output_text.insert(tk.END, rpn)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка семантического анализа: {e}")

def exit_application():
    root.destroy()

# Создание основного окна
root = tk.Tk()
root.title("Анализатор кода")

# Цветовая схема
bg_color = "#2b2b2b"  # Темно-серый фон
frame_color = "#3c3f41"  # Серый для рамок
btn_color = "#6a5acd"  # Темно-фиолетовый
text_color = "#ffffff"  # Белый текст

root.configure(bg=bg_color)

# Текстовое поле для вывода
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, bg=frame_color, fg=text_color, insertbackground=text_color, font=("Courier New", 12))
output_text.pack(pady=10)

# Панель кнопок
button_frame = tk.Frame(root, bg=bg_color)
button_frame.pack(pady=10)

btn_lexical = tk.Button(button_frame, text="Лексический анализ", command=run_lexical_analysis, bg=btn_color, fg=text_color, font=("Arial", 10))
btn_lexical.grid(row=0, column=0, padx=5)

btn_syntax = tk.Button(button_frame, text="Синтаксический анализ", command=run_syntax_analysis, bg=btn_color, fg=text_color, font=("Arial", 10))
btn_syntax.grid(row=0, column=1, padx=5)

btn_semantic = tk.Button(button_frame, text="Семантический анализ", command=run_semantic_analysis, bg=btn_color, fg=text_color, font=("Arial", 10))
btn_semantic.grid(row=0, column=2, padx=5)

btn_exit = tk.Button(button_frame, text="Завершить", command=exit_application, bg=btn_color, fg=text_color, font=("Arial", 10))
btn_exit.grid(row=0, column=3, padx=5)

# Запуск главного цикла
root.mainloop()
