from extensions import db


class Wishlist(db.Model):
    __tablename__ = "wishlist"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "content_id", name="one_wishlist_entry"),
    )