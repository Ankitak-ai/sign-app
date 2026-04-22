from __future__ import annotations

import json
import uuid
from datetime import datetime, UTC
from pathlib import Path

STORAGE_DIR = Path(".local_storage")
METADATA_FILE = STORAGE_DIR / "contracts.jsonl"


def save_contract_record(contract_data: dict, unsigned_pdf: bytes, signature: bytes | None = None, signed_pdf: bytes | None = None) -> str:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    contract_id = str(uuid.uuid4())

    unsigned_path = STORAGE_DIR / f"{contract_id}_unsigned.pdf"
    unsigned_path.write_bytes(unsigned_pdf)

    signature_path = None
    if signature:
        signature_path = STORAGE_DIR / f"{contract_id}_signature.png"
        signature_path.write_bytes(signature)

    signed_path = None
    if signed_pdf:
        signed_path = STORAGE_DIR / f"{contract_id}_signed.pdf"
        signed_path.write_bytes(signed_pdf)

    record = {
        "contract_id": contract_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "contract_data": contract_data,
        "unsigned_pdf": str(unsigned_path),
        "signature": str(signature_path) if signature_path else None,
        "signed_pdf": str(signed_path) if signed_path else None,
    }
    with METADATA_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return contract_id
