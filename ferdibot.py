#!/usr/bin/python3

import bottle
import requests
import logging

log = logging.getLogger(__name__)

timeout = 600

class FerdiBot:
    def __init__(self):
        self.token = open(".token").read().strip()
        self.session = requests.session()

    def request(self, method, url, **kw):
        return self.session.request(method, 'https://api.telegram.org/bot' + self.token + '/' + url, **kw)
        

    def updates(self):
        confirmed = 0
        params = {'timeout': timeout}
        while True:

            if confirmed:
                params['offset'] = confirmed + 1

            r = self.request('GET', 'getUpdates', params=params, timeout=timeout)

            if r.status_code != 200:
                continue

            answer = r.json()
            if answer['ok']:
                for update in answer['result']:
                    if confirmed < update['update_id']:
                        confirmed = update['update_id']
                    yield update
            else:
                log.debug('Request error: {}'.format(answer['description']))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    for update in FerdiBot().updates():
        log.debug("Got update: {}".format(update))
