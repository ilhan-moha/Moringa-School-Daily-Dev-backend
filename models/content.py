from datetime import datetime
from extensions import db


class Content(db.Model):
    __tablename__ = "content"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # video | audio | article
    body_or_url = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending | approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", backref="content_items")
    author = db.relationship("User", backref="content_items")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "body_or_url": self.body_or_url,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "author_id": self.author_id,
            "author": self.author.name if self.author else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }