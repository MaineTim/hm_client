import dataset
import datetime
import flask
import pprint

version = "2020-11-20.01"

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
            dict(location=key, temperature=round(content["temps"][key], 2)), ["location"]
        )
    table = db["ups"]
    for key in content["ups"]:
        table.upsert(
            dict(var=key, data=content["ups"][key]), ["var"]
        )
    db["data"].upsert(
        dict(data="time", store=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ["data"],
    )
    if content["ups"]["status"] != db["data"].find_one(data="state")["store"]:
        db["data"].upsert(dict(data="state", store=content["ups"]["status"]), ["data"])
        if content["ups"]["status"] == "OB":
            db["data"].upsert(dict(data="lastOB", store=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ["data"]
            )
        else:
            db["data"].upsert(dict(data="lastOL", store=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ["data"]
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
            dict(location=key, temperature=round(content["temps"][key], 2)), ["location"]
        )
    return flask.Response("200 OK", status=200, mimetype="application/json")


# Route renders and returns a status page.
@app.route("/status")
def status():
    temperatures = {}
    # Create a dict of temps for rendering.
    for entry in db["temperatures"].distinct("location", "temperature"):
        temperatures[entry["location"]] = entry["temperature"]
    return flask.render_template(
        "status.html",
        temperatures=temperatures,
        ups_status=db["ups"].find_one(var="status")["data"],
        ups_charge=db["ups"].find_one(var="charge")["data"],
        ups_runtime=db["ups"].find_one(var="runtime")["data"],
        ups_lastOL=db["data"].find_one(data="lastOL")["store"],
        ups_lastOB=db["data"].find_one(data="lastOB")["store"],
        update_time=db["data"].find_one(data="time")["store"],
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


if db["data"].find_one(data="state") == None:
    db["data"].upsert(dict(data="state", store="OL"), ["data"])
    db["data"].upsert(dict(data="lastOL", store="Not available"), ["data"])
    db["data"].upsert(dict(data="lastOB", store="Not available"), ["data"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000)
