import asyncio
import traceback

from aiohttp.web import HTTPError
from html import escape as he

@asyncio.coroutine
def _format_error(app, request, e):
    ## Format the error nicely and pass it up the chain.
    if e.text.startswith(str(e.status_code)):
        ## Default error message - Let's make it look decent.
        content = "<html><body><h1>{code} {reason}</h1>"
        content += "<p>An error occured in bugeye whilst trying to complete "
        content += "your request to <code>{path}</code>.</p>"
        content += "<p><pre><code>"
        content += he("".join(traceback.format_exception(e.__class__, e, None)))
        content += "</code></pre></p>"
        content += "<h2>Registered Routes</h2>"
        content += "<ul>"
        for name in app.router:
            route = app.router[name ]
            content += ("<li><b>{method}</b> <i>{name}</i><br /><code>    {" +
                        "str}</code></li>").format(**{
                'method': he(route.method),
                'name': he(name),
                'str': he(repr(route))})

        content += "</ul></body></html>"
        format_vals = {
            'code': e.status_code,
            'reason': e.reason,
            'path': request.path_qs,
        }

        e.text = content.format(**format_vals)
        e.content_type = "text/html"
    raise e


@asyncio.coroutine
def pretty_error(app, hanlder):
    @asyncio.coroutine
    def middleware(request):
        try:
            return (yield from hanlder(request))
        except HTTPError as e:
            return (yield from _format_error(app, request, e))

    return middleware
