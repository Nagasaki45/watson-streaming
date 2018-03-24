watson-streaming
################

Speech to text transcription from your microphone in real-time using IBM Watson.

Installing
----------

1. This project depends on PortAudio_ - a free, cross-platform, open-source, audio I/O library. Install it first.
2. Prepare your credentials from IBM Watson (free trials are available):

   - Visit the `IBM Watson projects`_ page.
   - Choose your project.
   - Copy the credentials to ``credentials.json`` somewhere on your computer.

3. ``pip install watson-streaming`` and you are ready to go!

.. _PortAudio: http://www.portaudio.com/
.. _`IBM Watson projects`: https://console.bluemix.net/developer/watson/projects

Using from the command line
---------------------------

.. code-block:: bash

    watson-streaming path/to/credentials.json  # And start talking


Using as a library
------------------

.. code-block:: python

    from watson_streaming import transcribe


    # Write whatever you want in your callback function (expecting a dict)
    def example_callback(data):
        if 'results' in data:
            transcript = data['results'][0]['alternatives'][0]['transcript']
            print(transcript)


    # Provide a dictionary of Watson input and output features.
    # For example
    settings = {
        'inactivity_timeout': -1,  # Don't kill me after 30 seconds
        'interim_results': True,
    }


    # You can't ask for a simpler API than this!
    transcribe(example_callback, settings, 'credentials.json')


Custom audio source
-------------------

By default, the audio from the computer sound card is sent to IBM Watson for transcription. If you want to send audio from another source (like a file, socket, etc.) use the `audio_gen` argument of the `transcribe` function. This should be a generator that yields audio samples, currently in 44100 Hz sample rate. See `examples/audio_from_file.py`.
