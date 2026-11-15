SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET XACT_ABORT ON;
-- 每次只新增一件带标记的在售商品，不删除或覆盖现有数据。
INSERT dbo.Products(owner_id,title,category,condition,price,campus,description,status)
OUTPUT INSERTED.id,INSERTED.title,INSERTED.owner_id,INSERTED.status
VALUES ('demo-2',N'【演示】小张的交易商品 '+LEFT(CONVERT(nvarchar(36),NEWID()),8),N'生活好物',N'正常使用',20,N'东校区',N'供本机答辩演示预约、取消与完成。','on_sale');
