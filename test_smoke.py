from fastapi.testclient import TestClient
from app import app, db, DB_NAME

client = TestClient(app)
sample = {'title': '接口测试商品', 'category': '教材', 'condition': '正常使用', 'price': '12.50', 'campus': '东校区', 'description': '测试真实数据库读写'}
product_id = None
try:
    assert client.get('/api/health').json()['database'] == DB_NAME
    response = client.post('/api/products', json=sample)
    assert response.status_code == 201, response.text
    product_id = response.json()['id']
    assert client.get(f'/api/products/{product_id}').json()['title'] == sample['title']
    assert any(p['id'] == product_id for p in client.get('/api/products', params={'mine': True}).json())
    response = client.patch(f'/api/products/{product_id}/status', json={'status': 'off_shelf'})
    assert response.status_code == 200 and response.json()['status'] == 'off_shelf', response.text
    assert all(p['id'] != product_id for p in client.get('/api/products').json())
    sample['title'] = '接口测试商品已编辑'
    response = client.put(f'/api/products/{product_id}', json=sample)
    assert response.status_code == 200 and response.json()['status'] == 'off_shelf', response.text
    response = client.patch(f'/api/products/{product_id}/status', json={'status': 'on_sale'})
    assert response.status_code == 200 and response.json()['title'] == sample['title'], response.text
    assert client.post('/api/products', json={**sample, 'title': '   '}).status_code == 422
    print('通过：数据库连接、创建、跨连接读取、编辑、下架、上架及无效输入')
finally:
    if product_id is not None:
        with db() as conn:
            conn.cursor().execute('DELETE FROM dbo.Products WHERE id=? AND owner_id=?', product_id, 'demo-gaoyu')
