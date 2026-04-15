# Krish Soni - Admin blueprint
# Routes for categories, flagged content, users, and platform metrics

from flask import Blueprint, request, jsonify, make_response
from backend.db_connection.db_connection import get_db

admin_blueprint = Blueprint('admin', __name__)


# ---
# GET /admin/categories - Get all categories
# Supports User Story 3.1
# ---
@admin_blueprint.route('/categories', methods=['GET'])
def get_categories():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT category_id, name, description, created_at
            FROM CATEGORIES
            ORDER BY name
        '''
        cursor.execute(query)
        categories = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(categories), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# POST /admin/categories - Create a new category
# Supports User Story 3.1
# ---
@admin_blueprint.route('/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()

        query = '''
            INSERT INTO CATEGORIES (name, description)
            VALUES (%s, %s)
        '''
        cursor.execute(query, (data['name'], data.get('description', '')))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Category created", "category_id": new_id}), 201
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# PUT /admin/categories/<category_id> - Update a category
# Supports User Story 3.1
# ---
@admin_blueprint.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()

        query = '''
            UPDATE CATEGORIES
            SET name = %s, description = %s
            WHERE category_id = %s
        '''
        cursor.execute(query, (
            data['name'],
            data.get('description', ''),
            category_id
        ))
        db.commit()
        cursor.close()
        db.close()

        return make_response(jsonify({"message": "Category updated"}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# DELETE /admin/categories/<category_id> - Delete a category
# Supports User Story 3.1
# ---
@admin_blueprint.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            'DELETE FROM CATEGORIES WHERE category_id = %s', (category_id,)
        )
        db.commit()
        cursor.close()
        db.close()

        return make_response(jsonify({"message": "Category deleted"}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# GET /admin/groups - Get all groups with member counts
# Supports User Story 3.2
# ---
@admin_blueprint.route('/groups', methods=['GET'])
def get_all_groups_admin():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT hg.group_id, hg.name, hg.description,
                   hg.is_public, hg.is_active,
                   hg.created_at,
                   u.first_name AS creator_first,
                   u.last_name AS creator_last,
                   COALESCE(SUM(CASE WHEN gm.is_active = TRUE THEN 1 ELSE 0 END), 0)
                       AS member_count
            FROM HABIT_GROUPS hg
            JOIN USERS u ON hg.creator_id = u.user_id
            LEFT JOIN GROUP_MEMBERS gm ON hg.group_id = gm.group_id
            GROUP BY hg.group_id, hg.name, hg.description,
                     hg.is_public, hg.is_active, hg.created_at,
                     u.first_name, u.last_name
            ORDER BY hg.created_at DESC
        '''
        cursor.execute(query)
        groups = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(groups), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# GET /admin/flagged - Get all flagged content
# Supports User Story 3.3
# ---
@admin_blueprint.route('/flagged', methods=['GET'])
def get_flagged_content():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT fc.flag_id, fc.content_type, fc.content_id,
                   fc.reason, fc.status, fc.created_at,
                   fc.resolved_at,
                   u.first_name AS reporter_first,
                   u.last_name AS reporter_last
            FROM FLAGGED_CONTENT fc
            JOIN USERS u ON fc.reported_by = u.user_id
            ORDER BY fc.created_at DESC
        '''
        cursor.execute(query)
        flagged = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(flagged), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# PUT /admin/flagged/<flag_id> - Resolve flagged content
# Supports User Story 3.3
# ---
@admin_blueprint.route('/flagged/<int:flag_id>', methods=['PUT'])
def resolve_flagged(flag_id):
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()

        query = '''
            UPDATE FLAGGED_CONTENT
            SET status = %s, resolved_at = NOW()
            WHERE flag_id = %s
        '''
        cursor.execute(query, (data.get('status', 'resolved'), flag_id))
        db.commit()
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Flagged content updated"}), 200
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# DELETE /admin/flagged/<flag_id> - Delete flagged content
# Supports User Story 3.3
# ---
@admin_blueprint.route('/flagged/<int:flag_id>', methods=['DELETE'])
def delete_flagged(flag_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            'DELETE FROM FLAGGED_CONTENT WHERE flag_id = %s', (flag_id,)
        )
        db.commit()
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Flagged content deleted"}), 200
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# GET /admin/metrics - Get platform-wide metrics
# Supports User Story 3.4
# ---
@admin_blueprint.route('/metrics', methods=['GET'])
def get_platform_metrics():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT
                (SELECT COUNT(*) FROM USERS) AS total_users,
                (SELECT COUNT(*) FROM USERS WHERE is_active = TRUE) AS active_users,
                (SELECT COUNT(*) FROM HABIT_LOGS
                 WHERE DATE(completed_at) = CURDATE()) AS habits_logged_today,
                (SELECT COUNT(*) FROM HABIT_GROUPS) AS total_groups
        '''
        cursor.execute(query)
        metrics = cursor.fetchone()
        cursor.close()
        db.close()

        return make_response(jsonify(metrics), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# GET /admin/users - Get all users
# Supports User Story 3.5
# ---
@admin_blueprint.route('/users', methods=['GET'])
def get_all_users():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT user_id, first_name, last_name, email,
                   role, is_active, created_at
            FROM USERS
            ORDER BY created_at DESC
        '''
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(users), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# PUT /admin/users/<user_id>/status - Activate/Deactivate user
# Supports User Story 3.5
# ---
@admin_blueprint.route('/users/<int:user_id>/status', methods=['PUT'])
def toggle_user_status(user_id):
    try:
        data = request.get_json() or {}
        if 'is_active' not in data:
            return make_response(jsonify({"error": "Missing required field: is_active"}), 400)

        db = get_db()
        cursor = db.cursor()

        query = '''
            UPDATE USERS
            SET is_active = %s
            WHERE user_id = %s
        '''
        cursor.execute(query, (data['is_active'], user_id))
        db.commit()
        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return make_response(jsonify({"error": "User not found"}), 404)
        cursor.close()
        db.close()

        status = "activated" if data['is_active'] else "deactivated"
        return make_response(
            jsonify({"message": f"User {status}"}), 200
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ---
# GET /admin/default-habits - Get default suggested habits
# Supports User Story 3.6
# ---
@admin_blueprint.route('/default-habits', methods=['GET'])
def get_default_habits():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT h.habit_id, h.name, h.description,
                   h.frequency, h.daily_goal,
                   c.name AS category_name
            FROM HABITS h
            JOIN CATEGORIES c ON h.category_id = c.category_id
            WHERE h.is_default = TRUE
        '''
        cursor.execute(query)
        defaults = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(defaults), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
