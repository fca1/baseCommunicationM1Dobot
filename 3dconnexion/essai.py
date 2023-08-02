import os

path_root = r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\3dconnexion\dll\x64"
os.environ["PATH"] += path_root

import pyspacemouse
import time


def button_0(state, buttons, pressed_buttons):
    print("Button:", pressed_buttons)


def button_0_1(state, buttons, pressed_buttons):
    print("Buttons:", pressed_buttons)


def someButton(state, buttons):
    print("Some button")


def callback():
    button_arr = [
        pyspacemouse.ButtonCallback(0, button_0),
        pyspacemouse.ButtonCallback(
            [1], lambda state, buttons, pressed_buttons: print("Button: 1")
        ),
        pyspacemouse.ButtonCallback([0, 1], button_0_1),
    ]

    success = pyspacemouse.open(
        dof_callback=None, button_callback=someButton, button_callback_arr=button_arr
    )
    if success:
        while True:
            x = pyspacemouse.read()
            print(x.roll, x.pitch)
            time.sleep(0.01)


if __name__ == "__main__":
    callback()
