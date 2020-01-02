from flask import Flask, request

app = Flask(__name__)

@app.route('/update/temperature', methods=['GET','PUT','POST'])
def update_temps():
    content = request.get_json()
    print(content['temps']['basement'])
    return "Hit!"


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=4455)
