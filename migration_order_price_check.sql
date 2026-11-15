SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID(N'dbo.Orders')
      AND name = N'CK_Orders_price_nonnegative'
)
    ALTER TABLE dbo.Orders WITH CHECK
        ADD CONSTRAINT CK_Orders_price_nonnegative CHECK (price >= 0);
COMMIT;
