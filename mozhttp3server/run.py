from quart import Quart, make_push_promise, url_for
from quart.static import send_file
import pathlib

app = Quart(__name__, static_folder="")
HERE = pathlib.Path(__file__).parent


def common_make_push_promise():
	for static_file in pathlib.Path(HERE, "common").rglob(".*"):
		await make_push_promise(url_for("static", filename=str(static_file)))


@app.route("/")
async def index():
	return "<b>Hello World!</b>"


@app.route("/shopping.html")
async def shopping():
	common_make_push_promise()
	for image in pathlib.Path(HERE, "shopping/images").rglob(".*"):
		await make_push_promise(url_for("", filename=f"shopping/images/{image.name}"))
	return await send_file(str(pathlib.Path(HERE, "shopping/shopping.html")))


@app.route("/other")
async def other():
    return "<b>Other</b>"
