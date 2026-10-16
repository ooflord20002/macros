import pydirectinput
import customtkinter as ctk
import threading
import keyboard
import time
import win32gui
import traceback
import win32con
from PIL import ImageGrab
import faulthandler

fault_log = open("crash.log", "w")
faulthandler.enable(fault_log)

def add_house():
    global houses_claimed

    houses_claimed += 1

    app.after(
        0,
        lambda: houses_label.configure(
            text=f"Houses Claimed: ~{houses_claimed}"
        )
    )

def is_black(rgb, tolerance=25):
    r, g, b = rgb
    return r <= tolerance and g <= tolerance and b <= tolerance

def roblox_has_focus():
    hwnd = get_roblox_window()

    if not hwnd:
        return False

    return hwnd == win32gui.GetForegroundWindow()

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

focus_thread = None

houses_claimed = 0
restart_count = 0
runtime_seconds = 0
is_running = False

def check_restart():
    
    if restart_requested.is_set():
        print("restart requested")

        pydirectinput.keyUp('w')
        pydirectinput.keyUp('a')
        pydirectinput.keyUp('s')
        pydirectinput.keyUp('d')

        raise SystemExit

def refocus_roblox():
    hwnd = get_roblox_window()

    if hwnd:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        except:
            pass

    return False

def recovery_check():

    if stop_event.is_set():
        raise SystemExit()

    if not roblox_has_focus():

        release_movement_keys()

        print("Lost focus during recovery")

        refocus_roblox()

        real_sleep(1)

        return True

    return False


def recovery_macro():
    global is_recovering

    is_recovering = True

    try:
        while True:

            if stop_event.is_set():
                    return

            refocus_roblox()

            release_movement_keys()

            real_sleep(4)
            if recovery_check():
                continue
            pydirectinput.press('esc')
            real_sleep(0.5)
            if recovery_check():
                continue
            pydirectinput.press('r')
            real_sleep(0.5)
            if recovery_check():
                continue
            pydirectinput.press('enter')
            real_sleep(7)
            if recovery_check():
                continue
            pydirectinput.keyDown('w')
            real_sleep(2)
            if recovery_check():
                continue
            pydirectinput.keyDown('d')
            real_sleep(0.4)
            if recovery_check():
                continue
            pydirectinput.keyUp('d')
            pydirectinput.keyUp('w')
            real_sleep(0.25)
            if recovery_check():
                continue
            pydirectinput.keyDown('d')
            real_sleep(1.9)
            if recovery_check():
                continue
            pydirectinput.keyUp('d')
            real_sleep(0.25)
            if recovery_check():
                continue

            press_count = 0

            while not corners_are_black():

                if stop_event.is_set():
                    return

                if recovery_check():
                    break

                pydirectinput.press('s')

                real_sleep(0.25)

                press_count += 1

                if press_count >= 15:
                    release_movement_keys()
                    break

            if corners_are_black():
                real_sleep(5)
                return
    except SystemExit:
        print("Recovery stopped")
        return

    except Exception:
        traceback.print_exc()


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

    try:
        while not stop_event.is_set():

            if restart_requested.is_set():

                temphouse = houses_claimed

                app.after(
                    0,
                    lambda: status_label.configure(
                        text="Status: Resetting",
                        text_color="yellow"
                    )
                )

                recovery_macro()

                if stop_event.is_set():
                    return

                restart_count += 1

                app.after(
                    0,
                    lambda: restarts_label.configure(
                        text=f"Restarts: {restart_count}"
                    )
                )

                restart_requested.clear()

                macro_thread = threading.Thread(
                    target=macro,
                    daemon=True
                )

                macro_thread.start()

                continue


            hwnd = get_roblox_window()

            if hwnd:

                foreground = win32gui.GetForegroundWindow()

                if foreground != hwnd:

                    if is_recovering:

                        refocus_roblox()

                        real_sleep(0.5)

                        continue

                    temphouse = houses_claimed

                    restart_requested.set()

                    print("Waiting for macro thread...")
                    if macro_thread and macro_thread.is_alive():
                        macro_thread.join(timeout=2)
                    print("Done waiting")

                    try:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                    except:
                        pass

                    real_sleep(1)

                    app.after(
                        0,
                        lambda: status_label.configure(
                            text="Status: Resetting",
                            text_color="yellow"
                        )
                    )

                    recovery_macro()
                    if stop_event.is_set():
                        return

                    restart_count += 1

                    app.after(
                        0,
                        lambda: restarts_label.configure(
                            text=f"Restarts: {restart_count}"
                        )
                    )

                    restart_requested.clear()

                    macro_thread = threading.Thread(
                        target=macro,
                        daemon=True
                    )

                    app.after(
                        0,
                        lambda: status_label.configure(
                            text="Status: Running",
                            text_color="green"
                        )
                    )

                    houses_claimed = temphouse
                    app.after(
                        0,
                        lambda: houses_label.configure(
                            text=f"Houses Claimed: ~{houses_claimed}"
                        )
                    )

                    macro_thread.start()

            real_sleep(0.05)

    except SystemExit:
        return

    except Exception:
        traceback.print_exc()

def interruptible_sleep(seconds):

    if stop_event.is_set():
        raise SystemExit()

    real_sleep(seconds)

    if stop_event.is_set():
        raise SystemExit()

def require_alignment():

    if not corners_are_black():

        restart_requested.set()

        raise SystemExit()

def macro():
    while True:
        try:
            #MainArea
            pydirectinput.keyDown('w')
            interruptible_sleep(0.45)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('d')
            interruptible_sleep(0.5)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('s')
            interruptible_sleep(1.15)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('a')
            interruptible_sleep(0.95)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('d')
            interruptible_sleep(1.25)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('w')
            interruptible_sleep(1)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            check_restart()
        
            #Bridge1
            pydirectinput.keyDown('d')
            interruptible_sleep(0.9)
            pydirectinput.keyDown('w')
            interruptible_sleep(0.06)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.08)
            pydirectinput.keyDown('w')
            interruptible_sleep(0.07)
            pydirectinput.keyUp('w')
            interruptible_sleep(1.55)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            add_house()
            check_restart()
        
            #NeighborHood1
            pydirectinput.keyDown('w')
            interruptible_sleep(0.5)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('d')
            interruptible_sleep(0.35)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('a')
            interruptible_sleep(0.4)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('w')
            interruptible_sleep(0.5)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('s')
            interruptible_sleep(1)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            check_restart()
        
            #ReturnBridge1
            pydirectinput.keyDown('a')
            interruptible_sleep(1.3)
            pydirectinput.keyDown('s')
            interruptible_sleep(0.1)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.07)
            pydirectinput.keyDown('s')
            interruptible_sleep(0.1)
            pydirectinput.keyUp('s')
            interruptible_sleep(1)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            check_restart()
        
            #MainArea Into Shop Area
            pydirectinput.keyDown('s')
            interruptible_sleep(1)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('a')
            interruptible_sleep(0.6)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('s')
            interruptible_sleep(3.05)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            check_restart()
        
            #Shop Area Into Bride3 Towards Neighborhood2
            pydirectinput.keyDown('d')
            interruptible_sleep(3)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            check_restart()
        
            #Neighborhood2
            pydirectinput.keyDown('s')
            interruptible_sleep(0.5)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('w')
            interruptible_sleep(0.3)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('d')
            interruptible_sleep(0.6)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('a')
            interruptible_sleep(0.3)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('w')
            interruptible_sleep(0.6)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('s')
            interruptible_sleep(0.4)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            check_restart()
        
            #Neighborhood2 Back To Shop Area
            pydirectinput.keyDown('a')
            interruptible_sleep(3.47)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            check_restart()
        
            #Shop Area To Neighborhood 3
            pydirectinput.keyDown('s')
            interruptible_sleep(2.85)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            check_restart()
        
            #Neighborhood3
            pydirectinput.keyDown('a')
            interruptible_sleep(0.6)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('d')
            interruptible_sleep(0.3)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('s')
            interruptible_sleep(0.6)
            pydirectinput.keyUp('s')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('w')
            interruptible_sleep(0.2)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('d')
            interruptible_sleep(0.7)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            add_house()
            pydirectinput.keyDown('a')
            interruptible_sleep(0.4)
            pydirectinput.keyUp('a')
            interruptible_sleep(0.25)
            check_restart()
        
            #Return To Main Areaa
            pydirectinput.keyDown('w')
            interruptible_sleep(3.1)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('d')
            interruptible_sleep(0.05)
            pydirectinput.keyUp('d')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('w')
            interruptible_sleep(4.3)
            pydirectinput.keyUp('w')
            interruptible_sleep(0.25)
            pydirectinput.keyDown('a')
            interruptible_sleep(0.6)
            pydirectinput.keyUp('a')
            interruptible_sleep(1.3)
            require_alignment()
            interruptible_sleep(3.7)
            check_restart()

            if checkbox.get():
                #Last Island Than Return
                pydirectinput.keyDown('s')
                interruptible_sleep(0.5)
                pydirectinput.keyUp('s')
                interruptible_sleep(0.25)
                pydirectinput.keyDown('a')
                interruptible_sleep(1.85)
                pydirectinput.keyUp('a')
                interruptible_sleep(4)
                pydirectinput.keyDown('w')
                interruptible_sleep(0.05)
                pydirectinput.keyUp('w')
                interruptible_sleep(4)
                pydirectinput.keyDown('d')
                interruptible_sleep(0.9)
                pydirectinput.keyUp('d')
                interruptible_sleep(0.25)
                pydirectinput.keyDown('w')
                interruptible_sleep(0.2)
                pydirectinput.keyUp('w')
                interruptible_sleep(0.25)
                pydirectinput.keyDown('d')
                interruptible_sleep(1.3)
                pydirectinput.keyUp('d')
                interruptible_sleep(0.25)
                pydirectinput.keyDown('w')
                interruptible_sleep(0.45)
                pydirectinput.keyUp('w')
                interruptible_sleep(1.3)
                require_alignment()
                interruptible_sleep(3.7)
                check_restart()
            else:
                pydirectinput.keyDown('d')
                pydirectinput.keyDown('w')
                interruptible_sleep(0.2)
                pydirectinput.keyUp('w')
                interruptible_sleep(0.25)
                pydirectinput.keyUp('d')
                interruptible_sleep(5)
                check_restart()
        except SystemExit:
            print("SystemExit caught")
            return

        except Exception:
            traceback.print_exc()
            return

def update_runtime():
    global runtime_seconds

    if is_running:

        runtime_seconds += 1

        hours = runtime_seconds // 3600
        minutes = (runtime_seconds % 3600) // 60
        seconds = runtime_seconds % 60

        runtime_label.configure(
            text=f"Runtime: {hours:02}:{minutes:02}:{seconds:02}"
        )

    app.after(1000, update_runtime)

def start():
    global macro_thread
    global focus_thread
    global is_running

    is_running = True

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

    global is_running

    is_running = False

    stop_event.set()

    restart_requested.clear()

    release_movement_keys()

    global is_recovering
    is_recovering = False

    app.after(
        0,
        lambda: status_label.configure(
            text="Status: Stopped",
            text_color="red"
        )
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

runtime_label = ctk.CTkLabel(
    stats_frame,
    text="Runtime: 00:00:00",
    font=("Arial", 20, "bold")
)

runtime_label.pack(pady=(5, 15))

try:
    update_runtime()
    app.mainloop()

except SystemExit:
    print("Main thread caught SystemExit")

except Exception:
    traceback.print_exc()
