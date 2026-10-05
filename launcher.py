"""KSMS AR큐브 실행기: HTTPS 서버를 켜고(꺼져 있으면) 앱 창(Edge 우선)을 연다."""
import os
import socket
import subprocess
import sys
import time
import webbrowser

APP_DIR = r'C:\Users\Kiseok\Desktop\[오픈코드]\KSMS AR큐브 v2'
URL = 'https://localhost:8445'
PORT = 8445


def port_open():
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect(('127.0.0.1', PORT))
        return True
    except OSError:
        return False
    finally:
        s.close()


def find_python():
    if getattr(sys, 'frozen', False):
        import shutil
        for exe in ('pythonw.exe', 'python.exe'):
            p = shutil.which(exe)
            if p:
                return p
        return None
    return sys.executable


def ensure_server():
    if port_open():
        return
    serve = os.path.join(APP_DIR, 'serve_https.py')
    py = find_python()
    if py is None:
        return
    try:
        subprocess.Popen([py, serve], cwd=APP_DIR,
                         creationflags=0x08000000,  # CREATE_NO_WINDOW
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    except OSError:
        return
    for _ in range(30):
        if port_open():
            break
        time.sleep(0.5)


def find_browser():
    """Edge 우선, Chrome 후순위. (이름, 경로) 반환, 없으면 (None, None)"""
    import shutil
    cands = [
        ('edge', [shutil.which('msedge'),
                  r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                  r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']),
        ('chrome', [shutil.which('chrome'),
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe']),
    ]
    for name, paths in cands:
        for p in paths:
            if p and os.path.exists(p):
                return name, p
    return None, None


def open_app():
    """일반 앱처럼 보이는 최소 창으로 열기 (주소창·탭 없음)"""
    name, exe = find_browser()
    if exe is None:
        webbrowser.open(URL)
        return
    base = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    profile = os.path.join(base, 'KSMS AR큐브', 'profile-' + name)
    os.makedirs(profile, exist_ok=True)
    try:
        subprocess.Popen([exe, '--app=' + URL, '--user-data-dir=' + profile])
    except OSError:
        webbrowser.open(URL)


def main():
    ensure_server()
    time.sleep(0.5)
    open_app()


if __name__ == '__main__':
    main()
