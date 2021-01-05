import os
import logging

import requests


def post_message(pretext='', title=''):
    slack_url = os.environ.get('SLACK_WEBHOOK', None)
    headers = {"Content-Type": "text/plain"}
    data = {
        "attachments": [
            {
                "fallback": "Required plain-text summary of the attachment.",
                "color": "#ff0000",
                "pretext": pretext,
                "author_name": "From: Sale portal BOT",
                "author_link": "https://sp.vnpay.vn",
                "title": title,
                "fields": [
                    {
                        "title": "Priority",
                        "value": "High",
                        "short": False
                    }
                ]
            }
        ]
    }
    if slack_url:
        try:
            resp: requests.Response = requests.request(method='post', url=slack_url, json=data, headers=headers)
            logging.info(resp.json())
        except Exception as e:
            logging.error(e)
