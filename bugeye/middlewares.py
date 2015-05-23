__author__ = 'lee'

import asyncio
import traceback

from aiohttp.web import HTTPError

@asyncio.coroutine
def pretty_error(app, hanlder):
    @asyncio.coroutine
    def middleware(request):
        try:
            return (yield from hanlder(request))
        except HTTPError as e:
            ## Format the error nicely and pass it up the chain.
            if e.text.startswith(str(e.status_code)):
                ## Default error message - Let's make it look decent.
                content = """<html><body><h1>{code} &nbsp; {reason}</h1>

                <p>An error occured in bugeye whilst trying to complete your request to <code>{path}</code>.</p>
                """
                content += "<p><code><pre>" + "".join(traceback.format_exception(e.__class__, e, None)) + \
                           "</code></pre></p>"
                content += "<p>A wise man once told me - know your exceptions</p>"
                content += "</body></html>"
                format_vals = {
                    'code': e.status_code,
                    'reason': e.reason,
                    'path': request.path_qs,
                }
                e.text = content.format(**format_vals)
                e.content_type = "text/html"
            raise
    return middleware
