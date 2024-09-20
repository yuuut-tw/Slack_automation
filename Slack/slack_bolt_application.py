
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import re
import json
import pandas as pd
import requests
from datetime import datetime, timedelta 

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

from jobs.EVA_task import LP_statement_task


## get credential data
credential_path = 'D:/yuting_repo/Slack_automation/data/.env'
load_dotenv(credential_path)
login_data = {'user':os.environ['web_user'], 'pwd':os.environ['web_pwd']}


token_bot_token = os.environ['slack_app_bolt_token']
slack_app_dexter_token = os.environ['slack_app_dexter_token']

app = App(token=token_bot_token)



@app.message(re.compile("Hey", flags=re.I))
def calculate_sum(message, say):

    say(f"I'm here!")


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


### Parsing PDF file (待改善)
@app.message(re.compile("OP_servers=.*\nJCS_servers=.*\nCDET_servers=.*\nEDRT_servers=.*"))
def execute_lp_statement(message, say):
    
    m = message['text']

    meg_split = m.split('\n')
    statements = ['OP_servers', 'JCS_servers', 'CDET_servers', 'EDRT_servers']
    statement_dict = dict()
    for n, statement in enumerate(statements):
        tmp = re.sub(f'{statement}=', '', meg_split[n]).replace("'",'"')
        statement_dict[statement] = json.loads(tmp)

    try:
        nas_path = os.environ['nas_path']
        output_file_path = LP_statement_task(nas_path, statement_dict).main()
        say(f'*Task completed!* :smile: \n *File Path* → `{output_file_path}`')
    
    except:
        say('*Task failed!* :cry:')



def main():
   
    handler = SocketModeHandler(app, slack_app_dexter_token)

    handler.connect()

    time.sleep(1200) ### running for 2 hours

    handler.close()
    

if __name__ == "__main__":

    main()