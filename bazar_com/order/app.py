from flask import Flask, request, jsonify
import requests
import csv
import datetime

ORDER_LOG = 'order_log.csv'

def log_order(item_id, title):
    with open(ORDER_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), item_id, title])
app = Flask(__name__)

CATALOG_SERVER = "http://catalog:5001"


@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase(item_id):
    # check stock
    info = requests.get(f"{CATALOG_SERVER}/info/{item_id}").json()
    if "quantity" not in info or info["quantity"] <= 0:
        return jsonify({"message": "Out of stock"}), 400

    # update stock
    update_resp = requests.post(f"{CATALOG_SERVER}/update/{item_id}", json={"quantity": -1})
    
    return jsonify({"message": f"bought book {info['title']}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5002)
