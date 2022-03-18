import numpy as np
import re
import tkinter as tk
from tkinter import * 
from tkinter import filedialog
from tkinter import scrolledtext


################################
# Загрузка теста и его парсинг
################################

window = tk.Tk()

# Пользователь указывает путь к txt файлу
text_path = filedialog.askopenfilename(title='Выберите классификатор')

window.destroy()

# читаем содержимое файла и удаляем табуляцию
with open(text_path, 'r', encoding='utf-8') as file:
    Text = file.read()
    Text = Text.replace("\t", "")

# разделяем файл на строки по пробелам и удаляем пустые строки
Text = Text.split(sep='\n')
Text = [i for i in Text if i != ('' or ' ')]

# отделяем вопросы
pattern = r'^\d{1,3}\.'  # строка начинается с 1 или 2 цыфр, а затем идёт точка (ограничение на 999 вопросов!!!)
Text_q = [i for i in Text if len(re.findall(pattern, i)) != 0]
print('Всего вопросов:', len(Text_q))

# отделяем ответы
pattern = r'^.\)'  # строка начинается с одного любого символа, а затем идёт скобка
Text_a = [i for i in Text if len(re.findall(pattern, i)) != 0]
print('Всего ответов:', len(Text_a))

# создаем список с ответами без "+" и массив с метками
pattern = r'\+'  # ищем строки с меткой +
Text_a_last = []
flags = np.zeros(100)

for i, st in enumerate(Text_a):
    if len(re.findall(pattern, st)) != 0:  # если в строке найдены метки
        new_i = re.sub(r'\+', '', st)  # удаляем ВСЕ метки
        Text_a_last.append(new_i)
        flags[i] = 1
    else:
        Text_a_last.append(st)

Text_a = Text_a_last
print('Кол-во верных ответов:', flags.sum())


#########################
# Блок обработки событий.
#########################

class Block:

    # Инициализация объектов
    def __init__(self, master):

        # счетчик количества вопросов
        self.question_count = 0

        # счетчик количества правильных ответов
        self.true_points = 0

        # Инициализация вопроса и ответов
        self.quest = scrolledtext.ScrolledText(window, width=75, height=5)
        self.quest.insert(tk.INSERT, Text_q[0])

        self.ans = scrolledtext.ScrolledText(window, width=75, height=15)
        self.ans.insert(tk.INSERT,
                        f'''
        {Text_a[0]}

        {Text_a[1]}

        {Text_a[2]}

        {Text_a[3]}

        {Text_a[4]}
        '''
                        )

        # Инициализация боксов выбора ответов
        self.check1 = tk.IntVar()  # в данную переменную записывается состояние box1 (1 или 0)
        self.box1 = Checkbutton(text='1', variable=self.check1, font=('Arial Bold', 12))

        self.check2 = tk.IntVar()
        self.box2 = Checkbutton(text='2', variable=self.check2, font=('Arial Bold', 12))

        self.check3 = tk.IntVar()
        self.box3 = Checkbutton(text='3', variable=self.check3, font=('Arial Bold', 12))

        self.check4 = tk.IntVar()
        self.box4 = Checkbutton(text='4', variable=self.check4, font=('Arial Bold', 12))

        self.check5 = tk.IntVar()
        self.box5 = Checkbutton(text='5', variable=self.check5, font=('Arial Bold', 12))

        # Инициализация лэйблов и кнопок
        self.mark = tk.Label(window, text='Выберите ответы: ', font=('Arial Bold', 12), fg='Green', bg='white')

        self.ButGiveAns = Button(text='Ответить', font=('Arial Bold', 12))  # кнопка перехода в состояние "ПРОВЕРКА"
        self.ButGiveAns['command'] = self.show_res

        self.ButNext = Button(text='Следующий', font=('Arial Bold', 12))  # кнопка перехода в состояние "СМЕНА ВОПРОСА"
        self.ButNext['command'] = self.next_q

        # Позиционирование виджитов
        self.quest.place(x=50, y=25)
        self.ans.place(x=50, y=150)

        self.box1.place(x=220, y=420)
        self.box2.place(x=270, y=420)
        self.box3.place(x=320, y=420)
        self.box4.place(x=370, y=420)
        self.box5.place(x=420, y=420)

        self.mark.place(x=50, y=420)
        self.ButGiveAns.place(x=480, y=420)
        self.ButNext.place(x=580, y=420)

    # Функция обработки события "ПРОВЕРКА" (нажатие кнопки "Ответить")
    def show_res(self):

        # создаем вектор таргетов и ответов
        targets = flags[5 * self.question_count: 5 * self.question_count + 5]
        answers = np.zeros(5)

        answers[0] = self.check1.get()  # записываем состояние box1 (0 или 1) в нулевой бит вектора answers
        answers[1] = self.check2.get()
        answers[2] = self.check3.get()
        answers[3] = self.check4.get()
        answers[4] = self.check5.get()

        # подсвечиваем истинно верные ответы зелёным цветом (задний фон чекбоксов)
        for i, box in enumerate([self.box1, self.box2, self.box3, self.box4, self.box5]):
            if targets[i] == 1:
                box['bg'] = 'green'

        # проверка ответа пользователя (сравнение вектора ответа с вектором таргета)
        if (targets == answers).sum() == 5:
            self.mark['text'] = 'Всё верно'  # меняем текст метки на статус "Всё верно"
            self.true_points += 1  # исли всё верно, то накидываем очко
        else:
            self.mark['text'] = 'Есть ошибки'

            # Функция обработки события "СМЕНА ВОПРОСА" (нажатие кнопки "Следующий")

    def next_q(self):

        # инкрементируем счётчик вопросов
        self.question_count += 1

        # когда ответили на все вопросы -> подводим итоги
        if self.question_count >= len(Text_q):
            self.FinalScore = tk.Label(window, text=f'Всего правильных ответов: {self.true_points}',
                                       font=('Arial Bold', 15), fg='white', bg='grey')
            self.FinalScore.place(x=360, y=210)

        else:  # в остальных же случаях:

            # удаляем подсветку чекбоксов
            for i, box in enumerate([self.box1, self.box2, self.box3, self.box4, self.box5]):
                box['bg'] = 'white'
                box.deselect()

            # смена вопроса
            self.quest.delete('1.0', 'end')  # очищаем всё поле с индекса "1" до последнего "end"
            self.quest.insert(tk.INSERT, Text_q[self.question_count])  # выводим следующий вопрос

            # смена ответов
            self.ans.delete('1.0', 'end')
            self.ans.insert(tk.INSERT,
                            f'''
            {Text_a[5 * self.question_count + 0]}

            {Text_a[5 * self.question_count + 1]}

            {Text_a[5 * self.question_count + 2]}

            {Text_a[5 * self.question_count + 3]}

            {Text_a[5 * self.question_count + 4]}
            '''
                            )

            # изменяем статус метки
            self.mark['text'] = 'Выберите ответы: '


#################
# Основной цыкл.
#################

window = tk.Tk()
window.title('Конструктор тестов (VladislavSoren)')
window.resizable(width=False, height=False)
window.geometry('720x480')
window['bg'] = 'grey'

first_block = Block(window)

window.mainloop()