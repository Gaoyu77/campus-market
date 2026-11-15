# 同学集市：数据库与后端

这是第一版本地开发后端。数据库使用 SQL Server，接口使用 Python FastAPI。当前实现商品的发布、列表、详情、编辑、上下架，数据持久化到独立数据库 `CampusMarket`。不修改课程实验数据库。

## 启动

### 新 Windows 电脑首次使用

1. 安装 Python 3.11（安装时勾选加入 PATH）、SQL Server 和 Microsoft ODBC Driver 18 for SQL Server。启动 SQL Server，并确保当前 Windows 账号有登录和创建数据库的权限。
2. 下载或克隆仓库，打开项目文件夹，双击 **首次初始化.bat**。它会创建项目内的 `.venv`、联网安装依赖，创建 `CampusMarket`，按顺序执行建表、迁移并导入演示数据。目标库已经存在时会停止，不覆盖、不重置。
3. 双击 **一键启动.bat**，等待浏览器打开 http://127.0.0.1:8000/。启动窗口保持打开；关闭窗口或按 Ctrl+C 停止本次启动的后端。已有对应后端在运行时会直接打开页面。

依赖安装失败时，请检查 Python、网络和 pip；数据库连接失败时，请检查 SQL Server 服务、ODBC Driver 和 Windows 登录权限。若初始化中途失败，已创建的数据库会保留，脚本不会自动删除它；请先检查错误及数据库状态，不要直接重复初始化。

如果要迁移旧电脑的实际商品和订单，请在新电脑用 SSMS 恢复原数据库备份，然后运行 **一键启动.bat**，不要执行首次初始化。GitHub 只保存结构和示例脚本，不包含实际数据库备份。

默认使用 Windows 身份连接 `localhost` 和 `CampusMarket`。命名实例或其他数据库可在启动前设置环境变量 `MARKET_DB_SERVER`、`MARKET_DB_NAME`；端口默认为 8000，可用 `MARKET_PORT` 修改。初始化要求目标库不存在，并需要创建数据库的权限。手动建库时，依次执行 `schema.sql`、`migration_orders.sql`、`migration_users_favorites.sql`、`migration_seller_consistency.sql`、`migration_order_price_check.sql`，之后执行 `seed_demo.py` 和 `seed_trade_examples.sql`。

一键启动只提供本机网页，不会启动或配置 Cloudflare 隧道；新电脑需要远程演示时，须另行配置受保护的访问入口。接口文档为 http://127.0.0.1:8000/docs，健康检查为 http://127.0.0.1:8000/api/health。

## 接口

- `GET /api/products`：公开在售商品；`include_sold=true` 包含已售商品，支持 `q`、`campus` 筛选。
- `GET /api/products?mine=true`：演示账号的所有商品。
- `GET /api/products/{id}`：查看商品。
- `POST /api/products`：发布商品。
- `PUT /api/products/{id}`：修改自己的商品，保留状态和发布时间。
- `PATCH /api/products/{id}/status`：传入 `{"status":"off_shelf"}` 或 `{"status":"on_sale"}`。

可运行 `python test_smoke.py` 验证数据库连接及核心接口。测试会删除其自身创建的测试商品。

## 当前边界

页面可以在小高和小张两个演示身份间切换，没有用户登录或真正的身份认证。本机提供受共享密码保护的远程演示入口；拿到密码的人都能切换演示身份并修改数据，不适合公开运营。发布、编辑、上下架、图片、收藏、订单及交易状态保存在数据库。交易采用预约、双方可取消、卖家确认完成的方式，不提供聊天或真实支付。旧示例商品中，仅小高和小张名下的商品支持预约；其他示例卖家不能切换，因此暂不支持预约。

初始化示例数据时，先执行全部建表和迁移脚本，在空数据库运行 `python seed_demo.py`，再执行 `seed_trade_examples.sql`；已有商品时 seed_demo 不会插入。`seed_trade_examples.sql` 仅按名称补充带【演示】标记的数据，不重置已有数据。

每次需要新的交易演示时，可以在 SSMS 的 `CampusMarket` 库中运行 `准备一件演示商品.sql`。它每次只新增一件小张名下的在售商品，不删除或覆盖已有记录；重复运行会新增多件，可按输出的商品编号辨认。

## 交易演示

1. 选择小张同学，打开小高发布的“数据库系统概论 · 第六版”，点击“预约购买”。
2. 在“我的订单”查看预约，可点击取消；取消后商品恢复在售。
3. 重新预约，再将演示身份切换成小高同学，打开“我的订单”，点击“确认完成”。
4. 订单变为已完成，商品变为已售出；刷新后仍可查看。演示会真实修改数据库，可先发布一件测试商品再操作。

订单接口使用请求头 `X-Demo-User` 区分演示身份。`POST /api/products/{id}/reserve` 创建预约，`GET /api/orders` 查询订单，`POST /api/orders/{id}/cancel` 和 `/complete` 分别取消或确认。可运行 `python test_orders.py` 检查并发预约、操作权限和状态联动。

收藏接口为 `GET /api/favorites`、`PUT /api/favorites/{id}` 和 `DELETE /api/favorites/{id}`。可运行 `python test_favorites.py` 检查收藏和身份隔离。

交易概览由 `GET /api/overview` 提供，已完成订单价格合计不代表真实收款。`GET /api/favorite-products` 只返回当前演示身份收藏的商品，包含已下架商品。可运行 `python test_overview_consistency.py` 验证统计、下架收藏及卖家一致性约束。

`build_frontend.py` 是交易功能之前生成页面的旧脚本，不要再运行，否则会覆盖当前交易页面。
