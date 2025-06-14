from flask import Flask, request, jsonify
import requests
import csv
import datetime
import os

app = Flask(__name__)

ORDER_LOG = 'order_log.csv'
CATALOG_SERVER = os.getenv("CATALOG_SERVER", "http://catalog1:5001")  # Can point to one catalog replica
OTHER_REPLICA = os.getenv("OTHER_REPLICA", "")  # The other order replica
FRONTEND_SERVER = os.getenv("FRONTEND_SERVER", "http://frontend:5000")

def log_order(item_id, title):
    with open(ORDER_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), item_id, title])
@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase(item_id):
    is_forwarded = request.headers.get("X-Replica-Forwarded") == "true"

    if not is_forwarded:
        # Step 1: Get item info from catalog
        info = requests.get(f"{CATALOG_SERVER}/info/{item_id}").json()
        if "quantity" not in info or info["quantity"] <= 0:
            return jsonify({"message": "Out of stock"}), 400

        # Step 2: Invalidate frontend cache
        try:
            requests.post(f"{FRONTEND_SERVER}/invalidate/{item_id}")
        except:
            pass

        # Step 3: Update stock in catalog (only original handles stock update)
        try:
            requests.post(f"{CATALOG_SERVER}/update/{item_id}", json={"quantity": -1})
        except:
            return jsonify({"message": "Catalog update failed"}), 500

        # Step 4: Log the order
        log_order(item_id, info['title'])

        # Step 5: Forward to the other replica
        if OTHER_REPLICA:
            try:
                requests.post(
                    f"{OTHER_REPLICA}/purchase/{item_id}",
                    headers={"X-Replica-Forwarded": "true"}
                )
            except:
                pass

        return jsonify({"message": f"bought book {info['title']}"})
    else:
        # Replica doesn't perform update, just acknowledges
        return jsonify({"message": f"replica acknowledged purchase of item {item_id}"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
