from models.content import Content
from models.subscription import Subscription
from services.content_service import attach_counts


def get_recommended_content(user):
    subscribed_category_ids = [
        s.category_id for s in Subscription.query.filter_by(user_id=user.id)
    ]

    if not subscribed_category_ids:
        return []

    items = (
        Content.query.filter(
            Content.status == "approved",
            Content.category_id.in_(subscribed_category_ids),
        )
        .order_by(Content.created_at.desc())
        .all()
    )
    return attach_counts(items)