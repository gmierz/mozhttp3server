import logging

from quart import Quart
from quart.ctx import _request_ctx_stack



class LoggedQuart(Quart):
    async def dispatch_request(self, request_context):
        request = (request_context or _request_ctx_stack.top).request
        if self.logger.level != logging.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"{request.method} {request.url}")
        return await super().dispatch_request(request_context)


app = LoggedQuart(__name__)

@app.route("/")
async def index():
    return "<b>Hello World!</b>"

