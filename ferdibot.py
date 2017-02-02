#!/usr/bin/python3

import bottle
import requests
import logging

log = logging.getLogger(__name__)

timeout = 1200

class User:
    def __init__(self, bot, json):
        self.bot = bot
        self.id = json['id']
        self.first_name = json['first_name']
        self.user = json.get('username')

    def __str__(self):
        if self.user is not None:
            return '@' + self.user
        return str(self.id)

class Chat:
    def __init__(self, bot, json):
        self.bot = bot
        self.id = json['id']

class Message:
    def __init__(self, bot, json):
        self.bot = bot
        self.entities = json.get('entities', [])
        self.date = json['date']
        self.id = json['message_id']
        self.frm = User(bot, json['from'])
        self.text = json['text']
        self.chat = Chat(bot, json['chat'])

    def __str__(self):
        return "{}: {}".format(self.frm, self.text)

    def reply(self, text):
        self.bot.sendMessage(self.chat, text)



class FerdiBot:
    def __init__(self):
        self.token = open(".token").read().strip()
        self.session = requests.session()


    def request(self, method, url, **kw):
        return self.session.request(method, 'https://api.telegram.org/bot' + self.token + '/' + url, **kw)
        

    def sendMessage(self, chat, msg):
        self.request('POST', 'sendMessage', data={'chat_id': chat.id, 'text': msg})

    def updates(self):
        confirmed = 0
        params = {'timeout': timeout}
        while True:

            if confirmed:
                params['offset'] = confirmed + 1

            r = self.request('GET', 'getUpdates', params=params, timeout=timeout+10)

            if r.status_code != 200:
                continue

            answer = r.json()
            if answer['ok']:
                for update in answer['result']:
                    if confirmed < update['update_id']:
                        confirmed = update['update_id']

                    if 'message' in update:
                        yield Message(self, update['message'])
                    else:
                        yield update
            else:
                log.debug('Request error: {}'.format(answer['description']))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    for update in FerdiBot().updates():
        log.debug("[MESSAGE] {}".format(update))
        if isinstance(update, Message):
            update.reply("Sorry " + update.frm.first_name + ", I have no features yet :(")
            
