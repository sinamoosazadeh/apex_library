# AX-02 — Venue Truth, Constraints and Conformance Harness

**Status:** Normative. Every statement about the venue that AXIOM relies on lives here or in the
machine-readable `venue_profile.json` produced by the harness in §10.
**Upstream:** AX-00 (§3 evidence boundary), AX-01 (§5 provenance law).
**Downstream:** AX-03, AX-04, AX-08, AX-11, AX-12, AX-14, AX-15.

**Source tags used below**

| Tag | Meaning |
|---|---|
| `[V-DOC]` | Read directly from Toobit's official API documentation on 2026-10-12 (pages listed in §1.2). |
| `[V-KIT]` | Read from the exchange's official `toobit-docs/agent-kit` repository at commit `2ee2d6b54617974c789a407f74c0bbf15cbb99f7` (2026-03-15). |
| `[V-PROVISIONAL]` | **Not yet verified in the form AXIOM needs**; must be replaced by a `VCH-*` probe result before the affected code path may be enabled in `LIVE`. |
| `[V-PROBE]` | Value must be produced by the harness at runtime and read from `venue_profile.json`; never hardcoded. |

---

## 1. Sources, hierarchy and re-verification

### 1.1 Source hierarchy (`AX-02:§1.1`)

When sources disagree, precedence is:

1. **Live venue response** (what the API actually returns, captured by the harness and stored on the L0
   tape). This is the only authority for trading decisions.
2. **Pinned official documentation** (`api-docs.toobit.com`, captured with date + content hash into
   `docs/venue/`).
3. **Pinned official toolkit** (`toobit-docs/agent-kit` at a fixed commit).
4. Third-party material (blogs, mirrors, prior projects): **never** a source of venue truth. If a
   third-party claim is all we have, the item is `[V-PROVISIONAL]` and its probe is blocking.

### 1.2 What was read on 2026-10-12 (audit trail)

From `api-docs.toobit.com`: `basic-information`, `usdt-m-market-data`, `usdt-m-account-and-trading`,
`usdt-m-websocket-market-data`, `usdt-m-api-v2`, `code-examples`, `usdt-m-error-codes`.
**Not read in full:** spot pages, copy-trading pages, agent/affiliate pages, and the later chunks of
the account/trading and v2 pages. Anything AXIOM depends on that lives in those later chunks is
therefore `[V-PROVISIONAL]` (see §11) until the harness reads it back from the live API.

### 1.3 Re-verification policy (`AX-02:§1.3`)

- On every process start, `exchangeInfo`, `riskLimits`, `commissionRate` are re-fetched and hashed; a
  change in a *policy-relevant* field (filters, status, contractMultiplier, risk tiers, commission)
  raises `EV-VENUE-DRIFT` and re-runs the affected `VCH-*` probes (AX-09 §4.4).
- Every 30 days, the full `VCH` suite is re-run and `venue_profile.json` is re-frozen; the diff is
  reviewed by the operator and journaled.
- Any previously unseen negative error code encountered in `LIVE` is journaled as
  `EV-VENUE-UNKNOWN-CODE`, forces the affected intent into the ambiguity protocol (§9), and triggers a
  documentation re-read task.

---

## 2. Transport, authentication, signing (`AX-02:§2`)

**Base URL:** `https://api.toobit.com` `[V-DOC]`. **Streams:** `wss://stream.toobit.com`, path
`/quote/ws/v1` `[V-DOC]`.

### 2.1 Authentication (`AX-02:§2.1`)

- API key is sent in the header **`X-BB-APIKEY`**; keys and secrets are **case sensitive** `[V-DOC]`.
- Security types: `NONE`, `TRADE`, `USER_DATA` (signed), `USER_STREAM`, `MARKET_DATA` `[V-DOC]`.
- AXIOM requires exactly one key with **`TRADE` enabled and withdrawal disabled**, and **IP
  whitelisting enabled** (the venue rejects unlocked keys with `-1023` `[V-DOC]`; see AX-12 §5).
- No credential may ever be written to the repository, the journal, logs, notifications or chat
  (INV-8). The key is loaded only by the config loader from the OS secret store (AX-12 §5.2).

### 2.2 Signing law (`AX-02:§2.2`) — normative, exact

1. Signature = `hex_lowercase(HMAC_SHA256(key = secretKey, message = totalParams))` `[V-DOC]`.
2. `totalParams` = **query string concatenated with the request body**, where the body participates
   only for `POST/PUT/DELETE` with `Content-Type: application/x-www-form-urlencoded` `[V-DOC]`.
3. **Parameter order in the request must match the order used for signature calculation** `[V-DOC]`.
   AXIOM therefore serialises parameters as an *ordered list*, signs that exact string, and sends that
   exact string. Sorting is forbidden (it changes the signed message and risks a `-1022`).
4. For `/api/v2/` routes with `Content-Type: application/json`, `totalParams = queryString + jsonBody`
   with **no separator**; the JSON body must be a **single-line, compact, byte-identical** copy of what
   is sent (the server strips line terminators when rebuilding the string) `[V-DOC]`.
5. `timestamp` (ms, UTC) is mandatory for signed routes; `recvWindow` is optional and **defaults to
   5000 ms** `[V-DOC]`. A server clock more than 1 s ahead of the client timestamp is rejected
   (`-1021`) `[V-DOC]`.
6. Signature values are **lowercase hex**; uppercase fails `[V-DOC]`.
7. The `signature` field itself is never part of the signed message `[V-DOC]`.

**Implementation constraints derived from the above (normative):**

| ID | Rule |
|---|---|
| `AX-02:§2.2-R1` | The wire layer exposes `signed_request(method, path, ordered_params, category) -> RawResponse`; no other code may construct signed requests. |
| `AX-02:§2.2-R2` | Parameter values are formatted by one canonical formatter: decimal quantities/prices as **plain decimal strings** (no exponent, no trailing-zero ambiguity — the exact string is stored, signed and sent); integers as integers; booleans lower-case. |
| `AX-02:§2.2-R3` | Clock: the client keeps `server_offset_ms` estimated by the procedure in §2.3 and rejects *any* signed request when `abs(server_offset_ms) > OFFSET_MAX_MS` (AX-15 `P-VEN-001`). |
| `AX-02:§2.2-R4` | Known-answer tests: `T-SIGN-001` (v1 form-encoded, fixed vector), `T-SIGN-002` (v2 JSON body), `T-SIGN-003` (parameter order permutation must change the signature), `T-SIGN-004` (uppercase rejected by our own validator). |

### 2.3 Clock discipline (`AX-02:§2.3`)

The venue's `-1021` behaviour makes clock correctness a *trading-safety* requirement, not hygiene.

**Offset estimation (procedure, `[D]`):** every 60 s, issue `GET /api/v1/time` (weight 1). For each
sample record `t_send` (before request), `t_recv` (after response), `t_server`:
`rtt = t_recv - t_send`; `offset_i = t_server - (t_send + rtt/2)`.
Keep the last `N=8` samples; the accepted offset is the value with the **minimum rtt** (classic NTP
filtering: the sample with the least network-induced bias). `max_rtt_used = 2 s`; samples above that
are discarded. The offset is only updated while `rtt < RTT_MAX_MS` (AX-15 `P-VEN-002`).

**Consequences:**
- `recvWindow` policy: send `recvWindow = max(5000, ceil(4 × p95_rtt_ms))` `[D]` — the venue default
  (5000) is used unless measured RTT history justifies more.
- If `-1021` is ever received: no retry with a new timestamp until the offset is re-estimated; the
  intent is routed through the ambiguity protocol if it was an order submission (a `-1021` rejection
  is *safe*: the order was not created — but this must be confirmed by query, not assumed, because the
  docs classify 5XX and timeouts as unknown while `-1021` is a definitive 4XX-class business error;
  AXIOM treats *any* non-success on a state-changing route as unresolved until Queried, see §9.1).
- All decision timestamps, bar boundaries and funding timers are computed in **UTC epoch ms**, never
  in local time; the bar-close detection uses the *server* clock offset (AX-03 §4.3).

---

## 3. REST inventory (`AX-02:§3`)

Weights are the venue's request-weight budget; `ORDERS` counts separately (60 per 2 s `[V-DOC]`).
"Use" states which AXIOM module consumes the endpoint and why.

### 3.1 Public market data

| Endpoint | Limit / weight | Used by | Notes / design consequence |
|---|---|---|---|
| `GET /api/v1/time` | weight 1 `[V-DOC]` | `vap` clock | basis of §2.3 |
| `GET /api/v1/exchangeInfo` | weight 1 `[V-DOC]` | `mdp`, `pfp`, `rg` | spot rules in `symbols`, perp rules in `contracts`; fields include `symbol` (`BTC-SWAP-USDT`), `status`, `contractMultiplier`, `marginToken`, `inverse`, `index`, `riskLimits[]`, `categories[]`, filters (§6.4). Doc warns the `rateLimits` field will be removed `[V-DOC]` → never rely on it |
| `GET /quote/v1/depth` | weight 1 for limit ≤100, 5 for 500, 10 for 1000 `[V-DOC]` | `mdp` cold start, `exp` pre-trade check | default limit 100; `limit=0` returns a very large payload `[V-DOC]` → forbidden in AXIOM |
| `GET /quote/v1/depth/merged` | weight 1 `[V-DOC]` | `exp` (T3) | merged-scale book; not needed for the core path |
| `GET /quote/v1/trades` | weight 1; default & max 60 `[V-DOC]` | `mdp` gap repair | 60 trades is the entire REST window → REST cannot rebuild a trade tape; the WS stream is mandatory (§4) |
| `GET /quote/v1/klines` | weight 1; default 1000, max 1000 `[V-DOC]` | `mdp` bar backfill/repair, `lnp` research | returns `[t,o,h,l,c,v,closeTime,quoteVol,trades,takerBuyBase,takerBuyQuote]` `[V-DOC]` — **taker-buy volumes are provided**, which makes signed-flow features computable from bars alone at low cost |
| `GET /quote/v1/index/klines` | default 2000, max 2000 `[V-DOC]` | `mdp` basis features | index bars; `from`/`to` are mandatory `[V-DOC]` |
| `GET /quote/v1/index` | — | `mdp` | spot index price for the pair underlying the contract |
| `GET /quote/v1/indexPriceComponents` | — `[V-DOC]` | `lnp` (T3), `rg` sanity | reveals the composite: `index`, `edp` (10-minute average), and the constituent exchanges/weights (sample lists BITGET, KUCOIN, COINBASE, MEXC, BYBIT, OKEX, BINANCE) `[V-DOC]`. Consequence: the venue index is a **cross-exchange composite**, so index-based features are not purely venue-local |
| `GET /quote/v1/markPrice` | **≤ 5 requests/second** `[V-DOC]` | `rg` liquidation distance, `mdp` | symbol ⇒ single object; omitted ⇒ array of all `[V-DOC]`. Prefer the WS `markPrice` stream to conserve this budget |
| `GET /quote/v1/markPrice/klines` | — `[V-DOC]` | `mdp`, `exp` | mark-price bars |
| `GET /quote/v1/openInterest` | weight 1 | `mdp` | **current value only, no history** `[V-DOC]` ⇒ AXIOM must build its own OI series by polling (§5.2) |
| `GET /quote/v1/globalLongShortAccountRatio` | default 30, max 500; only last 30 days `[V-DOC]` | `lnp` (T3) | account-count ratio, not size-weighted; low priority |
| `GET /quote/v1/contract/ticker/24hr` | weight 1 single symbol, **40 without symbol** `[V-DOC]` | `mdp` universe screen | never call without `symbol` |
| `GET /quote/v1/contract/ticker/price` | — | `mdp` | last price |
| `GET /api/v1/futures/fundingRate` | — `[V-DOC]` | `mdp`, `pfp` | fields: `rate`, `period` (`8H` in samples), `nextFundingTime`, `interest`, `fundingRateCap` (sample `0.003`), `fundingRateFloor` (sample `-0.003`) `[V-DOC].` |
| `GET /api/v1/futures/historyFundingRate` | default 20, max 1000 `[V-DOC]` | `mdp`, `lnp` | settled rates with `settleTime` — the correct input for carry accounting; **settlement timestamps are the venue's, not assumed** |
| `GET /api/v1/futures/riskLimits` | weight 1 `[V-DOC]` | `pfp`, `rg` | tiers `{level, quantity, maintainMargin, initialMargin, maxLeverage}` sorted by quantity `[V-DOC]`; drives §6.6 |
| `GET /api/v1/futures/insuranceBySymbol` | 14 days, refreshed daily 00:00 UTC `[V-DOC]` | `lnp` (T3) | venue-wide risk context; not a trading input by default |

### 3.2 Private account and trading (v1 surface — AXIOM's canonical wire)

| Endpoint | Weight | Use | Notes |
|---|---|---|---|
| `POST /api/v1/futures/order` | 1 `[V-PROVISIONAL]` | `exp` | place order; parameters and semantics in §6 |
| `POST /api/v1/futures/batchOrders` | 3 `[V-DOC]` | `exp` (T2) | batch placement; body is a JSON **array** while signature is form-style `[V-DOC]` — the only route where body ≠ signature string; AXIOM restricts its use to the flatten path |
| `POST /api/v1/futures/order/update` | 2 `[V-DOC]` | `exp` (T2) | modify `LIMIT`/`STOP`/`STOP_PROFIT_LOSS`; supports `quantity`, `valueQuantity`, `price`, `priceType`, `stopPrice`, `triggerBy`, `stopType`, `activePrice`, `fallbackType`, `fallbackQuantity` `[V-DOC]`; unset fields inherit from the original order `[V-DOC]` |
| `DELETE /api/v1/futures/order` | 1 `[V-DOC]` | `exp` | cancel by `orderId` or `origClientOrderId` (+`type`) `[V-DOC]` |
| `DELETE /api/v1/futures/batchOrders` | 3 `[V-DOC]` | `exp` emergency | cancel-all for a `symbol`+`side` `[V-DOC]`; used only in the flatten/kill path |
| `DELETE /api/v1/futures/cancelOrderByIds` | 3 `[V-DOC]` | `exp` (T2) | up to 100 ids; response `code:200` with a `result[]` list of per-id failures (e.g. `-2013`) `[V-DOC]` |
| `GET /api/v1/futures/order` | 1 `[V-DOC]` | `exp` ambiguity resolution | requires `orderId` or `origClientOrderId`; `type` supports only `LIMIT`/`STOP` `[V-DOC]`; a `STOP` query may return a TP/SL order `[V-DOC]` |
| `GET /api/v1/futures/openOrders` | 1 `[V-DOC]` | `exp` reconciliation | current working orders |
| `GET /api/v1/futures/historyOrders` | — `[V-KIT]` | `exp`, `lnp` | historical orders; time-range bounds apply (`-1129` one-year range `[V-DOC]`) |
| `GET /api/v1/futures/positions` | — `[V-KIT]` | `rg`, `exp` | current positions (omit `symbol` for all) |
| `GET /api/v1/futures/historyPositions` | — `[V-KIT]` | `lnp` | closed positions |
| `POST /api/v1/futures/leverage` | — `[V-KIT]` | `pfp` | set leverage per symbol; **AXIOM's rule: set only downward-relevant values derived in AX-07 §8, never above the tier cap** |
| `GET /api/v1/futures/accountLeverage` | — `[V-KIT]` | `rg` | read back leverage to verify it was applied |
| `POST /api/v1/futures/marginType` | — `[V-KIT]` | `pfp` | AXIOM uses `ISOLATED` only (§6.6) |
| `POST /api/v1/futures/position/trading-stop` | — `[V-KIT]` | `exp` | position-level TP/SL; the primary protection mechanism under the v1 wire |
| `GET /api/v1/futures/userTrades` | — `[V-KIT]` | `exp`, `lnp` | fills; the ground truth for cost accounting and reconciliation |
| `GET /api/v1/futures/balance` | — `[V-KIT]` | `rg` | account equity/margin fields |
| `GET /api/v1/futures/commissionRate` | — `[V-KIT]` | `exp` cost model | **the fee is read, never assumed** (`AX-08:§3.1`) |
| `GET /api/v1/futures/todayPnl` | — `[V-KIT]` | `rg` | daily PnL reference |
| `GET /api/v1/futures/balanceFlow` | 5 `[V-DOC]` | `cop` | transfers only; not a trading input |
| `GET /api/v1/account` | — `[V-KIT]` | `rg` | account snapshot |
| `GET /api/v1/account/checkApiKey` | — `[V-KIT]` | `cop` startup | validates key validity/permissions at boot |
| `POST /api/v1/subAccount/transfer` | 1 `[V-DOC]` | **forbidden** | AXIOM never moves funds |
| `POST /api/v1/account/withdraw`, `/api/v1/futures/flashClose`, `/api/v1/futures/reversePosition`, `/api/v1/futures/positionMargin`, `/api/v1/futures/autoAddMargin` | — | **forbidden** | present in the API, deliberately unused AXIOM capabilities; the code must not contain call sites (an import-lint test enforces this: `T-SEC-003`) |

### 3.3 v2 surface — evaluated, not adopted (`AX-02:§3.3`)

The venue exposes a newer `/api/v2/futures/*` family `[V-DOC]`: kebab-case paths, a
`{code, msg, data}` envelope, JSON request bodies signed as `queryString + jsonBody` `[V-DOC]`,
`side = BUY|SELL` with an explicit `positionSide = LONG|SHORT`, a native `MARKET` type, and — the
commercially interesting part — **entry orders that can carry `takeProfit`/`stopLoss` with their own
trigger type and order type in the same request** `[V-DOC]`.

**Decision (`ADR-006`, AX-18):** AXIOM's canonical wire is **v1**. Reasons: (a) it is the surface used
by the exchange's own official toolkit `[V-KIT]`, (b) it is the more completely documented family for
the endpoints AXIOM needs (positions, leverage, margin type, commission rate, TP/SL), (c) a
simultaneous adoption of two wire families would double the signing, status-mapping and conformance
surface for no alpha (A7). **Migration trigger (pre-specified):** if the harness shows that the v1
wire cannot place protection within the maximum unprotected window (`P-EXE-003`) with acceptable
reliability, the design switches to v2 for *order placement only*, and the VCH suite must pass in full
for v2 before any `LIVE` use. This is a decision rule, not an open question.

**Consequence of not adopting v2 today:** the unprotected window between entry fill and protective
order acknowledgement is a *measured* quantity (`VCH-23`) and a *monitored* risk state (`AX-08 §6.4`),
not an assumed-zero.

---

## 4. WebSocket inventory (`AX-02:§4`)

Base `wss://stream.toobit.com`, path `/quote/ws/v1` `[V-DOC]`. Subscriptions are JSON messages with
`{symbol(s), topic, event ∈ {sub, cancel, cancel_all}, params}` `[V-DOC]`.

| Topic | Payload (as documented) | AXIOM use | Caveats found |
|---|---|---|---|
| `trade` | array of `{v, t, p, q, m}`; 60 trades are pushed immediately on subscribe, then real-time `[V-DOC]` | trade tape, flow features, cascade detection | `m` is documented as a boolean with the comment `true = buy, false = sell` `[V-DOC]` — the *taker side* convention must be **probed** (`VCH-11`), because a mis-signed flow feature is worse than no feature |
| `kline_<interval>` | latest bar, pushed every second: `{t, s, sn, c, h, l, o, v}` `[V-DOC]` | bar construction, close detection | the sample carries **no quote volume and no trade count**, and `v` may be `"0"` in the sample `[V-DOC]`; therefore bar *volume semantics* come from REST backfill for closed bars (`VCH-12`) |
| `depth` | partial book snapshot with `b`/`a` arrays and a version string like `112801745_18` (`_18` = 18-bit precision) `[V-DOC]` | book metrics, participation caps | the doc says versions are **not guaranteed unique** `[V-DOC]` ⇒ version is *not* a reliable sequence; AXIOM uses its own monotonic `recv_seq` plus timestamp and treats venue version only as a diagnostic |
| `diffDepth` | incremental levels `[price, qty]`; `qty = 0` ⇒ delete level `[V-DOC]` | book maintenance | same version caveat; must be applied on top of a `depth` snapshot |
| `markPrice` | `{symbol, markPrice, time}` `[V-DOC]` | liquidation distance, stop triggering reference | — |
| `index` | `{symbol, index, edp, formula, time}`; request supports `reduceSerial`, `binary`, `limit` (sample `1500`) `[V-DOC]` | basis features | `edp` is the 10-minute average index price `[V-DOC]` — never confuse it with the spot index |
| `realtimes` | per-symbol 24h ticker (`c,h,l,o,v,qv,m,e=301`) `[V-DOC]` | cheap universe screen | `m` here is a *margin* field, unrelated to the trade stream's `m` `[V-DOC]` — a documented collision the parser must not conflate |
| `wholeRealTime` | all-symbol 24h ticker `[V-DOC]` | universe screen, breadth | samples show spot-style symbols (`ARC_SOL_ONCHAINUSDT`) `[V-DOC]` ⇒ filter by contract symbol pattern |
| `bookTicker` / `wholeBookTicker` | best bid/ask `{b, bq, a, aq, E, t}` `[V-DOC]` | spread cost, microprice | — |

**Connection law (`AX-02:§4.1`):**

1. Heartbeat: the client sends `{"ping": <ms>}` and expects `{"pong": <ms>}`; **the server disconnects
   within 5 minutes** otherwise `[V-DOC]`. AXIOM pings every `WS_PING_S` (AX-15 `P-VEN-010`), and
   treats a missing pong as a dead connection.
2. Reconnect: exponential backoff with jitter, capped; on reconnect, **resubscribe** and re-synchronise
   state: a fresh `depth` snapshot before applying `diffDepth`; bars are re-fetched from REST for any
   interval whose coverage has a hole.
3. Every message is stored on L0 **as received** (byte-for-byte payload plus receive metadata), before
   any interpretation. Interpretation failures never block storage (INV-10).
4. Gap detection uses: (a) monotonic trade id `v` `[V-DOC]` (documented as globally increasing and
   unique across symbols `[V-DOC]`), (b) our own `recv_seq` per stream, (c) bar boundary continuity.
   The trade-id property is `[V-DOC]`-stated but **probe-verified** (`VCH-13`) before it is used as a
   completeness oracle.
5. **User-data stream.** The documentation set includes `USER_STREAM` as a security type and an error
   code for an invalid `listenKey` (`-1125`) `[V-DOC]`, which implies a user-data stream exists, but
   the endpoint flow was not found in the pages read. **AXIOM does not depend on it**: fills and
   positions are obtained by REST reconciliation (§8 of AX-08). If `VCH-30` finds a working user-data
   stream, it is an optional latency improvement for reconciliation, adopted only after an ADR.

---

## 5. Capability matrix and the consequences the design must carry (`AX-02:§5`)

### 5.1 Available

Prices (last, mark, index, 24h), bars for all standard intervals with taker-buy split, trades with a
side flag and a monotonic id, top-of-book quotes, partial and incremental depth, position/order/fill
history of our own account, funding rate + settled funding history, current open interest, risk-limit
tiers, commission rate, account balance/margin state.

### 5.2 Must be constructed by us (because the venue keeps no history)

| Missing history | Construction method | Cost |
|---|---|---|
| Open-interest time series | poll `GET /quote/v1/openInterest` for each universe instrument on a fixed cadence, store on L0 | weight 1 per call; a 5-minute cadence over N instruments costs `N/5` weight per minute — negligible against 3000 `[D]` |
| Book-derived series (spread, depth, imbalance) | record the `bookTicker` stream continuously and `depth` snapshots at a fixed cadence | no request cost; storage cost bounded by retention (AX-04 §7) |
| Realized execution costs | internal ledger of fill vs decision mid (AX-08 §3.3) | none |
| Cross-sectional history of the venue universe | daily snapshots of `exchangeInfo` + ticker screens | one call/day + hashes |

### 5.3 Absent — and therefore out of scope for alpha (A3, AX-05 §2)

Options data (no options venue ⇒ no implied vol, no vol-risk-premium family); L3 queue-level data;
historical order-book depth older than what we record ourselves; trade history older than the venue's
REST windows; any cross-venue order-book data (and even cross-venue *reference* data would need an
owner decision, AX-04 §9); per-trader positioning beyond the account-count long/short ratio.

---

## 6. Order, position and margin semantics (`AX-02:§6`)

### 6.1 v1 order model (`AX-02:§6.1`) `[V-DOC]`/`[V-KIT]`

- `side ∈ {BUY_OPEN, SELL_OPEN, BUY_CLOSE, SELL_CLOSE}` — direction and intent are fused into one
  field. AXIOM's mapping (`[D]`, unit-tested by `T-SIDE-001`):
  `LONG entry → BUY_OPEN`, `SHORT entry → SELL_OPEN`, `LONG exit → SELL_CLOSE`, `SHORT exit → BUY_CLOSE`.
- `type ∈ {LIMIT, STOP}` in v1. **`type=MARKET` is not a v1 parameter**: a market order is expressed
  as `type=LIMIT` with `priceType=MARKET` `[V-DOC]`. AXIOM treats the pair `(LIMIT, MARKET)` as the
  single canonical "taker order" form to avoid the known rejection mode.
- `priceType ∈ {INPUT, MARKET}` (the toolkit additionally mentions `OPPONENT`, `QUEUE`, `OVER`) `[V-KIT]`;
  AXIOM uses only `INPUT` (bounded price) and `MARKET` (defined below).
- `timeInForce ∈ {GTC, FOK, IOC, POST_ONLY}` for `LIMIT` `[V-DOC]`.
- `quantity` is required; `valueQuantity` (quote-notional) is supported `[V-DOC]`. AXIOM sizes in
  *contract quantity* (AX-07 §7) because the risk math is in price units; `valueQuantity` is used only
  in the emergency flatten path where a notional instruction is more robust.
- `newClientOrderId` is mandatory for batch routes `[V-DOC]` and strongly recommended for single
  orders; **AXIOM always sends it** — it is the idempotency key (§9). Duplicate ids are rejected
  (`-1141`) `[V-DOC]`, which is exactly the behaviour INV-3 depends on.
- `stopPrice`, `triggerBy ∈ {MARK_PRICE, CONTRACT_PRICE}` (default `CONTRACT_PRICE`) `[V-DOC]`,
  `stopType ∈ {FIXED_STOP, TRAILING_STOP}`, `activePrice`, `fallbackType ∈ {RATE, PRICE}`,
  `fallbackQuantity` for trailing stops `[V-DOC]`.
- Stop order status vocabulary differs from the regular-order vocabulary (`ORDER_NEW` /
  `ORDER_FILLED` / `ORDER_CANCELED` vs `PENDING_NEW` / `NEW` / `PARTIALLY_FILLED` / `FILLED` /
  `CANCELED` / `REJECTED`) `[V-DOC]`, and TP/SL orders are auto-assigned a `clientOrderId` of the form
  `STOP_LONG_PROFIT_<ts>` `[V-DOC]` ⇒ AXIOM's status mapper must handle both vocabularies and
  server-generated ids (`T-MAP-001`).

### 6.2 Order type policy (`AX-02:§6.2`) — which construct AXIOM uses, and why

| Purpose | Construct | Reason |
|---|---|---|
| Entry (default) | `type=LIMIT`, `priceType=INPUT`, `timeInForce=IOC`, price = bounded limit from AX-08 §4.2 | gives a hard worst-price bound; an IOC that fails to fill simply does not fill, which is a *known* state (A1, A5) |
| Entry (only if policy switch enabled) | `POST_ONLY` limit | only when a measured maker-fee advantage and measured fill-time distribution justify it; otherwise the missed-fill cost dominates |
| Shortfall completion after partial fill | re-evaluated `IOC` with a fresh snapshot, at most `P-EXE-005` times | each attempt is a *new* decision under A1, not a chase |
| Protection | `POST /api/v1/futures/position/trading-stop` (position-level TP/SL) **and**, when the position cannot be protected by that route, `type=STOP` with `triggerBy=MARK_PRICE` | mark-price trigger avoids wick-triggered exits and is the venue's own liquidation reference (AX-07 §9) |
| Intentional full exit at a bounded price | `type=LIMIT`, `priceType=INPUT`, `timeInForce=IOC` | same bound logic as entry |
| Emergency flatten | `type=LIMIT`, `priceType=MARKET` (v1 taker form) with `BUY_CLOSE`/`SELL_CLOSE`, sizing from live position query, after cancelling protective orders | the only place where price certainty is deliberately surrendered to obtain certainty of exit; bounded by the blast-radius budget (INV-12) and journaled as `EV-EXEC-EMERGENCY` |
| Trailing stop | supported by the venue (`TRAILING_STOP` + `fallbackType`) but **not used by default** | its trigger dynamics are venue-internal, less observable, and stop*tightening* is better expressed as our own re-evaluated stop (AX-07 §9.3) |

### 6.3 Outcome-relevant order semantics (`AX-02:§6.3`)

- `status=PENDING_NEW` exists, so a successful **acceptance** is not a fill.
- `executedQty`/`executeQty` are both present and documented as synonyms `[V-DOC]`; `avgPrice=0` means
  "no fill yet" `[V-DOC]` — zero must never be treated as a price.
- `marginLocked` reflects reserved margin per order `[V-DOC]` — this is the number AXIOM uses for the
  open-order margin reservation in its own margin-utilisation calculation (AX-07 §8.4), rather than
  guessing the venue's reservation rule.

### 6.4 Instrument filters (`AX-02:§6.4`) `[V-DOC]`

From `exchangeInfo`, per symbol, AXIOM must apply: `PRICE_FILTER{minPrice,maxPrice,tickSize}`;
`LOT_SIZE{minQty,maxQty,stepSize}`; `MIN_NOTIONAL{minNotional}`; `TRADE_AMOUNT{minAmount,maxAmount,
minBuyPrice}`; `LIMIT_TRADING{buyPriceUpRate,sellPriceDownRate,...}`; `MARKET_TRADING{buyPriceUpRate,
sellPriceDownRate}`; `OPEN_QUOTE{...}`.
**Known ambiguity:** the documented comment says `LOT_SIZE.minQty/maxQty` for contracts are
"token quantity, not contracts" `[V-DOC]`, while the order parameter is described as "quantity
(contracts)" elsewhere `[V-DOC]`, and `contractMultiplier` (sample `0.0001` for `BTC-SWAP-USDT`)
converts contracts to base units. The exact unit chain is **probe-resolved** (`VCH-20`) and the result
is stored in `venue_profile.json` as `qty_unit_chain`; until then, quantization is implemented as a
*direction-aware* rounding towards risk reduction (AX-03 §5.3), which is safe under any unit chain.

### 6.5 Position and margin model (`AX-02:§6.5`)

- Position mode: AXIOM uses **one-way** mode; the v1 side vocabulary (`BUY_OPEN`…`SELL_CLOSE`)
  matches that model `[D]`.
- Margin mode: **isolated**, set explicitly via `marginType` and verified by reading it back
  (`T-STATE-002`), because cross-margin couples the whole account to a single position's loss (A5).
- Leverage: set via `POST /api/v1/futures/leverage` and verified via `accountLeverage`; the *value* is
  derived in AX-07 §8 from (a) the position's stop distance, (b) the allowed margin utilisation,
  (c) the tier cap from `riskLimits`. Never a round "nice" number.

### 6.6 Risk tiers (`AX-02:§6.6`) `[V-DOC]`

`riskLimits[]` gives `quantity` brackets with `initialMargin`, `maintainMargin`, `maxLeverage`. AXIOM
computes, for the actual position size: the applicable tier, the maintenance-margin rate, the implied
liquidation price band, and the resulting **liquidation distance**; a position whose liquidation
distance is below `P-RSK-014` (derived in AX-07 §9.4) is refused (INV-1). Tiers are refreshed on every
boot and on `EV-VENUE-DRIFT`.

### 6.7 Price bands (`AX-02:§6.7`)

`LIMIT_TRADING.buyPriceUpRate/sellPriceDownRate` (sample `0.1` = ±10 %) bound limit prices versus the
mark/last reference `[V-DOC]`. The order price validator must include this band; violations surface as
`-1138/-1195..-1201` `[V-DOC]`. Because the band is reference-relative and the reference moves, the
check is performed immediately before submission with the freshest mark price.

---

## 7. Rate-limit and request-budget model (`AX-02:§7`)

### 7.1 Published limits `[V-DOC]`

| Limit | Value | Failure mode |
|---|---|---|
| `REQUEST_WEIGHT` | 3000 per 1 minute | HTTP 429, `-1003 TOO_MANY_REQUESTS`; documented IP-ban variant |
| `ORDERS` | 60 order requests per 2 seconds | HTTP 429, `-1015 TOO_MANY_ORDERS` |
| Per-endpoint weights | §3 tables; `24hr` without symbol = 40; `depth` by limit | 429 |
| Mark price | ≤ 5 requests/second | 429 |
| Headers on every response | `X-Api-Limit-Status` (remaining), `X-Api-Limit` (max), `X-Api-Limit-Reset-Timestamp` `[V-DOC]` | used for feedback control |

**Venue guidance read verbatim from the docs:** after a 429, reduce request rate immediately and retry
only after the reset timestamp; do not retry at high frequency; prefer WebSocket streams over polling
`[V-DOC]`.

### 7.2 AXIOM's internal budget (`AX-02:§7.2`) — derived, not copied

Definitions: `W_pub` = published weight limit (3000/min, `[V]`), `f_safe` = safety fraction,
`W_int = floor(f_safe × W_pub)`. With `f_safe = 0.50` (AX-15 `P-VEN-020`, class `[O]` with default
0.50 and allowed range 0.20–0.70) the internal ceiling is 1500 weight/min and 30 order requests/2 s.
**Derivation of the default** `[D]`: the reserve must cover (a) clock sync, (b) exchangeInfo/riskLimit
refreshes, (c) the reconciliation burst after a restart, and (d) a full-universe bar backfill after a
network outage. A reserve of ≥ 50 % is the smallest value that keeps the post-outage recovery inside a
single minute at the universe sizes AXIOM supports (`AX-04 §8`). The class is `[O]` because the owner
may trade recovery speed against daily operating cost, but the *range* is bounded and the
justification is fixed.

**Priority classes** (strict, enforced by one token-bucket governor with per-class buckets):

| Class | Contents | Budget share | Behaviour when exhausted |
|---|---|---|---|
| P0 Safety | position query, open-orders query, cancel, flatten, kill | 40 % | never starved: P0 may borrow from lower classes |
| P1 Decision-critical | order submission, protective-order placement, mark price for risk checks | 35 % | queues with deadline; if the deadline passes, the intent is **abandoned, not forced** (fail-closed) |
| P2 Maintenance | reconciliation sweep, fills, balance, commissionRate | 20 % | defers to the next tick |
| P3 Optional/research | OI polling, funding history, ratio data, insurance, index components | 5 % | simply skipped; recorded as a coverage gap |

**Backoff law** `[D]`: on 429 or `-1003`/`-1015`, exponential backoff with base 1 s, factor 2, jitter
uniform ±20 %, maximum 60 s, and honour `X-Api-Limit-Reset-Timestamp` when it is later than the
computed wait. On `-1006`/`-1007` (unknown execution status) the request is **never simply retried**: it
enters the ambiguity protocol (§9).

---

## 8. Error taxonomy and required response (`AX-02:§8`)

Classes: **SAFE-RETRY** (idempotent read or a definitively-failed write that may be re-attempted),
**UNKNOWN** (execution status unknown ⇒ reconcile), **BUSINESS-REJECT** (a precondition failed; the
intent must be re-derived, not retried), **FATAL** (configuration/security/infrastructure; halt the
affected scope).

| Code | Name `[V-DOC]` | Class | Required AXIOM response |
|---|---|---|---|
| `-1000` | UNKNOWN | UNKNOWN (if write) / SAFE-RETRY (if read) | reads: retry with backoff; writes: ambiguity protocol |
| `-1001` | DISCONNECTED | SAFE-RETRY | retry with backoff |
| `-1002` | UNAUTHORIZED | FATAL | stop trading, alert operator (key/permission problem) |
| `-1003` | TOO_MANY_REQUESTS | SAFE-RETRY (throttled) | backoff per §7.2; if it recurs, reduce cadence and degrade |
| `-1005` | NO_PERMISSION | FATAL | key lacks a required permission; halt |
| `-1006` | UNEXPECTED_RESP | **UNKNOWN** | ambiguity protocol; never blind retry |
| `-1007` | TIMEOUT | **UNKNOWN** | ambiguity protocol |
| `-1014` | UNKNOWN_ORDER_COMPOSITION | BUSINESS-REJECT | the parameter combination is invalid for this venue; log, do not retry, file a design defect if AXIOM generated it |
| `-1015` | TOO_MANY_ORDERS | SAFE-RETRY (throttled) | order-rate backoff |
| `-1016` | SERVICE_SHUTTING_DOWN | UNKNOWN for writes | ambiguity protocol; expect a maintenance window |
| `-1020` | UNSUPPORTED_OPERATION | FATAL (design) | halt the affected path; ADR-level review |
| `-1021` | INVALID_TIMESTAMP | SAFE-RETRY after clock re-estimation | §2.3; writes are re-queried to confirm non-creation |
| `-1022` | INVALID_SIGNATURE | FATAL | halt; a signing defect is a release blocker |
| `-1023` | BIND_IP_WHITE_LIST_FIRST | FATAL | operator must whitelist the IP |
| `-1031` | FEATURE_SUSPENDED | BUSINESS-REJECT | the venue disabled the feature; degrade the dependent capability |
| `-1100`–`-1106`, `-1111`–`-1121` | parameter/format/precision family | BUSINESS-REJECT (design defect if reachable) | our validator must make these unreachable (`T-VALID-*`); if one occurs, log as a defect and refuse the intent |
| `-1125` | INVALID_LISTEN_KEY | n/a (unused) | not used by AXIOM |
| `-1127`, `-1129` | range limits | BUSINESS-REJECT (design defect) | query builder must respect documented maxima |
| `-1130` | INVALID_PARAMETER | BUSINESS-REJECT | log and refuse; investigate if the parameter was generated by AXIOM |
| `-1131` | INSUFFICIENT_BALANCE | BUSINESS-REJECT | the *sizing* was wrong: reduce size, re-derive; do not retry unchanged; record a margin-model defect if it recurs |
| `-1132`–`-1137` | price/quantity bound/precision family | BUSINESS-REJECT | pre-trade validator must catch these; refusal + defect ticket |
| `-1138` | ORDER_PRICE_WAVE_EXCEED | BUSINESS-REJECT | price band violation; re-price from fresh reference (§6.7) |
| `-1139` | ORDER_HAS_FILLED | BUSINESS info | the order is done; cancel attempts on filled orders are normal |
| `-1140`, `-1199`–`-1203`, `-1206` | amount/quantity limits | BUSINESS-REJECT | sizing/liquidity cap must prevent; refusal + defect ticket |
| `-1141` | ORDER_DUPLICATED | **SAFE-BY-DESIGN** | this is the idempotency guard working: query the original order by client id and adopt its state |
| `-1142` | ORDER_CANCELLED | info | target order already cancelled |
| `-1143` | ORDER_NOT_FOUND_ON_ORDER_BOOK | info | likely already filled/cancelled; query to confirm |
| `-1144` | ORDER_LOCKED | BUSINESS-REJECT | the venue locked it; treat as non-cancellable and escalate |
| `-1145` | ORDER_NOT_SUPPORT_CANCELLATION | BUSINESS-REJECT | do not attempt that cancel class again |
| `-1146` | ORDER_CREATION_TIMEOUT | **UNKNOWN** | ambiguity protocol |
| `-1147` | ORDER_CANCELLATION_TIMEOUT | **UNKNOWN** | ambiguity protocol |
| `-1148`–`-1150` | precision/create/cancel failures | BUSINESS-REJECT / UNKNOWN | `-1149` treated as UNKNOWN on writes until queried; `-1150` re-queried |
| `-1151` | SYMBOL_PROHIBIT_ORDER | BUSINESS-REJECT | instrument not open; remove from universe for the session |
| `-1153`, `-1171`, `-1204` | user/account problems | FATAL | halt and alert |
| `-1156` | ORDER_QUANTITY_INVALID | BUSINESS-REJECT | validator defect if reachable |
| `-1157` | SYMBOL_API_TRADING_NOT_AVAILABLE | BUSINESS-REJECT | API trading forbidden for that instrument (`status=API_TRADE_FORBIDDEN`); exclude it |
| `-1158` | CREATE_LIMIT_MAKER_ORDER_FAILED | BUSINESS-REJECT | POST_ONLY crossing the book; re-derive price |
| `-1161`, `-1164` | margin manoeuvres | n/a | AXIOM never adjusts margin |
| `-1165`, `-1166` | invalid stop/callback type | BUSINESS-REJECT | validator defect if reachable |
| `-1181`, `-1182` | withdrawal/deposit disallowed | n/a | out of scope |
| `-1193` | ORDER_COUNT_LIMIT | BUSINESS-REJECT | too many working orders; the open-order cap policy must prevent it |
| `-1194` | MARKET_ORDER_FORBIDDEN | BUSINESS-REJECT | the instrument forbids the taker form; emergency flatten must then use a wide bounded IOC limit |
| `-1195`–`-1201` | limit price bands | BUSINESS-REJECT | §6.7 |
| `-1207` | PLAN_ORDER_COUNT_LIMIT | BUSINESS-REJECT | cap on conditional orders; policy must prevent it |
| `-2010` | NEW_ORDER_REJECTED `[V-KIT]` | BUSINESS-REJECT | refuse; classify by the accompanying message |
| `-2011` | CANCEL_REJECTED `[V-KIT]` | BUSINESS-REJECT | order state changed; query then decide |
| `-2013` | NO_SUCH_ORDER `[V-DOC]` (seen in bulk-cancel results) | info | order already gone; query to confirm state |
| `-2014`, `-2015`, `-2017` | key format/permission/expiry `[V-KIT]` | FATAL | halt; operator action |
| `-1121` | BAD_SYMBOL | BUSINESS-REJECT | symbol mapping defect; defect ticket (contracts use `BTC-SWAP-USDT`, not `BTCUSDT`) |
| HTTP 403 | WAF | FATAL (operational) | stop all traffic; the source IP is being filtered; escalate |
| HTTP 429 | rate limited | SAFE-RETRY (throttled) | §7.2 |
| HTTP 5XX | server side | **UNKNOWN for writes** `[V-DOC]` | the documentation states explicitly: *do not treat as a failure; execution status is UNKNOWN* `[V-DOC]` ⇒ ambiguity protocol |

**Rule (`AX-02:§8-R1`):** the table above is the *only* place where error code → action mapping is
defined; the implementation generates it from `venue_profile.json`, and any code seen at runtime that
is **not** in the table is classified `UNKNOWN` and journaled (`EV-VENUE-UNKNOWN-CODE`). Unmapped codes
must never map to "assume it failed".

---

## 9. Uncertainty protocol at the transport boundary (`AX-02:§9`)

### 9.1 Classification (`AX-02:§9.1`)

A state-changing call is classified as:

| Outcome | Conditions |
|---|---|
| `KNOWN_SUCCESS` | HTTP 2XX **and** a business `code` in the success set (v1: `0`/`200` per route documentation `[V-DOC]`; v2: `code = 200` `[V-DOC]`) |
| `KNOWN_FAILURE` | HTTP 4XX **with** a business code that the table classifies as a definitive rejection (i.e. the request provably did not create/modify state: e.g. `-1021`, `-1022`, `-1100`-family, `-1131`, `-1138`) |
| `UNKNOWN` | **everything else**: timeouts, connection resets, HTTP 5XX `[V-DOC]`, `-1006`, `-1007`, `-1146`, `-1147`, `-1149`, or any code not in the table |

### 9.2 Resolution ladder for `UNKNOWN` (`AX-02:§9.2`) — normative

1. **Never resubmit** with the same intent before resolution (INV-3).
2. Query by the idempotency key: `GET /api/v1/futures/order?origClientOrderId=<key>&type=<LIMIT|STOP>`
   (weight 1), up to `P-EXE-010` attempts with backoff, within `P-EXE-011` seconds.
3. If the order exists ⇒ adopt its state (fill, partial, working, cancelled) and continue from there.
4. If the query returns `-2013`/no order **and** the position query shows no change **and**
   `openOrders` for the symbol shows nothing bearing the key ⇒ the effect did not happen: the intent
   may be re-derived from a *fresh* snapshot (a new decision, not a retry).
5. If the two sources disagree, or resolution times out: **the conservative branch**, chosen by intent
   type — entries are treated as *possibly executed* and reconciled (position adopted, protection
   placed, no new entry until the position is understood); exits are re-attempted with the smallest
   possible aggressive but bounded order after confirming the position still exists.
6. Every `UNKNOWN` event is journaled with the raw request, raw response (or its absence), the
   resolution trace, and the final adopted state; repeated incidents of the same kind raise a `SEV-2`
   incident and are reviewed against the `T-AMB-*` battery.

---

## 10. Venue Conformance Harness (VCH) (`AX-02:§10`)

**Definition.** The VCH is a *mandatory pre-trading program* (AX-14 gate `G1`) that exercises the venue
with read-only probes and, only in an owner-approved window, with a small set of *real* orders whose
sole purpose is to observe semantics. Its output is `venue_profile.json`, the only accepted source for
every `[V-PROBE]` value. Its results are `[MEASURED]` evidence.

**Safety law for order-probing probes (`VCH-2x`):** executed only in a dedicated `PROBE` mode, with
`P-VEN-030` maximum notional (default: the venue minimum notional; class `[O]`), immediately closed by
a protective order, and only on instruments whose spread is below `P-VEN-031`. Probe runs are
journalled with `environment = PROBE`, which is not a tradeable environment (AX-01 §2.5).

| Probe | Question it answers | Method | Acceptance / recorded field |
|---|---|---|---|
| `VCH-01` | Are the endpoints and base URLs as documented, reachable, and does `/api/v1/time` work? | read-only sweep | all used routes return documented shapes; `reachable_routes.json` |
| `VCH-02` | What are the exact *current* rate-limit headers and their semantics? | 20 paced requests, sample headers | `X-Api-Limit-Status` decreases and resets as documented; `rate_limit_model.json` |
| `VCH-03` | Which weight/limit applies to each used route today? | count remaining-weight decrement per call (difference of `X-Api-Limit-Status`) | measured weight per route ⇒ `endpoint_weights.json` |
| `VCH-04` | Does the `ORDERS` counter behave as documented (60/2 s)? | paced probing in `PAPER` window (no orders) vs measurement of header counter | `orders_bucket` parameters |
| `VCH-05` | Is signature verification parameter-order sensitive as documented? | send a permuted-order request twice | a permuted order must fail; else AXIOM adds its own canonical ordering only ⇒ `signing.json` |
| `VCH-06` | Is `recvWindow` default really 5000 and what is the effective tolerance? | binary search with deliberately skewed timestamps and a known-good signature | accepted/rejected boundary ⇒ `clock_tolerance.json` |
| `VCH-07` | Does `/api/v1/exchangeInfo` include `rateLimits` today (doc warns removal)? | fetch and parse | presence flag; the design never depends on it either way |
| `VCH-08` | What does the USDT-M contract list look like — are inverse contracts (`inverse=true`, `BTC-SWAP`) present in `contracts`? | fetch, classify | `instruments.json` with `category_selector = marginToken==USDT && inverse==false` |
| `VCH-09` | What are the real filter values, and what is the exact quantity unit chain for contracts? | fetch filters; place the minimal allowed order in the probe window and observe `origQty`/fill quantity vs notional | `qty_unit_chain`, `filters.json` — resolves the §6.4 ambiguity |
| `VCH-10` | What are the observed tick/step rounding behaviours at boundaries? | submit prices/quantities at ±1 step and at the clamp boundary | rounding rules confirmed; `rounding.json` |
| `VCH-11` | Does the trade stream's `m` mean taker-side as documented, and which side is "buy"? | run our tape and the REST-klines taker-buy volume for the same window and compare sign/aggregates | agreement within `P-VEN-040` ⇒ `trade_flag_semantics`; if not, the flag is discarded from features |
| `VCH-12` | Are bar volumes/counters from WS and REST consistent, and which one is authoritative for closed bars? | compare a completed bar from both sources | per-source authority ⇒ `bar_authority` (default rule: REST wins for closed bars) |
| `VCH-13` | Is the trade `v` field a per-symbol monotonic sequence, and is it global across symbols? | record streams for ≥ 60 min, analyse gaps | sequence semantics ⇒ enables/forbids tape-gap inference by id |
| `VCH-14` | Does the venue expose a user-data stream (`listenKey`) flow? | search docs + probe documented candidates | yes/no ⇒ optional latency path (ADR if yes) |
| `VCH-15` | What is the observed fill behaviour of `LIMIT+INPUT+IOC` (all-or-nothing vs partial)? | probe window, size = 1 step at/inside/outside the touch | `ioc_fill_model` parameters for AX-11 |
| `VCH-16` | What is the observed latency distribution of submit/ack/fill? | 50 probes with timestamps | `latency_distribution` used by AX-11 and by the latency budget in AX-08 §2 |
| `VCH-17` | Does a `type=STOP` order with `triggerBy=MARK_PRICE` behave as documented (trigger, then order)? | probe with a stop far from market, then cancel | semantics + status vocabulary confirmed |
| `VCH-18` | How does `position/trading-stop` interact with an existing price-type `STOP` order, and can both coexist? | probe in isolation on one instrument | the protection mechanism chosen for v1 (AX-08 §6) |
| `VCH-19` | What exactly happens on duplicate `newClientOrderId` (`-1141`) and what is the message? | submit the same key twice | confirms the idempotency guard; `duplicate_semantics` |
| `VCH-20` | Which HTTP/transport conditions actually map to `UNKNOWN` (5XX, timeout, reset)? | fault injection: kill connections mid-flight, use an intentionally short timeout | confirms §9.1 classification; `unknown_triggers` |
| `VCH-21` | What is the venue's behaviour when the price band is exceeded (`-1138` family)? | submit outside the band | band formula per instrument (`price_bands.json`) |
| `VCH-22` | Does cancel-all (`DELETE /batchOrders`) cancel protective orders too? | probe with a protective order present | crucial for the emergency path ⇒ `cancel_all_scope` |
| `VCH-23` | What is the **unprotected window**: time between entry ack and protection acknowledgment? | timestamped probe sequence, 20 repetitions | p95 recorded; compared to `P-EXE-003`; feeds AX-08 §6.4 |
| `VCH-24` | How are fees actually charged (open+close, maker/taker) and do they match `commissionRate`? | 20 round-trips of minimal size; reconcile `userTrades` | `fee_model` table; any discrepancy invalidates the cost model and blocks `LIVE` |
| `VCH-25` | How is funding actually applied (sign, timing, base)? | hold a minimal position across one settlement; read `balanceFlow`/`todayPnl` | `funding_model` confirmed; the cost model's funding term (AX-08 §3.2) is calibrated from this |
| `VCH-26` | What is the real minimum notional that is accepted, and does it vary by instrument? | boundary probe | `min_notional.json` |
| `VCH-27` | Does the venue accept `valueQuantity`-only orders, and how is it rounded? | probe | enables the notional-based emergency path |
| `VCH-28` | Which instruments forbid the taker/market form (`-1194`) or API trading (`-1157`)? | read `contracts[]` + try where cheap | universe rule: exclude forbidden forms |
| `VCH-29` | What are the observed status transitions for a partially filled then cancelled order? | bounded probe | status mapper table completed (`T-MAP-001` fixture source) |
| `VCH-30` | Are per-symbol limits (max open orders `-1193`, plan-order cap `-1207`) reachable in practice? | bounded probe up to a small cap | open-order cap policy (AX-08 §4.5) |
| `VCH-31` | Is the WS `depth` snapshot complete up to the requested levels, and how does `diffDepth` reconcile with it? | record 60 min, rebuild, compare against REST `depth` periodically | book reconstruction rules verified (`T-BOOK-001`) |
| `VCH-32` | Do WS kline pushes ever contradict the final REST bar, and how often? | compare 24 h | `ws_vs_rest_disagreement_rate`; if non-zero, the design's "REST is authority for closed bars" rule is mandatory, not optional |
| `VCH-33` | What is the real WS disconnect rate and pong latency under idle/heartbeat policy? | 24 h soak | `ws_stability.json`; sets reconnect budgets |
| `VCH-34` | Does `/quote/v1/markPrice` without symbol really return all symbols at ≤5 req/s? | 10 calls | confirms the cheap bulk mark path for `rg` |
| `VCH-35` | What is the practical maximum of `klines` rows per call today (1000 vs 2000 documented in different sections)? | request both | `klines_page_limit` — the discrepancy is resolved by measurement |
| `VCH-36` | How does the venue's `-2013` on bulk-cancel manifest in the response? | cancel a non-existent id | §3.2 parsed correctly |
| `VCH-37` | Are timestamps in WS payloads always event time (not send time)? | compare `t`/`E` with wall clock and with REST `t` | `ws_time_semantics` — decides whether WS timestamps may be used for event-time ordering |
| `VCH-38` | Is there a maintenance/blackout schedule discoverable from error behaviour (`-1016`)? | long soak, log 5XX/`-1016` | maintenance window statistics ⇒ alert policy |
| `VCH-39` | Does the venue impose a per-key or per-IP ban as documented for sustained `-1003`? | never tested deliberately; observation-only | policy: AXIOM never approaches the ban threshold |
| `VCH-40` | Does `exchangeInfo` mark instruments with `OPEN_FORBIDDEN`/`CLOSE_FORBIDDEN` today, and how fast do status changes propagate? | periodic snapshots | universe safety rule (§6.4 + AX-04 §4.5) |

**Harness outputs and their consumers**

| Artifact | Consumers |
|---|---|
| `venue_profile.json` (all `[V-PROBE]` values) | `vap`, `mdp`, `rg`, `exp`, `lnp` |
| `endpoint_weights.json`, `rate_limit_model.json` | the request governor (AX-02 §7.2) |
| `filters.json`, `qty_unit_chain`, `min_notional.json` | order validator (AX-08 §4.1) |
| `fee_model`, `funding_model`, `latency_distribution`, `ioc_fill_model` | cost model (AX-08 §3), simulator (AX-11) |
| `unknown_triggers`, `duplicate_semantics`, `cancel_all_scope` | ambiguity protocol implementation (AX-08 §5) |

**Blocking rule (`AX-02:§10-R1`):** `LIVE` is unreachable while any probe marked *blocking* in the
registry (AX-15 §7) is in state `FAILED` or `STALE`. `PAPER` requires only the probes marked
*paper-blocking* (all read-only probes).

---

## 11. Ambiguity register (`AX-02:§11`)

Open questions that the documentation does **not** settle, each with its probe and its fail-closed
fallback. This register exists so that **no implementer has to guess**: if the probe has not run, the
fallback behaviour is specified and is always the conservative one.

| ID | Open question | Probe | Until resolved (fallback) |
|---|---|---|---|
| `AMB-01` | Quantity unit chain for contracts (`contracts` ↔ base token) | `VCH-09` | size via `valueQuantity`-equivalent internal math and quantize downward; position checks use venue-reported `positions` only |
| `AMB-02` | Taker-side semantics of `m` | `VCH-11` | flow features that need it are disabled (`T2` components off) |
| `AMB-03` | Whether `klines` accepts 2000 rows or 1000 | `VCH-35` | use 1000 |
| `AMB-04` | Whether `rateLimits` remains in `exchangeInfo` | `VCH-07` | never read it |
| `AMB-05` | User-data stream existence and lease rules | `VCH-14` | REST reconciliation only |
| `AMB-06` | Whether `depth` WS covers the requested level count exactly | `VCH-31` | exchange-derived metrics disabled; participation caps from `bookTicker` only (notional at touch) |
| `AMB-07` | Whether WS timestamps are event time | `VCH-37` | ordering by our `recv_ts`; `event_ts` treated as informative |
| `AMB-08` | Whether cancel-all also cancels protective orders | `VCH-22` | emergency path cancels protective orders explicitly first, then positions are flattened, then a full `openOrders` sweep |
| `AMB-09` | Whether `position/trading-stop` coexists with `STOP` orders | `VCH-18` | protection implemented with `STOP` orders only |
| `AMB-10` | Exact rounding/validation order (round then validate, or the reverse) | `VCH-09`/`VCH-10` | validator applies quantization toward risk reduction and then the band check |
| `AMB-11` | Whether `-1003` affects the key, the IP, or both | `VCH-02`/observation | treat any 429 as a full stop of non-P0 traffic for 60 s |
| `AMB-12` | Whether a partially filled IOC leaves the remainder working | `VCH-15`/`VCH-29` | assume the remainder is cancelled; verify by query before retrying (this is the documented IOC semantics and is checked) |

---

## 12. Prohibited assumptions (`AX-02:§12`)

The implementation must **never**: hardcode a fee, funding rate, filter value, weight, limit, symbol
list, symbol format, tick/step, or error-code meaning; assume an order was not created after a timeout;
assume a cancel succeeded without confirmation; assume a position size from its own arithmetic
(positions come from the venue, reconciled); assume the venue's clock equals the local clock; assume a
WS message arrived (gaps are detected, not hoped away); assume an instrument remains in the universe
(status is re-read daily and on drift); assume any behaviour of a route not exercised by a `VCH` probe
in the current `venue_profile` version.
