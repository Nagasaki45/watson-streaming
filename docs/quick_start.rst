Quick start guide
=================

This project relies on `fluteline`_, an easy to use thread based pipelines library (it's highly recommended that you check out `its docs`_).
It supports the creation of speech-to-text pipelines using easy to use modular components.
First, instantiate the nodes that you want to use.
Assuming ``source`` and ``destination`` are two such instantiated nodes, connect them with ``source.connect(destination)``.
Then, start your nodes with the ``.start`` method.
When processing is done turn off the nodes with the ``.stop`` method.

The transcriber
---------------

.. autoclass:: watson_streaming.Transcriber
    :members:

Utilities
---------

.. automodule:: watson_streaming.utilities
    :members:

Examples
--------

The two examples bellow (copied from `here`_) can help you understand how to use the library for your needs.
The first one is for transcribing audio from the microphone using :class:`watson_streaming.utilities.MicAudioGen`.
The 2nd example is similar, but transcribes audio from a file instead, using :class:`watson_streaming.utilities.FileAudioGen`.

.. literalinclude:: ../examples/audio_from_mic.py

.. literalinclude:: ../examples/audio_from_file.py

.. _fluteline: https://github.com/Nagasaki45/fluteline
.. _`its docs`: https://fluteline.readthedocs.io/en/latest/
.. _here: https://github.com/Nagasaki45/watson-streaming/tree/master/examples
