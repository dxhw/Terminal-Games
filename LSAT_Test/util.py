import json
import random
import curses
import pathlib

QUESTION_PATH = pathlib.Path("LSAT_DATA")
LR_PATH = QUESTION_PATH / "all_lr.json"
RC_PATH = QUESTION_PATH / "all_rc.json"
AR_PATH = QUESTION_PATH / "all_ar.json"

##### Utils for loading questions #######
def load_full_test_questions():
    passage_types = ["LR", "LR", "RC", "LR"] # 0 == LR, 1 == RC
    if random.randint(0, 1) == 0:
        passage_types[0] = "RC" # 50% chance to have 2 RC passages
    random.shuffle(passage_types)
    questions = [load_questions(passage_type, True) for passage_type in passage_types]
    if any(not section for section in questions):
        # try again, one of the sections was empty for some reason
        return load_full_test_questions()
    return questions

def load_questions(test_type, is_test):
    if test_type == "FULL":
        return load_full_test_questions()
    elif test_type == "LR":
        filename = LR_PATH
    elif test_type == "AR":
        filename = AR_PATH
    else:
        filename = RC_PATH
    with open(filename, 'r') as file:
        questions = json.load(file)
        if is_test:
            questions = get_test_questions(questions, test_type)
        else:
            random.shuffle(questions)
        return questions
    
# modify the structure of rc questions so that context is included separately with each question
# instead of being at a higher level
# effectively, this makes rc questions formatted the same way that LR questions are
def restructure_rc_questions(data):
    restructured_data = []
    for item in data:
        context = item["context"]
        for question in item["questions"]:
            question_with_context = {
                "context": context,
                **question
            }
            restructured_data.append(question_with_context)
    return restructured_data

# gets the set of questions from an actual test
def get_test_questions(questions, test_type):
    try:
        index = random.randint(0, len(questions) - 2)
        if test_type == "LR" or test_type == "AR":
            first_question = index
            while questions[first_question]["id_string"][-2:] != "_1":
                first_question -= 1
            last_question = first_question + 1
            while questions[last_question]["id_string"][-2:] != "_1":
                last_question += 1
            return questions[first_question:last_question]
        else:
            first_question = index
            # find first question for first passage
            while questions[first_question]["context_id"][-2:] != "_1":
                first_question -= 1
            # there are always exactly 4 reading passages in the section
            last_question = first_question + 4
            return restructure_rc_questions(questions[first_question:last_question])
    except(IndexError):
        # if there's an index error (maybe hit the end of the questions json), just try again
        return get_test_questions(questions, test_type)

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

def wrapping_text(stdscr, start_y, target, color=None, x_offset=0):
    _, width = stdscr.getmaxyx()
    width -= 3
    width -= x_offset
    y_num = start_y
    to_print = target
    while (a := find_length_for_line_print(to_print, width)) != 0:
        if a == -1:
            return y_num
        try:
            if color:
                stdscr.addstr(y_num, x_offset, to_print[:a], color)
            else:
                stdscr.addstr(y_num, x_offset, to_print[:a])
        except:
            #screen too small
            return -1
        to_print = to_print[a:]
        y_num += 1
    # print remainder on final line
    if to_print != '':
        try:
            if color:
                stdscr.addstr(y_num, x_offset, to_print, color)
            else:
                stdscr.addstr(y_num, x_offset, to_print)
        except:
            return -1
    return y_num + 1 # returns the next line to print on
###########

def dark_colors():
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)

def light_colors():
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

def invert_colors(dark: bool):
    if dark:
        light_colors()
    else:
        dark_colors()