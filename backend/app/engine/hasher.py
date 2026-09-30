import hashlib
import json
import io
import base64
from typing import Dict, Any, Tuple
from decimal import Decimal
import qrcode


def _json_serial_fallback(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def create_canonical_report_payload(report_data: Dict[str, Any]) -> str:
    """
    Produces deterministic, canonical JSON representation of report content
    excluding mutable transport headers. Keys are sorted, whitespace is minimized.
    """
    # Exclude dynamic signature containers to form canonical hashable payload
    keys_to_exclude = {"canonical_hash", "qr_data_uri", "updated_at"}
    canonical_dict = {
        k: v for k, v in report_data.items()
        if k not in keys_to_exclude
    }
    return json.dumps(
        canonical_dict,
        sort_keys=True,
        separators=(',', ':'),
        default=_json_serial_fallback,
        ensure_ascii=False
    )


def compute_report_hash(report_data: Dict[str, Any]) -> str:
    """Computes SHA-256 cryptographic hash over canonical report payload."""
    canonical_str = create_canonical_report_payload(report_data)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


def verify_report_integrity(report_data: Dict[str, Any], expected_hash: str) -> bool:
    """Checks whether the report has been modified since it was signed."""
    actual_hash = compute_report_hash(report_data)
    return actual_hash == expected_hash


def generate_verification_qr_code(
    report_number: str,
    sha256_hash: str,
    base_verification_url: str = "https://weighproof.org/verify"
) -> Tuple[str, bytes]:
    """
    Generates QR code embedding verification URL and returns both
    base64 data URI string and raw PNG bytes.
    """
    verification_url = f"{base_verification_url}/{report_number}?hash={sha256_hash}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()
    b64_str = base64.b64encode(raw_bytes).decode("ascii")
    data_uri = f"data:image/png;base64,{b64_str}"

    return data_uri, raw_bytes
