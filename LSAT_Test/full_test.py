#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import curses
import time
from util import wrapping_text
from math import ceil, floor

TIME_LIMIT = 20000 # default
NO_ANSWER_GIVEN = 10
FULL_INTERMISSION_TIME = 60 * 10 # 10 minutes

# Function to display a question using curses
def display_section_questions(stdscr, question_data_list, cummulative_time=0, reveal=False, incorrect_list=None, time_taken=None, hide_timer=False, flagged=None):
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
    num_questions = len(question_data_list)
    selected_answers = [None] * num_questions
    if not flagged:
        flagged = [False] * num_questions

    elapsed_time = None
    start_time = time.time() - cummulative_time
    stdscr.nodelay(True) 

    question_index = 0
    just_changed = False

    while True:
        stdscr.erase()
        
        question_data = question_data_list[question_index]
        context = question_data["context"]
        question = question_data["question"]
        answers = question_data["answers"]
        correct_answer = question_data["label"]
        incorrect = incorrect_list[question_index] if incorrect_list else None

        if not reveal:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, TIME_LIMIT - elapsed_time)
            if remaining_time == 0:
                break
            if not(hide_timer):
                stdscr.addstr(0, 0, f"Time left: {remaining_time:.1f} seconds or {floor(ceil(remaining_time) / 60)} minutes and {ceil(remaining_time) - floor(ceil(remaining_time) / 60) * 60} seconds")
        else:
            if time_taken:
                time_color = green_text if time_taken < 80 else red_text
                stdscr.addstr(0, 0, f"Time taken: {time_taken:.1f} seconds", time_color)

        stdscr.addstr(1, 0, f"Question Number: {question_index + 1} / {num_questions}")
        if question_index + 1 == num_questions:
            stdscr.addstr(1, 28, "Last Question", red_text)
        try:
            true_indices = ", ".join(str(index + 1) for index, flag in enumerate(flagged) if flag)
            stdscr.addstr(2, 0, "flags: " + true_indices)
        except:
            pass
        stdscr.addstr(3, 0, "Context:")
        while (c_line_num := wrapping_text(stdscr, 3, context)) == -1:
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
            stdscr.addstr(q_line_num + 1, 0, "Choose an answer (1-5) using either the number or UP/DOWN arrow keys and Enter. Press 'f' to flag/unflag a question: ")
        except:
            pass

        a_line_num = q_line_num + 1
        num_options = len(answers)
        if current_row is None:
            if just_changed and selected_answers[question_index]:
                current_row = a_line_num + selected_answers[question_index] + 1
                just_changed = False
            else:
                current_row = a_line_num + 1
        
        for idx in range(num_options):
            color_num = 0
            if idx == selected_answers[question_index]:
                color_num = 3
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
            if incorrect == NO_ANSWER_GIVEN:
                try:
                    stdscr.addstr(0, 0, "NO ANSWER GIVEN", red_text)
                except:
                    pass
            height, _ = stdscr.getmaxyx()
            try:
                stdscr.addstr(height - 1, 0, f"Press enter to continue, {sum(x == -1 for x in incorrect_list)}/{num_questions} Correct")
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
        elif key == curses.KEY_LEFT and question_index > 0:
            just_changed = True
            current_row = None
            question_index -= 1
        elif key == curses.KEY_RIGHT and question_index < num_questions - 1:
            just_changed = True
            current_row = None
            question_index += 1
        elif key in range(49, 54):
            # 49 = 1
            selected_answers[question_index] = key - 49
            just_changed = True
            current_row = None
            if question_index != num_questions - 1:
                question_index += 1
        elif key == ord("f"):
            # flag or unflag
            flagged[question_index] = not(flagged[question_index])
        elif key == ord('\n'):
            selected_answers[question_index] = (current_row - (a_line_num + 1))
            just_changed = True
            current_row = None
            if all(answer is not None for answer in selected_answers):
                break
            if reveal and question_index == num_questions - 1:
                break
            if question_index != num_questions - 1:
                question_index += 1
        elif key == ord('\x1b'):
            break
    if not elapsed_time:
        elapsed_time = 0
    return selected_answers, elapsed_time - cummulative_time, flagged

def section_review(stdscr, answer_data, flagged):
    for i in range(len(answer_data)):
        question_data, incorrect = answer_data[i]
        display_section_questions(stdscr, question_data, 0, True, incorrect, None, flagged=flagged)

def full_test_review(stdscr, section_results):
    wrong_questions = []
    for section in section_results:
        wrong_questions.extend(section["incorrect_ids"])
    
    while True:
        stdscr.erase()
        stdscr.addstr(0, 0, "Test completed!")
        i = 1

        for section, sec_num in zip(section_results, [1, 2, 3, 4]):
            t = ceil(section["time"])
            score = section["score"]
            q_num = section["question_number"]
            to_print = f"Section {sec_num} Score: {score}/{q_num}. Time taken {t} seconds or {floor(t / 60)} minutes and {t - floor(t / 60) * 60} seconds"
            i = wrapping_text(stdscr, i, to_print)

        i = wrapping_text(stdscr, i, "To review a section, type the number of the section")
        i = wrapping_text(stdscr, i, "To exit the test, press 'esc'")

        i = wrapping_text(stdscr, i + 3, "Incorrect questions:")
        wrapping_text(stdscr, i, f"{' '.join(wrong_questions)}")

        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('1'):
            section_review(stdscr, section_results[0]["review"], section_results[0]["flagged"])
        elif key == ord('2'):
            section_review(stdscr, section_results[1]["review"], section_results[1]["flagged"])
        elif key == ord('3'):
            section_review(stdscr, section_results[2]["review"], section_results[2]["flagged"]) 
        elif key == ord('4'):
            section_review(stdscr, section_results[3]["review"], section_results[3]["flagged"])
        elif key == ord('\x1b'):
            break

# questions is a list of section question lists [sec1, sec2, ...]
def full_test(stdscr, questions, time_limit, hide_timer):
    global TIME_LIMIT
    TIME_LIMIT = time_limit
    section_results = []
    for section, sec_num in zip(questions, range(4)):
        section_results.append(run_section_test(stdscr, section, time_limit, hide_timer, is_full_test=True, section_number=sec_num))
    full_test_review(stdscr, section_results)

# Main function to run the test
def run_section_test(stdscr, questions, time_limit, hide_timer, is_full_test=False, section_number=None):
    global TIME_LIMIT
    TIME_LIMIT = time_limit
    score = 0
    wrong_questions = []
    incorrect = []

    full_review = []
    total_time = 0
    while True:
        full_test_time = total_time
        selected_answers, time_taken, flagged = display_section_questions(stdscr, questions, full_test_time, hide_timer=hide_timer)
        
        for selected, question in zip(selected_answers, questions):
            if selected == None:
                incorrect.append(NO_ANSWER_GIVEN)
                wrong_questions.append(question["id_string"])
                continue

            if selected == question["label"]:
                incorrect.append(-1)
                score += 1
            else:
                incorrect.append(selected)
                wrong_questions.append(question["id_string"])

        full_review.append((questions, incorrect))
        total_time += time_taken
        break

    if not is_full_test:
        while True:
            stdscr.erase()
            stdscr.addstr(0, 0, f"Test completed! Your score: {score}/{len(questions)}. Full time taken {ceil(total_time)} seconds or {floor(ceil(total_time) / 60)} minutes and {ceil(total_time) - floor(ceil(total_time) / 60) * 60} seconds")
            stdscr.addstr(1, 0, f"Note that the max time is {35 * 60} seconds or 35 minutes.")
            stdscr.addstr(3, 0, "Press 'esc' to exit.")
            stdscr.addstr(4, 0, "Press 'r' for full review")
            stdscr.addstr(5, 0, "Incorrect questions:")
            wrapping_text(stdscr, 6, f"{' '.join(wrong_questions)}")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('r'):
                section_review(stdscr, full_review, flagged)
            elif key == ord('\x1b'):
                break
    else:
        reveal_score = False
        intermission_start_time = time.time()
        while True:
            stdscr.erase()
            try:
                stdscr.addstr(0, 0, f"Section {section_number + 1} completed!")
                if section_number == 3:
                    stdscr.addstr(1, 0, "Press 'n' to move to see final test results")
                else:
                    stdscr.addstr(1, 0, "Press 'n' to move to the next section")  
                stdscr.addstr(2, 0, "Press 'r' for section review")
                stdscr.addstr(3, 0, "Press 's' to see score and time taken")
                if reveal_score:
                    stdscr.addstr(4, 0, f"Your score: {score}/{len(questions)}. Full time taken {ceil(total_time)} seconds or {floor(ceil(total_time) / 60)} minutes and {ceil(total_time) - floor(ceil(total_time) / 60) * 60} seconds")
                    stdscr.addstr(5, 0, f"Note that the max time is {35 * 60} seconds or 35 minutes.")
                if section_number == 1:
                    intermission_time_lapsed = time.time() - intermission_start_time
                    intermission_time_remaining = ceil(FULL_INTERMISSION_TIME - intermission_time_lapsed)
                    intermission_mins, intermission_secs = floor(intermission_time_remaining / 60), intermission_time_remaining - floor(intermission_time_remaining / 60) * 60
                    i = wrapping_text(stdscr, 6, f"If you are timing the test formally, you may now take a 10 minute intermission.")
                    wrapping_text(stdscr, i, f"Remaining time: {intermission_time_remaining} seconds or {intermission_mins} minutes and {intermission_secs} seconds")
            except:
                pass
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('r'):
                section_review(stdscr, full_review, flagged)
            elif key == ord('s'):
                reveal_score = True
            elif key == ord('n'):
                return {"review": full_review, "score": score, "question_number": len(questions), "time": total_time, "incorrect_ids": wrong_questions, "flagged": flagged}
