
import os
import re
import time
import requests
import numpy as np
import pandas as pd
import datetime
from dotenv import load_dotenv
import mysql.connector
import package.slack_function as sf

mt4_db =  {'name': 'mt4_sync', 'host': 'report.vi-data.net', 'port': 3306, 'user': 'risktp', 'pass': 'reader9876'}


def db_connector(client, database):

    con = mysql.connector.connect(
            host=client["host"],
            user=client["user"],
            password=client["pass"],
            database=database.replace('`',''),
            auth_plugin='mysql_native_password'
        )
    cursor = con.cursor(buffered=True)

    sql = f'''
        SELECT max(`REGDATE`) FROM startrader2report.`mt4_users`
        where regdate between '2023-03-30 00:00:00' and '2023-03-30 23:59:59'
    '''
    cursor.execute(sql)
    con.commit()
    row = cursor.fetchall()
    res = pd.DataFrame(row, columns=cursor.column_names)

    return res



def main():

    df_check = db_connector(mt4_db, 'startrader2report')

    return df_check





if __name__ == '__main__':

    
    for _ in range(30):

        check_result = main()
        final = check_result.values[0][0] 
        print(final)

        # with slack
        env_path = 'D:/yuting_repo/Slack_automation/data/.env'
        load_dotenv(env_path)
        token = os.environ['slack_app_minion_token']
        bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
        slack_bot = sf.SlackBot_YU('#events_result_check', token, bot_icon)
        slack_bot.send_message(final, 'startrader sync check')
        
        time.sleep(3600)