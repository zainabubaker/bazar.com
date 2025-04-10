from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CATALOG_SERVER = "http://catalog:5001"
ORDER_SERVER = "http://order:5002"


@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    response = requests.get(f"{CATALOG_SERVER}/search/{topic}")
    return jsonify(response.json())

@app.route('/info/<int:item_id>', methods=['GET'])
def info(item_id):
    response = requests.get(f"{CATALOG_SERVER}/info/{item_id}")
    return jsonify(response.json())

@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase(item_id):
    response = requests.post(f"{ORDER_SERVER}/purchase/{item_id}")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
