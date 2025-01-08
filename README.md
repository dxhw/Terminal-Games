# Terminal-Games

This repository includes games played in the terminal using python3.

The programs are:
* typer.py: A speed typing test
* substrings.py: A bomb-party-like [(jklm.fun)](jklm.fun) game where you type words including substrings
* lsat_test.py: An LSAT practice program for the logical reasoning and reading comprehension sections
* minesweeper.py: Minesweeper mimicking most of the functionality of [(minesweeperonline.com)](minesweeperonline.com)

Dataset Sources:
* Typer: [Project Gutenberg](https://www.gutenberg.org/)
* Substrings: https://github.com/dwyl/english-words
* LSAT Practice: https://github.com/zhongwanjun/AR-LSAT

Necessary packages:
* Typer: curses
* Substrings: curses
* LSAT Practice: curses
* Minesweeper: pygame, argparse

All games use match, case keywords, so they require python 3.10 at least

Have fun!

---
<details> <summary style="font-size: 1.5em; font-weight: bold;"> Help! I want to run the LSAT test but am not familiar with git/the terminal (MacOS/Linux instructions):</summary>

### Quick Instructions
Go to detailed instructions below if: this does not work for you/you want to know what this is doing/you are picky about how folders are named/organized on your computer/you are on Linux. 

1. Open your terminal
2. Run `git clone https://github.com/dxhw/Terminal-Games.git`
3. Run `echo 'alias lsat="cd ~/Terminal-Games/LSAT_Test && python3 lsat_test.py"' >> ~/.zshrc`
4. Run `echo 'alias lsat_update=“cd ~/Terminal-Games && git pull“’ >> ~/.zshrc`
5. Close and reopen the terminal
6. Done! Run `lsat` to run the game and `lsat_update` to update the game (e.g. if I have told you I updated it or you want to check if I made an update)

### Detailed Instructions

1. Check that python is properly installed on your machine. 
    * Open your terminal and run `which python3`. You should receive a response like `/Library/Frameworks/Python.framework/Versions/3.10/bin/python3`. Make sure the version number is 3.10 or greater.
    * If there is no result or the version number is not high enough, you will need to download an update to Python (https://www.python.org/downloads/)
2. Download this repository to your computer. 
    * Using the terminal, navigate to the directory (folder) that you want to put this responsitory into (use `cd` and the name of the folder e.g. `cd Desktop`). I suggest just putting it in `~`, AKA `/Users/[YOUR_PROFILE_NAME]` or your home directory, so you'll never have to see it. If you just open your terminal without `cd`ing anywhere, you will be in your home directory.
    * Run `git clone https://github.com/dxhw/Terminal-Games.git` This will download the repository as a folder called `Terminal-Games` into your current directory (you could change this if you want by including a folder name after the URL)
3. Set up an alias to run the LSAT program. So you don't really have to think about the terminal (e.g. navigating to that folder you just downloaded) we're going to make some shortcuts on your machine to automatically start up the program using shell aliases. 
    * Check what shell (the program that is running the terminal) your computer is using. Run `echo "$SHELL"`. You should probably see something like `/bin/zsh` or `/bin/bash`. For the following steps, if this command returned `/bin/bash` replace `/.zshrc` with `/.bashrc` in the following steps. (You probably already knew this because you are probably on Linux or have changed your shell intentionally.)
    * Create an alias to run the practice test. Run `echo 'alias lsat="cd ~/Terminal-Games/LSAT_Test && python3 lsat_test.py"' >> ~/.zshrc`. If you have placed the repository in a different location or renamed the folder, replace `cd ~/Terminal-Games...` with `cd ~/[DIRECTORY_YOU_MOVED_INTO_IN_STEP_2]/[NAME_YOU_GAVE_THE_FOLDER_IN_STEP_2]...`. 
<details>    
<summary style="margin-left: 80px;"> What does this do? </summary>
This alias: 

1. Moves to the `LSAT_Test` directory inside of this repository (this is necessary because of how the question file paths are set up) and 
2. Runs the `lsat_test` program using Python. 

The `echo 'alias [ALIAS_NAME]="[COMMAND]"' >> ~/.zshrc` says "append to my shell configuration file (`/.zshrc` or maybe `/.bashrc`) this alias command so that when I run the alias name, my terminal treats it as the full command"
</details>

4. Create an alias to update the repository. 
    * Run `echo 'alias lsat_update=“cd ~/Terminal-Games && git pull“’ >> ~/.zshrc` (if you have moved the target directory, renamed the cloned folder, or are using a different shell, adjust accordingly)
<details>
<summary style="margin-left: 80px;"> What does this do? </summary>
This alias: 

1. Moves to the `Terminal-Games` directory (the repository folder) and
2. Pulls the latest updates to this repository using `git pull`
</details>

5. Close and reopen the terminal (so that aliases take effect)
6. Done! You can now run the LSAT practice program using `lsat` and update using `lsat_update`.
</details>