import pyodbc
from fastapi.testclient import TestClient
from app import app, db

client = TestClient(app)
a, b = {'X-Demo-User':'demo-gaoyu'}, {'X-Demo-User':'demo-2'}
sample={'title':'统计与约束测试商品','category':'生活好物','condition':'正常使用','price':'15','campus':'东校区','description':'测试'}
pid=None
try:
    before=client.get('/api/overview').json()
    result=client.post('/api/products',json=sample,headers=b)
    assert result.status_code==201,result.text
    pid=result.json()['id']
    assert client.get('/api/overview').json()['on_sale']==before['on_sale']+1
    assert client.put(f'/api/favorites/{pid}',headers=a).status_code==204
    assert client.patch(f'/api/products/{pid}/status',json={'status':'off_shelf'},headers=b).status_code==200
    assert all(p['id']!=pid for p in client.get('/api/products',headers=a).json())
    assert any(p['id']==pid and p['status']=='off_shelf' for p in client.get('/api/favorite-products',headers=a).json())
    try:
        with db() as conn:
            conn.cursor().execute("INSERT dbo.Orders(product_id,buyer_id,seller_id,price,status) VALUES (?,? ,?,15,'cancelled')",pid,'demo-2','demo-gaoyu')
    except pyodbc.IntegrityError:
        pass
    else:
        raise AssertionError('数据库未阻止错误的订单卖家')
    assert client.patch(f'/api/products/{pid}/status',json={'status':'on_sale'},headers=b).status_code==200
    order=client.post(f'/api/products/{pid}/reserve',headers=a).json()['order_id']
    assert client.get('/api/overview').json()['reserved']==before['reserved']+1
    assert client.post(f'/api/orders/{order}/complete',headers=b).status_code==200
    after=client.get('/api/overview').json()
    assert after['completed_orders']==before['completed_orders']+1
    assert float(after['completed_amount'])==float(before['completed_amount'])+15
    print('通过：统计、下架收藏隔离、卖家外键与交易完成。')
finally:
    if pid:
        with db() as conn:
            conn.cursor().execute('DELETE dbo.Favorites WHERE product_id=?',pid)
            conn.cursor().execute('DELETE dbo.Orders WHERE product_id=?',pid)
            conn.cursor().execute('DELETE dbo.Products WHERE id=?',pid)
