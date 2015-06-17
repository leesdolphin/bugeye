Bugeye
======
Bugeye takes mkv (matroska) mjpeg video streams, and mkv audio streams as
arriving over IP as input, allows the user to mix the streams together using a
web interface and outputs the mixed streams, cut marks and the raw streams
themselves. It's useful as a video recording platform for events like
conferecnes and inspired by dvswitch and vyapar.

How it works
------------
Bugeye takes mkv (matroska) mjpeg video streams, and mkv audio streams as 
arriving over IP as input. They are mixed under direction from a user. The
outputs are:

1. The incoming raw mkv streams are written to disc.
2. The resulting mixed stream over IP, also a mkv mjpeg + audio.
3. The "cut marks", which is a text file saying how the how the inputs were
   mixed to produce the output stream.

Alternatively Bugeye can take the raw streams it wrote in a previous run as it's
input, together with the cut marks. In effect this allows the cut marks to be
edited to produce a different mixed output stream. This new result plus the new
cut marks are written to the disc as the outputs.

Architecture
------------
Bugeye is split into two bits. One is a web app which handles the  UI. It
displays the incoming streams and the mixed stream (ie, the output), and has
controls that provide the editing instructions. The editing instructions consist
of:

1. Which audio stream to use.
2. Main video feed.
3. Te secondary video feed
4. How the secondary feed is displayed (PIP, side by side, not used).
5. Plus positioning when editing (absolute position, fast forward and reverse).
6. Feed quality, for editing over slow links.  There are three possible knobs:
   frames per second, compression level and scaling.

The second bit is the back end. The UI just displays feeds from the back end,
and relays the user editing instructions to the backend. It has to ask the
backend what feeds are available and arrange the UI suitably, and save whatever
settings the user chooses (like video quality), and handle user authentication.

The back end therefore has two duties. It does the mixing described earlier. And
it is a web server, serving the front end static files and, sending all incoming
feeds and the resulting mixed feed the front end asks for.

To allow the control room to support the team in the talk rooms, the back end
will allow multiple web browsers to connect. However, they will see exactly the
same web page. Pressing a button on one effects all UI's identically.

Status
------
This project is very much in development status. Only the brave and/or foolish
should try to use it at this point. Assume it does an ``rm -rf /`` when you
start it.

Use
---

To run the server:
.. code:: console
    python3 -m bugeye.server

Copyright and License
---------------------

Bugeye is Copyright (C) the respective authors of the files, as noted at the top
of each file. If not noted, it is Copyright (C) 2015 Ryan Stuart. All original
code in Bugeye is licensed under the `GNU Affero General Public License
<http://scraper-helper.sourceforge.net/agpl-3.0.txt>`_.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

The copyright holders grant you an additional permission under Section 7 of the
GNU Affero General Public License, version 3, exempting you from the requirement
in Section 6 of the GNU General Public License, version 3, to accompany
Corresponding Source with Installation Information for the Program or any work
based on the Program. You are still required to comply with all other Section 6
requirements to provide Corresponding Source.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
