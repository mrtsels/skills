# 衡泰交易系统 (XTIMS) — API Reference

> Concrete API surface of the 粤财信托 衡泰综合资产管理系统 at `https://xtims.yuecaitrust.ltd/`.
> Discovered via browser console XHR interception + Ext.StoreManager extraction.
> ExtJS 5.0.27 / Spring MVC / RSA+JWT+WebSocket auth.

## Access

| Item | Value |
|------|-------|
| **URL** | https://xtims.yuecaitrust.ltd/login.action |
| **Account 1** | zhouyixin01 / Zhouyixin0341! (userId: 7087) |
| **Account 2** | zhouyixin02 / Zhouyixin0341! (userId: 7167) |
| **Version** | V5.0.27_B3_r150011 (2026-07-24) |
| **Biz Date Param** | `?xtims-biz-date=YYYY-MM-DD` on all requests |
| **Data transport** | **WebSocket/SockJS** (primary), HTTP AJAX fallback (from SPA) |

---

## Authentication Flow

```
Step 1: GET  /getPublicKey.action        → RSA public key (PEM)
Step 2: RSA encrypt password (JSEncrypt) → browser-side
Step 3: POST /doLogin.action             → JWT token
Step 4: WebSocket connect with JWT       → all data flows here
Step 5: (optional) POST /login.action    → sets JSESSIONID cookie
```

JWT: `localStorage['xtims-token']`, payload decoded:
```json
{"name": "周奕昕01", "id": "7087", "exp": 1784918244, "account": "zhouyixin01"}
```

---

## API Response Formats

### findAllUserList.action (GET)

Returns real user data with userIds:

```json
{
  "msg": "查询成功",
  "data": [
    {"userId": "8533", "name": "8888", "account": "8888"},
    {"userId": "7087", "name": "周奕昕01", "account": "zhouyixin01"},
    {"userId": "7167", "name": "周奕昕02", "account": "zhouyixin02"}
  ]
}
```

### requestCall4Grid.action (POST)

100 rows per query, each row has `order` (ordId, status, ordUser) and `trade` (instrument, amount, settleDate):

```json
{"count": 100, "data": [{"order": {...}, "trade": {...}}, ...]}
```

---

## Menu Handler Map (addPanelByPath)

| Menu | Path |
|------|------|
| 投资指令申请Plus | `XIRJS.workflow.order.OrderMainContainerPlus` |
| 交易执行及确认Plus | `XIRJS.settle.confirm.ConfirmMainPlus` |
| 后台结算确认Plus | `XIRJS.settle.SettleMainPlus` |
| 强制结算 | `XIRJS.settle.XYSettleMain` |
| 持仓查询 | `XIRJS.vueView.consolidatedStatement.positionQuery` |
| 资金余额查询 | `XIRJS.vueView.cashBalanceQueryNew` |
| 资金头寸查询 | `XIRJS.vueView.fundPositionQuery` |
| 资产余额查询 | `XIRJS.vueView.assetBalance` |
| 投资指令导入 | `XIRJS.vueView.batchInstructions` |
| 交易分发配置 | `XIRJS.rightsManagement.roles.designatedTrader` |
| 投资指令语义识别 | `XIRJS.vueView.semanticSranslation` |
| 投资意向 | `XIRJS.vueView.investmentOrderManagement.investmentIntention` |
| 账户划款 | `XIRJS.platform.app.trade.nostroCurrent.TradeMain` |

---

## Tab Container ID Mapping

| Page | Container ID |
|------|-------------|
| 投资指令申请Plus | `#NewInvestmentInstructionApplication` |
| 交易执行及确认Plus | `#ConfirmMainPlus` |
| 回购续期快速下单 | (floating popup, no fixed container) |

---

## Grid CSV Headers (investment instructions)

```
选择,提交审批日期,提交审批时间,原交易单号,续做类型,提交人,审批状态,审批节点,
产品账户,交易方向,证券代码,证券名称,价格类型,控制类型,价格,数量,交易金额(元),
交易单号,是否复制指令,交易对手,交易对手所属机构,质押券,到期收益率(%),
行权收益率(%),结算日期,业务类型,结算状态,交易单号,交易员,备注,审批单号
```

---

## 新增 Popup Menu - Repo Renewal Flow

The "新增" button opens a floating ExtJS menu: 回购业务 → 场内质押式协议回购 → 回购续期快速下单.

This opens a new tab with three sections:
1. 当日到期协议回购信息 (search)
2. 原交易信息 (selected expired repo details)
3. 新开交易信息 (form: term, rate, discount, counterparty)

---

## Automation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/heng_tai_browser.py` | Playwright: login, grid, orders, repo-renew |
| `scripts/heng_tai_client.py` | HTTP cookie: session check only |

```bash
python scripts/heng_tai_browser.py grid         # save CSV+JSON
python scripts/heng_tai_browser.py orders       # save trade execution CSV+JSON
python scripts/heng_tai_browser.py repo-renew   # open repo renewal page
```

Data output: `docs/jul-24-trading/data/{name}_{account}_{yyyymmdd}.csv` (utf-8-sig).

---

## Key Endpoints

| Endpoint | Method | Returns |
|----------|--------|---------|
| /getPublicKey.action | GET | RSA public key |
| /doLogin.action | POST | JWT token |
| /login.action | POST | JSESSIONID (200 + Set-Cookie) |
| /microservices/xtims-reporting-service/requestCall4Grid.action | POST | Grid data `{count, data}` |
| /secuAccTree/getSecuAccTree.action | POST | Account tree |
| /user/findAllUserList.action | GET | User list with userIds |
| /system/request.action | POST | Config |
| /menuLogin.action | POST | Menu navigation log |
