from flask import *
import json
import requests
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/weather', methods=['POST'])
def query_weather():
    data = json.loads(request.get_data(as_text=True))

    return 'fuck'


if __name__ == '__main__':
    app.run()
