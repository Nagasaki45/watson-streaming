watson-streaming
################

Speech to text transcription from your microphone in real-time using IBM Watson.

Installing
----------

1. This project depends on PortAudio_ - a free, cross-platform, open-source, audio I/O library. Install it first.
2. Download the ``credentials.json`` file from IBM Watson and put it in your current working directory.
3. ``pip install watson-streaming`` and you are ready to go!

.. _PortAudio: http://www.portaudio.com/

Using from the command line
---------------------------

.. code-block:: bash

    watson-streaming  # And start talking


Using as a library
------------------

.. code-block:: python

    from watson_streaming import transcribe


    # Write whatever you want in your callback function
    def example_callback(msg):
        msg = json.loads(msg)
        if 'results' in msg:
            transcript = msg['results'][0]['alternatives'][0]['transcript']
            print(transcript)


    # Provide a dictionary of Watson input and output features.
    # For example
    settings = {
        'inactivity_timeout': -1,  # Don't kill me after 30 seconds
        'interim_results': True,
    }


    # You can't ask for a simpler API than this!
    transcribe(example_callback, settings, 'credentials.json')
