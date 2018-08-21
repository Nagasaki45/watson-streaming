"""
Speech to text transcription in real-time using IBM Watson.
"""

import argparse
import json
import ssl
import time
import threading

import requests
import sounddevice
import websocket

import pipeline

AUTH_API = 'https://stream.watsonplatform.net/authorization/api/'
STT_API = 'https://stream.watsonplatform.net/speech-to-text/api/'
WS_URL = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize'

AUDIO_OPTS = {
    'dtype': 'int16',
    'samplerate': 44100,
    'channels': 1,
}
BUFFER_SIZE = 2048


class AudioGen(pipeline.Node):

    def enter(self):
        self.stream = sounddevice.RawInputStream(**AUDIO_OPTS)
        self.stream.start()

    def exit(self):
        self.stream.stop()
        self.stream.close()

    def generate(self):
        chunk, _ = self.stream.read(BUFFER_SIZE)
        self.put(chunk[:])  # To get the bytes out of the CFFI buffer


def parse_credentials(credentials_file):
    with open(credentials_file) as f:
        return json.load(f)['speech_to_text'][0]['credentials']


def obtain_token(credentials):
    params = {
        'url': STT_API,
    }
    auth = (credentials['username'], credentials['password'])
    url = AUTH_API + '/v1/token'
    response = requests.get(url, params=params, auth=auth)
    return response.text


class Transcriber(pipeline.Node):

    def __init__(self, settings, credentials_file):
        super(Transcriber, self).__init__()
        settings.update({
            'action': 'start',
            'content-type': 'audio/l16;rate={samplerate}'.format(**AUDIO_OPTS),
        })
        self.settings = settings
        self.token = obtain_token(parse_credentials(credentials_file))

    def enter(self):

        def on_message(_, msg):
            data = json.loads(msg)
            self.put(data)

        def on_open(ws):
            # Send the settings to sets expectations for the stream
            ws.send(json.dumps(self.settings).encode('utf8'))
            self.ws.is_open = True

        self.ws = websocket.WebSocketApp(
            WS_URL,
            header={'X-Watson-Authorization-Token': self.token},
            on_open=on_open,
            on_message=on_message,
        )
        self.ws.is_open = False

        ws_settings = {'sslopt': {'cert_reqs': ssl.CERT_NONE}}
        t = threading.Thread(target=self.ws.run_forever, kwargs=ws_settings)
        t.daemon = True  # Not passed to the constructor to support python 2
        t.start()

    def exit(self):
        self.ws.close()

    def consume(self, chunk):
        if self.ws.is_open:
            self.ws.send(chunk, websocket.ABNF.OPCODE_BINARY)


###############################################################################
#
# Demo Time!
#
# The `demo_callback` and the `main` functions are a good example of how
# to use the `transcribe` function.
#
###############################################################################


class Printer(pipeline.Node):
    def consume(self, item):
        if 'results' in item:
            print(item['results'][0]['alternatives'][0]['transcript'])


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('credentials', help='path to credentials.json')
    return parser.parse_args()


def main():
    args = parse_arguments()
    settings = {
        'inactivity_timeout': -1,  # Don't kill me after 30 seconds
        'interim_results': True,
    }

    nodes = [
        AudioGen(),
        Transcriber(settings, args.credentials),
        Printer(),
    ]

    pipeline.connect(nodes)
    pipeline.start(nodes)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pipeline.stop(nodes)


if __name__ == '__main__':
    main()
