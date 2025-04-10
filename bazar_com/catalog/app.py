from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

DATA_FILE = 'catalog_data.csv'

def read_catalog():
    with open(DATA_FILE, newline='') as f:
        return list(csv.DictReader(f))

def write_catalog(data):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "topic", "quantity", "price"])
        writer.writeheader()
        writer.writerows(data)

@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    catalog = read_catalog()
    results = [ {"id": item["id"], "title": item["title"]} for item in catalog if item["topic"] == topic ]
    return jsonify(results)

@app.route('/info/<int:item_id>', methods=['GET'])
def info(item_id):
    catalog = read_catalog()
    for item in catalog:
        if int(item["id"]) == item_id:
            return jsonify({
                "title": item["title"],
                "quantity": int(item["quantity"]),
                "price": float(item["price"])
            })
    return jsonify({"error": "Item not found"}), 404

@app.route('/update/<int:item_id>', methods=['POST'])
def update(item_id):
    update_data = request.json
    catalog = read_catalog()
    updated = False

    for item in catalog:
        if int(item["id"]) == item_id:
            item["quantity"] = str(int(item["quantity"]) + update_data.get("quantity", 0))
            item["price"] = str(update_data.get("price", float(item["price"])))
            updated = True
            break

    if updated:
        write_catalog(catalog)
        return jsonify({"message": "Updated successfully"})
    else:
        return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5001)
