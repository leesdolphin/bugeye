Discussions at Catalyst
=======================


Inputs are processed on the laptop.
  - This is configured using a config file on the laptop itself. It contains:
    - The location of the BugEye server.
    - A list of inputs that are found/present/available on this laptop
      - The name of the input
      - The location of the input(I.E. /dev/usb0)

For each input:
  1. The laptop will save the video in the rawest format possible.
  2. The laptop will also serve the video as a low-ish resolution stream.
  3. The laptop will then notify the BugEye server that the input is connected and the stream is available at a URL(dictated by step 2)

At a regular interval all saved input streams are synchronised to the BugEye server.
