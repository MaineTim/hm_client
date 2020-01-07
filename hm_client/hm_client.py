import dataset
import datetime
import flask
import pprint

version = "2020-01-05.01"

app = flask.Flask(__name__)
db = dataset.connect(
    url="sqlite:///data.db",
    engine_kwargs={"connect_args": {"check_same_thread": False}},
)


# Route accepts a json string that contains update data and
# stores it in an SQL db.
@app.route("/update", methods=["POST"])
def update():
    content = flask.request.get_json()
    table = db["temperatures"]
    for key in content["temps"]:
        table.upsert(
            dict(location=key, temperature=content["temps"][key]), ["location"]
        )
    db["data"].upsert(
        dict(data="time", time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ["data"],
    )
    return flask.Response("200 OK", status=200, mimetype="application/json")


# Route accepts a json string that contains temperature data and
# stores it in an SQL db.
@app.route("/update/temperature", methods=["POST"])
def update_temps():
    content = flask.request.get_json()
    table = db["temperatures"]
    for key in content["temps"]:
        table.upsert(
            dict(location=key, temperature=content["temps"][key]), ["location"]
        )
    return flask.Response("200 OK", status=200, mimetype="application/json")


# Route renders and returns a status page.
@app.route("/status")
def status():
    temperatures = {}
    # Create a dict of temps for rendering.
    for entry in db["temperatures"].distinct("location", "temperature"):
        temperatures[entry["location"]] = entry["temperature"]
    update_time = db["data"].find_one(data="time")["time"]
    return flask.render_template(
        "status.html",
        temperatures=temperatures,
        update_time=update_time,
        version=version,
    )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return_string = """
<html>
    <head>
        <title>Housemon Ver. %s</title>
    </head>
    <body>
        <p>The path you seek, /%s, is not the path to enlightenment.</p>
    </body>
</html>"""
    return return_string % (version, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
