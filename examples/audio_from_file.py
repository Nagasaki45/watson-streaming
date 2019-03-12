'''
Speech to text transcription, from an audio file, in real-time, using
IBM Watson.
'''

import argparse
import contextlib
import time
import wave

import fluteline

import watson_streaming
import watson_streaming.utilities


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('credentials', help='path to credentials.json')
    parser.add_argument('audio_file', help='path to .wav audio file')
    return parser.parse_args()


def main():
    args = parse_arguments()
    settings = {
        'interim_results': True,
    }

    nodes = [
        watson_streaming.utilities.FileAudioGen(args.audio_file),
        watson_streaming.Transcriber(settings, args.credentials),
        watson_streaming.utilities.Printer(),
    ]

    fluteline.connect(nodes)
    fluteline.start(nodes)

    try:
        with contextlib.closing(wave.open(args.audio_file)) as f:
            wav_length = f.getnframes() / f.getnchannels() / f.getframerate()
        # Sleep till the end of the file + some seconds slack
        time.sleep(wav_length + 5)
    finally:
        fluteline.stop(nodes)


if __name__ == '__main__':
    main()
