
from datetime import datetime
from extensions import db

MAX_THREAD_DEPTH = 3


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(
        db.Integer,
        db.ForeignKey("content.id"),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    parent_comment_id = db.Column(
        db.Integer,
        db.ForeignKey("comments.id"),
        nullable=True
    )
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="comments"
    )

    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id])
    )

    def to_dict(self, depth=0, max_depth=MAX_THREAD_DEPTH):
        return {
            "id": self.id,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "user": (
                f"{self.user.first_name} {self.user.last_name}"
                if self.user else None
            ),
            "parent_comment_id": self.parent_comment_id,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "replies": [
                r.to_dict(
                    depth=depth + 1,
                    max_depth=max_depth
                )
                for r in self.replies
            ] if depth < max_depth else [],
        }
