import requests
import os
api_user = os.environ.get('API_USER')
api_key = os.environ.get('API_KEY')


def send_mail(title, subject, html):
    url = "http://api.sendcloud.net/apiv2/mail/send"

    API_USER = '...'
    API_KEY = '...'

    params = {
        "apiUser": API_USER,  # 使用api_user和api_key进行验证
        "apiKey": API_KEY,
        "to": "",  # 收件人地址, 用正确邮件地址替代, 多个地址用';'分隔
        "from": "",  # 发信人, 用正确邮件地址替代
        "fromName": "server",
        "subject": subject,
        "html": html
    }

    r = requests.post(url, data=params)
    return r.json()
