'''
Speech to text transcription, from your mike, in real-time, using IBM Watson.
'''

import argparse
import time

import fluteline

import watson_streaming
import watson_streaming.utilities


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('credentials', help='path to credentials.json')
    return parser.parse_args()


def main():
    args = parse_arguments()
    apikey, hostname = watson_streaming.utilities.config(args.credentials)
    settings = {
        'inactivity_timeout': -1,  # Don't kill me after 30 seconds
        'interim_results': True,
    }

    nodes = [
        watson_streaming.utilities.MicAudioGen(),
        watson_streaming.Transcriber(settings, apikey, hostname),
        watson_streaming.utilities.Printer(),
    ]

    fluteline.connect(nodes)
    fluteline.start(nodes)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        fluteline.stop(nodes)


if __name__ == '__main__':
    main()
