"""Create a new demonstration database without modifying an existing one."""
import os
from pathlib import Path
import re
import subprocess
import sys

import pyodbc

ROOT = Path(__file__).resolve().parent
SERVER = os.environ.get('MARKET_DB_SERVER', 'localhost')
NAME = os.environ.get('MARKET_DB_NAME', 'CampusMarket')
SCRIPTS = ('schema.sql', 'migration_orders.sql', 'migration_users_favorites.sql',
           'migration_seller_consistency.sql', 'migration_order_price_check.sql')


def connect(database, autocommit=True):
    return pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes;', autocommit=autocommit)


def main():
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}', NAME):
        raise ValueError('数据库名只能以英文字母开头，并包含英文字母、数字和下划线。')
    with connect('master') as conn:
        cursor = conn.cursor()
        if cursor.execute('SELECT DB_ID(?)', NAME).fetchval() is not None:
            raise RuntimeError(f'数据库 {NAME} 已存在，已停止初始化；没有改动现有数据库。')
        cursor.execute(f'CREATE DATABASE [{NAME}]')
    print(f'已创建数据库 {NAME}，开始建立表和约束。', flush=True)
    try:
        with connect(NAME) as conn:
            cursor = conn.cursor()
            for script in SCRIPTS:
                print(f'执行 {script}', flush=True)
                cursor.execute((ROOT / script).read_text(encoding='utf-8-sig'))
                while cursor.nextset():
                    pass
        subprocess.run([sys.executable, str(ROOT / 'seed_demo.py')], cwd=ROOT, check=True)
        with connect(NAME) as conn:
            cursor = conn.cursor()
            cursor.execute((ROOT / 'seed_trade_examples.sql').read_text(encoding='utf-8-sig'))
            while cursor.nextset():
                pass
        print(f'初始化完成：{NAME}。')
    except Exception:
        print(f'初始化未完成；已创建的 {NAME} 被保留，请检查错误并处理后再重试。', file=sys.stderr)
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'初始化失败：{exc}', file=sys.stderr)
        sys.exit(1)
