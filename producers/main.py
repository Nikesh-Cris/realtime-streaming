import json
import random
import time
import uuid
from datetime import datetime
from azure.eventhub import EventHubProducerClient, EventData
from concurrent.futures import ThreadPoolExecutor

# Azure Event Hub details
CONNECTION_STR = '<connection-string>'
EVENT_HUB_NAME = '<event-hub-name>'

# Sample data
products_list = [
    {"id": "P001", "name": "Laptop", "price": 1200.00, "currency": "USD"},
    {"id": "P002", "name": "Phone", "price": 800.00, "currency": "USD"},
    {"id": "P003", "name": "Headphones", "price": 150.00, "currency": "USD"},
    {"id": "P004", "name": "Camera", "price": 600.00, "currency": "EUR"},
    {"id": "P005", "name": "Shoes", "price": 100.00, "currency": "EUR"},
    {"id": "P006", "name": "Watch", "price": 250.00, "currency": "GBP"},
    {"id": "P007", "name": "Power Bank", "price": 45.00, "currency": "GBP"},
    {"id": "P008", "name": "Speaker", "price": 50.00, "currency": "USD"},
    {"id": "P009", "name": "Mouse", "price": 100.00, "currency": "INR"},
    {"id": "P010", "name": "Wireless Headphones", "price": 100.00, "currency": "INR"},
    {"id": "P011", "name": "Smart TV", "price": 500.00, "currency": "USD"},
    {"id": "P012", "name": "PS5", "price": 1000.00, "currency": "USD"},
    {"id": "P013", "name": "Desktop", "price": 1200.00, "currency": "USD"},
]

currency_country_map = {
    "USD": ["United States", "Canada"],
    "EUR": ["Germany", "France", "Spain"],
    "INR": ["India"],
    "GBP": ["United Kingdom"]
}

shop_names = ["SuperStore", "Techie Gadgets", "Fashion Hub", "World Cameras", "Shoe Palace"]

producer = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STR, eventhub_name=EVENT_HUB_NAME)

customer_id = 1

def generate_random_order(customer_id):
    selected_products = random.sample(products_list, random.randint(1, 3))
    for product in selected_products:
        product["qty"] = random.randint(1, 5)
    currency = selected_products[0]["currency"]
    location = random.choice(currency_country_map[currency])
    return {
        "customerId": customer_id,
        "products": selected_products,
        "orderDate": datetime.utcnow().isoformat() + "Z",
        "location": location,
        "shopDetails": {
            "shopId": str(uuid.uuid4()),
            "shopName": random.choice(shop_names)
        },
        "orderId": str(uuid.uuid4())
    }

def send_orders_per_second(start_id, count):
    event_data_batch = producer.create_batch()
    for i in range(count):
        order = generate_random_order(start_id + i)
        print(f"Sending order: {json.dumps(order)}")
        event_data_batch.add(EventData(json.dumps(order)))
    producer.send_batch(event_data_batch)

def main():
    global customer_id
    orders_per_minute = 10000
    orders_per_second = orders_per_minute // 60
    try:
        while True:
            start_time = time.time()
            send_orders_per_second(customer_id, orders_per_second)
            customer_id += orders_per_second
            elapsed = time.time() - start_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
    except KeyboardInterrupt:
        print("Stopped sending events.")
    finally:
        producer.close()

if __name__ == "__main__":
    main()