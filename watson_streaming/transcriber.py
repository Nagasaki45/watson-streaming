import json
import ssl
import threading
try:
    from urllib.parse import urlparse
    from urllib.parse import urlencode
except ImportError:  # python 2
    from urlparse import urlparse
    from urllib import urlencode

import fluteline
import requests
import websocket

AUTH_API = 'https://iam.bluemix.net/identity/token/'
URL_TEMPLATE = 'wss://{}/speech-to-text/api/v1/recognize'
URL_ONLY_PARAMS = [
    'access_token',
    'watson-token',
    'model',
    'language_customization_id',
    'acoustic_customization_id',
    'base_model_version',
    'x-watson-learning-opt-out',
    'x-watson-metadata',
]


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

        params = {
            'access_token': _request_token(apikey),
        }
        for param in URL_ONLY_PARAMS:
            if param in settings:
                params[param] = settings.pop(param)
        self._url = URL_TEMPLATE.format(hostname) + "?" + urlencode(params)

        settings.setdefault('action', 'start')
        settings.setdefault('content-type', 'audio/l16;rate=44100')
        self.settings = settings

        self._ws = websocket.WebSocket(enable_multithread=True)

    def enter(self):

        def receive_messages():
            while True:
                msg = self._ws.recv()
                if not msg:
                    break
                data = json.loads(msg)
                self.output.put(data)

        self._ws.connect(self._url)
        self._ws.send(json.dumps(self.settings).encode('utf8'))
        result = json.loads(self._ws.recv())
        assert result['state'] == 'listening'

        t = threading.Thread(target=receive_messages)
        t.daemon = True  # Not passed to the constructor to support python 2
        t.start()

    def exit(self):
        self._ws.close()

    def consume(self, chunk):
        self._ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
