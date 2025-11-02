import json
import sqlite3
from datetime import datetime
import os


def process_test_results():
    """Process pytest JSON results and store in database"""
    
    # Read test results
    with open('report.json', 'r') as f:
        results = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect('dashboard/build_results.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            total_tests INTEGER,
            passed INTEGER,
            failed INTEGER,
            skipped INTEGER,
            duration REAL,
            build_status TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            build_id INTEGER,
            test_name TEXT,
            file_path TEXT,
            line_number INTEGER,
            error_message TEXT,
            traceback TEXT,
            FOREIGN KEY (build_id) REFERENCES builds(id)
        )
    ''')
    
    # Check build status
    build_log_exists = os.path.exists('build.log')
    with open('build.log', 'r') as f:
        build_log = f.read()
        build_status = 'SUCCESS' if 'error' not in build_log.lower() else 'FAILED'
    
    # Insert build summary
    cursor.execute('''
        INSERT INTO builds (timestamp, total_tests, passed, failed, skipped, duration, build_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        results['summary']['total'],
        results['summary'].get('passed', 0),
        results['summary'].get('failed', 0),
        results['summary'].get('skipped', 0),
        results['duration'],
        build_status
    ))
    
    build_id = cursor.lastrowid
    
    # Insert failed tests
    for test in results.get('tests', []):
        if test['outcome'] == 'failed':
            cursor.execute('''
                INSERT INTO test_failures (build_id, test_name, file_path, line_number, error_message, traceback)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                build_id,
                test['nodeid'],
                test.get('location', [''])[0],
                test.get('location', [None, None])[1],
                test.get('call', {}).get('longrepr', ''),
                test.get('call', {}).get('traceback', '')
            ))
    
    conn.commit()
    conn.close()
    
    print(f"Results processed and stored. Build ID: {build_id}")


if __name__ == '__main__':
    process_test_results()