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


Using as a library
------------------

What you need to know:

- This project relies on `fluteline`_, an easy to use thread based pipelines library.
- ``watson_streaming.Transcriber`` is a consumer-producer, it receives audio samples and spits out transcriptions.
- ``watson_streaming.utilities`` include some useful things that you can plug in the pipeline, like audio producers (from file or from microphone).
- To learn how to use the library see the ``examples`` folder.
- TODO: Proper documentation is coming soon.

.. _fluteline: https://github.com/Nagasaki45/fluteline
