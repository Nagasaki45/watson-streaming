import os.path
import unittest

import fluteline

import watson_streaming
import watson_streaming.transcriber
import watson_streaming.utilities

CREDENTIALS_PATH = 'credentials.json'
AUDIO_PATH = 'examples/audio_file.wav'


class TestSanity(unittest.TestCase):

    def setUp(self):
        if os.path.isfile(CREDENTIALS_PATH):
            config = watson_streaming.transcriber._parse_credentials(CREDENTIALS_PATH)
        else:
            config = os.environ['WATSON_APIKEY'], os.environ['WATSON_HOSTNAME']
        self.apikey, self.hostname = config

    def test_sanity(self):
        transcriber = watson_streaming.Transcriber(
            settings={'interim_results': True},
            apikey=self.apikey,
            hostname=self.hostname,
        )
        file_audio_gen = watson_streaming.utilities.FileAudioGen(AUDIO_PATH)

        pipeline = [file_audio_gen, transcriber]
        fluteline.connect(pipeline)
        fluteline.start(pipeline)

        while True:
            result = transcriber.output.get()
            if 'results' in result:
                transcript = result['results'][0]['alternatives'][0]['transcript']
                expected = 'several tornadoes'
                if transcript.startswith(expected):
                    break
        else:
            raise AssertionError("Didn't get expected transcript")

        fluteline.stop(pipeline)
