
# coding: utf-8

# In[1]:


import os
from flask import *
from Bayes_predict import *
from werkzeug import secure_filename
from email_helper import *


# In[ ]:


app = Flask(__name__)
a=PredictSpam()

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/bayes',methods=['GET', 'POST'])
def upload_file():
    data = request.get_data()
    dataList=process_email_content(data.decode('utf8'))
    a.predict(dataList)
    return str(int(a.predict(dataList)))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)

