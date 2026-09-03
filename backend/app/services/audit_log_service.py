from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogOut


class AuditLogService:
    def get_audit_logs(
        self,
        db: Session,
        limit: int = 50,
    ) -> list[AuditLogOut]:
        rows = (
            db.query(AuditLog)
            .order_by(
                AuditLog.created_at.desc(),
                AuditLog.id.desc(),
            )
            .limit(limit)
            .all()
        )

        return [
            AuditLogOut.model_validate(row)
            for row in rows
        ]
