import json
import ssl
import threading

import fluteline
import requests
import websocket

AUTH_API = 'https://stream.watsonplatform.net/authorization/api/'
STT_API = 'https://stream.watsonplatform.net/speech-to-text/api/'
WS_URL = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize'


def _parse_credentials(credentials_file):
    with open(credentials_file) as f:
        return json.load(f)['speech_to_text'][0]['credentials']


def _request_token(username, password):
    params = {
        'url': STT_API,
    }
    auth = (username, password)
    url = AUTH_API + '/v1/token'
    response = requests.get(url, params=params, auth=auth)
    msg = 'Failed to get a token. Check your credentials'
    assert response.status_code == 200, msg
    return response.text


class Transcriber(fluteline.Consumer):
    '''
    A `fluteline`_ consumer-producer.

    Send audio samples to it (1 channel, 44100kHz, 16bit, little-endian)
    and it will spit out the results from watson.
    '''

    def __init__(self, settings, credentials_file=None,
                 username=None, password=None):
        '''
        :param dict settings: IBM Watson settings. Consult the official
            IBM Watson docs for more information.
        :param string credentials_file: Path to your IBM Watson credentials.
            Alternatively, provide your username and password.
        :param string username: IBM Watson username.
        :param string password: IBM Watson password.
        '''
        super(Transcriber, self).__init__()

        if credentials_file is None:
            msg = 'Provide either credentials_file or username and password'
            assert None not in (username, password), msg
        else:
            credentials = _parse_credentials(credentials_file)
            username = credentials['username']
            password = credentials['password']

        settings.update({
            'action': 'start',
            'content-type': 'audio/l16;rate=44100',
        })
        self.settings = settings
        self.token = _request_token(username, password)
        self._watson_ready = threading.Event()

    def enter(self):

        def on_message(_, msg):
            data = json.loads(msg)
            if data.get('state') == 'listening':
                self._watson_ready.set()
            self.put(data)

        def on_open(ws):
            ws.send(json.dumps(self.settings).encode('utf8'))

        self._ws = websocket.WebSocketApp(
            WS_URL,
            header={'X-Watson-Authorization-Token': self.token},
            on_open=on_open,
            on_message=on_message,
        )

        # ping_timeout is a workaround for websocket-client/websocket-client#466
        ws_settings = {'sslopt': {'cert_reqs': ssl.CERT_NONE}, 'ping_timeout': 10}
        t = threading.Thread(target=self._ws.run_forever, kwargs=ws_settings)
        t.daemon = True  # Not passed to the constructor to support python 2
        t.start()

    def exit(self):
        self._ws.close()
        self._watson_ready.clear()

    def consume(self, chunk):
        self._watson_ready.wait()
        self._ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
