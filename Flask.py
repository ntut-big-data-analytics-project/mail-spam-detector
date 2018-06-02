# coding: utf-8

from flask import *

from api.Bayes_predict import *
from email_helper import *

app = Flask(__name__)
a = None


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/bayes', methods=['GET', 'POST'])
def upload_file():
    global a
    if a is None:
        a = PredictSpam()
    data = request.get_data()
    dataList = process_email_content(data.decode('utf8'))
    ret = a.predict(dataList)
    return str(int(ret))


@app.route('/process-email', methods=['POST'])
def process_email_request():
    data = request.get_data().decode('utf8')
    return EMAIL_CONTENT_DELIMITER.join(process_email_content(data))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4123)
