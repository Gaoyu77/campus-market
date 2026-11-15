"""Start the local demo and open it in the default browser."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

from app import DB_NAME, db

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get('MARKET_PORT', '8000'))
URL = f'http://127.0.0.1:{PORT}/'


def health():
    try:
        with urllib.request.urlopen(URL + 'api/health', timeout=2) as response:
            return json.load(response)
    except (OSError, ValueError):
        return None


def main():
    with db() as conn:
        conn.cursor().execute('SELECT TOP 1 id FROM dbo.Products').fetchone()
    current = health()
    if current:
        if current.get('database') != DB_NAME:
            raise RuntimeError(f'{PORT} 端口上的集市连接了其他数据库，请先检查已有服务。')
        print('集市已在运行，打开浏览器。')
        webbrowser.open(URL)
        return
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app:app', '--host', '127.0.0.1', '--port', str(PORT)], cwd=ROOT)
    try:
        for _ in range(50):
            if process.poll() is not None:
                raise RuntimeError(f'后端未能启动，请检查 {PORT} 端口是否被占用。')
            result = health()
            if result and result.get('database') == DB_NAME:
                print('集市已启动。关闭此窗口或按 Ctrl+C 将停止后端。', flush=True)
                webbrowser.open(URL)
                process.wait()
                return
            time.sleep(0.2)
        raise RuntimeError('后端启动超时，请检查 SQL Server 和数据库。')
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n集市已停止。')
    except Exception as exc:
        print(f'启动失败：{exc}', file=sys.stderr)
        sys.exit(1)
