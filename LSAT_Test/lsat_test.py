#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import curses
import json
import random
import time

QUESTION_PATH = "LSAT_DATA/"
LR_PATH = QUESTION_PATH + "all_lr.json"
RC_PATH = QUESTION_PATH + "all_rc.json"

TIME_LIMIT = 20000 #80

# TODO:
# Allow for proper turning off of time limit
# Add time-attack mode (see how many questions you can answer in X amount of time)
# add realistic test mode
# Put correct/incorrect thing on the main page
# Fig bug with scrolling down in menu

# Function to load questions from a JSON file
def load_questions(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
def welcome_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Welcome to the LSAT Practice Game!")
    arr_line = wrapping_text(stdscr, 1, "Use arrow keys to select a mode and press Enter to start.")
    num_line = wrapping_text(stdscr, arr_line, "Or press the number associated with the mode on your keyboard.")
    option_start_line = num_line + 1
    num_options = 4 # increase if adding more options
    stdscr.addstr(option_start_line, 0, "1. Logical Reasoning Mode")
    stdscr.addstr(option_start_line + 1, 0, "2. Reading Comphrension Mode")
    stdscr.addstr(option_start_line + 2, 0, "3. Time Strict Logical Reasoning Mode")
    stdscr.addstr(option_start_line + 3, 0, "4. Time Strict Reading Comphrension Mode")
    #add new options here

    current_row = option_start_line
    chosen_option = -1
    
    while chosen_option == -1:
        for i in range(option_start_line, option_start_line + num_options):
            if i == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(i, 0, stdscr.instr(i, 0).decode('utf-8').strip())
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(i, 0, stdscr.instr(i, 0).decode('utf-8').strip())
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > option_start_line:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < option_start_line + num_options - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            chosen_option = current_row - option_start_line  # return 0 for Original Mode, 1 for Time-based Mode, ...
        elif key == 49: # 1
            chosen_option = 0
        elif key == 50: # 2
            chosen_option = 1
        elif key == 51: # 3
            chosen_option = 2
        elif key == 52: # 2
            chosen_option = 3
        # add here for new options

        stdscr.refresh()
    global TIME_LIMIT
    match chosen_option:
        case 0:
            return "LR"
        case 1:
            return "RC"
        case 2:
            TIME_LIMIT = 80
            return "LR"
        case 3:
            TIME_LIMIT = 480 # 8 minutes
            return "RC"
        
        # add new options here
    
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

# Function to display a question using curses
def display_question_lr(stdscr, question_data, reveal=False, incorrect=-1, time_taken=None):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
    green_text = curses.color_pair(1)
    red_text = curses.color_pair(2)
    current_row = None
    end = False
    start_time = time.time()
    stdscr.nodelay(True) 
    elapsed_time = None

    while True:
        stdscr.erase()
        
        context = question_data["context"]
        question = question_data["question"]
        answers = question_data["answers"]
        correct_answer = question_data["label"]
        if not reveal:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, TIME_LIMIT - elapsed_time)
            if remaining_time == 0:
                chosen_option = None
                break
            stdscr.addstr(0, 0, f"Time left: {remaining_time:.1f} seconds")
        else:
            if time_taken:
                time_color = green_text if time_taken < 80 else red_text
                stdscr.addstr(0, 0, f"Time taken: {time_taken:.1f} seconds", time_color)
        stdscr.addstr(1, 0, "Context:")
        while (c_line_num := wrapping_text(stdscr, 2, context)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (c)")
            except:
                pass
        try:
            stdscr.addstr(c_line_num + 1, 0, "Question:")
        except:
            pass
        
        while (q_line_num := wrapping_text(stdscr, c_line_num + 2, question)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (q)")
            except:
                pass
        
        if q_line_num != -1:
            try:
                stdscr.addstr(q_line_num + 1, 0, "Choose an answer (1-5) using either the number or arrow keys: ")
            except:
                pass

        a_line_num = q_line_num + 1
        num_options = len(answers)
        if not current_row:
            current_row = a_line_num + 1
        
        for idx in range(num_options):
            color_num = 0
            if reveal and idx == correct_answer:
                color_num = 1
            if reveal and idx == incorrect:
                color_num = 2
            
            option_row = a_line_num + 1 + 2 * idx
            option_text = f"{idx + 1}. {answers[idx]}"
            if idx == current_row - (a_line_num + 1):
                stdscr.attron(curses.A_REVERSE)
                if color_num != 0:
                    color_num += 3
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))
                stdscr.attroff(curses.A_REVERSE)
            else:
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))

        if reveal:
            height, _ = stdscr.getmaxyx()
            try:
                stdscr.addstr(height - 1, 0, "Press enter to continue")
            except:
                pass

        stdscr.refresh()
        key = stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            current_row = None
        elif key == curses.KEY_UP and current_row > a_line_num + 1:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < a_line_num + 2 * num_options - 2:
            current_row += 1
        elif key in range(49, 54):
            # 49 = 1
            chosen_option = key - 49
            break
        elif key == ord('\n'):
            chosen_option = (current_row - (a_line_num + 1))
            break
        elif key == ord('\x1b'):
            chosen_option = None
            end = True
            break
    if not elapsed_time:
        elapsed_time = 0
    return chosen_option, correct_answer, end, elapsed_time

def display_questions_rc(stdscr, question_data_list, reveal=False, incorrect_list=None, time_taken=None):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    green_text = curses.color_pair(1)
    red_text = curses.color_pair(2)
    current_row = None
    questions = question_data_list["questions"]
    context = question_data_list["context"]
    selected_answers = [None] * len(questions)
    start_time = time.time()
    stdscr.nodelay(True)
    elapsed_time = None
    end = False

    q_idx = 0
    just_changed = False
    while True:
        stdscr.erase()
        
        if not reveal:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, TIME_LIMIT - elapsed_time)
            if remaining_time == 0:
                break
            stdscr.addstr(0, 0, f"Time left: {remaining_time:.1f} seconds")
        else:
            if time_taken:
                time_color = green_text if time_taken < 480 else red_text
                stdscr.addstr(0, 0, f"Time taken: {time_taken:.1f} seconds", time_color)
        stdscr.addstr(1, 0, "Context:")
        while (c_line_num := wrapping_text(stdscr, 2, context)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (c)")
            except:
                pass
        question_start_line = c_line_num + 1
        num_options = 5

        question_data = questions[q_idx]
        question = question_data["question"]
        answers = question_data["answers"]
        correct_answer = question_data["label"]
        incorrect = incorrect_list[q_idx] if incorrect_list else None

        try:
            stdscr.addstr(question_start_line + 1, 0, f"Question {q_idx + 1}:")
            reveal_x = 12
            if q_idx + 1 == len(questions):
                stdscr.addstr(question_start_line + 1, 12, "Last Question", red_text)
                reveal_x = 27
            if reveal:
                stdscr.addstr(question_start_line + 1, reveal_x, f"{'Incorrect' if incorrect != -1 else 'Correct!'}", red_text if incorrect != -1 else green_text)
        except:
            pass

        while (q_line_num := wrapping_text(stdscr, question_start_line + 2, question)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (q)")
            except:
                pass

        if q_line_num != -1:
            try:
                stdscr.addstr(q_line_num + 1, 0, "Choose an answer (use UP/DOWN arrow keys and Enter to select): ")
            except:
                pass

        a_line_num = q_line_num + 1
        if current_row is None:
            if just_changed and selected_answers[q_idx]:
                current_row = a_line_num + selected_answers[q_idx] + 1
                just_changed = False
            else: 
                current_row = a_line_num + 1

        for idx in range(num_options):
            color_num = 0
            if idx == selected_answers[q_idx]:
                color_num = 3
            if reveal and idx == correct_answer:
                color_num = 1
            if reveal and idx == incorrect:
                color_num = 2
            
            option_row = a_line_num + 1 + 2 * idx
            option_text = f"{idx + 1}. {answers[idx]}"
            if idx == current_row - (a_line_num + 1):
                stdscr.attron(curses.A_REVERSE)
                if color_num != 0:
                    color_num += 3
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))
                stdscr.attroff(curses.A_REVERSE)
            else:
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))

        if reveal:
            height, _ = stdscr.getmaxyx()
            try:
                stdscr.addstr(height - 1, 0, f"Press enter to continue, {sum(x == -1 for x in incorrect_list)}/{len(questions)} Correct")
            except:
                pass

        stdscr.refresh()
        key = stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            current_row = None
        elif key == curses.KEY_UP and current_row > a_line_num + 1:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < a_line_num + 2 * num_options - 2: #something is wrong here
            current_row += 1
        elif key == curses.KEY_LEFT and q_idx > 0:
            just_changed = True
            current_row = None
            q_idx -= 1
        elif key == curses.KEY_RIGHT and q_idx < len(questions) - 1:
            just_changed = True
            current_row = None
            q_idx += 1
        elif key in range(49, 54):
            # 49 = 1
            selected_answers[q_idx] = key - 49
            just_changed = True
            current_row = None
            if q_idx != len(questions) - 1:
                q_idx += 1
        elif key == ord('\n'):
            selected_answers[q_idx] = (current_row - (a_line_num + 1))
            just_changed = True
            current_row = None
            if all(answer is not None for answer in selected_answers):
                break
            if reveal and q_idx == len(questions) - 1:
                break
            if q_idx != len(questions) - 1:
                q_idx += 1
        elif key == ord('\x1b'):
            end = True
            break

    if not elapsed_time:
        elapsed_time = 0
    return selected_answers, [q_data["label"] for q_data in questions], end, elapsed_time

# Main function to run the test
def main(stdscr, questions, test_type):
    random.shuffle(questions)
    score = 0
    wrong_questions = []
    completed_questions = 0

    for question_data in questions:
        if test_type == "LR":
            selected_answer, correct_answer, escaped, time_taken = display_question_lr(stdscr, question_data)
            if escaped:
                break

            if selected_answer == correct_answer:
                score += 1
            else:
                wrong_questions.append(question_data["id_string"])

            height, _ = stdscr.getmaxyx()
            wrapping_text(stdscr, height - 3, f"{'Correct!' if selected_answer == correct_answer else 'Wrong!'} Press 'r' to review, 'esc' to end the test, and any other key to continue.")
            completed_questions += 1
            stdscr.nodelay(False)
            key = stdscr.getch()
            if key == ord('r'):
                incorrect = selected_answer if selected_answer != correct_answer else None
                display_question_lr(stdscr, question_data, True, incorrect, time_taken)
            if key == '\x1b': # escape
                break
        else:
            num_correct = 0
            incorrect = []
            selected_answers, correct_answers, escaped, time_taken = display_questions_rc(stdscr, question_data)
            if escaped:
                break

            for selected_answer, correct_answer in zip(selected_answers, correct_answers):
                if selected_answer == correct_answer:
                    incorrect.append(-1)
                    num_correct += 1
                    score += 1
                else:
                    incorrect.append(selected_answer)
                    if question_data["context_id"] not in wrong_questions:
                        wrong_questions.append(question_data["context_id"])

            height, _ = stdscr.getmaxyx()
            wrapping_text(stdscr, height - 3, f"{num_correct}/{len(correct_answers)} Correct! Press 'r' to review, 'esc' to end the test, and any other key to continue.")
            completed_questions += len(correct_answers)
            stdscr.nodelay(False)
            key = stdscr.getch()
            if key == ord('r'):
                display_questions_rc(stdscr, question_data, True, incorrect, time_taken)
            if key == '\x1b': # escape
                break

    while True:
        stdscr.erase()
        stdscr.addstr(0, 0, f"Test completed! Your score: {score}/{completed_questions}")
        stdscr.addstr(2, 0, "Press 'esc' to exit.")
        stdscr.addstr(3, 0, "Incorrect questions:")
        wrapping_text(stdscr, 4, f"{' '.join(wrong_questions)}")
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('\x1b'):
            break

# Entry point
if __name__ == "__main__":
    try:
        test_type = curses.wrapper(welcome_screen)
        if test_type == "LR":
            questions = load_questions(LR_PATH)
        elif test_type == "RC":
            questions = load_questions(RC_PATH)
        curses.wrapper(main, questions, test_type)
        print("Test exited")
    except KeyboardInterrupt:
        print("Test exited")
