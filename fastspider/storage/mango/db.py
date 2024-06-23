from pymongo import MongoClient
from pymongo.errors import OperationFailure

from fastspider.logger import logger


class MongoDBWrapper:
    def __init__(self, uri, database_name):
        self.uri = uri
        self.database_name = database_name
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.database_name]
            logger.info(f"Connected to MongoDB database: {self.database_name}")
        except ConnectionError as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise e

    def insert_one(self, collection_name, document):
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return result.inserted_id
        except OperationFailure as e:
            return None

    def insert_many(self, collection_name, documents):
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(documents)
            return result.inserted_ids
        except OperationFailure as e:
            raise e

    def find_one(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.find_one(query)
            return result
        except OperationFailure as e:
            return None

    def find_many(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.find(query)
            return list(result)
        except OperationFailure as e:
            return []

    def update_one(self, collection_name, query, update):
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {'$set': update})
            return result.modified_count
        except OperationFailure as e:
            return 0

    def delete_one(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            return result.deleted_count
        except OperationFailure as e:
            return 0

    def find_all_with_fields(self, collection_name, query: dict = None, fields=[]):
        if query is None:
            query = {}
        try:
            field_map = {'_id': 0}
            for field in fields:
                field_map[field] = 1
            collection = self.db[collection_name]
            cursor = collection.find(query, field_map)
            result = [doc for doc in cursor]
            return result
        except OperationFailure as e:
            logger.error(f"Error finding documents with field {field_name}: {e}")
            return []

    def close(self):
        if self.client:
            self.client.close()
        logger.info(f"Closed MongoDB database: {self.database_name}")
