"""
This idea is from https://github.com/DougieWougie/MouseJiggler/blob/main/pico/boot.py
Remember this disables identifying as USB and  REPL, to work on more devices. 
More here https://learn.adafruit.com/customizing-usb-devices-in-circuitpython/circuitpy-midi-serial#dont-lock-yourself-out-3096636-14

This would force the board into safemode:
    microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
    microcontroller.reset()
SafeModeReason.PROGRAMMATIC for this vs SafemodeReason.USER for a button press.
When supervisor.runtime.safe_mode_reason == USER, safemode.py is skipped.
So I basically can't choose to turn storage and repl on at will. 
Just make use the reset button for that! Make life easy. 

To preform a soft reset, similar to hitting <CTRL><D> at the REPL prompt, use supervisor.reload().
"""
import storage
import usb_cdc

storage.disable_usb_drive()    # Disable USB Drive
usb_cdc.disable()              # Disable REPL