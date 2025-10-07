from tinydb import TinyDB, Query
from datetime import datetime
import os

DB_PATH = os.getenv("DATA_STORE_PATH", "data.json")

def _db():
    return TinyDB(DB_PATH)

def load_last_seen():
    db = _db()
    table = db.table('meta')
    recs = table.search(Query().key == 'last_seen')
    if not recs:
        return None
    val = recs[0]['value']
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return None

def save_last_seen(dt: datetime):
    db = _db()
    table = db.table('meta')
    table.upsert({'key': 'last_seen', 'value': dt.isoformat()}, Query().key == 'last_seen')
