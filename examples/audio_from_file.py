'''
Speech to text transcription, from an audio file, in real-time, using
IBM Watson.
'''

import argparse
import time

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

    # It's impossible to know when Watson finished sending the entire
    # transcript. So let's wait forever or exit manually.
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        fluteline.stop(nodes)


if __name__ == '__main__':
    main()
