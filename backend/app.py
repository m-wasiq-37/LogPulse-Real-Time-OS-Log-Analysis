import os
import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from utils.env_loader import load_env
from utils.security import verify_password, hash_password
from services.db_service import get_db, get_user, create_user, save_log, get_logs, filter_logs
from services.log_watcher import start_log_watcher
from routes.auth_routes import auth_bp
from routes.log_routes import log_bp
from routes.analytics_routes import analytics_bp

load_env()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devsecret')

socketio = SocketIO(app, async_mode='eventlet')

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(log_bp)
app.register_blueprint(analytics_bp)

@app.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', username=session['username'])

@socketio.on('connect')
def handle_connect():
    if not session.get('username'):
        return False
    emit('connected', {'msg': 'Connected to LogPuls WebSocket.'})

def broadcast_log(log):
    socketio.emit('new_log', log, broadcast=True)

# Start log watcher thread
start_log_watcher(broadcast_log, save_log)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)