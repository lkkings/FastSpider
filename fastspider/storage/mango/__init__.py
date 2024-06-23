from typing import List, Dict

from fastspider import Item
from fastspider.storage.base_storage import BaseStorage
from fastspider.storage.mango.db import MongoDBWrapper


class MangoDB(BaseStorage):
    client: MongoDBWrapper

    def __init__(self, cfg: Dict) -> None:
        super().__init__()
        self.cfg = cfg.get('mongodb',{}).copy()
        self._collection = None

    def init(self):
        mongo_uri = self.cfg['uri']
        database = self.cfg['database']
        self.client = MongoDBWrapper(uri=mongo_uri, database_name=database)

    def all(self):
        return super().all()

    def _save(self, items: List[Item]):
        items = [dict(item) for item in items]
        self.client.insert_many(collection_name=self.collection, documents=items)
