from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from pymongo import MongoClient
import urllib.request
import json
# from selenium import webdriver
from bs4 import BeautifulSoup

app = Flask(__name__)
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post', methods=['POST'])
def post_request():
    url = request.form["url"]
    with urllib.request.urlopen(url) as response:
        html = response.read()
    soup=BeautifulSoup(html, "html.parser")
    # print(type(soup))
    # <class 'bs4.BeautifulSoup'>

    # string
    import re
    soup=str(soup)
    soup= re.sub('<[^>]*>','/',soup)
    # print(soup)

    # import nltk
    # soup_tokens = nltk.word_tokenize(soup)

    # /でsplitするのが一番キレイ（\u3000はhtmlに表示した際には空白に変換される）
    soup_tokens = soup.split("/")
    # print(soup_tokens)
    # title=[w for w in soup_tokens if re.search('^第', w)]
    sentence_tokens=[w for w in soup_tokens if re.search('[ぁ-んァ-ン一-龥]', w)]
    # print(sentence_tokens)

    data = {
            "Inputs": {
                    "input1":
                    [
                    {
                            'ID': "",
                            'sentences': "",
                            'label': "",
                            'sub_label': "",

                    }
                    ],
            },
        "GlobalParameters":  {
        }
     }
    for i in range(len(sentence_tokens)):
        data["Inputs"]['input1'].append({
                            'ID': "",
                            'sentences': sentence_tokens[i],
                            'label': "",
                            'sub_label': "",
        })

    body = str.encode(json.dumps(data))
    url = 'https://japaneast.services.azureml.net/subscriptions/d73fbe84f4b54375ade5a9bee7b54f9b/services/3f34940641ed44028d5b1a741f38f7e4/execute?api-version=2.0&format=swagger'
    api_key = 'H/JXCpXwfNcUv2jzd/+zD8xxVYO1PO7mbSzESoC6uw93V0GMeWz/kCCiXVlRGKExqrmgQsze4TBIJe++WZWleA==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        bytes_result = response.read()
        str_result = bytes_result.decode("UTF-8")
        import nltk
        str_result_tokens = nltk.word_tokenize(str_result)
        import re
        label_list=[w for w in str_result_tokens if re.search('aaa|bbb', w)]
        print(label_list)

        data2 = {
                                "sentences":[{"文":"1"}],
                                "label": [{"ラベル":"1"}]
         }

        for i in range(len(sentence_tokens)):
            data2["sentences"].append({
                                "文":sentence_tokens[i]
            })

        for i in range(len(label_list)):
            data2["label"].append({
                                "ラベル":label_list[i]
            })

        client = MongoClient("mongodb://zakishima:cUwtgzOWiY7D4Sn8FYi12aE1itKZRhg8pzRDGc5h1F36i6xyahyzjsCIpAbnhUEQNeejWNWlsAVPvjEYoHjlyQ==@zakishima.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")
        db = client.testdb
        co = db.collection3
        co.insert_one(data2)

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))

if __name__ == "__main__":
    app.run()
