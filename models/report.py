from datetime import datetime
from extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending | resolved | dismissed
    resolved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    content = db.relationship("Content", backref="reports")
    reporter = db.relationship("User", foreign_keys=[reporter_id])
    resolved_by = db.relationship("User", foreign_keys=[resolved_by_id])

    def to_dict(self):
        return {
            "id": self.id,
            "content_id": self.content_id,
            "content_title": self.content.title if self.content else None,
            "reporter_id": self.reporter_id,
            "reporter": self.reporter.name if self.reporter else None,
            "reason": self.reason,
            "status": self.status,
            "resolved_by_id": self.resolved_by_id,
            "created_at": self.created_at.isoformat(),
        }