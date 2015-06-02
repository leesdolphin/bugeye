Your document looks like an attempt to get your head around what we are
doing. This is a necessary first step, but it isn't what I think of an
as API.

For an existing library the API doco is a "nice to have" - it provides
an alternative to reading the source code to figure out what how to use
the library. In a new project with multiple programmers working in
parallel on different parts of it there is no code to look at, as it's
in the process of being written. So for new projects the *only* way one
programmer can use the services being written by another programmer is
if there is an API written down somewhere they can both code against. In
this role API doco is not a "nice to have". The project can't proceed
without it.

To write API's you need to have at least a rough of idea of how the
project is divided between the programmers. Then you ask yourself the
question: "what does programmer A have to know\
 about the interfaces programmer B is providing so they can write their
code". The API explains that interface so programmer A can write code
using it, and programmer B can write the code providing it.\
 Notice this definition not only tells you what you have do document, it
also tells you the level detail you need to go into.

We've have broken down the tasks and responsibilities:

-   Ryan - Browser.
-   Lee - HTTP server.
-   Russell - Video Mixing.

So now lets look at what each programmer needs from the other. I'll
cover myself by pointing out a first draft of an API is like the first
draft of any other code - it's going to be full of bugs.\
 But there is no "unit test" I can do, so the only quality control we
can do is code review. **Ie - you are expected find mistakes and point
them out.**

Ryan \<===\> Lee
================

Live editing in the room
------------------------

The purpose of live editing is two fold:

1.  It produces a live stream that can be shown to the outside world.
2.  The mixing done is re-used as the basis of the post editing. Post
    editing produces final talk video's uploaded to youtube and the
    like.

Ryan and Lee communicate via HTTP requests, so we need to define URL's.
Firstly, there is the static content the browser needs. For now lets
assume the content is provided in a ".zip" file (Python handles these
well, and having it in one file makes deployment easier):

-   GET / - Gets the file "bugeye/www/index.html" from the .zip file.
-   GET /index.html - ditto.
-   GET /static/**some/thing** - returns the file
    "bugeye/www/static/**something** from the .zip file.

Next there is the configuration information. This is how the browser
discovers the media feeds available, the URL's they are obtained from,
the servers idea of the time, and the current mixing settings:

-   GET /config - returns a JSON string.

Configuration JSON:

        {
          # Media feeds.  The first one is always the mixed feed.
          # The remainder are the inputs.  The URL's are flexible
          # because we may need to change them if the transcoding
          # load gets too large.
          #
          # Elements:
          #
          #   0     The URL to fetch the feed from.  This will be a WebM
          #         stream, suitable for HTML5 video.
          #
          #   1     Type of feed.   'video' if video only, 'audio' if audio
          #         only 'av' if it contains both audio and video.
          #
          #   2     How the feed is being used to mixed output.  Values:
          #          ''         Not used.
          #          'video'    The main video feed stream.
          #          'pip'      Picture in picture video.
          #          'audio'    The audio feed.
          #
          #   3     Description of feed.
          #
          'media': [
            [a_url,  'av',     'mixer',  'output'],
            [a_url,  'video',  'main',   'camera-1'],
            [a_url,  'audio',  'audio',  'lecturn mic'],
            [a_url,  'video',  'pip',    'laptop'],
            [a_url,  'audio',  '',       'roving mic']
          ],
          #
          # For live editing this is the name of the room.  (This is the
          # name of the directory the room's data is stored under).
          # For post editing this is blank.
          #
          room: 'swanky-room-a',
          #
          # The servers idea of the time.  The format is a float giving
          # seconds from midnight, local time.  Positions in video streams
          # are specified as a time from midnight.
          #
          'time': seconds-part-midnight,
        }

GET'ing the mixing URL alters how the inputs are mixed to produce the
output:

-   GET /mix?*use*=*src*[&*use*=*src* ...]

The URL takes two parameters:

-   *use* One of:
    -   'audio' - set the audio for the mixed stream.
    -   'pip' - set the picture in picture source for the mixed stream,
    -   'video' - set the main video feed for the mixed stream.
-   *src* The media feed to use. It is an index into the media array in
    the /config data. Use 0 to switch pip off and silence.

The mixing actions above not only alter the output, they are also saved
to an editing log file so the mix can be repeated and more importantly
edited after the fact. Text notes aimed at the person doing the post
editing can also be added to the edit log by doing a POST to the notes
URL. If multiple posts are done for the same *talk-id* the last one is
used.

-   POST /notes

The post contains the following fields:

-   *talk-id* A string which serving as a unique identifier for the
    talk. Only a restricted character set is available: letters, numbers
    '.' and '-'.
-   *talk-begin* The time the talk began, as seconds from midnight.
-   *talk-end* The time the talk ended, as seconds from midnight.
-   *title* The talks title.
-   *presenter* The name(s) of the people presenting the talk.
-   *comments* Room coordinators comments. Can be several lines long,
    lines are delimited by '\\n'.

If several browsers connect to the same server during live editing they
are all equivalent, and in particular they will all show an identical
web page. The URL below is provided so a browser can save it's layout so
others can copy it. POST's to it have one field, called 'state'. GET's
to it return whatever was last POST'ed to 'state'.

-   POST /state - Saves the field 'state' (and it's mime type).
-   GET /state - Returns the field 'state' with it's associated mime
    type.

To avoid polling the browser can open a websocket to the server. Once
opened the server will send URL's here if their contents have changed.
Currently there are only two: 'config' and 'state'.

-   WEBSOCKET /notify

Post editing
------------

After live editing is done the input streams and the edit log are copied
to a backend server. There post-editing is done. The output of the post
editing is later branded, transcoded, and uploaded to distribution and
archive sites by a separate process.

Although the editing side of post editing is identical to live editing,
it differs in these ways:

-   The post editor must choose the talk they are will work on. The live
    editor has no choice as it's a live stream.
-   The post editor's job is to review the mix done by the live editor,
    only changing it if necessary. Thus the post editor gets to see the
    edit log, and add and delete mixing instructions.
-   To speed up the process post editor will change their position in
    the video stream, and fast forward and fast reverse it.
-   The post editor may be operating remotely and thus wish to reduce
    the quality of the video feed they are getting.
-   There is no "browser sharing" for remote feeds. Each browser gets
    it's own unique session.

They following URL returns the talks available for post-editing:

-   GET /talk-list.json

The following JSON structure.

        {
          #
          # The key is made up of fields from the mapping,
          # joined with underscores.  The key uniquely identifies
          # a mixing run.  The first of these is produced by the
          # live edit.  The remainder are post editing runs.
          # The key fields are composed of a restricted character set:
          # letters, numbers, '.' and '-'.
          #
          'room_date_talk-id_post-edit-time': {
            #
            # Room that produced the live stream.
            #
            'room': 'room-name',
            #
            # Day the live stream was produced.
            #
            'talk-date': 'yyyy-mm-dd',
            #
            # Unique id for the talk on that day.
            #
            'talk-id': 'talk-id',
            #
            # Times the editor suggests the talk started and ended,
            # as seconds from midnight local time.
            #
            'talk-begin': seconds-past-midnight,
            'talk-end': seconds-past-midnight,
            #
            # Talk notes.
            #
            'title': 'talk title',
            'presenters': 'presenters',
            'comments': 'comments',
            #
            # The person who produced this post edit, and when it was
            # finalised.  If this is the live stream the person is blank.
            #
            'post-editor': '',
            'post-edit-time': 'yyyy-mm-ddThh-mm-ssZ',
            #
            # If set to 'yes' this edit is to be handed over to the
            # transcoders.
            #
            'finalised': ''
            #
            # The mixing instructions.  These specify the inputs for each
            # mixed, in the order they occurred.  The time is the time
            # from midnight.  The video starts on the first entry, and
            # ends on the last.
            #
            'post-mix': [
              [seconds-past-midnight, 'audio=n pip=n video=n'],
              [seconds-past-midnight, 'audio=n pip=n video=n'],
              ...
              [seconds-past-midnight]
            ]
          },
          ...
        }

Editing is done entirely in browser. To display the input feeds and the
mixed output, the browser issues mixing instructions (ie uses the /mix
url, setting all *use*'s) and then fetches media stream URL's (using the
URL's returned by /config) in the same way as the live editing session.
However in the post editing session the browser must add parameters to
the media URL's that select the room, date and starting position. It can
also add parameters that effect the quality and hence bit rate of the
feed, and also the playback speed. All media URL's should be changed at
the same time. With the exception of the quality settings all parameters
must be identical in all URL's. Unlike the live editing session these
mixing instructions are not recorded by the server, rather they are
saved by the browser and sent back later. The quality parameters only
effect the display during the editing session.

-   room=*room* the name of the room the feed is coming from.
-   day=*date* the day the live stream was captured.
-   time=*seconds-past-midnight* the feed is to start play at
    *seconds-past-midnight*.
-   speed=*speed* the speed of playback. Eg, 1 means play at twice
    normal speed, -2 means fast reverse at twice normal speed. Audio is
    turned off for speeds other than 1.
-   quality=*q* jpeg compression, a number from 0 (highest) to 100
    (uncompressed).
-   fps=*fps* frames per second.
-   scale=*scale* a number from 0 to 1 - downscale video resolution by
    this factor.

Once the editing session is complete the browser posts the modified JSON
block for the 'room\_date\_talk-id' back. The 'post-mix' is sent as
lines consisting of 'seconds-part-midnight /mix/....'.

-   POST /post-edit/room\_date\_talk-id

Lee \<===\> Russell
===================

Russell will provide Lee with a single Python class:

    class Mixer(object):

        #
        #
        on_media = None

        #
        # Create a mixer.  Parameters:
        #
        #  room      For live editing this is the room name.  For post editing
        #            this is None.
        #
        #  data_dir  The mixer will save the media feeds under this directory,
        #            and read it's input feeds from this directory in "post"
        #            mode.
        #
        #  on_media  A function called to give raw WebM data to the server.
        #            Each call may come from a different thread.  Do not block
        #            the thread by doing I/O.  It takes three parameters:
        #
        #              on_media(feed_idx, settings_id, data)
        #
        #            Feed_idx is an index into the feeds returned by
        #            get_feeds(), settings_id is the settings_id parameter to
        #            set_media(), and data is the raw WebB frame(s).  Calls
        #            to this function cease when on_feed fires, and are
        #            resumed when set_media() is called for the feed.
        #
        #  on_feed   A function called when the feeds returned by get_feeds()
        #            may have changed.  Each call may come from a different
        #            thread.  Do not block the thread by doing I/O.  It takes
        #            no arguments.  In "live" mode this only happens as part
        #            of a set_feeds() call, in "post" mode it can happen
        #            at any time.
        #
        def __init__(self, room, data_dir, on_media, on_feed):
            pass

        #
        # Set the input feeds for "live" mode.  Not used for "post" mode.
        # Feeds is a sequence:
        #
        #   [None, ("url", "type", "desc"), ...]
        #
        # The feeds are the same sequence as the "media" array returned by
        # /config.  "url" is the URL the feed can be collected from using
        # a HTTP request, something like "http://ip:port" or maybe
        # "rtp://ip:port".  "type" is one of "audio", "video" or "av".
        # "desc" is the descrption.
        #
        def set_feeds(self, feeds):
            pass

        #
        # Return the current feeds.  Format same as "set_feeds()".
        #
        def get_feeds(self):
            pass

        #
        # Set the mixing instructions.  Settings is a dict, all keys are
        # optional.
        #
        #    {
        #       'audio': N,
        #       'pip': N,
        #       'video': N,
        #    }
        #
        # Here N specifies which input steam to use for 'video'
        # (main video feed), 'pip' (picture in picture video feed) and
        # and 'audio' (the sound feed).  N is the integer index into
        # the feeds as returned by get_feeds().
        #
        def set_mix(self, settings):
            pass

        #
        # Set the media format for an output stream (ie, as passed to
        # on_media).  It also starts the data flowing to on_media for a feed.
        #
        # Params:
        #
        #   setting_id  Anything.  It is only use is as a paramater to
        #               on_media.
        #
        #   feed_idx    Index into the feeds returned by get_feeds().  Index
        #               0 is the mixed output feed.
        #
        #   scale       Downscale by this factor, a float 0.0 ... 1.0.
        #
        #   quality     jpeg quality, a number from 0 ... 100, or -1 for
        #               "same as input".
        #
        #   fps         Output frames per second.
        #
        def set_media(self, setting_id, feed_idx, scale, quality, fps):
          pass

Disk layout.
============

Something will have to move the media files around. The Mixer and Server
will create / use the following directory format under the "data\_dir"
the constructor is passed. All file names start with this prefix:

> /datadir/*room*/*day*/*time*-

-   *room* the name of the room as it will appear in GET
    /talk-list.json.
-   *day* The day the recording was made, format *YYYY-mm-dd*.
-   *time* - Time of day, format *HHMMSS.sss*.

Four different file types are written to the rooms directory:

-   /datadir/*room*/*day*/*time*-config.txt This file is is written
    every time there is feed change (so there will be at least one - at
    the start of the day). It contains lines of the format "*feed\_idx*
    *url* *type* *desc*". These lines contain the same information
    returned by get\_feeds(), with *feed\_idx* being the index into the
    sequence. These files are written and read by Russell's mixer.

-   /datadir/*room*/*day*/*time*-av*n*.webm These are the incoming media
    streams. A new file is started every 10 minutes. *n* is the
    *feed\_idx*. These files are written and read by Russell's mixer.

-   /datadir/*room*/*day*/*time*-mix.txt Mixing instructions. These
    files are written every time the operating changes the source inputs
    to the mix. There is one line per mixing input, ie "audio=*n*",
    "pip=*n*" and "video=*n*". *n* is the *feed\_idx*. These files are
    written and read by Russell's mixer.

-   /datadir/*room*/*day*/*time*-edit.txt Editing instructions. These
    files contain the information\
     POST'ed to /post-edit/room\_date\_talk-id. The format is something
    that can be parsed as a POSIX shell fragment, ie, "*NAME='value'*".
    The quotes are NOT optional. If quotes occur in the text they must
    be quoted using "*'\\''*". These files are read and written by Lee's
    server.

    -   TALK\_ROOM='room-name'
    -   TALK\_DATE='yyyy-mm-dd'
    -   TALK\_ID='talk-id'
    -   TALK\_BEGIN='nnnn.n'
    -   TALK\_END='nnnn.n'
    -   TALK\_TITLE='a title'.
    -   TALK\_PRESENTERS='presenters'
    -   TALK\_COMMENT='a line'
    -   TALK\_COMMENT='another line'
    -   ...
    -   TALK\_POST\_EDITOR='somebody'
    -   TALK\_POST\_EDIT\_TIME': 'yyyy-mm-ddThh-mm-ssZ',
    -   TALK\_FINALISED=""
    -   TALK\_POST\_MIX='nnnnn.n audio=n pip=n video=n'
    -   TALK\_POST\_MIX='nnnnn.n audio=n pip=n video=n'
    -   ...
    -   TALK\_POST\_MIX='nnnnn.n"

To avoid race conditions files are always written to this directory with
".part" appended to their name, then when complete are renamed to their
final name. Thereafter they are immutable.
