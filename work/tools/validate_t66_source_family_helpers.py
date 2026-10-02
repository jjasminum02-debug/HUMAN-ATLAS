"""Canonical field hashing for source-family records (separate from HA claims)."""
import hashlib
import json

def value_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()
