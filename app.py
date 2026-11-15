import os
from contextlib import contextmanager
from decimal import Decimal
from typing import Literal

import pyodbc
from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel, Field, field_validator
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title='同学集市 API', version='0.1')
DB_SERVER = os.environ.get('MARKET_DB_SERVER', 'localhost')
DB_NAME = os.environ.get('MARKET_DB_NAME', 'CampusMarket')
DEMO_OWNER = 'demo-gaoyu'
DEMO_USERS = {'demo-gaoyu': '小高同学', 'demo-2': '小张同学'}


def identity(value: str | None):
    user = value or DEMO_OWNER
    if user not in DEMO_USERS:
        raise HTTPException(400, '无效的演示身份')
    return user


@app.get('/', include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / 'index.html')


@contextmanager
def db():
    connection = pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;TrustServerCertificate=yes;')
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


class ProductInput(BaseModel):
    title: str = Field(min_length=1, max_length=45)
    category: str = Field(min_length=1, max_length=30)
    condition: Literal['全新未用', '几乎全新', '正常使用']
    price: Decimal = Field(ge=0, le=999999, decimal_places=2)
    campus: Literal['东校区', '西校区', '南校区']
    description: str = Field(min_length=1, max_length=1000)
    image_data: str | None = Field(default=None, max_length=14_000_000)

    @field_validator('title', 'description', 'category')
    @classmethod
    def nonblank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('不能只填写空格')
        return value

    @field_validator('image_data')
    @classmethod
    def image_type(cls, value):
        if value is not None and not value.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,', 'data:image/webp;base64,')):
            raise ValueError('图片须为 JPEG、PNG 或 WebP 数据')
        return value


class StatusInput(BaseModel):
    status: Literal['on_sale', 'off_shelf']


FIELDS = 'id,owner_id,title,category,condition,price,campus,description,image_data,status,created_at'


def serialize(row):
    return dict(zip(FIELDS.split(','), row))


@app.get('/api/health')
def health():
    with db() as conn:
        name = conn.cursor().execute('SELECT DB_NAME()').fetchval()
    return {'status': 'ok', 'database': name}


@app.get('/api/users')
def users():
    with db() as conn:
        return [{'id': r.id, 'name': r.display_name} for r in conn.cursor().execute('SELECT id,display_name FROM dbo.Users WHERE is_demo=1 ORDER BY id').fetchall()]


@app.get('/api/favorites')
def favorites(x_demo_user: str | None = Header(default=None)):
    with db() as conn:
        return [r.product_id for r in conn.cursor().execute('SELECT product_id FROM dbo.Favorites WHERE user_id=?', identity(x_demo_user)).fetchall()]


@app.put('/api/favorites/{product_id}', status_code=204)
def add_favorite(product_id: int, x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    with db() as conn:
        c = conn.cursor()
        row = c.execute("SELECT id FROM dbo.Products WHERE id=? AND (status<>'off_shelf' OR owner_id=?)", product_id, user).fetchone()
        if not row:
            raise HTTPException(404, '商品不存在')
        c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.Favorites WITH (UPDLOCK,HOLDLOCK) WHERE user_id=? AND product_id=?) INSERT dbo.Favorites(user_id,product_id) VALUES (?,?)', user, product_id, user, product_id)


@app.delete('/api/favorites/{product_id}', status_code=204)
def remove_favorite(product_id: int, x_demo_user: str | None = Header(default=None)):
    with db() as conn:
        conn.cursor().execute('DELETE FROM dbo.Favorites WHERE user_id=? AND product_id=?', identity(x_demo_user), product_id)


@app.get('/api/favorite-products')
def favorite_products(x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    with db() as conn:
        fields = ','.join('p.' + field for field in FIELDS.split(','))
        rows = conn.cursor().execute(f'SELECT {fields} FROM dbo.Favorites f JOIN dbo.Products p ON p.id=f.product_id WHERE f.user_id=? ORDER BY f.created_at DESC, p.id DESC', user).fetchall()
        return [serialize(row) for row in rows]


@app.get('/api/overview')
def overview():
    with db() as conn:
        c = conn.cursor()
        counts = {r.status:r.total for r in c.execute('SELECT status, COUNT(*) AS total FROM dbo.Products GROUP BY status').fetchall()}
        orders = c.execute("SELECT COUNT(*) AS total, COALESCE(SUM(price),0) AS amount FROM dbo.Orders WHERE status='completed'").fetchone()
        categories = [{'name':r.category,'count':r.total} for r in c.execute('SELECT category,COUNT(*) AS total FROM dbo.Products GROUP BY category ORDER BY total DESC,category').fetchall()]
        campuses = [{'name':r.campus,'count':r.total} for r in c.execute('SELECT campus,COUNT(*) AS total FROM dbo.Products GROUP BY campus ORDER BY total DESC,campus').fetchall()]
        return {'on_sale':counts.get('on_sale',0),'reserved':counts.get('reserved',0),'completed_orders':orders.total,'completed_amount':orders.amount,'categories':categories,'campuses':campuses}


@app.get('/api/products')
def products(mine: bool = False, include_sold: bool = False, q: str = Query(default='', max_length=100), campus: str = '', x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    clauses = ['owner_id = ?'] if mine else ["status IN ('on_sale','reserved','sold')" if include_sold else "status = 'on_sale'"]
    args = [user] if mine else []
    if campus:
        clauses.append('campus = ?')
        args.append(campus)
    if q.strip():
        clauses.append('CHARINDEX(?, title) > 0')
        args.append(q.strip())
    with db() as conn:
        rows = conn.cursor().execute(f"SELECT {FIELDS} FROM dbo.Products WHERE {' AND '.join(clauses)} ORDER BY created_at DESC, id DESC", *args).fetchall()
        return [serialize(row) for row in rows]


@app.get('/api/products/{product_id}')
def product(product_id: int, x_demo_user: str | None = Header(default=None)):
    with db() as conn:
        row = conn.cursor().execute(f'SELECT {FIELDS} FROM dbo.Products WHERE id=? AND (status <> ? OR owner_id=?)', product_id, 'off_shelf', identity(x_demo_user)).fetchone()
        if not row:
            raise HTTPException(404, '商品不存在')
        return serialize(row)


@app.post('/api/products', status_code=201)
def create_product(data: ProductInput, x_demo_user: str | None = Header(default=None)):
    with db() as conn:
        row = conn.cursor().execute(f'INSERT dbo.Products (owner_id,title,category,condition,price,campus,description,image_data) OUTPUT {", ".join("INSERTED." + f for f in FIELDS.split(","))} VALUES (?,?,?,?,?,?,?,?)', identity(x_demo_user), data.title, data.category, data.condition, data.price, data.campus, data.description, data.image_data).fetchone()
        return serialize(row)


@app.put('/api/products/{product_id}')
def update_product(product_id: int, data: ProductInput, x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    with db() as conn:
        cursor = conn.cursor().execute("UPDATE dbo.Products SET title=?,category=?,condition=?,price=?,campus=?,description=?,image_data=? WHERE id=? AND owner_id=? AND status IN ('on_sale','off_shelf')", data.title, data.category, data.condition, data.price, data.campus, data.description, data.image_data, product_id, user)
        if cursor.rowcount != 1:
            raise HTTPException(404, '商品不存在或不可编辑')
    return product(product_id, user)


@app.patch('/api/products/{product_id}/status')
def change_status(product_id: int, data: StatusInput, x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    with db() as conn:
        cursor = conn.cursor().execute("UPDATE dbo.Products SET status=? WHERE id=? AND owner_id=? AND status IN ('on_sale','off_shelf')", data.status, product_id, user)
        if cursor.rowcount != 1:
            raise HTTPException(404, '商品不存在或不可操作')
    return product(product_id, user)


@app.get('/api/orders')
def orders(x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    with db() as conn:
        rows = conn.cursor().execute('SELECT o.id,o.product_id,p.title,o.buyer_id,o.seller_id,o.price,o.status,o.created_at FROM dbo.Orders o JOIN dbo.Products p ON p.id=o.product_id WHERE o.buyer_id=? OR o.seller_id=? ORDER BY o.id DESC', user, user).fetchall()
        return [dict(zip(('id','product_id','title','buyer_id','seller_id','price','status','created_at'), row)) for row in rows]


@app.post('/api/products/{product_id}/reserve', status_code=201)
def reserve(product_id: int, x_demo_user: str | None = Header(default=None)):
    buyer = identity(x_demo_user)
    with db() as conn:
        c = conn.cursor()
        row = c.execute("UPDATE dbo.Products SET status='reserved' OUTPUT INSERTED.owner_id,INSERTED.price WHERE id=? AND status='on_sale' AND owner_id<>? AND owner_id IN ('demo-gaoyu','demo-2')", product_id, buyer).fetchone()
        if not row:
            raise HTTPException(409, '商品不可预约，或不能预约自己的商品')
        order = c.execute("INSERT dbo.Orders(product_id,buyer_id,seller_id,price,status) OUTPUT INSERTED.id VALUES (?,?,?,?,'reserved')", product_id, buyer, row.owner_id, row.price).fetchval()
        return {'order_id': order}


@app.post('/api/orders/{order_id}/{action}')
def change_order(order_id: int, action: Literal['cancel', 'complete'], x_demo_user: str | None = Header(default=None)):
    user = identity(x_demo_user)
    with db() as conn:
        c = conn.cursor()
        # Update the product first in every transaction to keep lock order consistent.
        row = c.execute('SELECT product_id FROM dbo.Orders WHERE id=?', order_id).fetchone()
        if not row:
            raise HTTPException(404, '订单不存在')
        p = c.execute("UPDATE dbo.Products SET status=? OUTPUT INSERTED.id WHERE id=? AND status='reserved'", 'on_sale' if action == 'cancel' else 'sold', row.product_id).fetchone()
        if not p:
            raise HTTPException(409, '订单状态已变化')
        o = c.execute("UPDATE dbo.Orders SET status=?,updated_at=SYSDATETIME() OUTPUT INSERTED.id WHERE id=? AND status='reserved' AND (seller_id=? OR (?='cancel' AND buyer_id=?))", 'cancelled' if action == 'cancel' else 'completed', order_id, user, action, user).fetchone()
        if not o:
            raise HTTPException(403, '无权操作或订单已结束')
        return {'status': 'cancelled' if action == 'cancel' else 'completed'}
