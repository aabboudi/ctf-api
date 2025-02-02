import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
# MongoDB Connection URI
MONGO_URI = os.getenv('MONGODB_URI')

# JWT Token
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

# Database Client
client = MongoClient(MONGO_URI)
db = client['players']
players_collection = db['profiles']
flags_collection = db['flags']

staff_db = client['staff']
singletons_collection = staff_db['singletons']
store_collection = staff_db['store']

# Database Indexes
players_collection.create_index(
  [('username', 1),
  ('nccid', 1),
  ('macaddr', 1),
  ('ipaddr', 1)], 
  unique=True
)

flags_collection.create_index(
  [('flag', 1),],
  unique=True
)

store_collection.create_index(
  [('itemid', 1),],
  unique=True
)
