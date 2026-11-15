from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app import app, db

client = TestClient(app)
seller = {'X-Demo-User': 'demo-gaoyu'}
buyer = {'X-Demo-User': 'demo-2'}
sample = {'title':'交易联调测试商品','category':'生活好物','condition':'正常使用','price':'12.50','campus':'东校区','description':'临时测试'}
pid = None
try:
    r = client.post('/api/products', json=sample, headers=seller)
    assert r.status_code == 201, r.text
    pid = r.json()['id']
    assert client.post(f'/api/products/{pid}/reserve', headers=seller).status_code == 409
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: client.post(f'/api/products/{pid}/reserve', headers=buyer), range(2)))
    assert sorted(r.status_code for r in results) == [201,409], [r.text for r in results]
    order = next(r.json()['order_id'] for r in results if r.status_code == 201)
    assert client.get(f'/api/products/{pid}', headers=seller).json()['status'] == 'reserved'
    assert client.put(f'/api/products/{pid}', json=sample, headers=seller).status_code == 404
    assert client.post(f'/api/orders/{order}/complete', headers=buyer).status_code == 403
    assert client.get(f'/api/products/{pid}', headers=seller).json()['status'] == 'reserved'
    assert client.post(f'/api/orders/{order}/cancel', headers=buyer).status_code == 200
    assert client.get(f'/api/products/{pid}').json()['status'] == 'on_sale'
    order2 = client.post(f'/api/products/{pid}/reserve', headers=buyer).json()['order_id']
    assert client.post(f'/api/orders/{order}/cancel', headers=buyer).status_code == 403
    assert client.get(f'/api/products/{pid}', headers=seller).json()['status'] == 'reserved'
    assert next(o for o in client.get('/api/orders', headers=buyer).json() if o['id'] == order2)['status'] == 'reserved'
    assert client.post(f'/api/orders/{order2}/complete', headers=seller).status_code == 200
    assert client.get(f'/api/products/{pid}').json()['status'] == 'sold'
    assert client.post(f'/api/orders/{order2}/cancel', headers=buyer).status_code == 409
    print('通过：身份、并发预约、限制编辑、权限、取消、重新预约和完成。')
finally:
    if pid:
        with db() as conn:
            conn.cursor().execute('DELETE FROM dbo.Orders WHERE product_id=?', pid)
            conn.cursor().execute('DELETE FROM dbo.Products WHERE id=?', pid)
