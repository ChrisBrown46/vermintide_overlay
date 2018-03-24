import _thread
import glob
import os
import re
import threading
import time
import tkinter

import psutil


# TK Setup
ROOT = tkinter.Tk()

# Bosses variables
PRINT = True
BOSS_NUMBER = 0
NOTHING = 0
BOSS1 = ''
BOSS1_LOCATION = ''
BOSS2 = ''
BOSS2_LOCATION = ''
BOSS3 = ''
BOSS3_LOCATION = ''
BOSS_LOOT = 'No'
BOSS_LOOT_LOCATION = ''
BOSS_TEXT = tkinter.StringVar()
BOSS_TEXT.set('Waiting for new map.')

# Horde variables
HORDE_FIRST_WAVE = False
HORDE_SECOND_WAVE = False
HORDE_THIRD_WAVE = False
HORDE_TEXT = tkinter.StringVar()

# Bosses dialog
x_location = 1536
y_location = 0
bosses_label = tkinter.Label(ROOT, textvariable = BOSS_TEXT, font = ('Calibri', '20'), fg = 'black', bg = 'white')
bosses_label.master.overrideredirect(True)
bosses_label.master.geometry('+' + str(x_location) + '+' + str(y_location))
bosses_label.master.lift()
bosses_label.master.wm_attributes("-topmost", True)
bosses_label.master.wm_attributes("-disabled", True)
bosses_label.pack()

# Horde dialog
x_location = 1536
y_location = 0
horde_label = tkinter.Label(ROOT, textvariable = HORDE_TEXT, font = ('Calibri', '20'), fg = 'black', bg = 'white')
horde_label.master.overrideredirect(True)
horde_label.master.geometry('+' + str(x_location) + '+' + str(y_location))
horde_label.master.lift()
horde_label.master.wm_attributes("-topmost", True)
horde_label.master.wm_attributes("-disabled", True)
horde_label.pack()


def get_most_recent_file_vermintide():
    list_of_files = glob.glob(os.getenv('APPDATA') + '\Fatshark\Vermintide 2\console_logs\*')
    latest_file = max(list_of_files, key = os.path.getctime)
    return latest_file


def wait_for_game_launch():
    while True:
        for process in psutil.process_iter():
            if process.name() == 'vermintide2_dx12.exe':
                time.sleep(5)
                return


def read_file(file_name):
    global BOSS_TEXT, BOSS1, BOSS2, BOSS3, BOSS1_LOCATION, BOSS2_LOCATION, PRINT
    global BOSS3_LOCATION, BOSS_LOOT, BOSS_LOOT_LOCATION, BOSS_NUMBER, NOTHING
    global HORDE_FIRST_WAVE, HORDE_SECOND_WAVE, HORDE_THIRD_WAVE, HORDE_TEXT

    file = open(file_name, 'r')
    while True:
        time.sleep(0.001)
        line = file.readline()
        if line != '':
            print(line)

        # Bosses, Patrols, and Loot Rats Section
        if 'Added boss/special event:' in line and PRINT:
            if '1' in line[30:]:
                BOSS1 = line[67:]
                if 'nothing' in BOSS1:
                    BOSS1 += '\n'
                    BOSS_NUMBER += 1
                    BOSS1_LOCATION = ''
            elif '2' in line[30:]:
                BOSS2 = line[67:]
                if 'nothing' in BOSS2:
                    BOSS2 += '\n'
                    NOTHING = 2
                    BOSS2_LOCATION = ''
            elif '3' in line[30:]:
                BOSS3 = line[67:]
                if 'nothing' in BOSS3:
                    BOSS3 += '\n'
                    NOTHING = 3
                    BOSS3_LOCATION = ''
                PRINT = False

        if 'boss_event' in line and 'Vector3Box' in line:
            matches = re.search(r'Box(\(.*\))\s+boss_event_(\S*)', line)
            BOSS_NUMBER += 1
            if BOSS_NUMBER == 1:
                BOSS1_LOCATION = matches.group(1) + '\n\n'
                BOSS1 = matches.group(2) + '\n'
                if NOTHING == 2:
                    BOSS_NUMBER += 1
                    if NOTHING == 3:
                        BOSS_NUMBER += 1
            elif BOSS_NUMBER == 2:
                BOSS2_LOCATION = matches.group(1) + '\n\n'
                BOSS2 = matches.group(2) + '\n'
                if NOTHING == 3:
                    BOSS_NUMBER += 1
            elif BOSS_NUMBER == 3:
                BOSS3_LOCATION = matches.group(1) + '\n\n'
                BOSS3 = matches.group(2) + '\n'

        if 'rare_event_loot_rat' in line and 'Vector3Box' in line:
            BOSS_LOOT = 'Yes\n'
            matches = re.search(r'(\(.*\))', line)
            BOSS_LOOT_LOCATION = matches.group(1)

        if BOSS_NUMBER == 3:
            _thread.start_new_thread(update_bosses, ())

        # Hordes Section
        if 'Time for new HOOORDE!':
            if 'multi_first_wave' in line:
                HORDE_FIRST_WAVE = True
            elif 'multi_consecutive_wave' in line:
                HORDE_SECOND_WAVE = True
            elif 'multi_last_wave' in line:
                HORDE_THIRD_WAVE = True

        if 'wants to spawn' in line:
            if 'ahead' in line:
                if HORDE_THIRD_WAVE:
                    HORDE_THIRD_WAVE = 'Third horde ahead with '
                elif HORDE_SECOND_WAVE:
                    HORDE_SECOND_WAVE = 'Second horde ahead with '
                elif HORDE_FIRST_WAVE:
                    HORDE_FIRST_WAVE = 'First horde ahead with '
            if 'behind' in line:
                if HORDE_THIRD_WAVE:
                    HORDE_THIRD_WAVE = 'Third horde behind with '
                elif HORDE_SECOND_WAVE:
                    HORDE_SECOND_WAVE = 'Second horde behind with '
                elif HORDE_FIRST_WAVE:
                    HORDE_FIRST_WAVE = 'First horde behind with '

        if 'managed to spawn' in line:
            matches = re.search(r'(\d+)/', line)
            if HORDE_THIRD_WAVE:
                HORDE_THIRD_WAVE += matches.group(1)
                _thread.start_new_thread(update_horde, (3,))
            elif HORDE_SECOND_WAVE:
                HORDE_SECOND_WAVE += matches.group(1)
                _thread.start_new_thread(update_horde, (2,))
            elif HORDE_FIRST_WAVE:
                HORDE_FIRST_WAVE += matches.group(1)
                _thread.start_new_thread(update_horde, (1,))

        if '-> spawning' in line:
            matches = re.search(r'\s(\d+)', line)
            matches = matches.group(1)

            if HORDE_THIRD_WAVE:
                HORDE_THIRD_WAVE += matches
                _thread.start_new_thread(update_horde, (3,))
            elif HORDE_SECOND_WAVE:
                HORDE_SECOND_WAVE += matches
                _thread.start_new_thread(update_horde, (2,))
            elif HORDE_FIRST_WAVE:
                HORDE_FIRST_WAVE += matches
                _thread.start_new_thread(update_horde, (1,))


def update_bosses():
    global BOSS_NUMBER, PRINT, NOTHING
    time.sleep(0.05)
    BOSS_TEXT.set('Event 1 - ' + BOSS1 + BOSS1_LOCATION +
                  'Event 2 - ' + BOSS2 + BOSS2_LOCATION +
                  'Event 3 - ' + BOSS3 + BOSS3_LOCATION +
                  'Loot rat - ' + BOSS_LOOT + BOSS_LOOT_LOCATION)
    BOSS_NUMBER = 0
    NOTHING = 0
    PRINT = True


def update_horde(wave_number):
    global HORDE_TEXT

    if wave_number == 1:
        HORDE_TEXT.set(HORDE_FIRST_WAVE)

    elif wave_number == 2:
        HORDE_TEXT.set(HORDE_TEXT.get() + '\n' + HORDE_SECOND_WAVE)

    elif wave_number == 3:
        HORDE_TEXT.set(HORDE_TEXT.get() + '\n' + HORDE_THIRD_WAVE)
        time.sleep(30)
        HORDE_TEXT.set('')


if __name__ == '__main__':
    wait_for_game_launch()

    most_recent_log = get_most_recent_file_vermintide()

    read_thread = threading.Thread(target = read_file, args = (most_recent_log,))
    read_thread.start()

    horde_label.mainloop()

    read_thread.join()
