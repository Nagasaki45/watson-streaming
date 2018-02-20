"""
Speech to text transcription in real-time using IBM Watson.
"""

import contextlib
import json
import logging
import ssl
import threading

import requests
import sounddevice
import websocket

AUTH_API = 'https://stream.watsonplatform.net/authorization/api/'
STT_API = 'https://stream.watsonplatform.net/speech-to-text/api/'
WS_URL = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize'

AUDIO_OPTS = {
    'dtype': 'int16',
    'samplerate': 44100,
    'channels': 1,
}
BUFFER_SIZE = 2048

logger = logging.getLogger(__name__)


def audio_gen():
    """
    Generate audio chunks.
    """
    with sounddevice.RawInputStream(**AUDIO_OPTS) as stream:
        while True:
            chunk, _ = stream.read(BUFFER_SIZE)
            yield chunk[:]  # To get the bytes out of the CFFI buffer


def send_audio(ws):
    """
    Get chunks of audio and send them to the websocket.
    """
    for chunk in audio_gen():
        ws.send(chunk, websocket.ABNF.OPCODE_BINARY)


def on_error(ws, error):
    logger.warning(error)


def on_close(ws):
    logger.warning('WebSockets connection closed')


def start_communicate(ws, settings):
    """
    Send the initial control message and start sending audio chunks.
    """
    logger.info('WebSockets connection opened')

    settings.update({
        'action': 'start',
        'content-type': 'audio/l16;rate={samplerate}'.format(**AUDIO_OPTS),
    })

    # Send the initial control message which sets expectations for the
    # binary stream that follows:
    ws.send(json.dumps(settings).encode('utf8'))
    # Spin off a dedicated thread where we are going to read and
    # stream out audio.
    t = threading.Thread(target=send_audio, args=(ws, ), daemon=True)
    t.start()


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


def transcribe(callback, settings, credentials_file):
    """
    Main API for Watson STT transcription.

    callback:         function to call when Watson sends us messages.
    settings:         dictionary of input and output features.
    credentials_file: path to 'credentials.json'.
    """
    credentials = parse_credentials(credentials_file)
    token = obtain_token(credentials)

    ws = websocket.WebSocketApp(
        WS_URL,
        header={'X-Watson-Authorization-Token': token},
        on_open=lambda ws: start_communicate(ws, settings),
        on_message=lambda ws, msg: callback(msg),
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})


###############################################################################
#
# Demo Time!
#
# The `demo_callback` and the `main` functions are a good example of how
# to use the `transcribe` function.
#
###############################################################################


def demo_callback(msg):
    """
    Nicely print received transcriptions.
    """
    msg = json.loads(msg)
    if 'results' in msg:
        transcript = msg['results'][0]['alternatives'][0]['transcript']
        print(transcript)


def main():
    settings = {
        'inactivity_timeout': -1,  # Don't kill me after 30 seconds
        'interim_results': True,
    }
    transcribe(demo_callback, settings, 'credentials.json')


if __name__ == '__main__':
    main()
