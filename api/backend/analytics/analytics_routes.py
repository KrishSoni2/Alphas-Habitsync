# Matvey Rolett (Data Analyst)
# Analytics blueprint - completion rates, streaks, heatmap, growth data

from flask import Blueprint, request, jsonify, make_response
from backend.db_connection.db_connection import get_db

analytics_blueprint = Blueprint('analytics', __name__)


# --
# GET /analytics/completion-rates - Completion rates by category
# Supports User Story 4.1
# --
@analytics_blueprint.route('/completion-rates', methods=['GET'])
def get_completion_rates():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT c.name AS category_name,
                   COUNT(hl.log_id) AS completion_count
            FROM HABIT_LOGS hl
            JOIN HABITS h ON hl.habit_id = h.habit_id
            JOIN CATEGORIES c ON h.category_id = c.category_id
            WHERE hl.status = 'completed'
            GROUP BY c.name
            ORDER BY completion_count DESC
        '''
        cursor.execute(query)
        rates = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(rates), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# --
# GET /analytics/streaks - Average streak statistics
# Supports User Story 4.2
# --
@analytics_blueprint.route('/streaks', methods=['GET'])
def get_streak_stats():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT AVG(current_streak) AS avg_current_streak,
                   AVG(longest_streak) AS avg_longest_streak,
                   MAX(longest_streak) AS max_streak,
                   COUNT(*) AS total_streaks
            FROM (
                SELECT user_id, habit_id,
                       MAX(current_streak) AS current_streak,
                       MAX(longest_streak) AS longest_streak
                FROM STREAKS
                GROUP BY user_id, habit_id
            ) deduped_streaks
        '''
        cursor.execute(query)
        stats = cursor.fetchone()
        cursor.close()
        db.close()

        return make_response(jsonify(stats), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# --
# GET /analytics/group-vs-solo - Compare group vs solo users
# Supports User Story 4.3
# --
@analytics_blueprint.route('/group-vs-solo', methods=['GET'])
def get_group_vs_solo():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM GROUP_MEMBERS gm
                        WHERE gm.user_id = hl.user_id
                          AND gm.is_active = TRUE
                    ) THEN 'group_user'
                    ELSE 'solo_user'
                END AS user_type,
                COUNT(hl.log_id) AS completion_count
            FROM HABIT_LOGS hl
            WHERE hl.status = 'completed'
            GROUP BY user_type
        '''
        cursor.execute(query)
        comparison = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(comparison), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# --
# GET /analytics/heatmap - Time-of-day heatmap data
# Supports User Story 4.4
# --
@analytics_blueprint.route('/heatmap', methods=['GET'])
def get_heatmap():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT HOUR(completed_at) AS completion_hour,
                   COUNT(*) AS total_completions
            FROM HABIT_LOGS
            WHERE status = 'completed'
            GROUP BY HOUR(completed_at)
            ORDER BY completion_hour
        '''
        cursor.execute(query)
        heatmap = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(heatmap), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# --
# GET /analytics/popular-habits - Most popular habits
# Supports User Story 4.5
# --
@analytics_blueprint.route('/popular-habits', methods=['GET'])
def get_popular_habits():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT h.name, c.name AS category_name,
                   COUNT(hl.log_id) AS times_logged
            FROM HABIT_LOGS hl
            JOIN HABITS h ON hl.habit_id = h.habit_id
            JOIN CATEGORIES c ON h.category_id = c.category_id
            GROUP BY h.habit_id, h.name, c.name
            ORDER BY times_logged DESC
            LIMIT 10
        '''
        cursor.execute(query)
        popular = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(popular), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# --
# GET /analytics/user-growth - User growth over time
# Supports User Story 4.6
# --
@analytics_blueprint.route('/user-growth', methods=['GET'])
def get_user_growth():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT DATE_FORMAT(created_at, '%%Y-%%m') AS month,
                   COUNT(*) AS new_users
            FROM USERS
            GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
            ORDER BY month
        '''
        cursor.execute(query)
        growth = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(growth), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)


# --
# GET /analytics/daily-completions - Daily completion trend
# Supports User Story 4.1
# --
@analytics_blueprint.route('/daily-completions', methods=['GET'])
def get_daily_completions():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = '''
            SELECT DATE(completed_at) AS log_date,
                   COUNT(*) AS total_completions
            FROM HABIT_LOGS
            WHERE status = 'completed'
            GROUP BY DATE(completed_at)
            ORDER BY log_date
        '''
        cursor.execute(query)
        daily = cursor.fetchall()
        cursor.close()
        db.close()

        return make_response(jsonify(daily), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
