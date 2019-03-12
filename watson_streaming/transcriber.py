import json
import ssl
import threading
try:
    from urllib.parse import urlparse
except ImportError:  # python 2
    from urlparse import urlparse

import fluteline
import requests
import websocket

AUTH_API = 'https://iam.bluemix.net/identity/token/'
URL_TEMPLATE = 'wss://{}/speech-to-text/api/v1/recognize?access_token={}'


def _parse_credentials(credentials_file):
    with open(credentials_file) as f:
        credentials = json.load(f)
    hostname = urlparse(credentials['url']).netloc
    return credentials['apikey'], hostname


def _request_token(apikey):
    params = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': apikey,
    }
    response = requests.post(AUTH_API, params=params)
    msg = 'Failed to get a token. Check your credentials'
    assert response.status_code == 200, msg
    return response.json()['access_token']


class Transcriber(fluteline.Consumer):
    '''
    A `fluteline`_ consumer-producer.

    Send audio samples to it (1 channel, 44100kHz, 16bit, little-endian)
    and it will spit out the results from watson.
    '''

    def __init__(self, settings, credentials_file=None,
                 apikey=None, hostname=None):
        '''
        :param dict settings: IBM Watson settings. Consult the official
            IBM Watson docs for more information.
        :param string credentials_file: Path to your IBM Watson credentials.
            Alternatively, provide an apikey and hostname.
        :param string apikey: API key for the IBM Watson service.
        :param string hostname: IBM Watson hostname.
        '''
        super(Transcriber, self).__init__()

        if credentials_file is None:
            msg = 'Provide either credentials_file or apikey and hostname'
            assert None not in (apikey, hostname), msg
        else:
            apikey, hostname = _parse_credentials(credentials_file)

        token = _request_token(apikey)
        self._url = URL_TEMPLATE.format(hostname, token)

        settings.setdefault('action', 'start')
        settings.setdefault('content-type', 'audio/l16;rate=44100')
        self.settings = settings
        self._watson_ready = threading.Event()

    def enter(self):

        def on_message(_, msg):
            data = json.loads(msg)
            if data.get('state') == 'listening':
                self._watson_ready.set()
            self.output.put(data)

        def on_open(ws):
            ws.send(json.dumps(self.settings).encode('utf8'))

        def on_error(_, error):
            print('error', error)

        self._ws = websocket.WebSocketApp(
            self._url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
        )

        ws_settings = {'sslopt': {'cert_reqs': ssl.CERT_NONE}}
        t = threading.Thread(target=self._ws.run_forever, kwargs=ws_settings)
        t.daemon = True  # Not passed to the constructor to support python 2
        t.start()

    def exit(self):
        self._ws.close()
        self._watson_ready.clear()

    def consume(self, chunk):
        self._watson_ready.wait()
        self._ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
