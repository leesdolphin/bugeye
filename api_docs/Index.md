BugEye - Live Mixing and Editing
================================

Conventions
-----------

Where the context is ambiguous; a URL will be specified with `://servername/`
at the start.

All file names should be specified using `some/file/path` where the 'base' url
is the root of the git repository.


Serving Static Files
--------------------

Static files will be served under `://servername/static/` from the `static/`
directory. Additionally `://servername/` and `://servername/index.html`
serve `static/index.html`. Mime types will be guessed from the file name.

Caching should be something considered, so it will probably be acomplished
with HEAD and an ETag(of some description).

Some examples:

 - GET `://servername/` - gets the file `static/index.html`
 - GET `://servername/static/some/file.js` - gets `static/some/file.js`

Live Stream Mixing
------------------


