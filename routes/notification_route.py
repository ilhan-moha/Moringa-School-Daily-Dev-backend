from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.notification_service import (get_user_notifications, mark_notification_as_read, mark_all_notifications_as_read)

notification_bp = Blueprint("notification", __name__, url_prefix="/api/notifications")

@notification_bp.get("")
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    notifications = get_user_notifications(user_id)
    return jsonify({"notifications": [notification.to_dict() for notification in notifications]}), 200

@notification_bp.patch("/<int:notification_id>/read")
@jwt_required()
def mark_as_read(notification_id):
    user_id = int(get_jwt_identity())
    notification = mark_notification_as_read(notification_id, user_id)

    if not notification:
        return jsonify({"message": "Notification not found"}), 404
    return jsonify({"message": "Notification marked as read", "notification": notification.to_dict()}), 200

@notification_bp.patch("/read-all")
@jwt_required()
def mark_all_as_read():
    user_id = int(get_jwt_identity())
    mark_all_notifications_as_read(user_id)
    return jsonify({"message": "All notifications marked as read"}), 200