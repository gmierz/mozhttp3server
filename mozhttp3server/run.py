from quart import Quart, make_push_promise, url_for
from quart.static import send_file
import pathlib

app = Quart(__name__, static_folder="")
HERE = pathlib.Path(__file__).parent


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
