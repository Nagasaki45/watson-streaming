import json
import wave

import fluteline
import sounddevice

AUDIO_OPTS = {
    'dtype': 'int16',
    'samplerate': 44100,
    'channels': 1,
}
BUFFER_SIZE = 2048


class MicAudioGen(fluteline.Producer):

    def enter(self):
        self.stream = sounddevice.RawInputStream(**AUDIO_OPTS)
        self.stream.start()

    def exit(self):
        self.stream.stop()
        self.stream.close()

    def produce(self):
        chunk, _ = self.stream.read(BUFFER_SIZE)
        self.put(chunk[:])  # To get the bytes out of the CFFI buffer


class FileAudioGen(fluteline.Producer):

    def __init__(self, audio_file):
        super(FileAudioGen, self).__init__()
        self.audio_file = audio_file

    def enter(self):
        self.file_ = wave.open(self.audio_file)

    def exit(self):
        self.file_.close()

    def produce(self):
        samples = self.file_.readframes(BUFFER_SIZE)
        if samples:
            self.put(samples)
        else:
            self.stop()


class Printer(fluteline.Consumer):
    def consume(self, item):
        if 'results' in item:
            print(item['results'][0]['alternatives'][0]['transcript'])
