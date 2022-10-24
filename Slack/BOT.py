
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import json
import time
from datetime import datetime

from dotenv import load_dotenv # 環境變數
import package.slack_function as sf

from pathlib import Path
import pyscreenshot as ImageGrab
import schedule
import slack

# for uploading pics
from imgur_python import Imgur

# screen shot function
import package.screen_shot_function as sc


## Making screenshot -> uploading imgur -> return image URL
def screenshot_to_imgur(IMGUR_CLIENT):
    
    filepath = sc.take_screenshot()
    image = IMGUR_CLIENT.image_upload(filepath, "desktop_screen_shot", "")
    image_link = image["response"]["data"]["link"]

    return image_link


if __name__ == '__main__':


    ## main
    for _ in range(20):
        
        # slack
        env_path = './data/.env'
        load_dotenv(env_path)
        token = os.environ['slack_token']
        # slack_client = slack.WebClient(token)

        # Imgur
        IMGUR_CONFIG = {
        "client_id": os.getenv("IMGUR_ID"),
        "client_secret": os.getenv("IMGUR_SECRET"),
        "access_token": os.getenv("IMGUR_ACCESS_TOKEN"),
        "refresh_token": os.getenv("IMGUR_REFRESH_TOKEN")
        }

        IMGUR_CLIENT = Imgur(config=IMGUR_CONFIG)

        image_link = screenshot_to_imgur(IMGUR_CLIENT)
        
        bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
        slack_bot = sf.SlackBot('#mybot', token, bot_icon)
        
        slack_bot.send_picture_as_message(image_link) #### Blocks format required!!
    
        print('Screenshot sent!')
      
        time.sleep(300)

