SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET XACT_ABORT ON;
BEGIN TRANSACTION;
-- 新增独立示例，不重置或覆盖已有商品和订单。
IF NOT EXISTS (SELECT 1 FROM dbo.Products WHERE owner_id='demo-2' AND title=N'【演示】小张的计算器')
    INSERT dbo.Products(owner_id,title,category,condition,price,campus,description,status)
    VALUES ('demo-2',N'【演示】小张的计算器',N'生活好物',N'正常使用',25,N'东校区',N'可用于演示小高预约小张发布的商品。','on_sale');
IF NOT EXISTS (SELECT 1 FROM dbo.Products WHERE owner_id='demo-gaoyu' AND title=N'【演示】小高的笔记本')
BEGIN
    DECLARE @cancelled_id INT;
    INSERT dbo.Products(owner_id,title,category,condition,price,campus,description,status)
    VALUES ('demo-gaoyu',N'【演示】小高的笔记本',N'生活好物',N'全新未用',10,N'西校区',N'示例商品，附一条已取消预约记录。','on_sale');
    SET @cancelled_id=SCOPE_IDENTITY();
    INSERT dbo.Orders(product_id,buyer_id,seller_id,price,status)
    VALUES (@cancelled_id,'demo-2','demo-gaoyu',10,'cancelled');
END;
IF NOT EXISTS (SELECT 1 FROM dbo.Products WHERE owner_id='demo-2' AND title=N'【演示】已成交的台灯')
BEGIN
    DECLARE @sold_id INT;
    INSERT dbo.Products(owner_id,title,category,condition,price,campus,description,status)
    VALUES ('demo-2',N'【演示】已成交的台灯',N'生活好物',N'正常使用',30,N'东校区',N'已成交的示例商品，用于展示订单记录。','sold');
    SET @sold_id=SCOPE_IDENTITY();
    INSERT dbo.Orders(product_id,buyer_id,seller_id,price,status)
    VALUES (@sold_id,'demo-gaoyu','demo-2',30,'completed');
END;
COMMIT;
