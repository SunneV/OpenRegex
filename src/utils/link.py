import base64
import json
import zlib

from project import log


def encode_dict(data: dict) -> str:
    """Compresses a dictionary using zlib and encodes it in URL-safe Base64."""
    json_data = json.dumps(data, separators=(",", ":")).encode()
    compressed = zlib.compress(json_data)
    encoded = base64.urlsafe_b64encode(compressed).decode().rstrip("=")
    log.debug(f"Link length: {len(encoded)}")
    return encoded


def decode_dict(encoded: str) -> dict:
    """Decodes a URL-safe Base64 encoded string and decompresses it with zlib."""
    padded_encoded = encoded + "=" * (-len(encoded) % 4)  # Add padding back if removed
    compressed = base64.urlsafe_b64decode(padded_encoded)
    json_data = zlib.decompress(compressed).decode()
    return json.loads(json_data)
