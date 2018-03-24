import _thread
import glob
import os
import re
import threading
import time
import tkinter


ROOT = tkinter.Tk()
TEXT = tkinter.StringVar()

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

HORDE_ACTIVE = ''
HORDE_LOCATION = ''


def get_most_recent_file_vermintide():
    list_of_files = glob.glob(os.getenv('APPDATA') + '\Fatshark\Vermintide 2\console_logs\*')
    latest_file = max(list_of_files, key = os.path.getctime)
    return latest_file


def read_file(file_name):
    global TEXT, BOSS1, BOSS2, BOSS3, BOSS1_LOCATION, BOSS2_LOCATION, PRINT
    global BOSS3_LOCATION, BOSS_LOOT, BOSS_LOOT_LOCATION, BOSS_NUMBER, NOTHING
    file = open(file_name, 'r')

    while True:
        time.sleep(0.001)
        line = file.readline()

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
            BOSS_LOOT_LOCATION = line[53:83]

        if BOSS_NUMBER == 3:
            _thread.start_new_thread(update_gui, ())


def update_gui():
    global BOSS_NUMBER, PRINT, NOTHING
    time.sleep(0.01)
    TEXT.set('Event 1 - ' + BOSS1 + BOSS1_LOCATION +
             'Event 2 - ' + BOSS2 + BOSS2_LOCATION +
             'Event 3 - ' + BOSS3 + BOSS3_LOCATION +
             'Loot rat - ' + BOSS_LOOT + BOSS_LOOT_LOCATION)
    BOSS_NUMBER = 0
    NOTHING = 0
    PRINT = True


x_location = 1195
y_location = 450
gui_label = tkinter.Label(ROOT, textvariable = TEXT, font = ('Calibri', '20'), fg = 'black', bg = 'white')
gui_label.master.overrideredirect(True)
gui_label.master.geometry('+' + str(x_location) + '+' + str(y_location))
gui_label.master.lift()
gui_label.master.wm_attributes("-topmost", True)
gui_label.master.wm_attributes("-disabled", True)
gui_label.pack()

if __name__ == '__main__':
    most_recent_log = get_most_recent_file_vermintide()

    read_thread = threading.Thread(target = read_file, args = (most_recent_log,))
    read_thread.start()

    gui_label.mainloop()

    read_thread.join()
