#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import curses
import time
from util import wrapping_text
from math import ceil, floor

LR_QUESTION_NUMBER = 26
RC_PASSAGE_NUMBER = 4
TIME_LIMIT = 20000 # default

# Function to display a question using curses
def display_question_lr(stdscr, question_data, cummulative_time=0, question_number=0, hide_timer=False, num_questions=LR_QUESTION_NUMBER, reveal=False, incorrect=-1, time_taken=None):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
    green_text = curses.color_pair(1)
    red_text = curses.color_pair(2)
    current_row = None
    end = False
    start_time = time.time() - cummulative_time
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
            if not(hide_timer):
                stdscr.addstr(0, 0, f"Time left: {remaining_time:.1f} seconds or {floor(ceil(remaining_time) / 60)} minutes and {ceil(remaining_time) - floor(ceil(remaining_time) / 60) * 60} seconds")
        else:
            if time_taken:
                time_color = green_text if time_taken < 80 else red_text
                stdscr.addstr(0, 0, f"Time taken: {time_taken:.1f} seconds", time_color)

        if reveal and (question_number != None):
            stdscr.addstr(1, 0, f"Question Number: {question_number} / {num_questions}")
        elif question_number != None:
            stdscr.addstr(1, 0, f"Question Number: {question_number}")
        stdscr.addstr(2, 0, "Context:")
        while (c_line_num := wrapping_text(stdscr, 2, context)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (c)")
            except:
                pass
            stdscr.refresh()
            continue

        try:
            stdscr.addstr(c_line_num + 1, 0, "Question:")
        except:
            pass
        
        while (q_line_num := wrapping_text(stdscr, c_line_num + 2, question)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (q)")
            except:
                pass
            stdscr.refresh()
            continue

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
            
            option_row = a_line_num + 1 + 3 * idx
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
    return chosen_option, correct_answer, end, elapsed_time - cummulative_time

def display_questions_rc(stdscr, question_data_list, cummulative_time=0, reveal=False, incorrect_list=None, time_taken=None, hide_timer=False):
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
    start_time = time.time() - cummulative_time
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
            if not(hide_timer):
                stdscr.addstr(0, 0, f"Time left: {remaining_time:.1f} seconds or {floor(ceil(remaining_time) / 60)} minutes and {ceil(remaining_time) - floor(ceil(remaining_time) / 60) * 60} seconds")
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
            stdscr.refresh()
            continue

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
            continue

        while (q_line_num := wrapping_text(stdscr, question_start_line + 2, question)) == -1:
            try:
                stdscr.addstr(0, 0, "Screen too small (q)")
            except:
                pass
            stdscr.refresh()
            continue

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
    return selected_answers, [q_data["label"] for q_data in questions], end, elapsed_time - cummulative_time

def full_review_lr(stdscr, answer_data):
    for i in range(len(answer_data)):
        question_data, incorrect, time_taken = answer_data[i]
        display_question_lr(stdscr, question_data, 0, i + 1, False, len(answer_data), True, incorrect, time_taken)

def full_review_rc(stdscr, answer_data):
    for question_data_list, incorrect_list, time_taken in answer_data:
        display_questions_rc(stdscr, question_data_list, 0, True, incorrect_list, time_taken)

# def full_test(stdscr, questions, LR_section_count, RC_section_count):
#     random.shuffle(questions[0])
#     random.shuffle(questions[1])
#     section_list = (["LR"] * LR_section_count) + (["RC"] * RC_section_count)
#     random.shuffle(section_list)
    

# Main function to run the test
def run_section_non_test(stdscr, questions, test_type, time_limit, hide_timer, is_test=False):
    global TIME_LIMIT 
    TIME_LIMIT = time_limit
    score = 0
    wrong_questions = []
    completed_questions = 0
    completed_passages = 0

    full_review = []
    total_time = 0
    for question_data in questions:
        if is_test:
            full_test_time = total_time
        else:
            full_test_time = 0
        if test_type == "LR":
            selected_answer, correct_answer, escaped, time_taken = display_question_lr(stdscr, question_data, full_test_time, completed_questions + 1, hide_timer)
            if escaped:
                break

            if selected_answer == correct_answer:
                score += 1
            else:
                wrong_questions.append(question_data["id_string"])

            incorrect = selected_answer if selected_answer != correct_answer else None
            completed_questions += 1
            

            full_review.append((question_data, incorrect, time_taken))
            total_time += time_taken

            height, _ = stdscr.getmaxyx()
            wrapping_text(stdscr, height - 3, f"{'Correct!' if selected_answer == correct_answer else 'Wrong!'} Press 'r' to review, 'esc' to end the test, and any other key to continue.")
            stdscr.nodelay(False)
            key = stdscr.getch()
            if key == ord('r'):
                display_question_lr(stdscr, question_data, 0, None, False, None, True, incorrect, time_taken)
            elif key == '\x1b': # escape
                break
        else: # RC mode
            num_correct = 0
            incorrect = []

            if is_test:
                full_test_time = total_time
            else:
                full_test_time = 0

            selected_answers, correct_answers, escaped, time_taken = display_questions_rc(stdscr, question_data, full_test_time, hide_timer=hide_timer)
            if escaped:
                break

            completed_passages += 1

            for selected_answer, correct_answer in zip(selected_answers, correct_answers):
                if selected_answer == correct_answer:
                    incorrect.append(-1)
                    num_correct += 1
                    score += 1
                else:
                    incorrect.append(selected_answer)
                    if question_data["context_id"] not in wrong_questions:
                        wrong_questions.append(question_data["context_id"])
            
            full_review.append((question_data, incorrect, time_taken))
            total_time += time_taken
            completed_questions += len(correct_answers)
            
            if is_test:
                if completed_passages == RC_PASSAGE_NUMBER:
                    break
                stdscr.nodelay(False)
                key = stdscr.getch()
                if key == '\x1b': # escape
                    break
            else:
                height, _ = stdscr.getmaxyx()
                wrapping_text(stdscr, height - 3, f"{num_correct}/{len(correct_answers)} Correct! Press 'r' to review, 'esc' to end the test, and any other key to continue.")
                stdscr.nodelay(False)
                key = stdscr.getch()
                if key == ord('r'):
                    display_questions_rc(stdscr, question_data, 0, True, incorrect, time_taken)
                elif key == '\x1b': # escape
                    break
    while True:
        stdscr.erase()
        stdscr.addstr(0, 0, f"Test completed! Your score: {score}/{completed_questions}. Full time taken {ceil(total_time)} seconds or {floor(ceil(total_time) / 60)} minutes and {ceil(total_time) - floor(ceil(total_time) / 60) * 60} seconds")
        if is_test:
            stdscr.addstr(1, 0, f"Note that the max time is {35 * 60} seconds or 35 minutes.")
        stdscr.addstr(3, 0, "Press 'esc' to exit.")
        stdscr.addstr(4, 0, "Press 'r' for full review")
        stdscr.addstr(5, 0, "Incorrect questions:")
        wrapping_text(stdscr, 6, f"{' '.join(wrong_questions)}")
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('r'):
            if test_type == "LR":
                full_review_lr(stdscr, full_review)
            else:
                full_review_rc(stdscr, full_review)
        elif key == ord('\x1b'):
            break