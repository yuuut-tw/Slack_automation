


import time
from optparse import Option
import os
import requests
from dotenv import load_dotenv # 環境變數

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Secret_Jobs():

    def __init__(self):
       pass 
       
    # Selenium
    def terminate_job_with_selenium(url, login_data):

        # credential data
        url = 'xxx'
        credential_path = 'xxx'

        ## get credential data
        load_dotenv(credential_path)
        login_data = {'user':os.environ['web_user'], 'pwd':os.environ['web_pwd']}

        chrome_options = Options()
        chrome_options.add_argument("--headless") ## headless mode: opening without browser
        
        chrome_path = 'D:/yuting_repo/Slack_automation/data/chromedriver'
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


