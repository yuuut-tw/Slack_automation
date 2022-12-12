
import os
import re
import json
import pandas as pd
import requests


from dotenv import load_dotenv # 環境變數
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from jobs.tool_man_jobs import Secret_Jobs
from jobs.monitor_jobs import Monitor_Jobs

import time
from optparse import Option
import os
import requests
from dotenv import load_dotenv # 環境變數

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# Install the Slack app and get xoxb- token in advance
# slack setting
# credential data


## get credential data
credential_path = 'D:/yuting_repo/Slack_automation/data/.env'
load_dotenv(credential_path)
login_data = {'user':os.environ['web_user'], 'pwd':os.environ['web_pwd']}


token_bot_token = os.environ['slack_app_bolt_token']
slack_app_dexter_token = os.environ['slack_app_dexter_token']

app = App(token=token_bot_token)


@app.message(re.compile("calculate|cal"))
def calculate_sum(message, say):

    m = message['text']
    
    numbers = re.findall('\d+', m)
    numbers_int = [int(d) for d in numbers]
    say(f'total : {sum(numbers_int)}')


### terminate web jos via selenium
@app.message("terminate!")
def terminate_web_job(message, say):
    try:
        Monitor_Jobs().terminate_web_job() 
        say(f'The job has done!')

    except Exception as e:
        say(f'Job filled cuz {e}!')


### clock in / clock out!
@app.message(re.compile("Check-in|Check-out"))
def punch_time_clock(message, say):
    try:
        mode = str.lower(message['text'])
        Secret_Jobs().Punch_Time_Clock(mode) 
        say(f'{mode} job done!')

    except:
        say(f'{message} failed!')


def main():
   
    handler = SocketModeHandler(app, slack_app_dexter_token)
    handler.start()
 

if __name__ == "__main__":
    
    main()

