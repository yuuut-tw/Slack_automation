
# import related library
from slack import WebClient
from slack.errors import SlackApiError
import json
from datetime import datetime

class SlackBot():

    # payload sample
    payload = {
    "channel": "Data_Team_BOT",
    "blocks": []
  }

    # the constructor of the class. It takes the channel name, slack bot taken, and bot avatar
    # as input parameters.
    def __init__(self, channel, token, bot_icon):
        self.channel = channel
        self.token = token
        self.bot_icon = bot_icon
    
    # set the channel
    def __decide_channel(self):
        self.payload["channel"] = self.channel

    # use the input message to change the payload content. this method will remove previous
    # message to prevent duplicate. 
    def decide_message(self, message):
        m = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        message
                    )
                }
            }
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        self.payload["blocks"].append(m)

    # use input url of picture to change the payload content.
    # this method will remove previous message to prevent duplicate.
    def decide_picture_as_message(self, pic_url):
               
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        accessory = {          
                     
                    "type": "image",
                    "title": {
                        "type":"plain_text",
                        "text":f"Current status{current_time}"},
                    "image_url": f"{pic_url}",
                    "alt_text": "image"
                
                      }
        
        self.payload["blocks"].append(accessory)
        
    # decide slack app's avatar
    def __decide_bot_icon(self, url):
        self.payload["icon_url"] = url

    # craft and return the entire message payload as a dictionary.
    def __get_message_payload(self):
        self.__decide_channel()
        return self.payload

    # use slack api to send message 
    def send_message(self, decide_message):
        slack_web_client = WebClient(self.token)
        self.decide_message(decide_message)
        self.__decide_bot_icon(self.bot_icon)
        message = self.__get_message_payload()
        slack_web_client.chat_postMessage(**message)

    # use slack api to send picture's url as picture message
    def send_picture_as_message(self, decide_picture_as_message):
        slack_web_client = WebClient(self.token) # build connection
        self.__decide_bot_icon(self.bot_icon) # bot icon
        self.decide_picture_as_message(decide_picture_as_message) #　decide which url to send 
        message = self.__get_message_payload() # decide channel
        slack_web_client.chat_postMessage(**message) # posting message!!!

    # determine file location and send as message 
    def send_file(self, file_location):
        slack_web_client = WebClient(self.token)
        try:
            response = slack_web_client.files_upload(
                channels=self.channel,
                file=file_location
            )
            assert response["file"]  # the uploaded file
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")



class SlackBot_YU():

    # payload sample
    payload = {
    "channel": "",
    "blocks": []}

    # the constructor of the class. It takes the channel name, slack bot taken, and bot avatar
    # as input parameters.
    def __init__(self, channel, token, bot_icon):
        self.channel = channel
        self.token = token
        self.bot_icon = bot_icon
    
    # set the channel
    def __decide_channel(self):
        self.payload["channel"] = self.channel

    # use the input message to change the payload content. this method will remove previous
    # message to prevent duplicate. 
    def decide_message(self, message, title):
        m = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@U04F39Q9NQ1> \n *Event* : `{title}` \n *Info* : `{message}`"
                       
                }
            }
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        self.payload["blocks"].append(m)

    # use input url of picture to change the payload content.
    # this method will remove previous message to prevent duplicate.
    def decide_picture_as_message(self, pic_url):
               
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        accessory = {          
                     
                    "type": "image",
                    "title": {
                        "type":"plain_text",
                        "text":f"Current status{current_time}"},
                    "image_url": f"{pic_url}",
                    "alt_text": "image"
                
                      }
        
        self.payload["blocks"].append(accessory)
        
    # decide slack app's avatar
    def __decide_bot_icon(self, url):
        self.payload["icon_url"] = url

    # craft and return the entire message payload as a dictionary.
    def __get_message_payload(self):
        self.__decide_channel()
        return self.payload

    # use slack api to send message 
    def send_message(self, decide_message, title):
        slack_web_client = WebClient(self.token)
        self.decide_message(decide_message, title)
        self.__decide_bot_icon(self.bot_icon)
        message = self.__get_message_payload()
        slack_web_client.chat_postMessage(**message)

    # use slack api to send picture's url as picture message
    def send_picture_as_message(self, decide_picture_as_message):
        slack_web_client = WebClient(self.token) # build connection
        self.__decide_bot_icon(self.bot_icon) # bot icon
        self.decide_picture_as_message(decide_picture_as_message) #　decide which url to send 
        message = self.__get_message_payload() # decide channel
        slack_web_client.chat_postMessage(**message) # posting message!!!

    # determine file location and send as message 
    def send_file(self, file_location):
        slack_web_client = WebClient(self.token)
        try:
            response = slack_web_client.files_upload(
                channels=self.channel,
                file=file_location
            )
            assert response["file"]  # the uploaded file
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")