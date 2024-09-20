
import time
import os
import requests
from dotenv import load_dotenv # 環境變數

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Secret_Jobs():

    def __init__(self):
        self.credential_path = 'D:/yuting_repo/Slack_automation/data/.env'
        self.chrome_path = 'D:/yuting_repo/Slack_automation/data/chromedriver'
        
        
    # get enviroment varibles 
    def __get_env_variables(self):
        load_dotenv(self.credential_path)
    

    # Selenium
    def terminate_job_with_selenium(self):

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


    @staticmethod
    def random_sec():
        sec = randint(3, 10)
        return sec


    # Selenium
    def Punch_Time_Clock(self, mode):

        ## get credential data
        self.__get_env_variables()
        login_data = {'user':os.environ['HR_user'], 'pwd':os.environ['HR_pwd']}
        url = os.environ['HR_url']

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_path = self.chrome_path 
        driver = webdriver.Chrome(chrome_path,
                                  options=chrome_options)
        
        driver.get(url)

        # login     
        driver.find_element('id', "user_username").send_keys(login_data['user'])
        time.sleep(self.random_sec())
        driver.find_element('id', "user_passwd").send_keys(login_data['pwd'])
        time.sleep(self.random_sec())
        driver.find_element('xpath', '//*[@id="s_buttom"]/div').click() # 登入button
        time.sleep(self.random_sec())
        
        if mode == "check-in":
            driver.find_element('xpath', '//*[@id="submit1948070738"]').click() # 上班!
        else:
            driver.find_element('xpath', '//*[@id="submit298093894"]').click() # 下班!

        print('881')

        driver.close()

