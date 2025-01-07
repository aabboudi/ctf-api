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
client = MongoClient(MONGO_URI)
db = client['players']
players_collection = db['profiles']

# Create Indexes
players_collection.create_index(
  [('username', 1),
  ('nccid', 1),
  ('macaddr', 1),
  ('ipaddr', 1)], 
  unique=True
)
