
import os
import re
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import package.slack_function as sf


def output_validation(df_output):

    hunters = [['XXX', '0988-XXXXXX']]

    for h in hunters:
        name = h[0]
        phone = h[1]
        validate_result = df_output.query(f'name=="{name}" & phone == "{phone}"')

        if len(validate_result):
            return f'Matched! {name} Check your invoice number'
        else:
            return 'Nope'


# information
def main():
    url = 'https://www.yeswater.com.tw/news.php?action=view&id=77&c=12&fbclid=IwAR20fId16YtbCeTl1De1ZBXGqVmP8W1UTso0bwmN_KERzLYi9CpLGPf-DiE' 

    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    target_info = soup.select('table span')
    winner_list = [i.text for i in target_info]

    # dataframe
    groups = len(winner_list) / 4
    raw_data = np.array_split(winner_list, groups)
    df_output = pd.DataFrame(columns=['date', 'name', 'phone', 'invoice_number'], data=raw_data[1:])

    # validation
    result = output_validation(df_output)

    return result


if __name__ == '__main__':

    check_result = main()
    print(check_result)

    # with slack
    env_path = 'D:/yuting_repo/Slack_automation/data/.env'
    load_dotenv(env_path)
    token = os.environ['slack_app_minion_token']
    bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
    slack_bot = sf.SlackBot_YU('#events_result_check', token, bot_icon)
    slack_bot.send_message(check_result, 'Water Lottery')
    