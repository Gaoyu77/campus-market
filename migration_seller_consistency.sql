SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name='UQ_Products_id_owner')
    ALTER TABLE dbo.Products ADD CONSTRAINT UQ_Products_id_owner UNIQUE (id,owner_id);
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name='FK_Orders_ProductSeller')
    ALTER TABLE dbo.Orders WITH CHECK ADD CONSTRAINT FK_Orders_ProductSeller FOREIGN KEY (product_id,seller_id) REFERENCES dbo.Products(id,owner_id);
COMMIT;
