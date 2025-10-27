from flask import Blueprint

participants_bp = Blueprint('participants', __name__)

@participants_bp.route('/participants')
def list_participants():
    return "Participants list coming soon"
