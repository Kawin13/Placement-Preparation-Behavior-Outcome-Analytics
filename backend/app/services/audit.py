from typing import Any, Dict, Optional
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.core.logging import logger

SENSITIVE_KEYS = {"password", "token", "password_hash", "secret", "authorization"}


def _sanitize_details(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively removes sensitive keys and serializes Decimal/UUID from audit log metadata."""
    if not data or not isinstance(data, dict):
        return data
    sanitized = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_KEYS:
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = _sanitize_details(v)
        elif isinstance(v, Decimal):
            sanitized[k] = float(v)
        elif isinstance(v, uuid.UUID):
            sanitized[k] = str(v)
        else:
            sanitized[k] = v
    return sanitized


class AuditService:
    @staticmethod
    def record_event(
        db: Session,
        institution_id: uuid.UUID,
        action: str,
        entity_type: str,
        actor_user_id: Optional[uuid.UUID] = None,
        entity_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details_json: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Creates an immutable audit log record for security and administrative events.
        Automatically redacts any sensitive keys.
        """
        sanitized_details = _sanitize_details(details_json)
        audit_entry = AuditLog(
            institution_id=institution_id,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            details_json=sanitized_details,
        )
        db.add(audit_entry)
        try:
            db.commit()
            db.refresh(audit_entry)
            logger.info(f"Audit event logged: action={action} entity={entity_type}:{entity_id} actor={actor_user_id}")
            return audit_entry
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to record audit event: {exc}")
            raise
