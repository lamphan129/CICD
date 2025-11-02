from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime, timedelta
import json


app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('build_results.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/builds')
def get_builds():
    """Get last 30 days of builds"""
    conn = get_db_connection()
    builds = conn.execute('''
        SELECT * FROM builds 
        ORDER BY timestamp DESC 
        LIMIT 30
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(build) for build in builds])


@app.route('/api/build/<int:build_id>')
def get_build_details(build_id):
    """Get detailed information about a specific build"""
    conn = get_db_connection()
    
    build = conn.execute('SELECT * FROM builds WHERE id = ?', (build_id,)).fetchone()
    failures = conn.execute('''
        SELECT * FROM test_failures WHERE build_id = ?
    ''', (build_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'build': dict(build),
        'failures': [dict(failure) for failure in failures]
    })


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    conn = get_db_connection()
    
    # Last 7 days success rate
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_builds,
            SUM(CASE WHEN failed = 0 AND build_status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_builds,
            AVG(duration) as avg_duration,
            SUM(failed) as total_failures
        FROM builds
        WHERE timestamp > ?
    ''', (seven_days_ago,)).fetchone()
    
    # Most failing tests
    failing_tests = conn.execute('''
        SELECT test_name, COUNT(*) as failure_count
        FROM test_failures
        WHERE build_id IN (
            SELECT id FROM builds WHERE timestamp > ?
        )
        GROUP BY test_name
        ORDER BY failure_count DESC
        LIMIT 10
    ''', (seven_days_ago,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'stats': dict(stats),
        'most_failing_tests': [dict(test) for test in failing_tests]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)