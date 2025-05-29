
from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["iot_data"]
collection = db["weights"]

@app.get("/current-weight")
def get_current_weight():
    latest_entry = collection.find_one(sort=[("timestamp", -1)])
    if latest_entry:
        return {
            "weight": latest_entry.get("weight", 0),
            "timestamp": datetime.fromtimestamp(latest_entry.get("timestamp", 0)).isoformat()
        }
    else:
        return {"weight": 0, "timestamp": ""}
