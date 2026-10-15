import pydirectinput
import customtkinter as ctk
import threading
import keyboard
import time
import win32gui
import win32con
from PIL import ImageGrab

def add_house():
    global houses_claimed
    houses_claimed += 1
    houses_label.configure(text=f"Houses Claimed: ~{houses_claimed}")

def is_black(rgb, tolerance=25):
    r, g, b = rgb
    return r <= tolerance and g <= tolerance and b <= tolerance


def corners_are_black():
    hwnd = get_roblox_window()

    if not hwnd:
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    screenshot = ImageGrab.grab()

    top_right = screenshot.getpixel((right - 70, top + 70))
    bottom_left = screenshot.getpixel((left + 20, bottom - 20))

    return (
        is_black(top_right) and
        is_black(bottom_left)
    )

def release_movement_keys():
    pydirectinput.keyUp('w')
    pydirectinput.keyUp('a')
    pydirectinput.keyUp('s')
    pydirectinput.keyUp('d')

is_recovering = False

macro_thread = None

stop_event = threading.Event()

real_sleep = time.sleep

restart_requested = threading.Event()

restart_recovery = threading.Event()

focus_thread = None

def check_restart():
    if restart_requested.is_set():

        pydirectinput.keyUp('w')
        pydirectinput.keyUp('a')
        pydirectinput.keyUp('s')
        pydirectinput.keyUp('d')

        raise SystemExit

def recovery_macro():
    global is_recovering

    is_recovering = True

    try:
        while True:

            restart_recovery.clear()
            release_movement_keys()

            time.sleep(4)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.press('esc')
            time.sleep(0.5)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.press('r')
            time.sleep(0.5)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.press('enter')
            time.sleep(7)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.keyDown('w')
            time.sleep(2)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.keyDown('d')
            time.sleep(0.4)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.keyUp('d')
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.keyDown('d')
            time.sleep(1.9)
            if restart_recovery.is_set():
                release_movement_keys()
                continue
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            if restart_recovery.is_set():
                release_movement_keys()
                continue

            press_count = 0

            while not corners_are_black():

                pydirectinput.press('s')
                time.sleep(0.25)

                press_count += 1

                if press_count >= 15:
                    release_movement_keys()
                    break

            if restart_recovery.is_set():
                continue

            if corners_are_black():
                time.sleep(5)
                return

    finally:
        is_recovering = False

def get_roblox_window():
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Roblox" in title:
                windows.append(hwnd)

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def focus_guard():
    global macro_thread
    global restart_count
    global houses_claimed

    while not stop_event.is_set():

        hwnd = get_roblox_window()

        if hwnd:

            foreground = win32gui.GetForegroundWindow()

            if foreground != hwnd:

                if is_recovering:

                    restart_recovery.set()

                    try:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                    except:
                        pass

                    real_sleep(0.5)

                    continue

                temphouse = houses_claimed

                restart_requested.set()

                if macro_thread and macro_thread.is_alive():
                    macro_thread.join(timeout=2)

                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                except:
                    pass

                real_sleep(1)

                status_label.configure(
                        text="Status: Resetting",
                        text_color="yellow"
                    )

                recovery_macro()

                restart_count += 1

                restarts_label.configure(text=f"Restarts: {restart_count}")

                restart_requested.clear()

                macro_thread = threading.Thread(
                    target=macro,
                    daemon=True
                )

                status_label.configure(
                        text="Status: Running",
                        text_color="green"
                    )

                houses_claimed = temphouse
                houses_label.configure(text=f"Houses Claimed: ~{houses_claimed}")

                macro_thread.start()

        real_sleep(0.05)

def interruptible_sleep(seconds):
    if stop_event.wait(seconds):
        raise SystemExit

time.sleep = interruptible_sleep

def macro():
    while True:
        try:
            #MainArea
            pydirectinput.keyDown('w')
            time.sleep(0.45)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            pydirectinput.keyDown('d')
            time.sleep(0.5)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('s')
            time.sleep(1.15)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            pydirectinput.keyDown('a')
            time.sleep(0.9)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('d')
            time.sleep(1.2)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            pydirectinput.keyDown('w')
            time.sleep(1)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            check_restart()
        
            #Bridge1
            pydirectinput.keyDown('d')
            time.sleep(0.9)
            pydirectinput.keyDown('w')
            time.sleep(0.06)
            pydirectinput.keyUp('w')
            time.sleep(0.08)
            pydirectinput.keyDown('w')
            time.sleep(0.07)
            pydirectinput.keyUp('w')
            time.sleep(1.55)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            add_house()
            check_restart()
        
            #NeighborHood1
            pydirectinput.keyDown('w')
            time.sleep(0.5)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            pydirectinput.keyDown('d')
            time.sleep(0.35)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('a')
            time.sleep(0.4)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            pydirectinput.keyDown('w')
            time.sleep(0.5)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('s')
            time.sleep(1)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            check_restart()
        
            #ReturnBridge1
            pydirectinput.keyDown('a')
            time.sleep(1.3)
            pydirectinput.keyDown('s')
            time.sleep(0.1)
            pydirectinput.keyUp('s')
            time.sleep(0.07)
            pydirectinput.keyDown('s')
            time.sleep(0.1)
            pydirectinput.keyUp('s')
            time.sleep(1)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            check_restart()
        
            #MainArea Into Shop Area
            pydirectinput.keyDown('s')
            time.sleep(1)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            pydirectinput.keyDown('a')
            time.sleep(0.6)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            pydirectinput.keyDown('s')
            time.sleep(3.05)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            check_restart()
        
            #Shop Area Into Bride3 Towards Neighborhood2
            pydirectinput.keyDown('d')
            time.sleep(3)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            check_restart()
        
            #Neighborhood2
            pydirectinput.keyDown('s')
            time.sleep(0.5)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('w')
            time.sleep(0.3)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            pydirectinput.keyDown('d')
            time.sleep(0.6)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('a')
            time.sleep(0.3)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            pydirectinput.keyDown('w')
            time.sleep(0.6)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('s')
            time.sleep(0.4)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            check_restart()
        
            #Neighborhood2 Back To Shop Area
            pydirectinput.keyDown('a')
            time.sleep(3.47)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            check_restart()
        
            #Shop Area To Neighborhood 3
            pydirectinput.keyDown('s')
            time.sleep(2.85)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            check_restart()
        
            #Neighborhood3
            pydirectinput.keyDown('a')
            time.sleep(0.6)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('d')
            time.sleep(0.3)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            pydirectinput.keyDown('s')
            time.sleep(0.6)
            pydirectinput.keyUp('s')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('w')
            time.sleep(0.2)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            pydirectinput.keyDown('d')
            time.sleep(0.7)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            add_house()
            pydirectinput.keyDown('a')
            time.sleep(0.4)
            pydirectinput.keyUp('a')
            time.sleep(0.25)
            check_restart()
        
            #Return To Main Areaa
            pydirectinput.keyDown('w')
            time.sleep(3.1)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            pydirectinput.keyDown('d')
            time.sleep(0.05)
            pydirectinput.keyUp('d')
            time.sleep(0.25)
            pydirectinput.keyDown('w')
            time.sleep(4.3)
            pydirectinput.keyUp('w')
            time.sleep(0.25)
            pydirectinput.keyDown('a')
            time.sleep(0.6)
            pydirectinput.keyUp('a')
            time.sleep(5)
            check_restart()

            if checkbox.get():
                #Last Island Than Return
                pydirectinput.keyDown('s')
                time.sleep(0.5)
                pydirectinput.keyUp('s')
                time.sleep(0.25)
                pydirectinput.keyDown('a')
                time.sleep(1.85)
                pydirectinput.keyUp('a')
                time.sleep(4)
                pydirectinput.keyDown('w')
                time.sleep(0.05)
                pydirectinput.keyUp('w')
                time.sleep(4)
                pydirectinput.keyDown('d')
                time.sleep(0.9)
                pydirectinput.keyUp('d')
                time.sleep(0.25)
                pydirectinput.keyDown('w')
                time.sleep(0.2)
                pydirectinput.keyUp('w')
                time.sleep(0.25)
                pydirectinput.keyDown('d')
                time.sleep(1.3)
                pydirectinput.keyUp('d')
                time.sleep(0.25)
                pydirectinput.keyDown('w')
                time.sleep(0.45)
                pydirectinput.keyUp('w')
                time.sleep(5)
                check_restart()
            else:
                pydirectinput.keyDown('d')
                pydirectinput.keyDown('w')
                time.sleep(0.2)
                pydirectinput.keyUp('w')
                time.sleep(0.25)
                pydirectinput.keyUp('d')
                time.sleep(5)
                check_restart()
        except SystemExit:
            return


def start():
    global macro_thread
    global focus_thread

    if macro_thread is None or not macro_thread.is_alive():

        stop_event.clear()

        macro_thread = threading.Thread(
            target=macro,
            daemon=True
        )

        focus_thread = threading.Thread(
            target=focus_guard,
            daemon=True
        )

        macro_thread.start()
        focus_thread.start()

        status_label.configure(
            text="Status: Running",
            text_color="lime"
        )


def stop():
    stop_event.set()

    status_label.configure(
        text="Status: Stopped",
        text_color="red"
    )

keyboard.add_hotkey("f1", start)
keyboard.add_hotkey("f2", stop)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Macro")
app.geometry("1000x500")

title_frame = ctk.CTkFrame(
    app,
    corner_radius=15
)

title_frame.pack(
    padx=20,
    pady=(20, 10),
    fill="x"
)

title = ctk.CTkLabel(
    title_frame,
    text="F1 to Start | F2 to Stop",
    font=("Arial", 32, "bold")
)

title.pack(pady=20)

control_frame = ctk.CTkFrame(
    app,
    corner_radius=15
)

control_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)

checkbox = ctk.CTkCheckBox(
    control_frame,
    text=(
        "Toggle for extra alignment thingy that wastes a ton of time "
        "after each run but might make you more straight I think"
    )
)

checkbox.pack(pady=(20, 10))

status_label = ctk.CTkLabel(
    control_frame,
    text="Status: Stopped",
    text_color="red",
    font=("Arial", 18, "bold")
)

status_label.pack(pady=(0, 20))

stats_frame = ctk.CTkFrame(
    app,
    corner_radius=15
)

stats_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)

houses_claimed = 0
restart_count = 0

houses_label = ctk.CTkLabel(
    stats_frame,
    text=f"Houses Claimed: ~{houses_claimed}",
    font=("Arial", 20, "bold")
)

houses_label.pack(pady=(15, 5))

restarts_label = ctk.CTkLabel(
    stats_frame,
    text=f"Restarts: {restart_count}",
    font=("Arial", 20, "bold")
)

restarts_label.pack(pady=(5, 15))

app.mainloop()
