from extensions import db


class Reaction(db.Model):
    __tablename__ = "reactions"

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # like | dislike

    __table_args__ = (
        db.UniqueConstraint("content_id", "user_id", name="one_reaction_per_user"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "type": self.type,
        }