#!/usr/bin/env python

"""
Speech to text transcription in real-time using IBM Watson, pyaudio,
and websocket-client.
"""

import contextlib
import json
import threading

import pyaudio
import requests
import websocket

AUTH_API = 'https://stream.watsonplatform.net/authorization/api/'
STT_API = 'https://stream.watsonplatform.net/speech-to-text/api/'
WS_URL = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize'

CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class Color:
    """
    ANSI colors copied from https://stackoverflow.com/a/287944/1224456.
    """
    GREEN = '\033[92m'
    NO_COLOR = '\033[0m'


# These context managers simplify closing pyaudio

@contextlib.contextmanager
def pyaudio_terminator(pyaudio):
    try:
        yield pyaudio
    finally:
        pyaudio.terminate


@contextlib.contextmanager
def stream_closer(stream):
    try:
        yield stream
    finally:
        stream.stop_stream()
        stream.close()


def audio_gen():
    """
    Generate audio chunks.
    """
    stream_options = {
        'input': True,  # this is not an output
        'format': FORMAT,
        'channels': CHANNELS,
        'rate': RATE,
    }
    with pyaudio_terminator(pyaudio.PyAudio()) as p:
        with stream_closer(p.open(**stream_options)) as stream:
            while True:
                yield stream.read(CHUNK)


def send_audio(ws):
    """
    Get chunks of audio and send them to the websocket.
    """
    for chunk in audio_gen():
        ws.send(chunk, websocket.ABNF.OPCODE_BINARY)


def on_error(ws, error):
    print('ERROR', error)


def on_close(ws):
    print('CLOSE')


def start_communicate(ws, settings):
    """
    Send the initial control message and start sending audio chunks.
    """
    print('OPEN')

    settings.update({
        'action': 'start',
        'content-type': f'audio/l16;rate={RATE}',
    })

    # Send the initial control message which sets expectations for the
    # binary stream that follows:
    ws.send(json.dumps(settings).encode('utf8'))
    # Spin off a dedicated thread where we are going to read and
    # stream out audio.
    t = threading.Thread(target=send_audio, args=(ws, ), daemon=True)
    t.start()


def parse_credentials():
    with open('credentials.json') as f:
        return json.load(f)['speech_to_text'][0]['credentials']


def obtain_token(credentials):
    params = {
        'url': STT_API,
    }
    auth = (credentials['username'], credentials['password'])
    url = AUTH_API + '/v1/token'
    response = requests.get(url, params=params, auth=auth)
    return response.content.decode()


def transcribe(callback, settings):
    """
    Main API for Watson STT transcription.

    callback: a function to call when Watson sends us messages.
    settings: a dictionary of input and output features.
    """
    credentials = parse_credentials()
    token = obtain_token(credentials)

    ws = websocket.WebSocketApp(
        WS_URL,
        header={'X-Watson-Authorization-Token': token},
        on_open=lambda ws: start_communicate(ws, settings),
        on_message=lambda ws, msg: callback(msg),
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()


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
    transcribe(demo_callback, settings)


if __name__ == '__main__':
    main()
