import curses
import time
from util import wrapping_text, invert_colors, dark_colors
from math import ceil, floor

DEFAULT_TIME_LIMIT = 20000
TIME_LIMIT = 20000 # default
NO_ANSWER_GIVEN = 10
FULL_INTERMISSION_TIME = 60 * 10 # 10 minutes

# Function to display a question using curses
def display_section_questions(stdscr, question_data_list, cummulative_time=0, reveal=False, incorrect_list=None, time_taken=None, hide_timer=False, flagged=None):
    curses.start_color()
    dark_colors()
    dark = True
    green_text = curses.color_pair(1)
    red_text = curses.color_pair(2)
    question_color = curses.color_pair(8)

    current_row = None
    num_questions = len(question_data_list)
    selected_answers = [None] * num_questions
    if not flagged:
        flagged = [False] * num_questions
    decoys = [set() for _ in range(num_questions)] # decoys are not maintained for reviewing

    elapsed_time = None
    saved_paused_time = 0
    pause_start = None
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
            if pause_start:
                paused_time = saved_paused_time + time.time() - pause_start
            else:
                paused_time = saved_paused_time
            elapsed_time = time.time() - start_time - paused_time
            remaining_time = max(0, TIME_LIMIT - elapsed_time)
            if remaining_time == 0:
                break
            if not(hide_timer):
                if TIME_LIMIT == DEFAULT_TIME_LIMIT:
                    elapsed_time = floor(elapsed_time)
                    wrapping_text(stdscr, 0, f"Elapsed time: {elapsed_time} seconds or {floor(elapsed_time / 60)} minutes and {elapsed_time - floor(elapsed_time / 60) * 60} seconds")
                else:
                    remaining_time = ceil(remaining_time)
                    wrapping_text(stdscr, 0, f"Time left: {remaining_time} seconds or {floor(remaining_time / 60)} minutes and {remaining_time - floor(remaining_time / 60) * 60} seconds")
            if pause_start:
                wrapping_text(stdscr, 0, "TIMER PAUSED", red_text, 60)
        else:
            if time_taken:
                time_color = green_text if time_taken < 80 else red_text
                wrapping_text(stdscr, 0, f"Time taken: {time_taken:.1f} seconds", time_color)

        wrapping_text(stdscr, 1, f"Question Number: {question_index + 1} / {num_questions}")
        if question_index + 1 == num_questions:
            wrapping_text(stdscr, 1, "Last Question (Enter to Submit)", red_text, 28)
        
        true_indices = ", ".join(str(index + 1) for index, flag in enumerate(flagged) if flag)
        wrapping_text(stdscr, 2, "flags: " + true_indices)

        wrapping_text(stdscr, 3, "Context:")
        while (c_line_num := wrapping_text(stdscr, 3, context)) == -1:
            wrapping_text(stdscr, 0, "Screen too small (c)", red_text)
            stdscr.refresh()
            continue

        wrapping_text(stdscr, c_line_num + 1, "Question:", question_color)
        
        # bitwise OR attributes together
        while (q_line_num := wrapping_text(stdscr, c_line_num + 2, question, question_color | curses.A_UNDERLINE)) == -1:
            wrapping_text(stdscr, 0, "Screen too small (q)", red_text)
            stdscr.refresh()
            continue

        wrapping_text(stdscr, q_line_num + 1, "Use 1-5 or arrows to choose answer. (f)lag, (x)decoy, (h)ide/unhide timer, (l)ight/dark mode, (p)ause timer")

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
                color_num = 3 # yellow
            if reveal and idx == correct_answer:
                color_num = 1 # green
            if reveal and idx == incorrect:
                color_num = 2 # red
            
            option_row = a_line_num + 1 + 3 * idx
            option_text = f"{idx + 1}. {answers[idx]}"
            if idx == current_row - (a_line_num + 1):
                stdscr.attron(curses.A_REVERSE)
                if color_num != 0:
                    color_num += 3
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))
                stdscr.attroff(curses.A_REVERSE)
            elif idx in decoys[question_index]:
                # dim marked decoys
                stdscr.attron(curses.A_DIM)
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))
                stdscr.attroff(curses.A_DIM)
            else:
                wrapping_text(stdscr, option_row, option_text, curses.color_pair(color_num))

        if reveal:
            if incorrect == NO_ANSWER_GIVEN:
                wrapping_text(stdscr, 0, "NO ANSWER GIVEN", red_text)
            elif incorrect == -1:
                wrapping_text(stdscr, 0, "Correct!", green_text)
            else:
                wrapping_text(stdscr, 0, "Incorrect", red_text)
            height, _ = stdscr.getmaxyx()
            wrapping_text(stdscr, height - 1, f"Press enter to continue, {sum(x == -1 for x in incorrect_list)}/{num_questions} Correct")

        stdscr.refresh()
        key = stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            current_row = None
        elif (key == curses.KEY_UP or key == ord('w')) and current_row > a_line_num + 1:
            current_row -= 1
        elif (key == curses.KEY_DOWN or key == ord('s')) and current_row < a_line_num + 2 * num_options - 2:
            current_row += 1
        elif (key == curses.KEY_LEFT or key == ord('a')) and question_index > 0:
            just_changed = True
            current_row = None
            question_index -= 1
        elif (key == curses.KEY_RIGHT or key == ord('d')) and question_index < num_questions - 1:
            just_changed = True
            current_row = None
            question_index += 1
        elif key in range(49, 54):
            # 49 = 1
            if not reveal:
                selected_answers[question_index] = key - 49
            just_changed = True
            current_row = None
            if question_index != num_questions - 1:
                question_index += 1
        elif key == ord('x'):
            # mark decoys
            chosen_row = current_row - (a_line_num + 1)
            if chosen_row in decoys[question_index]:
                decoys[question_index].remove(chosen_row)
            else:
                decoys[question_index].add(chosen_row)
        elif key == ord("f"):
            # flag or unflag
            flagged[question_index] = not(flagged[question_index])
        # move forward and select answer with either enter or space
        elif key == ord('\n') or key == ord(' '): 
            if not reveal:
                selected_answers[question_index] = (current_row - (a_line_num + 1))
            just_changed = True
            current_row = None
            # submit if all questions answered and "enter" pressed on final question
            # (don't submit with space)
            if all(answer is not None for answer in selected_answers) and key == ord('\n'):
                break
            if reveal and question_index == num_questions - 1:
                break
            if question_index != num_questions - 1:
                question_index += 1
        elif key == ord('\x1b'):
            break
        elif key == ord('h'):
            hide_timer = not(hide_timer)
        elif key == ord('l'):
            invert_colors(dark)
            dark = not(dark)
            stdscr.bkgd(' ', curses.color_pair(7))
        elif key == ord('p'):
            if not pause_start:
                pause_start = time.time()
            else:
                saved_paused_time += time.time() - pause_start
                pause_start = None

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
        wrapping_text(stdscr, 0, "Test completed!")
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
            l = wrapping_text(stdscr, 0, f"Test completed! Your score: {score}/{len(questions)}. Full time taken {ceil(total_time)} seconds or {floor(ceil(total_time) / 60)} minutes and {ceil(total_time) - floor(ceil(total_time) / 60) * 60} seconds")
            l = wrapping_text(stdscr, l, f"Note that the max time is {35 * 60} seconds or 35 minutes.")
            l = wrapping_text(stdscr, l, "Press 'esc' to exit.")
            l = wrapping_text(stdscr, l, "Press 'r' for full review")
            l = wrapping_text(stdscr, l, "Incorrect questions:")
            wrapping_text(stdscr, l, f"{' '.join(wrong_questions)}")
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
            l = wrapping_text(stdscr, 0, f"Section {section_number + 1} completed!")
            display_string = "Press 'n' to move to see final test results" if section_number == 3 else "Press 'n' to move to the next section"
            l = wrapping_text(stdscr, l, display_string)
            l = wrapping_text(stdscr, l, "Press 'r' for section review")
            l = wrapping_text(stdscr, l, "Press 's' to see score and time taken")
            if reveal_score:
                l = wrapping_text(stdscr, l, f"Your score: {score}/{len(questions)}. Full time taken {ceil(total_time)} seconds or {floor(ceil(total_time) / 60)} minutes and {ceil(total_time) - floor(ceil(total_time) / 60) * 60} seconds")
                l = wrapping_text(stdscr, l, f"Note that the max time is {35 * 60} seconds or 35 minutes.")
            if section_number == 1:
                intermission_time_lapsed = time.time() - intermission_start_time
                intermission_time_remaining = ceil(FULL_INTERMISSION_TIME - intermission_time_lapsed)
                intermission_mins, intermission_secs = floor(intermission_time_remaining / 60), intermission_time_remaining - floor(intermission_time_remaining / 60) * 60
                l = wrapping_text(stdscr, l + 2, f"If you are timing the test formally, you may now take a 10 minute intermission.")
                wrapping_text(stdscr, l, f"Remaining time: {intermission_time_remaining} seconds or {intermission_mins} minutes and {intermission_secs} seconds")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('r'):
                section_review(stdscr, full_review, flagged)
            elif key == ord('s'):
                reveal_score = True
            elif key == ord('n'):
                return {"review": full_review, "score": score, "question_number": len(questions), "time": total_time, "incorrect_ids": wrong_questions, "flagged": flagged}
