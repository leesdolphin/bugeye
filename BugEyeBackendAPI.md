# Use Cases #

## Configuration

### Creating a room. 

A room is just an arbitrary location
from which a single recording is obtained.
This would be configured using a JSON POST request to /room.
The data would contain at least a room name -
This should probably be immutable; or we work on an ID.

### Adding source

I guess that this could be completed automatically
when a new source is created/connected. [1]
This would be configured using a JSON POST request to /source
A source is referenced by a UID,
and can optionally have a name
(human readable like `Auditorium Left Camera`).
Also it must have a real stream location (I.E. the DVSwitch location)
and what type of stream it is
(Audio, Video, Audio/Video (Possibly also Idle Loop)).

###### [1] The other important thing to note is that it will need to be decided which part of the back end will handle setting up the on-the-fly re-encoding.

### Configuring a Room

Once a room is added, it can have sources added to it.
By default a room has (no/all - UI decision maybe) sources.
Using the UI socket (API - /room/<id>/ui),
the user can choose which sources are displayed.
A list of sources would be returned from a GET request to /source

## Recording

Once a room is all setup recording can *start*. [2]
A UI will be expected to hook both into the UI socket
and the Mixer socket (API - /room/<id>/mixer).
The UI socket will handle UI related changes (such as displayed sources)
and the Mixer socket will handle any changes related to mixing
(such as cut marks, source changes etc.).
This will allow anything that needs to listen to mixer changes
to only receive the relevant updates. 

###### [2] My understanding of the recording system is that there will be no real start/end points, it will just start when a source starts.

## Creating a Cut Mark

When the user creates a cut mark (/point)
the UI will send a message over the Mixer socket
to indicate the creation of a cut mark.
The server will then send a message indicating
a cut has happened to all connected parties
over the Mixer socket (see caveats).  

## Changing the Source

When the user changes source
(either from one to another, or from single picture to picture in picture)
then the UI will send a message over the Mixer socket
indicating the new state.
As above, the server will then send a message
indicating a new mixer state to all connected clients.

### Editing

There will be a list of cut-lists,
each of which can either be *raw* or *combined* (more info in the API section);
and each can be either *shown* or *hidden*.
I think that all cut-lists should be versioned
so that a history can be tracked and viewed.
This will hopefully prevent any *accidents* from causing problems later.
Once any edits have been made to the cut-list [3]
they can either be saved as a new *combined* cut-list,
or saved into the originating cut list.
Personally, if the start/end points are changed
then it should be a new cut-list;
if they haven't changed then they should be saved
as an edit of the existing cut-list.
Because of this, the ability to hide old cut-lists is important.
A cut-list can also be named and have talk information attached to them
to make searching/viewing easier.
The only thing that has not been considered
is how the UI will actually get the video.

* Will the API need to provide some kind of WebM streams?
* If so then editing will likely become more like the recording as the sources will be streamed and the changes to mixer will need to be connected to.

###### [3] I'm unsure how the cut-lists will be stored and or transmitted; This is probably dependant on how the lists will be interpreted into the final video.

# API Notes

## Room

* Name
* ?Session listing?
* Storage directory.

## Source

* ?Name? - otherwise auto generated
* Raw steam address - the raw DV streaming location
* Low res webm stream address
* High res webm stream address

## Mixer Socket

## Caveats

* Any valid message that is sent will be echoed back to the initiator.
* The exact data that should be sent is still up in the air - I have no idea.
* Not entirely sure how this will fit. Will the UI need to provide a Frame No. or a Time? Will the user be able to add comments/description about a cut point or a time in the video?

## UI Socket

