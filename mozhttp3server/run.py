import platform
from quart import Quart, make_push_promise, url_for, request, abort
from quart.static import send_file
import pathlib
import os

from mozhttp3server.throttling.linux import LinuxThrottler
from mozhttp3server.throttling.macos import MacosThrottler


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


@app.route("/")
async def index():
    return await get_static_page("index")


@app.route("/shopping.html")
async def shopping():
    return await get_static_page("shopping")


@app.route("/news.html")
async def news():
    return await get_static_page("news")


@app.route("/_throttler")
async def th_index():
    return app.throttler.status


def check_key():
    key = request.headers.get("X-WEBNETEM-KEY")
    if key is None or key != os.environ.get("WEBNETEM-KEY"):
        abort(401)


@app.route("/_throttler/shape", methods=["POST"])
async def th_shape():
    check_key()
    data = await request.get_json()
    return app.throttler.shape(data)


@app.route("/_throttler/reset")
async def th_reset():
    check_key()
    return app.throttler.teardown()
