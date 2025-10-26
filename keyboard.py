#!/usr/bin/env python3
import os
import evdev
from evdev import InputDevice, ecodes
import subprocess
import sys

SOUND_DIR = "/path/to/sounds"
SOUNDS = {
    'key': os.path.join(SOUND_DIR, 'key.wav'),
    'space': os.path.join(SOUND_DIR, 'space.wav'),
    'backspace': os.path.join(SOUND_DIR, 'backspace.wav'),
    'enter': os.path.join(SOUND_DIR, 'enter.wav')
}

LOG = open('/tmp/keyboard-debug.log', 'w', buffering=1)

def log(msg):
    print(msg, file=LOG, flush=True)
    print(msg, flush=True)

def play_sound(sound_name):
    if sound_name not in SOUNDS:
        log(f"Unknown sound: {sound_name}")
        return
    log(f"Playing: {sound_name}")
    subprocess.Popen(['aplay', '-q', SOUNDS[sound_name]], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)

def find_keyboard():
    log("Scanning devices...")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    log(f"Found {len(devices)} devices")
    
    for device in devices:
        log(f"  Device: {device.name} at {device.path}")
        if "keyboard" in device.name.lower():
            log(f"Selected: {device.name}")
            return device
    
    for device in devices:
        caps = device.capabilities().get(ecodes.EV_KEY, [])
        if ecodes.KEY_A in caps and ecodes.KEY_SPACE in caps:
            log(f"Selected (has keys): {device.name}")
            return device
    
    if devices:
        log(f"Using fallback: {devices[0].name}")
        return devices[0]
    
    log("ERROR: No devices found!")
    return None

def main():
    log("=== KEYBOARD SOUNDS STARTING ===")
    
    device = find_keyboard()
    if not device:
        log("FATAL: No keyboard device!")
        return
    
    log(f"Listening on {device.path}...")
    log("Press keys to test...")
    
    count = 0
    for event in device.read_loop():
        count += 1
        if count % 10 == 0:
            log(f"Events received: {count}")
        
        if event.type == ecodes.EV_KEY:
            key_event = evdev.categorize(event)
            log(f"KEY: {key_event.keycode} state={key_event.keystate}")
            
            if key_event.keystate == 1:
                keycode = key_event.keycode
                if keycode == 'KEY_ENTER':
                    play_sound('enter')
                elif keycode == 'KEY_SPACE':
                    play_sound('space')
                elif keycode == 'KEY_BACKSPACE':
                    play_sound('backspace')
                elif keycode.startswith('KEY_'):
                    play_sound('key')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=LOG)
