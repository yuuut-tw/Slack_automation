
import time
import pyscreenshot as ImageGrab
import schedule
from datetime import datetime


def take_screenshot():
    print("Taking screenshot...")

    image_name = f"ScreenShot_test"
    screenshot = ImageGrab.grab()
    filepath = rf"D:/temp_area_yu/screenshot/{image_name}.png"
    screenshot.save(filepath)

    print("Screenshot taken...")

    return filepath
