from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.writeshelf

# Get all collections
collections = ['users', 'books', 'reviews', 'follows', 'activities']

for collection_name in collections:
    collection = db[collection_name]
    count = collection.count_documents({})
    print(f"\n=== {collection_name.upper()} ({count} documents) ===")
    
    if count > 0:
        print("\nSample documents:")
        for doc in collection.find().limit(3):
            print(doc)
