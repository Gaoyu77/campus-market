"""Insert the original prototype examples once into an empty database."""
from app import db

examples = [
    ('demo-gaoyu','数据库系统概论 · 第六版','教材书籍','正常使用',18,'东校区','课程结束了，把它传给下一位需要的同学。部分章节有铅笔标注，书页完整。','on_sale'),
    ('demo-2','头戴式无线耳机，支持蓝牙连接','数码电子','几乎全新',160,'东校区','支持蓝牙连接，可面交试听。','on_sale'),
    ('demo-3','书桌暖光台灯，带原装电源','生活好物','几乎全新',35,'西校区','带原装电源，可以校内面交。','on_sale'),
    ('demo-4','复古数码相机，含电池和充电器','数码电子','正常使用',280,'南校区','含电池和充电器，可面交试拍。','on_sale'),
    ('demo-5','校园通勤自行车，刹车正常','运动出行','正常使用',220,'东校区','日常代步自行车，可以先试骑。','on_sale'),
    ('demo-6','奶油绿机械键盘 · 无线版','数码电子','几乎全新',120,'西校区','无线机械键盘，按键功能正常。','on_sale'),
    ('demo-7','帆布双肩包，全新未使用','服饰配件','全新未用',45,'南校区','全新未使用，支持校内面交。','on_sale'),
    ('demo-8','汪曾祺《人间草木》','教材书籍','几乎全新',12,'东校区','书页完整，已经售出。','sold'),
    ('demo-gaoyu','闲置收纳盒，一组两个','生活好物','正常使用',15,'东校区','一组两个收纳盒，边角有少量使用痕迹。','off_shelf'),
]
with db() as conn:
    c = conn.cursor()
    if c.execute('SELECT COUNT(*) FROM dbo.Products').fetchval():
        print('已有商品，未插入示例。')
    else:
        for row in examples:
            c.execute('IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE id=?) INSERT dbo.Users(id,display_name,is_demo) VALUES (?, ?, 0)', row[0], row[0], '示例卖家')
            c.execute('INSERT dbo.Products (owner_id,title,category,condition,price,campus,description,status) VALUES (?,?,?,?,?,?,?,?)', *row)
        print('已插入 9 条示例商品。')
