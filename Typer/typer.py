#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import time
import curses
from curses import wrapper
import random
import math
import os

DEFAULT_LENGTH = 1
DEFAULT_CAP = True
BOOK_PATH = "books_for_typer/"
is_custom = False

def random_file(length, cap):
    books = os.listdir(BOOK_PATH)
    with open(BOOK_PATH + random.choice(books), "r", errors='replace') as f:
        lines = f.readlines()
        if len(lines) < 4:
            return random_file(length, cap)
        lines = [line for line in lines if len(line) > 3]
        lines = [line.strip() for line in lines]
        num = random.randint(3, len(lines) - 3)
        chosen_lines = lines[num - length : num + length]
        orig_lines = chosen_lines
        first_char = chosen_lines[0][0]
        i = -1
        check_line = num - length
        while (not first_char.isupper()):
            if i < 0:
                check_line -= 1
                i = len(lines[check_line]) - 1
                if check_line == num - length - 4:
                    break
                chosen_lines[0] = ' ' + chosen_lines[0]
            first_char = lines[check_line][i]
            if first_char != '\n':
                chosen_lines[0] = first_char + chosen_lines[0]
            i -= 1
        if not first_char.isupper():
            chosen_lines = orig_lines
        last_char = chosen_lines[-1][-1]
        i = 0
        check_line = num + length
        if last_char not in {'.', '?', '!'}:
            chosen_lines[-1] += ' '
        while (last_char not in {'.', '?', '!'}):
            if i >= len(lines[check_line]):
                i = 0
                check_line += 1
                if check_line == num + length + 4:
                    break
                chosen_lines[-1] += ' '
                continue
            last_char = lines[check_line][i]
            if last_char != '\n':
                chosen_lines[-1] += last_char
            i += 1
        chosen_lines = " ".join(chosen_lines)
        chosen_lines = chosen_lines.replace("  ", " ")
        if not cap:
            chosen_lines = chosen_lines.lower()
        if chosen_lines[-1] == ' ':
            chosen_lines = chosen_lines[:-1]
        if len(chosen_lines) == 0:
            return random_file(length, cap)
        if chosen_lines[0] == " ":
            chosen_lines = chosen_lines[1:]
        return chosen_lines
    
def load_text(filename, cap=DEFAULT_CAP):
    if filename == "":
        filename = "random"
    if filename == "random":
        return random_file(DEFAULT_LENGTH, DEFAULT_CAP)
    if filename == "random short":
        return random_file(1, cap)
    if filename == "random medium":
        return random_file(2, cap)
    if filename == "random long":
        return random_file(3, cap)
    is_custom = True
    try:
        with open("./" + filename, 'r') as file:
            text = file.read()
            if not cap:
                text = text.lower()
            return text
    except FileNotFoundError:
        print("\nFile not found. Make sure you are in the directory of your file!")
        time.sleep(2)
    return None

def calculate_wpm(start_time, end_time, typed_characters):
    if start_time == end_time:
        return 0
    minutes = (end_time - start_time) / 60
    words = typed_characters / 5
    wpm = words / minutes
    return round(wpm)

def start_screen(stdscr):
    stdscr.erase()
    try:
        stdscr.addstr("Welcome to the typing test")
    except:
        print("\nYour screen is too small!")
        time.sleep(2)
        return
    stdscr.addstr("\nPress any key to begin")
    stdscr.refresh()
    stdscr.getkey()
    return get_file(stdscr)

def get_file(stdscr):
    stdscr.erase()
    file_name = ""
    char = ''
    try:
        stdscr.addstr("Please enter the file you'd like to type\nor type \"random\" if you would like a random text!\n")
    except:
        print("\nYour screen is too small!")
        time.sleep(2)
        return None
    try:
        stdscr.addstr("You can specify the length of your random text with \"random short\",\n\"random medium\", or \"random long\"\n")
    except:
        print("\nYour screen is too small!")
        time.sleep(2)
        return None
    while (char := stdscr.getkey()) != '\n':
        if ord(char) == 27 or ord(char) == 3:
            return None
        stdscr.erase()
        try:
            stdscr.addstr("Please enter the file you'd like to type\nor type \"random\" if you would like a random text!\n")
        except:
            time.sleep(2)
            print("\nYour screen is too small!")
            return None
        try:
            stdscr.addstr("You can specify the length of your random text with \"random short\",\n\"random medium\", or \"random long\"\n")
        except:
            print("\nYour screen is too small!")
            time.sleep(2)
            return None
        if char in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(file_name) > 0:
                file_name = file_name[:-1]
        else: file_name += char
        stdscr.addstr(7, 0, file_name)
    if file_name == "":
        return load_text("")
    stdscr.erase()
    try:
        stdscr.addstr("Would you like capital letters? [[y]/n]\n")
    except:
        print("\nYour screen is too small!")
        time.sleep(2)
        return None
    key = stdscr.getkey()
    if ord(key) == 27 or ord(key) == 3:
        return None
    cap = True if ord(key) == 121 else False
    target_text = load_text(file_name, cap)
    stdscr.erase()

    return target_text

def complex_display(stdscr, target, current, width, wpm=0):
    num_lines_needed = math.ceil(len(target) / width)
    idx = math.ceil(len(target) / num_lines_needed)
    for i in range(num_lines_needed):
        if ((i + 1) * idx) <= len(target):
            stdscr.addstr(i * 2, 0, target[i * idx:(i + 1) * idx])
        else:
            stdscr.addstr(i * 2, 0, target[i * idx:])
    stdscr.addstr((num_lines_needed * 2) + 1, 0, f"WPM: {wpm}")

    for i, char in enumerate(current):
        color = curses.color_pair(2) if i >= len(target) or char != target[i] else curses.color_pair(1)
        row_num = i // idx
        stdscr.addstr((row_num * 2) + 1, i - (row_num * idx), char, color)

def find_length_for_line_print(all_text, width) -> int:
    if len(all_text) <= width:
        return 0
    i = width
    while all_text[i] != ' ':
        i -= 1
        if i < 1:
            return -1
    return i + 1

def complex_display_2(stdscr, target, current, width, wpm=0):
    width -= 3
    y_num = 0
    to_print = target
    while (a := find_length_for_line_print(to_print, width)) != 0:
        if a == -1:
            return
        try:
            stdscr.addstr(y_num, 0, to_print[:a])
        except:
            if not is_custom:
                load_new(stdscr)
            print("\nYour screen is too small!")
            return -1
        to_print = to_print[a:]
        y_num += 2
    if to_print != '':
        try:
            stdscr.addstr(y_num, 0, to_print)
        except:
            print("\nYour screen is too small!")
            return -1

    try: 
        stdscr.addstr((y_num + 5) + 1, 0, f"WPM: {wpm}")
    except:
        print("\nYour screen is too small!")
        return -1

    current_print = current
    y_num = 1
    total_i = 0
    while (b := find_length_for_line_print(current_print, width)) != 0:
        if b == -1:
            return
        for i in range(b):
            color = curses.color_pair(2) if total_i >= len(target) or current_print[i] != target[total_i] else curses.color_pair(1)
            try:
                stdscr.addstr(y_num, i, current_print[i], color)
            except:
                print("\nYour screen is too small!")
                return -1
            total_i += 1
        current_print = current_print[b:]
        y_num += 2
    if current_print != '':
        for i, char in enumerate(current_print):
            color = curses.color_pair(2) if total_i >= len(target) or char != target[total_i] else curses.color_pair(1)
            try:
                stdscr.addstr(y_num, i, char, color)
            except:
                print("\nYour screen is too small!")
                return -1
            total_i += 1


def simple_display(stdscr, target, current, wpm=0):
    stdscr.addstr(target)
    stdscr.addstr(2, 0, f"WPM: {wpm}")

    for i, char in enumerate(current):
        color = curses.color_pair(2) if i >= len(target) or char != target[i] else curses.color_pair(1)
        stdscr.addstr(1, i, char, color)

def display_text(stdscr, target, current, wpm=0):
    _, width = stdscr.getmaxyx()
    if len(target) > width:
        if complex_display_2(stdscr, target, current, width, wpm) == -1:
            return -1
    else:
        simple_display(stdscr, target, current, wpm)

def load_new(stdscr):
    wpm_test(stdscr, load_text("random"))

def wpm_test(stdscr, target):
    current_text = []
    wpm = 0
    start_time = time.time()
    stdscr.nodelay(True)

    while True:
        wpm = calculate_wpm(start_time, time.time(), len(current_text))

        stdscr.erase()
        if display_text(stdscr, target, current_text, wpm) == -1:
            stdscr.nodelay(False)
            return -1
        stdscr.refresh()

        if "".join(current_text) == target:
            stdscr.nodelay(False)
            break

        try:
            key = stdscr.getkey()
        except:
            continue
        if ord(key) == 27 or ord(key) == 3:
            stdscr.nodelay(False)
            break

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(current_text) > 0:
                current_text.pop()
        elif ord(key) == 9:
            stdscr.nodelay(False)
            key = stdscr.getkey()
            if ord(key) == 13 or ord(key) == 10:
                return load_new(stdscr)
            elif ord(key) == 114:
                #restart same texxt
                start_time = time.time()
                current_text = []
                stdscr.nodelay(True)
            else:
                stdscr.nodelay(True)
                if key in ("KEY_BACKSPACE", '\b', "\x7f"):
                    if len(current_text) > 0:
                        current_text.pop()
                else:
                    current_text.append(key)
        else:
            current_text.append(key)
        if len(current_text) > len(target):
            if current_text[-1] == ' ':
                stdscr.nodelay(False)
                break
            if len(current_text) > (len(target) + 5):
                stdscr.nodelay(False)
                break

def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    target = start_screen(stdscr)

    while True:
        if target == None:
            break
        if wpm_test(stdscr, target) == -1:
            print("\nYour screen is too small!")
            time.sleep(2)
            break
        height, _= stdscr.getmaxyx()
        try: 
            stdscr.addstr(height - 2, 0, "You completed the text!")
        except:
            print("\nYour screen is too small!")
            time.sleep(2)
            break
        try:
            stdscr.addstr(height - 1, 0, "Press any key to continue...")
        except:
            print("\nYour screen is too small!")
            time.sleep(2)
            break
        key = stdscr.getkey()
        if ord(key) == 27 or ord(key) == 3:
            break
        target = get_file(stdscr)


if __name__ == "__main__":
    try: 
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("Game exited")