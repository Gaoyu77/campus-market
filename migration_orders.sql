SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET XACT_ABORT ON;
BEGIN TRANSACTION;
DECLARE @legacy sysname;
SELECT @legacy=name FROM sys.check_constraints WHERE parent_object_id=OBJECT_ID('dbo.Products') AND name <> 'CK_Products_status' AND definition LIKE '%status%';
IF @legacy IS NOT NULL
BEGIN
    DECLARE @legacy_sql NVARCHAR(MAX) = N'ALTER TABLE dbo.Products DROP CONSTRAINT ' + QUOTENAME(@legacy);
    EXEC sp_executesql @legacy_sql;
END;
IF OBJECT_ID('dbo.Orders','U') IS NULL
BEGIN
    DECLARE @constraint sysname;
    SELECT @constraint=name FROM sys.check_constraints WHERE parent_object_id=OBJECT_ID('dbo.Products') AND definition LIKE '%[[]status[]]%';
    IF @constraint IS NOT NULL
    BEGIN
        DECLARE @sql NVARCHAR(MAX) = N'ALTER TABLE dbo.Products DROP CONSTRAINT ' + QUOTENAME(@constraint);
        EXEC sp_executesql @sql;
    END;
    ALTER TABLE dbo.Products ADD CONSTRAINT CK_Products_status CHECK (status IN ('on_sale','off_shelf','reserved','sold'));
    CREATE TABLE dbo.Orders (
        id INT IDENTITY PRIMARY KEY,
        product_id INT NOT NULL REFERENCES dbo.Products(id),
        buyer_id NVARCHAR(40) NOT NULL,
        seller_id NVARCHAR(40) NOT NULL,
        price DECIMAL(8,2) NOT NULL,
        status VARCHAR(12) NOT NULL CHECK (status IN ('reserved','cancelled','completed')),
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT CK_Orders_buyer CHECK (buyer_id <> seller_id)
    );
    CREATE UNIQUE INDEX UX_Orders_active_product ON dbo.Orders(product_id) WHERE status='reserved';
END;
COMMIT;
