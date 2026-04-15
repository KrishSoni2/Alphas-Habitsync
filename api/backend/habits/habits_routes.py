# Sahib Chawla
# Habits blueprint - routes for habits, streaks, goals, and completions

from datetime import date

from flask import Blueprint, request, jsonify, make_response
from backend.db_connection.db_connection import get_db

habits_blueprint = Blueprint('habits', __name__)


def _get_next_streak(current_streak, last_logged_date, frequency):
    """Calculate the next streak value for daily and weekly habits."""
    today = date.today()

    if last_logged_date is None or last_logged_date > today:
        return 1

    days_since_last_log = (today - last_logged_date).days
    normalized_frequency = frequency.lower()

    if normalized_frequency == 'weekly':
        return current_streak + 1 if 0 < days_since_last_log <= 7 else 1

    return current_streak + 1 if days_since_last_log == 1 else 1


# ----
# GET /habits/user/<user_id> - Get all habits for a user
# Supports User Story 1.2, 1.4
# ----
@habits_blueprint.route('/user/<int:user_id>', methods=['GET'])
def get_user_habits(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT h.habit_id, h.name, h.description, h.frequency,
                   h.daily_goal, h.is_active, h.is_public,
                   c.name AS category_name, c.category_id
            FROM HABITS h
            JOIN CATEGORIES c ON h.category_id = c.category_id
            WHERE h.user_id = %s
            ORDER BY c.name, h.name
        '''
        cursor.execute(query, (user_id,))
        habits = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(habits), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# POST /habits - Create a new habit
# Supports User Story 1.1
# ----
@habits_blueprint.route('/', methods=['POST'])
def create_habit():
    try:
        data = request.get_json()

        required_fields = ['user_id', 'category_id', 'name', 'frequency']
        for field in required_fields:
            if field not in data:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}), 400
                )

        db = get_db()
        cursor = db.cursor()

        query = '''
            INSERT INTO HABITS (user_id, category_id, name, description,
                               frequency, daily_goal, is_public, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query, (
            data['user_id'],
            data['category_id'],
            data['name'],
            data.get('description', ''),
            data['frequency'],
            data.get('daily_goal', 1),
            data.get('is_public', False),
            True
        ))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Habit created", "habit_id": new_id}), 201
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# PUT /habits/<habit_id> - Update a habit
# Supports User Story 1.1 (editing)
# ----
@habits_blueprint.route('/<int:habit_id>', methods=['PUT'])
def update_habit(habit_id):
    try:
        data = request.get_json() or {}
        required_fields = ['name', 'category_id', 'frequency']
        for field in required_fields:
            if field not in data:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}), 400
                )

        db = get_db()
        cursor = db.cursor()

        query = '''
            UPDATE HABITS
            SET name = %s, description = %s, category_id = %s,
                frequency = %s, daily_goal = %s, is_public = %s
            WHERE habit_id = %s
        '''
        cursor.execute(query, (
            data['name'],
            data.get('description', ''),
            data['category_id'],
            data['frequency'],
            data.get('daily_goal', 1),
            data.get('is_public', False),
            habit_id
        ))
        db.commit()
        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return make_response(jsonify({"error": "Habit not found"}), 404)
        cursor.close()
        db.close()

        return make_response(jsonify({"message": "Habit updated"}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# DELETE /habits/<habit_id> - Delete a habit
# ----
@habits_blueprint.route('/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('DELETE FROM HABIT_LOGS WHERE habit_id = %s', (habit_id,))
        cursor.execute('DELETE FROM STREAKS WHERE habit_id = %s', (habit_id,))
        cursor.execute('DELETE FROM HABIT_SCHEDULE WHERE habit_id = %s', (habit_id,))
        cursor.execute('DELETE FROM GROUP_HABITS WHERE habit_id = %s', (habit_id,))
        cursor.execute('DELETE FROM AI_RECOMMENDATIONS WHERE habit_id = %s', (habit_id,))
        cursor.execute('DELETE FROM HABITS WHERE habit_id = %s', (habit_id,))
        db.commit()
        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return make_response(jsonify({"error": "Habit not found"}), 404)
        cursor.close()
        db.close()

        return make_response(jsonify({"message": "Habit deleted"}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# POST /habits/complete - Log a habit completion
# Supports User Story 1.3
# ----
@habits_blueprint.route('/complete', methods=['POST'])
def complete_habit():
    try:
        data = request.get_json() or {}
        required_fields = ['habit_id', 'user_id']
        for field in required_fields:
            if field not in data:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}), 400
                )

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            '''
                SELECT habit_id, frequency
                FROM HABITS
                WHERE habit_id = %s AND is_active = TRUE
            ''',
            (data['habit_id'],)
        )
        habit = cursor.fetchone()
        if habit is None:
            cursor.close()
            db.close()
            return make_response(jsonify({"error": "Habit not found"}), 404)

        status = data.get('status', 'completed')
        if status == 'completed':
            cursor.execute(
                '''
                    SELECT log_id
                    FROM HABIT_LOGS
                    WHERE habit_id = %s
                      AND user_id = %s
                      AND status = 'completed'
                      AND DATE(completed_at) = CURDATE()
                    LIMIT 1
                ''',
                (data['habit_id'], data['user_id'])
            )
            existing_log = cursor.fetchone()
            if existing_log is not None:
                cursor.execute(
                    '''
                        SELECT MAX(current_streak) AS current_streak,
                               MAX(longest_streak) AS longest_streak
                        FROM STREAKS
                        WHERE user_id = %s AND habit_id = %s
                    ''',
                    (data['user_id'], data['habit_id'])
                )
                streak_snapshot = cursor.fetchone() or {}
                cursor.close()
                db.close()
                return make_response(
                    jsonify({
                        "message": "Habit already completed today",
                        "current_streak": streak_snapshot.get('current_streak', 0),
                        "longest_streak": streak_snapshot.get('longest_streak', 0)
                    }),
                    200
                )

        query = '''
            INSERT INTO HABIT_LOGS (habit_id, user_id, completed_at, status)
            VALUES (%s, %s, NOW(), %s)
        '''
        cursor.execute(query, (
            data['habit_id'],
            data['user_id'],
            status
        ))

        streak_payload = None
        if status == 'completed':
            cursor.execute(
                '''
                    SELECT streak_id, current_streak, longest_streak, last_logged_date
                    FROM STREAKS
                    WHERE user_id = %s AND habit_id = %s
                    ORDER BY last_logged_date DESC, streak_id DESC
                    LIMIT 1
                ''',
                (data['user_id'], data['habit_id'])
            )
            existing_streak = cursor.fetchone()
            next_streak = _get_next_streak(
                existing_streak['current_streak'] if existing_streak else 0,
                existing_streak['last_logged_date'] if existing_streak else None,
                habit['frequency']
            )
            longest_streak = max(
                existing_streak['longest_streak'] if existing_streak else 0,
                next_streak
            )

            if existing_streak is None:
                cursor.execute(
                    '''
                        INSERT INTO STREAKS (
                            user_id, habit_id, current_streak, longest_streak, last_logged_date
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    ''',
                    (data['user_id'], data['habit_id'], next_streak, longest_streak, date.today())
                )
            else:
                cursor.execute(
                    '''
                        UPDATE STREAKS
                        SET current_streak = %s,
                            longest_streak = %s,
                            last_logged_date = %s
                        WHERE streak_id = %s
                    ''',
                    (next_streak, longest_streak, date.today(), existing_streak['streak_id'])
                )

            streak_payload = {
                "current_streak": next_streak,
                "longest_streak": longest_streak
            }

        db.commit()
        cursor.close()
        db.close()

        return make_response(
            jsonify({
                "message": "Habit completion logged",
                **(streak_payload or {})
            }),
            201
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# GET /habits/streaks/<user_id> - Get streaks for a user
# Supports User Story 1.2
# ----
@habits_blueprint.route('/streaks/<int:user_id>', methods=['GET'])
def get_user_streaks(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT h.habit_id, h.name AS habit_name,
                   MAX(s.current_streak) AS current_streak,
                   MAX(s.longest_streak) AS longest_streak,
                   MAX(s.last_logged_date) AS last_logged_date
            FROM STREAKS s
            JOIN HABITS h ON s.habit_id = h.habit_id
            WHERE s.user_id = %s
            GROUP BY h.habit_id, h.name
            ORDER BY current_streak DESC, habit_name
        '''
        cursor.execute(query, (user_id,))
        streaks = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(streaks), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# GET /habits/goals/<user_id> - Get goals for a user
# Supports User Story 1.6
# ----
@habits_blueprint.route('/goals/<int:user_id>', methods=['GET'])
def get_user_goals(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT goal_id, goal_type, target_value, created_at
            FROM GOALS
            WHERE user_id = %s
        '''
        cursor.execute(query, (user_id,))
        goals = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(goals), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# POST /habits/goals - Create a new goal
# Supports User Story 1.6
# ----
@habits_blueprint.route('/goals', methods=['POST'])
def create_goal():
    try:
        data = request.get_json()
        db = get_db()
        cursor = db.cursor()

        query = '''
            INSERT INTO GOALS (user_id, goal_type, target_value)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(query, (
            data['user_id'],
            data['goal_type'],
            data['target_value']
        ))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        return make_response(
            jsonify({"message": "Goal created", "goal_id": new_id}), 201
        )

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# ----
# GET /habits/logs/<user_id> - Get habit logs for a user
# Supports User Story 1.2, 1.3
# ----
@habits_blueprint.route('/logs/<int:user_id>', methods=['GET'])
def get_user_logs(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT hl.log_id, h.name AS habit_name,
                   hl.completed_at, hl.status
            FROM HABIT_LOGS hl
            JOIN HABITS h ON hl.habit_id = h.habit_id
            WHERE hl.user_id = %s
            ORDER BY hl.completed_at DESC
            LIMIT 50
        '''
        cursor.execute(query, (user_id,))
        logs = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(logs), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
