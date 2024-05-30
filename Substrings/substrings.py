#!/Library/Frameworks/Python.framework/Versions/3.10/bin/python3

import curses
import json
import random
import time
import string

LIFE_NUM = 3
TIME_LIMIT = 7
START_GAME = True

# Load word dictionary from JSON file
with open('words_dictionary.json', 'r') as f:
    word_data = json.load(f)
    word_list = list(word_data.keys())
    words = set(word_list)

def get_random_substring():
    length = random.choice([2, 3]) # want either 2 or 3 letters
    word = random.choice(word_list) # get a random word from the word list
    while len(word) <= length: # don't want a word that is 2 or 3 letters long
        word = random.choice(word_list)
    start_index = random.randint(0, len(word) - length)
    return word[start_index : start_index + length] # get a random 2-3 characters from the word

def welcome_screen(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Welcome to the Substring Game!")
    arr_line = wrapping_text(stdscr, "Use arrow keys to select a mode and press Enter to start.", 1)
    num_line = wrapping_text(stdscr, "Or press the number associated with the mode on your keyboard.", arr_line + 1)
    option_start_line = num_line + 2
    num_options = 4 # increase if adding more options
    stdscr.addstr(option_start_line, 0, "1. Original Mode")
    stdscr.addstr(option_start_line + 1, 0, "2. Time-based Mode")
    stdscr.addstr(option_start_line + 2, 0, "3. Time-based Hard Mode")
    stdscr.addstr(option_start_line + 3, 0, "4. How to Play?")
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
        elif key == 52: # 4
            chosen_option = 3
        # add here for new options

        stdscr.refresh()
    global TIME_LIMIT
    match chosen_option:
        case 0:
            return 0
        case 1:
            TIME_LIMIT = 7
            return 1
        case 2:
            TIME_LIMIT = 3
            return 1 
        case 3:
            return 2
        # add new options here

def help_screen(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    green_text = curses.color_pair(1)
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Instructions:")
        line_1 = wrapping_text(stdscr, "After selecting one of the other options you will see a screen with a prompt like:", 1)
        line_2 = wrapping_text(stdscr, "Type a word containing: el", line_1 + 2) if line_1 != -1 else -1
        if line_2 != -1:
            try:
                stdscr.addstr(line_2 + 1, 0, "Your word: ")
            except:
                pass
        line_3 = wrapping_text(stdscr, "Type a word that includes that substring", line_2 + 3) if line_2 != -1 else -1
        if line_3 != -1:
            try:
                stdscr.addstr(line_3 + 1, 0, "For example, 'hello'")
                stdscr.addstr(line_3 + 1, 15, "el", green_text)
            except:
                pass

        line_4 = wrapping_text(stdscr, "Exit the game by pressing 'esc' at any time", line_3 + 3) if line_3 != -1 else -1
        line_5 = wrapping_text(stdscr, """In original mode, hit 'tab' to skip a prompt. You'll lose a life for each invalid inputted word (a word that doesn't match the prompt or is not in the dictionary). If you have already used a word, it will also be invalid. If you correctly answer a prompt or lose all of your lives, you will get a new prompt. In this mode, the game will not end until you press 'esc'""", line_4 + 1) if line_4 != -1 else -1

        line_6 = wrapping_text(stdscr, """In timed mode, 'tab' will not do anything. You will not lose a life for invalid inputs, but you will lose a life when the time runs out. You can regain a life by using every letter in the alphabet in your correct inputs. You'll be able to see the letters you have left to type in a line like the following:""", line_5 + 2) if line_5 != -1 else -1
        letter_dict = {let : False for let in string.ascii_lowercase}
        letter_dict[' '] = True
        if line_6 != -1:
            print_letters(stdscr, letter_dict, line_6 + 1)
            wrapping_text(stdscr, "Have fun! Press any button to leave the help screen", line_6 + 3)

        stdscr.nodelay(False)
        key = stdscr.getch()
        if key not in [curses.KEY_RESIZE, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP]:
            break
        stdscr.refresh()
        stdscr.nodelay(True)

def average_word_length(word_list):
    total_length = sum(len(word) for word in word_list)
    return round(total_length / len(word_list), 3) if len(word_list) > 0 else 0

def find_length_for_line_print(all_text, width) -> int:
    if len(all_text) <= width:
        return 0 # can print everything on one line
    i = width
    while all_text[i] != ' ':
        i -= 1
        if i < 1:
            return -1
    return i + 1

def wrapping_text(stdscr, target, start_y, color=None):
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
    return y_num # returns the last line it prints on

def original_mode(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    green_text = curses.color_pair(1)
    red_text = curses.color_pair(2)
    default_text = curses.color_pair(0)
    
    stdscr.nodelay(1)
    stdscr.timeout(100)
    score = 0
    failures = 0
    failed_prompts = []
    prompt = get_random_substring()
    used_words = set()

    while True:
        # Initialize game state
        lives = LIFE_NUM
        valid = ""
        user_input = ""
        end_game = False

        while lives > 0:
            
            stdscr.clear()
            top_line_num = wrapping_text(stdscr, f"Type a word containing: {prompt}", 0)
            line_num = wrapping_text(stdscr, f"Lives: {lives}  Score: {score}  Failed Prompts: {failures}", top_line_num + 1)
            stdscr.addstr(line_num + 1, 0, "Your word: ")

            if valid == "valid":
                stdscr.addstr(line_num + 2, 0, "Nice!", green_text)
            elif valid == "invalid":
                stdscr.addstr(line_num + 2, 0, "Invalid word", red_text)
            elif valid == "used":
                stdscr.addstr(line_num + 2, 0, "Word already used", red_text)
            elif valid == "short":
                stdscr.addstr(line_num + 2, 0, "Your input is too short!", red_text)

            for i, char in enumerate(user_input):
                color = green_text if prompt in user_input else default_text
                try:
                    stdscr.addstr(line_num + 1, 11 + i, char, color)
                except:
                    wrapping_text(stdscr, "Your screen is too small. Please resize it.", line_num + 2, red_text)

            stdscr.refresh()

            try:
                key = stdscr.getkey()
            except curses.error:
                key = None

            if key == '\x1b':  # ESC key to end the game
                end_game = True
                break
            elif key == '\t':  # TAB key to skip prompt
                failures += 1
                failed_prompts.append(prompt)
                prompt = get_random_substring()
                user_input = ""
                lives = LIFE_NUM
                continue
            elif key == "\n":  # Enter key to submit the word
                user_input = user_input.strip()
                if len(user_input) < len(prompt):
                    valid = "short"
                    continue

                if prompt in user_input and user_input in words:
                    if user_input in used_words:
                        lives -= 1
                        valid = "used"
                    else:
                        lives = LIFE_NUM
                        used_words.add(user_input)
                        score += 1
                        valid = "valid"
                        prompt = get_random_substring()
                else:
                    lives -= 1
                    valid = "invalid"
                user_input = ""

            elif key == '\b' or key == "\x7f":  # Backspace key
                user_input = user_input[:-1]
            elif key is not None and key != "KEY_RESIZE":
                user_input += key

        if end_game:
            break
        failed_prompts.append(prompt)
        failures += 1
        stdscr.addstr(line_num + 2, 0, "Failed prompt, new prompt!")
        stdscr.refresh()
        time.sleep(1)
        prompt = get_random_substring()
    
    global START_GAME
    while True:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, "Game Over. Press 'r' to restart or 'esc' to exit!")
            stdscr.addstr(1, 0, f"Your final score is: {score}; Failed prompt number: {failures}")
        except:
            pass
        failed_prompts = ' '.join(failed_prompts)
        line = wrapping_text(stdscr, f"Failed Prompts: {failed_prompts}", 2)
        word_len = average_word_length(used_words)
        stdscr.addstr(line + 1, 0, f"Average used word length is: {word_len}")
        stdscr.addstr(line + 2, 0, "Used words:")
        wrapping_text(stdscr, ' '.join(used_words), line + 3)
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('r'):
            START_GAME = True
            break
        elif key == 27:
            START_GAME = False
            break
        #print out used words

def print_letters(stdscr, letter_dict, start_y):
    _, width = stdscr.getmaxyx()
    width -= 3
    y_num = start_y
    target = ' '.join(letter_dict.keys())
    current_print = target
    total_i = 0
    while (b := find_length_for_line_print(current_print, width)) != 0:
        if b == -1:
            return
        for i in range(b):
            if letter_dict[current_print[i]] == False:
                try:
                    stdscr.addstr(y_num, i, current_print[i])
                except:
                    return -1
            total_i += 1
        current_print = current_print[b:]
        y_num += 1
    if current_print != '':
        for i, char in enumerate(current_print):
            if letter_dict[current_print[i]] == False:
                try:
                    stdscr.addstr(y_num, i, char)
                except:
                    return -1
            total_i += 1
    return y_num # returns the last line it prints on


def time_mode(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    green_text = curses.color_pair(1)
    red_text = curses.color_pair(2)
    default_text = curses.color_pair(0)
    
    stdscr.nodelay(1)
    stdscr.timeout(100)
    score = 0
    prompt = get_random_substring()
    used_words = set()
    failures = []

    while True:
        # Initialize game state
        lives = LIFE_NUM
        valid = ""
        original_start = time.time()
        start_time = original_start
        user_input = ""
        letter_dict = {let : False for let in string.ascii_lowercase}
        letter_dict[' '] = True

        while lives > 0:
            elapsed_time = time.time() - start_time
            remaining_time = max(0, TIME_LIMIT - elapsed_time)

            stdscr.clear()
            top_line_num = wrapping_text(stdscr, f"Type a word containing: {prompt}", 0)
            line_num = wrapping_text(stdscr, f"Lives: {lives}  Score: {score}", top_line_num + 1)
            line_num = wrapping_text(stdscr, "Use each letter once to regain a life!", line_num + 1)
            line_num = print_letters(stdscr, letter_dict, line_num + 1)
            stdscr.addstr(line_num + 1, 0, f"Time left: {remaining_time:.1f} seconds")
            stdscr.addstr(line_num + 2, 0, "Your word: ")

            if valid == "valid":
                stdscr.addstr(line_num + 3, 0, "Nice!", green_text)
            elif valid == "invalid":
                stdscr.addstr(line_num + 3, 0, "Invalid word", red_text)
            elif valid == "used":
                stdscr.addstr(line_num + 3, 0, "Word already used", red_text)
            elif valid == "out of time":
                stdscr.addstr(line_num + 3, 0, "Out of time! New Prompt", red_text)
            elif valid == "short":
                stdscr.addstr(line_num + 3, 0, "Your input is too short!", red_text)

            for i, char in enumerate(user_input):
                color = green_text if prompt in user_input else default_text
                try:
                    stdscr.addstr(line_num + 2, 11 + i, char, color)
                except:
                    start_time = time.time() #refresh time here to be fair
                    wrapping_text(stdscr, "Your screen is too small. Please resize it.", line_num + 3, red_text)

            stdscr.refresh()
            
            if remaining_time == 0:
                failures.append(prompt)
                lives -= 1
                prompt = get_random_substring()
                start_time = time.time()
                valid = "out of time"
                user_input = ""
                continue

            try:
                key = stdscr.getkey()
            except curses.error:
                key = None

            if key == '\x1b':  # ESC key to end the game
                break
            elif key == '\t':  # TAB key does nothing
                continue
            elif key == "\n":  # Enter key to submit the word
                user_input = user_input.strip()
                if len(user_input) < len(prompt):
                    valid = "short"
                    continue

                if prompt in user_input and user_input in words:
                    if user_input in used_words:
                        valid = "used"
                    else:
                        used_words.add(user_input)
                        for letter in user_input:
                            letter_dict[letter] = True
                        if all(letter_dict.values()):
                            lives += 1
                            letter_dict = {let : False for let in string.ascii_lowercase}
                            letter_dict[' '] = True
                        score += 1
                        valid = "valid"
                        start_time = time.time()
                        prompt = get_random_substring()
                else:
                    valid = "invalid"
                user_input = ""

            elif key == '\b' or key == "\x7f":  # Backspace key
                user_input = user_input[:-1]
            elif key is not None and key != "KEY_RESIZE":
                user_input += key
        end_time = time.time()
        break
    
    global START_GAME
    while True:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, "Game Over. Press 'r' to restart or 'esc' to exit!")
        except:
            pass
        elapsed_time = end_time - original_start
        line = wrapping_text(stdscr, f"Your final score is: {score} and you lasted {elapsed_time:.1f}s", 1)
        word_len = average_word_length(used_words)
        try:
            stdscr.addstr(line  + 1, 0, f"Average used word length is: {word_len}")
        except:
            pass
        failed_prompts = ' '.join(failures)
        line = wrapping_text(stdscr, f"Failed Prompts: {failed_prompts}", line + 2)
        stdscr.addstr(line + 1, 0, "Used Words:")
        wrapping_text(stdscr, ' '.join(used_words), line + 2)
        stdscr.refresh()
        time.sleep(2)
        stdscr.nodelay(False)
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('r'):
            START_GAME = True
            break
        elif key == 27:
            START_GAME = False
            break

            #print out used words

def main(stdscr, mode):
    match mode:
        case 0:
            original_mode(stdscr)
        case 1:
            time_mode(stdscr)
        case 2:
            help_screen(stdscr)

if __name__ == "__main__":
    try: 
        while START_GAME:
            mode = curses.wrapper(welcome_screen)
            curses.wrapper(main, mode)
        print("Game exited")
    except KeyboardInterrupt:
        print("Game exited")
