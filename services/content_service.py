from extensions import db
from models.content import Content
from models.reaction import Reaction
from models.comment import Comment
from services.notification_service import create_content_notifications



def create_content(data, current_user):
    status = "approved" if current_user.role in ("admin", "writer") else "pending"

    content = Content(
        title=data["title"],
        type=data["type"],
        body_or_url=data["body_or_url"],
        category_id=data["category_id"],
        author_id=current_user.id,
        status=status,
    )
    db.session.add(content)
    db.session.commit()

    if content.status == "approved":
        create_content_notifications(content)

    return content

def approve_content(content):
    content.status = "approved"
    db.session.commit()

    create_content_notifications(content)

    return content


def update_content(content, data):
    for field in ("title", "body_or_url", "category_id"):
        if field in data:
            setattr(content, field, data[field])
    db.session.commit()
    return content


def approve_content(content):
    content.status = "approved"
    db.session.commit()
    return content


def get_feed(category_id=None):
    query = Content.query.filter_by(status="approved")
    if category_id:
        query = query.filter_by(category_id=category_id)
    items = query.order_by(Content.created_at.desc()).all()
    return attach_counts(items)


def get_pending():
    items = Content.query.filter_by(status="pending").order_by(Content.created_at.desc()).all()
    return attach_counts(items)


def get_content_with_counts(content):
    """Single-item version, for GET /api/content/:id"""
    return attach_counts([content])[0]


def attach_counts(items):
    """Adds real likes/dislikes/comments_count to each content item's dict.
    Returns a list of dicts (not Content objects) — routes should return these directly."""
    result = []
    for item in items:
        likes = Reaction.query.filter_by(content_id=item.id, type="like").count()
        dislikes = Reaction.query.filter_by(content_id=item.id, type="dislike").count()
        comments_count = Comment.query.filter_by(content_id=item.id).count()

        data = item.to_dict()
        data["likes"] = likes
        data["dislikes"] = dislikes
        data["comments_count"] = comments_count
        result.append(data)
    return result


def validate_content_payload(data):
    required = ["title", "type", "body_or_url", "category_id"]
    if not all(data.get(f) for f in required):
        return "title, type, body_or_url, and category_id are required"
    if data["type"] not in ("video", "audio", "article"):
        return "type must be video, audio, or article"
    return None