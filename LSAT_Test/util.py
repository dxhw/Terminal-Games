#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import json
import random

QUESTION_PATH = "LSAT_DATA/"
LR_PATH = QUESTION_PATH + "all_lr.json"
RC_PATH = QUESTION_PATH + "all_rc.json"

##### Utils for loading questions #######
def load_questions(test_type, is_test):
    if test_type == "LR":
        filename = LR_PATH
    else:
        filename = RC_PATH
    with open(filename, 'r') as file:
        questions = json.load(file)
        if is_test:
            questions = get_test_questions(questions, test_type)
        else:
            random.shuffle(questions)
        return questions

# gets the set of questions from an actual test
def get_test_questions(questions, test_type):
    index = random.randint(0, len(questions) - 2)
    if test_type == "LR":
        first_question = index
        while questions[first_question]["id_string"][-2:] != "_1":
            first_question -= 1
        last_question = index
        while questions[last_question]["id_string"][-2:] != "_1":
            last_question += 1
    else:
        first_question = index
        # find first question for first passage
        while questions[first_question]["context_id"][-2:] != "_1":
            first_question -= 1
        # there are always exactly 4 reading passages in the section
        last_question = first_question + 4
    return questions[first_question:last_question]

################

#### Utils for pretty printing ######
def find_length_for_line_print(all_text, width) -> int:
    if len(all_text) <= width:
        return 0 # can print everything on one line
    i = width
    while all_text[i] != ' ':
        i -= 1
        if i < 1:
            return -1
    return i + 1

def wrapping_text(stdscr, start_y, target, color=None):
    _, width = stdscr.getmaxyx()
    width -= 3
    y_num = start_y
    to_print = target
    while (a := find_length_for_line_print(to_print, width)) != 0:
        if a == -1:
            return y_num
        try:
            if color:
                stdscr.addstr(y_num, 0, to_print[:a], color)
            else:
                stdscr.addstr(y_num, 0, to_print[:a])
        except:
            #screen too small
            return -1
        to_print = to_print[a:]
        y_num += 1
    # print remainder on final line
    if to_print != '':
        try:
            if color:
                stdscr.addstr(y_num, 0, to_print, color)
            else:
                stdscr.addstr(y_num, 0, to_print)
        except:
            return -1
    return y_num + 1 # returns the next line to print on
###########
