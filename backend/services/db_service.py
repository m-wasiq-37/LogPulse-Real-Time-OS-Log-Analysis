import os
from pymongo import MongoClient, DESCENDING
from utils.env_loader import load_env

load_env()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['logpuls']

def get_db():
    return db

def get_user(username):
    return db.users.find_one({'username': username})

def create_user(username, password_hash):
    db.users.insert_one({'username': username, 'password': password_hash})

def save_log(log):
    db.logs.insert_one(log)

def get_logs(limit=100):
    return list(db.logs.find().sort('timestamp', DESCENDING).limit(limit))

def filter_logs(params):
    query = {}
    if 'level' in params and params['level']:
        query['level'] = params['level']
    if 'source' in params and params['source']:
        query['source'] = params['source']
    if 'start' in params and 'end' in params and params['start'] and params['end']:
        query['timestamp'] = {'$gte': params['start'], '$lte': params['end']}
    return list(db.logs.find(query).sort('timestamp', DESCENDING).limit(200))