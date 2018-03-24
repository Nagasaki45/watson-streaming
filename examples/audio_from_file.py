import wave
import watson_streaming


def example_callback(data):
    if 'results' in data:
        transcript = data['results'][0]['alternatives'][0]['transcript']
        print(transcript)


def audio_gen():
    """Generate samples from a .wav file."""
    with wave.open('audio_file.wav') as f:
        while True:
            samples = f.readframes(2048)
            if not samples:
                break
            yield samples


settings = {
    'interim_results': True,
}


watson_streaming.transcribe(
    example_callback,
    settings,
    watson_streaming.parse_arguments().credentials,
    audio_gen
)
