import os
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from app.models.user import User, UserRole
from app.models.document import Document
from app.models.conversation import Conversation
from app.schemas.tenant import TenantStats

class TenantStatsService:
    @staticmethod
    def get_stats(db: Session, tenant_id: uuid.UUID) -> TenantStats:
        # 1. Employees count
        employees_count = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.role == UserRole.EMPLOYEE
        ).count()

        # 2. Admins count
        admins_count = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.role == UserRole.ADMIN
        ).count()

        # 3. Documents count
        documents_count = db.query(Document).filter(
            Document.tenant_id == tenant_id
        ).count()

        # 4. Chunks count
        chunks_sum = db.query(func.sum(Document.chunk_count)).filter(
            Document.tenant_id == tenant_id
        ).scalar()
        chunks_count = int(chunks_sum) if chunks_sum is not None else 0

        # 5. Conversations count
        conversations_count = db.query(Conversation).filter(
            Conversation.tenant_id == tenant_id
        ).count()

        # 6. Storage Used Bytes
        storage_used_bytes = 0
        documents = db.query(Document.file_path).filter(
            Document.tenant_id == tenant_id
        ).all()
        for doc in documents:
            if doc.file_path and os.path.exists(doc.file_path):
                try:
                    storage_used_bytes += os.path.getsize(doc.file_path)
                except OSError:
                    pass

        return TenantStats(
            employees_count=employees_count,
            admins_count=admins_count,
            documents_count=documents_count,
            chunks_count=chunks_count,
            conversations_count=conversations_count,
            storage_used_bytes=storage_used_bytes
        )
