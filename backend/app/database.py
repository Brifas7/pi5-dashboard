import sqlite3
import os

DB_PATH = os.path.expanduser('~/pi5-dashboard/data/dashboard.db')

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        device_id TEXT NOT NULL, sensor_type TEXT NOT NULL, value REAL NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS device_registry (
        device_id TEXT PRIMARY KEY, device_name TEXT NOT NULL,
        device_type TEXT NOT NULL, category TEXT, capabilities TEXT,
        last_seen TEXT, connection_info TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS automation_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT, rule_name TEXT NOT NULL,
        category TEXT, trigger_type TEXT NOT NULL, trigger_config TEXT,
        conditions TEXT, action_list TEXT, enabled INTEGER DEFAULT 1,
        created_date TEXT DEFAULT (datetime('now')), last_triggered TEXT,
        trigger_count INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notification_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        type TEXT NOT NULL, source_device TEXT, message TEXT NOT NULL,
        read INTEGER DEFAULT 0, cleared INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS system_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        device_id TEXT, event_description TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS theme_definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, theme_name TEXT NOT NULL UNIQUE,
        theme_type TEXT NOT NULL, color_config TEXT, background_asset TEXT,
        date_start TEXT, date_end TEXT, active INTEGER DEFAULT 0)""")
    c.execute('CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_sensor_device ON sensor_readings(device_id, sensor_type)')
    conn.commit()
    conn.close()

def log_sensor_reading(device_id, sensor_type, value):
    conn = get_db()
    conn.execute('INSERT INTO sensor_readings (device_id, sensor_type, value) VALUES (?, ?, ?)',
        (device_id, sensor_type, value))
    conn.commit()
    conn.close()

def log_system_event(device_id, description):
    conn = get_db()
    conn.execute('INSERT INTO system_events (device_id, event_description) VALUES (?, ?)',
        (device_id, description))
    conn.commit()
    conn.close()

def log_notification(notif_type, source_device, message):
    conn = get_db()
    conn.execute('INSERT INTO notification_log (type, source_device, message) VALUES (?, ?, ?)',
        (notif_type, source_device, message))
    conn.commit()
    conn.close()
