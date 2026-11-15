IF OBJECT_ID(N'dbo.Products', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Products (
        id INT IDENTITY PRIMARY KEY,
        owner_id NVARCHAR(40) NOT NULL,
        title NVARCHAR(45) NOT NULL CHECK (LEN(LTRIM(RTRIM(title))) > 0),
        category NVARCHAR(30) NOT NULL,
        condition NVARCHAR(20) NOT NULL,
        price DECIMAL(8,2) NOT NULL CHECK (price >= 0 AND price <= 999999),
        campus NVARCHAR(20) NOT NULL,
        description NVARCHAR(1000) NOT NULL CHECK (LEN(LTRIM(RTRIM(description))) > 0),
        image_data NVARCHAR(MAX) NULL,
        status VARCHAR(12) NOT NULL DEFAULT 'on_sale' CHECK (status IN ('on_sale','off_shelf','sold')),
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    );
    CREATE INDEX IX_Products_status_created ON dbo.Products(status, created_at DESC);
    CREATE INDEX IX_Products_owner ON dbo.Products(owner_id, created_at DESC);
END;
