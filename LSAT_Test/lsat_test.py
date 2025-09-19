import curses
from util import load_questions, wrapping_text
from full_test import run_section_test, full_test
from non_test import run_section_non_test

# TODO:
# Allow for proper turning off of time limit, consider hiding timer by default for no time limit modes
# I personally do not like this for the base LR/RC modes, but maybe the test modes?

# Fix bug with scrolling down in menu (not welcome screen, but question options)

# allow for saving and reviewing results (this would be very hard for non test mode
# but relatively easy for tests)
# need to consider how to make this easily accessible to people (do people know where on their
# machine this program is stored? Probably shouldn't arbitrarily store on peoples' desktops etc.)

# Note: full test does not and cannot pull a full set of 4 sections that were offered together
# the data is too old to have the new format (so it would only be 3 sections) and is also
# badly structured for that. I do not believe the sections within a test differ in difficulty, etc.
# so this should not be a problem for practicing purposes

def welcome_screen(stdscr):
    curses.curs_set(0)

    current_row = None
    chosen_option = -1
    hide_timer = False
    
    while chosen_option == -1:
        stdscr.clear()
        wrapping_text(stdscr, 0, "Welcome to the LSAT Practice Game!")
        arr_line = wrapping_text(stdscr, 1, "Use arrow keys to select a mode and press Enter or Space to start. (WASD also supported throughout this program)")
        num_line = wrapping_text(stdscr, arr_line, "Or press the number associated with the mode on your keyboard. (press 'g' for a secret game mode!)")
        option_start_line = num_line + 1
        num_options = 10 # increase if adding more options
        wrapping_text(stdscr, option_start_line, "1. Logical Reasoning Mode")
        wrapping_text(stdscr, option_start_line + 1, "2. Reading Comphrension Mode")
        wrapping_text(stdscr, option_start_line + 2, "3. Time Strict Logical Reasoning Mode (80s per Q)")
        wrapping_text(stdscr, option_start_line + 3, "4. Time Strict Reading Comphrension Mode (8 min per passage)")
        wrapping_text(stdscr, option_start_line + 4, "5. LR Test Mode")
        wrapping_text(stdscr, option_start_line + 5, "6. RC Test Mode")
        wrapping_text(stdscr, option_start_line + 6, "7. No Time Limit LR Test Mode")
        wrapping_text(stdscr, option_start_line + 7, "8. No Time Limit RC Test Mode")
        wrapping_text(stdscr, option_start_line + 8, "9. Full Test Mode")
        wrapping_text(stdscr, option_start_line + 9, "0. No Time Limit Full Test Mode")
        #add new options here
        if not current_row:
            current_row = option_start_line

        wrapping_text(stdscr, stdscr.getmaxyx()[0] - 3, "Hide Timer? (press 'h') " + str(hide_timer) + "  ")
        for i in range(option_start_line, option_start_line + num_options):
            if i == current_row:
                stdscr.attron(curses.A_REVERSE)
                wrapping_text(stdscr, i, stdscr.instr(i, 0).decode('utf-8').strip())
                stdscr.attroff(curses.A_REVERSE)
            else:
                wrapping_text(stdscr, i, stdscr.instr(i, 0).decode('utf-8').strip())
        
        key = stdscr.getch()
        if key == ord('h'):
            hide_timer = not(hide_timer)
        elif (key == curses.KEY_UP or key == ord('w')) and current_row > option_start_line:
            current_row -= 1
        elif (key == curses.KEY_DOWN or key == ord('s')) and current_row < option_start_line + num_options - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key == ord(' ') or key in [10, 13]:
            chosen_option = current_row - option_start_line  # return 0 for Original Mode, 1 for Time-based Mode, ...
        elif key == 49: # 1
            chosen_option = 0
        elif key == 50: # 2
            chosen_option = 1
        elif key == 51: # 3
            chosen_option = 2
        elif key == 52: # 4
            chosen_option = 3
        elif key == 53: #5
            chosen_option = 4
        elif key == 54: #6
            chosen_option = 5
        elif key == 55: #7
            chosen_option = 6
        elif key == 56: #8
            chosen_option = 7
        elif key == 57: #9
            chosen_option = 8
        elif key == 48: #0
            chosen_option = 9
        elif key == ord("g"):
            chosen_option = 100 # secret logic games mode
        # add here for new options

        stdscr.refresh()
    default_time_limit = 20000 #80
    is_test = True
    not_test = False
    options = {
    0: ("LR", not_test, default_time_limit, hide_timer),
    1: ("RC", not_test, default_time_limit, hide_timer),
    2: ("LR", not_test, 80, hide_timer),         # 80 seconds per LR question
    3: ("RC", not_test, 480, hide_timer),        # 8 minutes per RC passage
    4: ("LR", is_test, 35 * 60, hide_timer),     # 35 minutes
    5: ("RC", is_test, 35 * 60, hide_timer),     # 35 minutes
    6: ("LR", is_test, default_time_limit, hide_timer),
    7: ("RC", is_test, default_time_limit, hide_timer),
    8: ("FULL", is_test, 35 * 60, hide_timer),
    9: ("FULL", is_test, default_time_limit, hide_timer),
    100: ("AR", is_test, default_time_limit, hide_timer),
    # add new options here
    }

    return options.get(chosen_option)

# Entry point
if __name__ == "__main__":
    try:
        test_type, is_test, time_limit, hide_timer = curses.wrapper(welcome_screen)
        questions = load_questions(test_type, is_test)
        if test_type == "FULL":
            curses.wrapper(full_test, questions, time_limit, hide_timer)
        elif is_test:
            curses.wrapper(run_section_test, questions, time_limit, hide_timer)
        else:
            curses.wrapper(run_section_non_test, questions, test_type, time_limit, hide_timer)
        print("Test exited")
    except KeyboardInterrupt:
        print("Test exited")
