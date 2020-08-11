from quart import Quart

app = Quart(__name__)

@app.route("/")
async def index():
    return "<b>Hello World!</b>"

