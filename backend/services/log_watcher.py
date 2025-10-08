import threading
import time
import random
import platform

from rich import print as rprint
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_LEVELS = ['INFO', 'WARNING', 'ERROR']
EVENT_SOURCES = ['System', 'Application', 'Security', 'Setup']

def simulate_log():
    return {
        'timestamp': int(time.time() * 1000),
        'level': random.choice(LOG_LEVELS),
        'source': random.choice(EVENT_SOURCES),
        'event_id': random.randint(1000, 9999),
        'message': random.choice([
            'Login succeeded',
            'Service started',
            'Disk warning',
            'Access denied',
            'File not found',
            'Update installed',
            'Power event',
            'System error detected',
            'Application crash',
            'Security audit'
        ])
    }

def windows_event_reader():
    # If running on Windows, try to read Event Logs (requires admin).
    # For demo, simulate logs instead.
    while True:
        log = simulate_log()
        yield log
        time.sleep(random.uniform(0.5, 1.5))

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, callback, logfile):
        self.callback = callback
        self.logfile = logfile
        self.last_size = 0

    def on_modified(self, event):
        if event.src_path == self.logfile:
            with open(self.logfile, 'r') as f:
                f.seek(self.last_size)
                lines = f.readlines()
                self.last_size = f.tell()
                for line in lines:
                    log = parse_log_line(line.strip())
                    if log:
                        self.callback(log)

def parse_log_line(line):
    # Example: "2025-10-08 20:39:00|ERROR|System|1004|Disk failure"
    try:
        ts, lvl, src, eid, msg = line.split('|', 4)
        return {
            'timestamp': int(time.mktime(time.strptime(ts, '%Y-%m-%d %H:%M:%S'))) * 1000,
            'level': lvl,
            'source': src,
            'event_id': int(eid),
            'message': msg
        }
    except Exception:
        return None

def start_log_watcher(broadcast_func, save_func):
    def run():
        # Try to watch a file called "sample.log"
        logfile = '/app/sample.log'
        if platform.system() == 'Windows' and False:  # Placeholder: Use Windows EventLog API
            reader = windows_event_reader()
            for log in reader:
                save_func(log)
                broadcast_func(log)
                rprint(f"[bold blue]LOG:[/bold blue] {log}")
        else:
            # Simulate logs + file watcher
            observer = Observer()
            handler = LogFileHandler(lambda log: (save_func(log), broadcast_func(log)), logfile)
            observer.schedule(handler, path=logfile, recursive=False)
            observer.start()
            while True:
                log = simulate_log()
                save_func(log)
                broadcast_func(log)
                rprint(f"[bold blue]LOG:[/bold blue] {log}")
                time.sleep(random.uniform(1, 2))
    thread = threading.Thread(target=run, daemon=True)
    thread.start()