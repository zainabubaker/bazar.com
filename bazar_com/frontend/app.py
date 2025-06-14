from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# ------------------------------
# Replica servers for load balancing (we’ll use these in Step 2)
CATALOG_REPLICAS = [
    "http://catalog1:5001",
    "http://catalog2:5001"
]
ORDER_REPLICAS = [
    "http://order1:5002",
    "http://order2:5002"
]
catalog_index = 0
order_index = 0

# ------------------------------
# In-memory cache: {item_id: (data, timestamp)}
CACHE = {}
CACHE_TTL = 60  # seconds

# ------------------------------
# Helper: Get next replica (Round-Robin)
def get_next_replica(replica_list, current_index_name):
    global catalog_index, order_index
    if current_index_name == "catalog":
        server = replica_list[catalog_index]
        catalog_index = (catalog_index + 1) % len(replica_list)
    else:
        server = replica_list[order_index]
        order_index = (order_index + 1) % len(replica_list)
    return server

# ------------------------------
@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    catalog_server = get_next_replica(CATALOG_REPLICAS, "catalog")
    response = requests.get(f"{catalog_server}/search/{topic}")
    return jsonify(response.json())

@app.route('/info/<int:item_id>', methods=['GET'])
def info(item_id):
    now = time.time()
    # Check cache first
    if item_id in CACHE:
        data, timestamp = CACHE[item_id]
        if now - timestamp < CACHE_TTL:
            return jsonify(data)

    # Cache miss → call catalog
    catalog_server = get_next_replica(CATALOG_REPLICAS, "catalog")
    response = requests.get(f"{catalog_server}/info/{item_id}")
    data = response.json()

    # Save to cache only if success
    if response.status_code == 200:
        CACHE[item_id] = (data, now)

    return jsonify(data)

@app.route('/purchase/<int:item_id>', methods=['POST'])
def purchase(item_id):
    order_server = get_next_replica(ORDER_REPLICAS, "order")
    response = requests.post(f"{order_server}/purchase/{item_id}")
    return jsonify(response.json())
