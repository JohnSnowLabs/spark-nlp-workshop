import json
import logging
import os
import uuid

import config
import requests


class ChatGPTManager:
    parent_message = str(uuid.uuid4())

    @staticmethod
    def ask(msg, token=None):

        headers = {
            "Authorization": f"Bearer {token if token not in ['' , None] else os.getenv('SESSION_TOKEN', '')}",
            "Accept": "text/event-stream",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en,es-ES;q=0.9,es;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://chat.openai.com",
            "Referer": "https://chat.openai.com/chat",
            "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        endpoint = "https://chat.openai.com/backend-api/conversation"

        data = {
                "action": "next",
                "messages": [
                    {
                        "id": str(uuid.uuid4()),
                        "role": "user",
                        "content": {
                             "content_type": "text",
                             "parts": [msg]
                         }
                     }
                ],
                "parent_message_id": "0836c708-8233-4a30-8dd3-e986bde5cc5e",
                "model": "text-davinci-002-render"
        }
        jdata = json.dumps(data)
        res = requests.post(endpoint, data=jdata, headers=headers)
        try:
            answer = "\n".join(json.loads(res.text.split('data: ')[-2])['message']['content']['parts'])
        except Exception as e:
            answer = f"chatGPT returned an error: {e}"
            logging.error(answer)
        return answer


if __name__ == '__main__':
    ChatGPTManager().ask("Generate an example of a 10-K filing")
