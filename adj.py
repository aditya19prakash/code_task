from pymongo import MongoClient

# Your MongoDB connection string
connection_string = "mongodb+srv://adiprakash1962001:08NtMEDr3JegxFcH@cluster0.mxx9w0f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to the client
client = MongoClient(connection_string)

# Replace 'your_database_name' with the actual database name
db = client['coding_problems_db']

# Loop through all collections and delete all documents
for collection_name in db.list_collection_names():
    result = db[collection_name].delete_many({})
    print(f"Deleted {result.deleted_count} documents from '{collection_name}' collection.")

print("All data deleted.")
