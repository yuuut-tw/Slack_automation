
import os, sys

import json
import time
from datetime import datetime

from dotenv import load_dotenv # 環境變數
import package.slack_function as sf # slack function from others

from pathlib import Path
import pyscreenshot as ImageGrab # for screenshoting

from imgur_python import Imgur # for uploading pics


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Monitor_Jobs():

    def __init__(self):
        self.credential_path = 'D:/yuting_repo/Slack_automation/data/.env'
        self.chrome_path = 'D:/yuting_repo/Slack_automation/data/chromedriver'
        self.screenshot_dir_path = 'D:/yuting_repo/Slack_automation/data/screenshots/'


    # get enviroment varibles 
    def __get_env_variables(self):
        load_dotenv(self.credential_path)
    

    def screenshot_to_imgur(self, IMGUR_CLIENT):
        '''
        Making screenshot -> uploading imgur -> return image URL
        '''
        screenshot = ImageGrab.grab()
        filepath = self.screenshot_dir_path + 'ScreenShot_test.png'
        screenshot.save(filepath)
        
        print('screent shot job done & saved!')

        image = IMGUR_CLIENT.image_upload(filepath, "desktop_screen_shot", "")
        image_link = image["response"]["data"]["link"]

        return image_link


    def sending_screenshot_to_slack(self):
        
        ## get credential data
        self.__get_env_variables()
        token = os.environ['slack_token']
        
        # Imgur
        IMGUR_CONFIG = {
        "client_id": os.getenv("IMGUR_ID"),
        "client_secret": os.getenv("IMGUR_SECRET"),
        "access_token": os.getenv("IMGUR_ACCESS_TOKEN"),
        "refresh_token": os.getenv("IMGUR_REFRESH_TOKEN")
        }

        IMGUR_CLIENT = Imgur(config=IMGUR_CONFIG)

        ## screent shot job
        image_link = self.screenshot_to_imgur(IMGUR_CLIENT)

        # sending to slack (using another class)
        bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
        slack_bot = sf.SlackBot('#mybot', token, bot_icon)
        slack_bot.send_picture_as_message(image_link) #### Blocks format required!!
    
        print('Screenshot sent!')


    def terminate_web_job(self):
        '''
        Using Selenium
        '''
        ## get credential data
        self.__get_env_variables()
        login_data = {'user':os.environ['web_user'], 'pwd':os.environ['web_pwd']}
        url = os.environ['web_url']

        chrome_options = Options()
        chrome_options.add_argument("--headless") ## headless mode: opening without browser
        
        chrome_path = self.chrome_path
        driver = webdriver.Chrome(chrome_path,
                                  options=chrome_options)
        
        driver.get(url)

        # login     
        driver.find_element('id', "input-6").send_keys(login_data['user'])
        time.sleep(2)
        driver.find_element('id', "input-10").send_keys(login_data['pwd'])
        time.sleep(3)
        driver.find_element('id', 'btnLogin').click() # 登入button
        time.sleep(5)

        ## detect how many unexecution jobs and get the first one
        total_processing_jobs = driver.find_elements(By.CLASS_NAME, 'material-icons')
        target = len(total_processing_jobs)
        driver.find_element('xpath', f'//*[@id="tab-1"]/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{target}]/td[9]/button/span/span').click() # 按掉報錯的job，通常是最後一個

        driver.close()