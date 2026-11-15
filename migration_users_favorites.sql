SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF OBJECT_ID('dbo.Users','U') IS NULL
BEGIN
    CREATE TABLE dbo.Users (
        id NVARCHAR(40) NOT NULL PRIMARY KEY,
        display_name NVARCHAR(50) NOT NULL,
        is_demo BIT NOT NULL DEFAULT 0
    );
END;
IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE id='demo-gaoyu') INSERT dbo.Users VALUES ('demo-gaoyu',N'小高同学',1);
IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE id='demo-2') INSERT dbo.Users VALUES ('demo-2',N'小张同学',1);
INSERT dbo.Users (id,display_name,is_demo)
SELECT owner_id, N'示例卖家', 0 FROM dbo.Products p
WHERE NOT EXISTS (SELECT 1 FROM dbo.Users u WHERE u.id=p.owner_id)
GROUP BY owner_id;
INSERT dbo.Users (id,display_name,is_demo)
SELECT person.id, N'示例用户', 0 FROM (SELECT buyer_id AS id FROM dbo.Orders UNION SELECT seller_id FROM dbo.Orders) person
WHERE NOT EXISTS (SELECT 1 FROM dbo.Users u WHERE u.id=person.id);
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Products_Users')
    ALTER TABLE dbo.Products ADD CONSTRAINT FK_Products_Users FOREIGN KEY (owner_id) REFERENCES dbo.Users(id);
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Orders_Buyer')
    ALTER TABLE dbo.Orders ADD CONSTRAINT FK_Orders_Buyer FOREIGN KEY (buyer_id) REFERENCES dbo.Users(id);
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Orders_Seller')
    ALTER TABLE dbo.Orders ADD CONSTRAINT FK_Orders_Seller FOREIGN KEY (seller_id) REFERENCES dbo.Users(id);
IF OBJECT_ID('dbo.Favorites','U') IS NULL
BEGIN
    CREATE TABLE dbo.Favorites (
        user_id NVARCHAR(40) NOT NULL REFERENCES dbo.Users(id),
        product_id INT NOT NULL REFERENCES dbo.Products(id),
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_Favorites PRIMARY KEY (user_id, product_id)
    );
END;
COMMIT;
