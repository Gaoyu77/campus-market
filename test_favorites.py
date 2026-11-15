from fastapi.testclient import TestClient
from app import app, db

client = TestClient(app)
a, b = {'X-Demo-User':'demo-gaoyu'}, {'X-Demo-User':'demo-2'}
sample = {'title':'收藏联调测试商品','category':'生活好物','condition':'正常使用','price':3,'campus':'东校区','description':'临时测试'}
pid = None
try:
    assert {u['id'] for u in client.get('/api/users').json()} == {'demo-gaoyu','demo-2'}
    result = client.post('/api/products', json=sample, headers=a)
    assert result.status_code == 201, result.text
    pid = result.json()['id']
    assert client.put(f'/api/favorites/{pid}',headers=a).status_code == 204
    assert client.put(f'/api/favorites/{pid}',headers=a).status_code == 204
    assert pid in client.get('/api/favorites',headers=a).json()
    assert pid not in client.get('/api/favorites',headers=b).json()
    assert client.put(f'/api/favorites/{pid}',headers=b).status_code == 204
    assert client.delete(f'/api/favorites/{pid}',headers=a).status_code == 204
    assert pid not in client.get('/api/favorites',headers=a).json()
    assert pid in client.get('/api/favorites',headers=b).json()
    assert client.put('/api/favorites/999999999',headers=a).status_code == 404
    print('通过：用户、收藏持久化、身份隔离、重复收藏、取消收藏及不存在商品。')
finally:
    if pid:
        with db() as conn:
            conn.cursor().execute('DELETE FROM dbo.Favorites WHERE product_id=?',pid)
            conn.cursor().execute('DELETE FROM dbo.Products WHERE id=?',pid)
