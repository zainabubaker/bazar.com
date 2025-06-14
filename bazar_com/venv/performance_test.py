import time
import requests

URL = "http://localhost:5000"

def measure_response_time(endpoint, method='GET'):
    start = time.time()
    if method == 'GET':
        response = requests.get(f"{URL}{endpoint}")
    else:
        response = requests.post(f"{URL}{endpoint}")
    end = time.time()
    return round((end - start) * 1000, 2), response.json()

def run_tests():
    item_id = 1

    print("=== Measuring /info with Caching ===")
    # First request (cache miss)
    t1, _ = measure_response_time(f"/info/{item_id}")
    print(f"1st /info (cache miss): {t1} ms")

    # Second request (cache hit)
    t2, _ = measure_response_time(f"/info/{item_id}")
    print(f"2nd /info (cache hit): {t2} ms")

    print("\n=== Measuring /purchase (forces invalidation) ===")
    t3, _ = measure_response_time(f"/purchase/{item_id}", method='POST')
    print(f"/purchase: {t3} ms")

    # Request after invalidation (cache miss again)
    t4, _ = measure_response_time(f"/info/{item_id}")
    print(f"/info after purchase (cache miss): {t4} ms")

run_tests()
