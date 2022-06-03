# -*- coding:utf-8 -*-
import pymorphy2
from string import punctuation

morph = pymorphy2.MorphAnalyzer()

forb_words = {"АНАЛ": "####",
              "БЛЯТЬ": "#####",
              "БЛЯДЬ": "#####",
              "БЛЯ": "###",
              "МУДАЧЬЁ": "бакланы",
              "НАХУЙ": "#####",
              "ПИЗДА": "#####",
              "ПИЗДЕЦ": "######",
              "ХУЙ": "###",
              "ХУЙЛО": "#####",
              "ХУЙНЯ": "#####",
              "ХИТРОВЫЕБАННЫЙ": "##############",
              "СУКА": "####",
              "СУЧКА": "#####",
              "ПИЗДАТЫЙ": "крутой",
              "МРАЗЬ": "паршивая",
              "МУДАК": "глупец",
              "ШЛЮХА": "#####",
              "ЁБ": "##",
              "ЕБ": "##",
              "ЕБАТЬ": "#####",
              "ПИДАРАС": "########",
              "ПИДОР": "#####",
              "ЁБАННЫЙ": "#######",
              "ЧМО": "смерд",
              "ЕБАННЫЙ": "#######",
              "ПОЕБАТЬ": "#######",
              "ОДНОХУЙСТВЕННО": "###############",
              "ТРАХАТЬ": "#######",
              "ПОПА": "####",
              "ЖОПА": "####",
              "ОЧКО": "####",
              "ХУЁВЫЙ": "плохой",
              "ЕБАНУТЬСЯ": "####",
              "ЕБАНЬКО": "дурачок",
              "ДЕБИЛ": "глупец",
              "ДЕБИЛОИД": "глупец",
              "ПАДЛА": "подлец",
              "ДУРА":"глупышка",
              "ДУРАК": "глупец",
              "КОНЧЕНЫЙ":"безнадёжный",
              "НЕГОДЯЙ":"негодник",
              "ИДИОТ": "глупец"
              }


def transformator(dict_word, sent_word):  # согласование по падежу
    mot1 = morph.parse(dict_word)[0]  # берем слово из словаря
    mot2 = morph.parse(sent_word)[0]  # берем слово из предложения
    if mot2.tag.POS == 'ADJF':
        mot1 = mot1.inflect({mot2.tag.number, mot2.tag.case, mot2.tag.gender}).word  # преобразуем словарное по основному
    elif mot2.tag.POS == 'NOUN':
        mot1 = mot1.inflect({mot2.tag.number, mot2.tag.case}).word
    return mot1

def without_punct(word):  # дезинфекция от знаков препинания :)
    prcs_word = ''
    for symbol in word:
        if symbol not in punctuation or symbol == '-':
            prcs_word += symbol
    return prcs_word

def if_it_was_capital(com, term, mot, flag):  # проверяем, писалось ли слово с заглавной буквы
    if flag:
        return com + mot.capitalize() + term
    else:
        return com + mot + term

def dist_Lev(a, b):  # Вычисление расстояния Левенштейна между a и b
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]

def test_spelling(parole):  # пытаемся распознать непонятное слово
    for forb_word in forb_words.keys():
        forb_word = forb_word.lower()
        for i in range(len(parole)):
            fragment = parole[i:i+len(parole)]
            if dist_Lev(fragment, forb_word) <= len(forb_word) * 0.3:
                return forb_word
            else:
                return parole

phrase = input("Введите текст для анализа: ").strip().split()
phrase_out = []
bad_words_count = 0

for phr_word in phrase:
    cap = False  # заглавная/строчная - автоматом на строчную
    gob = True  # good or bad - нецензурное слово / обычное, когда что печатать
    s1, s2 = "", ""  # знаки препинания до и после
    if phr_word[0] in punctuation:  # проверка на знаки препинания в начале слова
        s1 = phr_word[0]
    if phr_word[-1] in punctuation:  # проверка на знаки препинания в конце слова
        s2 = phr_word[-1]
    w = without_punct(phr_word)  # очистка от знаков препинания
    if w[0].isupper():  # заглавная или строчная буква
        cap = True
    w = test_spelling(w.lower())  # пытаемся распознать непонятные слова
    # print(w)
    for x in forb_words.keys():  # проходимся по нашему словарю
        init_form = str(morph.parse(w.upper())[0].normal_form)  # берем начальную форму
        form_2 = str(morph.parse(x)[0].normal_form)  # то же самое
        if dist_Lev(init_form, form_2) <= len(form_2) * 0.3:  # Левенштейн
            if '#' not in forb_words[x]:
                x1 = transformator(forb_words[x], w.upper())  # если не мат, то согласуем замену
            else:
                x1 = forb_words[x]  # если мат, то заменяем решётками из словаря
            phrase_out.append(if_it_was_capital(s1, s2, x1, cap))
            bad_words_count += 1
            # print(if_it_was_capital(s1, s2, x1, cap), end=' ')
            gob = False  # слово ненормативное, мы его напечатали сразу выше
            break  # если мы нашли это слово в словаре, больше не нужно по нему проходиться
    if gob:  # если нормативное, то печатаем как оно было
        phrase_out.append(if_it_was_capital(s1, s2, w, cap))
    else:
        gob = True  # иначе изменяем флаг и идём далее
    z = ' '.join(phrase_out)
if bad_words_count != 0:
    print(f"Готово! Вот цензурированный текст: {z}\nЗаменено слов: {bad_words_count}")
else:
    print("Матов не найдено. Всё хорошо!")
