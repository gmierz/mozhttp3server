import platform
import pathlib
import os
import json
import time
import functools

from quart import Quart, make_push_promise, url_for, request, abort, Response
from quart.static import send_file

from mozhttp3server.throttling.linux import LinuxThrottler
from mozhttp3server.throttling.macos import MacosThrottler


FIVE_MINUTES = 60 * 5
app = Quart(__name__, static_folder="")
HERE = pathlib.Path(__file__).parent

# init netem (should be elsewhere)
system = platform.system()
if system == "Linux":
    klass = LinuxThrottler
elif system == "Darwin":
    klass = MacosThrottler
else:
    raise Exception("Linux or macOS required")
nic = "eth0"
inbound = True
include = []
exclude = ["dport=22", "sport=22"]
netem = klass(nic, inbound, include, exclude, app.logger)
netem.initialize()
app.throttler = netem


async def common_make_push_promise():
    for static_file in pathlib.Path(HERE, "common").rglob(".*"):
        await make_push_promise(url_for("static", filename=str(static_file)))


async def get_static_page(name):
    await common_make_push_promise()
    for image in pathlib.Path(HERE, name, "images").rglob(".*"):
        await make_push_promise(url_for("", filename=f"{name}/images/{image.name}"))
    return await send_file(str(pathlib.Path(HERE, name, f"{name}.html")))


_CALLERS = {}


def log_caller():
    _CALLERS[request.remote_addr] = time.time()


def last_caller():
    if len(_CALLERS) == 0:
        return None
    by_time = [(when, ip) for ip, when in _CALLERS.items()]
    by_time.sort(reverse=True)
    return by_time[0]


@app.route("/")
async def index():
    return await get_static_page("index")


# static pages we server in h2 and h3
for page in "shopping", "news", "gallery", "photoblog":

    async def _view(page):
        log_caller()
        return await get_static_page(page)

    view = functools.partial(_view, page)
    view.__name__ = page

    app.add_url_rule(f"/{page}.html", view_func=view)


@app.route("/_throttler")
async def th_index():
    return app.throttler.status


def check_key():
    key = request.headers.get("X-WEBNETEM-KEY")
    if key is None or key != os.environ.get("WEBNETEM_KEY"):
        abort(
            Response(
                status=401,
                content_type="application/json",
                response=json.dumps({"ERROR": "Unauthorized"}),
            )
        )


@app.route("/_throttler/shape", methods=["POST"])
async def th_shape():
    check_key()
    log_caller()
    data = await request.get_json()
    return app.throttler.shape(data)


@app.route("/_throttler/reset")
async def th_reset():
    check_key()
    log_caller()
    return app.throttler.teardown()


@app.route("/_throttler/start_test")
async def th_start():
    check_key()
    last = last_caller()
    force = False
    if last is not None:
        when, ip = last
        if ip == request.remote_addr:
            # Same IP, restarting
            force = True
        else:
            # Another IP, but not active in the past 5 minutes
            force = time.time() - when > FIVE_MINUTES

    log_caller()
    return app.throttler.start_test(force=force)


@app.route("/_throttler/stop_test")
async def th_stop():
    check_key()
    log_caller()
    return app.throttler.stop_test()
