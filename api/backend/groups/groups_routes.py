# Author: Kenneith Chu Chen
# Groups blueprint - routes for groups, members, group habits, and notes

from flask import Blueprint, request, jsonify, make_response
from backend.db_connection.db_connection import get_db

groups_blueprint = Blueprint('groups', __name__)


#
# GET /groups/ - Get all groups
# Supports User Story 2.1, 3.2
#
@groups_blueprint.route('/', methods=['GET'])
def get_all_groups():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT hg.group_id, hg.name, hg.description,
                   hg.is_public, hg.is_active, hg.created_at,
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


#
# GET /groups/<group_id> - Get a specific group with details
# Supports User Story 2.3
#
@groups_blueprint.route('/<int:group_id>', methods=['GET'])
def get_group(group_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT hg.group_id, hg.name, hg.description,
                   hg.is_public, hg.is_active,
                   u.first_name AS creator_first,
                   u.last_name AS creator_last,
                   COALESCE(SUM(CASE WHEN gm.is_active = TRUE THEN 1 ELSE 0 END), 0)
                       AS member_count
            FROM HABIT_GROUPS hg
            JOIN USERS u ON hg.creator_id = u.user_id
            LEFT JOIN GROUP_MEMBERS gm ON hg.group_id = gm.group_id
            WHERE hg.group_id = %s
            GROUP BY hg.group_id, hg.name, hg.description,
                     hg.is_public, hg.is_active,
                     u.first_name, u.last_name
        '''
        cursor.execute(query, (group_id,))
        group = cursor.fetchone()
        cursor.close()
        db.close()

        if group is None:
            return make_response(jsonify({"error": "Group not found"}), 404)

        return make_response(jsonify(group), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# POST /groups/ - Create a new group
# Supports User Story 2.1
#
@groups_blueprint.route('/', methods=['POST'])
def create_group():
    try:
        data = request.get_json()

        required_fields = ['name', 'creator_id']
        for field in required_fields:
            if field not in data:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}), 400
                )

        db = get_db()
        cursor = db.cursor()

        query = '''
            INSERT INTO HABIT_GROUPS (name, description, creator_id,
                                      is_public, is_active)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (
            data['name'],
            data.get('description', ''),
            data['creator_id'],
            data.get('is_public', True),
            True
        ))
        db.commit()
        new_id = cursor.lastrowid

        # Add the creator as a leader of the group
        cursor.execute(
            '''INSERT INTO GROUP_MEMBERS (group_id, user_id, role, is_active)
               VALUES (%s, %s, %s, %s)''',
            (new_id, data['creator_id'], 'leader', True)
        )
        db.commit()
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Group created", "group_id": new_id}), 201
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# GET /groups/<group_id>/members - Get members of a group
# Supports User Story 2.3
#
@groups_blueprint.route('/<int:group_id>/members', methods=['GET'])
def get_group_members(group_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT gm.group_member_id, u.user_id,
                   u.first_name, u.last_name, u.email,
                   gm.role, gm.joined_at, gm.is_active
            FROM GROUP_MEMBERS gm
            JOIN USERS u ON gm.user_id = u.user_id
            WHERE gm.group_id = %s
            ORDER BY gm.role DESC, u.first_name
        '''
        cursor.execute(query, (group_id,))
        members = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(members), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# POST /groups/<group_id>/members - Add a member to a group
# Supports User Story 2.1
#
@groups_blueprint.route('/<int:group_id>/members', methods=['POST'])
def add_group_member(group_id):
    try:
        data = request.get_json() or {}
        if 'user_id' not in data:
            return make_response(jsonify({"error": "Missing required field: user_id"}), 400)

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            '''
                SELECT group_member_id
                FROM GROUP_MEMBERS
                WHERE group_id = %s AND user_id = %s
                LIMIT 1
            ''',
            (group_id, data['user_id'])
        )
        existing_member = cursor.fetchone()

        if existing_member is None:
            cursor.execute(
                '''
                    INSERT INTO GROUP_MEMBERS (group_id, user_id, role, is_active)
                    VALUES (%s, %s, %s, %s)
                ''',
                (group_id, data['user_id'], data.get('role', 'member'), True)
            )
            response_payload = {"message": "Member added to group"}
            status_code = 201
        else:
            cursor.execute(
                '''
                    UPDATE GROUP_MEMBERS
                    SET role = %s, is_active = TRUE
                    WHERE group_member_id = %s
                ''',
                (data.get('role', 'member'), existing_member['group_member_id'])
            )
            response_payload = {"message": "Member reactivated in group"}
            status_code = 200

        db.commit()
        cursor.close()
        db.close()

        return make_response(jsonify(response_payload), status_code)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# DELETE /groups/<group_id>/members/<user_id> - Remove member
# Supports User Story 2.6
#
@groups_blueprint.route('/<int:group_id>/members/<int:user_id>', methods=['DELETE'])
def remove_group_member(group_id, user_id):
    try:
        db = get_db()
        cursor = db.cursor()

        query = '''
            UPDATE GROUP_MEMBERS
            SET is_active = FALSE
            WHERE group_id = %s AND user_id = %s
        '''
        cursor.execute(query, (group_id, user_id))
        db.commit()
        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return make_response(jsonify({"error": "Member not found"}), 404)
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Member removed from group"}), 200
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# POST /groups/<group_id>/habits - Assign a habit to a group
# Supports User Story 2.2
#
@groups_blueprint.route('/<int:group_id>/habits', methods=['POST'])
def assign_group_habit(group_id):
    try:
        data = request.get_json() or {}
        required_fields = ['habit_id', 'assigned_by']
        for field in required_fields:
            if field not in data:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}), 400
                )

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            '''
                SELECT group_habit_id
                FROM GROUP_HABITS
                WHERE group_id = %s AND habit_id = %s
                LIMIT 1
            ''',
            (group_id, data['habit_id'])
        )
        existing_assignment = cursor.fetchone()

        if existing_assignment is None:
            cursor.execute(
                '''
                    INSERT INTO GROUP_HABITS (group_id, habit_id, assigned_by)
                    VALUES (%s, %s, %s)
                ''',
                (group_id, data['habit_id'], data['assigned_by'])
            )
            response_payload = {"message": "Habit assigned to group"}
            status_code = 201
        else:
            cursor.execute(
                '''
                    UPDATE GROUP_HABITS
                    SET assigned_by = %s, assigned_at = CURRENT_TIMESTAMP
                    WHERE group_habit_id = %s
                ''',
                (data['assigned_by'], existing_assignment['group_habit_id'])
            )
            response_payload = {"message": "Habit assignment refreshed"}
            status_code = 200

        db.commit()
        cursor.close()
        db.close()

        return make_response(jsonify(response_payload), status_code)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# GET /groups/<group_id>/habits - Get habits assigned to a group
# Supports User Story 2.2
#
@groups_blueprint.route('/<int:group_id>/habits', methods=['GET'])
def get_group_habits(group_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT gh.group_habit_id, h.habit_id, h.name,
                   h.description, h.frequency,
                   c.name AS category_name
            FROM GROUP_HABITS gh
            JOIN HABITS h ON gh.habit_id = h.habit_id
            JOIN CATEGORIES c ON h.category_id = c.category_id
            WHERE gh.group_id = %s
            ORDER BY h.name
        '''
        cursor.execute(query, (group_id,))
        habits = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(habits), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# POST /groups/notes - Send a note to a group member
# Supports User Story 2.4
#
@groups_blueprint.route('/notes', methods=['POST'])
def send_note():
    try:
        data = request.get_json() or {}
        required_fields = ['sender_id', 'receiver_id', 'message']
        for field in required_fields:
            if field not in data:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}), 400
                )

        db = get_db()
        cursor = db.cursor()

        query = '''
            INSERT INTO NOTES (sender_id, receiver_id, group_id, message)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query, (
            data['sender_id'],
            data['receiver_id'],
            data.get('group_id'),
            data['message']
        ))
        db.commit()
        cursor.close()
        db.close()

        return make_response(jsonify({"message": "Note sent"}), 201)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# GET /groups/<group_id>/notes - Get notes for a group
# Supports User Story 2.4
#
@groups_blueprint.route('/<int:group_id>/notes', methods=['GET'])
def get_group_notes(group_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT n.note_id, n.message, n.sent_at,
                   s.first_name AS sender_first,
                   s.last_name AS sender_last,
                   r.first_name AS receiver_first,
                   r.last_name AS receiver_last
            FROM NOTES n
            JOIN USERS s ON n.sender_id = s.user_id
            JOIN USERS r ON n.receiver_id = r.user_id
            WHERE n.group_id = %s
            ORDER BY n.sent_at DESC
        '''
        cursor.execute(query, (group_id,))
        notes = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(notes), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# GET /groups/<group_id>/summary - Weekly group summary
# Supports User Story 2.5
#
@groups_blueprint.route('/<int:group_id>/summary', methods=['GET'])
def get_group_summary(group_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT
                (
                    SELECT COUNT(*)
                    FROM GROUP_MEMBERS gm
                    WHERE gm.group_id = %s AND gm.is_active = TRUE
                ) AS total_members,
                (
                    SELECT COUNT(*)
                    FROM GROUP_HABITS gh
                    WHERE gh.group_id = %s
                ) AS total_assigned_habits,
                (
                    SELECT COUNT(*)
                    FROM HABIT_LOGS hl
                    JOIN GROUP_HABITS gh ON gh.habit_id = hl.habit_id
                    WHERE gh.group_id = %s
                ) AS total_logs
        '''
        cursor.execute(query, (group_id, group_id, group_id))
        summary = cursor.fetchone()
        cursor.close()
        db.close()

        return make_response(jsonify(summary), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


#
# GET /groups/user/<user_id> - Get groups for a specific user
# Supports User Story 2.1
#
@groups_blueprint.route('/user/<int:user_id>', methods=['GET'])
def get_user_groups(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT hg.group_id, hg.name, hg.description,
                   hg.is_public, hg.is_active,
                   gm.role,
                   COALESCE(SUM(CASE WHEN gm2.is_active = TRUE THEN 1 ELSE 0 END), 0)
                       AS member_count
            FROM GROUP_MEMBERS gm
            JOIN HABIT_GROUPS hg ON gm.group_id = hg.group_id
            LEFT JOIN GROUP_MEMBERS gm2 ON hg.group_id = gm2.group_id
            WHERE gm.user_id = %s AND gm.is_active = TRUE
            GROUP BY hg.group_id, hg.name, hg.description,
                     hg.is_public, hg.is_active, gm.role
        '''
        cursor.execute(query, (user_id,))
        groups = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(groups), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
