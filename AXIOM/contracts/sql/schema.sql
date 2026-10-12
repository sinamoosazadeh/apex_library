-- AXIOM — local store DDL (SQLite, WAL, single writer) — contract v1
--
-- Authority: AX-04 §6 (storage layers L0–L3, journal, write path), AX-03 §5 (hashing and
-- the journal hash chain), AX-13 §5 (journal event catalogue), AX-13 §6 (configuration).
-- ADR-005 fixes SQLite in WAL mode with exactly one writer per database file.
--
-- Law enforced in this schema (not merely documented):
--   * `journal` is append-only: UPDATE and DELETE are blocked by triggers (AX-03 §5.3).
--   * L1 rows are mutable only through an upsert that increments `revision`; every mutation
--     is visible in the audit tables (`corrections`, `repairs`).
--   * L0 bytes live in segment files on disk; the database stores only their index
--     (`l0_segments`) with content hashes, so L0 can always be re-read and verified.
--   * every table that records an observation carries its `source` tag and the
--     `first_ingest_ts` availability stamp (AX-03 §3.4) — no decision may read a row
--     whose availability is in the future of the tape cursor.

PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;          -- durability of the journal is worth the write cost (INV-3)
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- ---------------------------------------------------------------------------
-- 0. Meta
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS meta_schema (
  version      INTEGER PRIMARY KEY,
  applied_ts   INTEGER NOT NULL,
  description  TEXT    NOT NULL
);

-- ---------------------------------------------------------------------------
-- 1. L0 — raw segmented archive index (bytes live on disk)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS l0_segments (
  segment_id     TEXT PRIMARY KEY,           -- ULID
  stream         TEXT NOT NULL,              -- e.g. 'ws.kline_60', 'rest.depth', 'rest.funding'
  opened_ts      INTEGER NOT NULL,
  closed_ts      INTEGER,
  bytes          INTEGER NOT NULL,
  records        INTEGER NOT NULL,
  content_hash   TEXT NOT NULL,              -- SHA-256 of the closed segment (AX-03 §5.2)
  path           TEXT NOT NULL,
  verified_ts    INTEGER,
  CHECK (closed_ts IS NULL OR closed_ts >= opened_ts)
);
CREATE INDEX IF NOT EXISTS ix_l0_stream_ts ON l0_segments(stream, opened_ts);

-- ---------------------------------------------------------------------------
-- 2. Reference data
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instruments (
  instrument_id       TEXT PRIMARY KEY,       -- '<symbol>:<quote>' e.g. 'BTCUSDT:USDT'
  index_symbol        TEXT NOT NULL,
  contract_multiplier TEXT NOT NULL,          -- stored as text: exact decimal (AX-03 §4.1)
  tick                TEXT NOT NULL,
  step                TEXT NOT NULL,
  min_notional        TEXT NOT NULL,
  status              TEXT NOT NULL,          -- venue status verbatim (TRADING, ...)
  inverse             INTEGER NOT NULL DEFAULT 0,
  max_leverage        INTEGER,
  factors_hash        TEXT NOT NULL,          -- hash of the venue payload that produced this row
  first_seen_ts       INTEGER NOT NULL,
  last_seen_ts        INTEGER NOT NULL,
  retired_ts          INTEGER,
  source              TEXT NOT NULL,          -- V-DOC | V-KIT | V-PROBE
  CHECK (inverse IN (0,1))
);

CREATE TABLE IF NOT EXISTS instrument_status_history (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,
  status        TEXT NOT NULL,
  source        TEXT NOT NULL,
  raw_hash      TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts)
);

-- ---------------------------------------------------------------------------
-- 3. L1 — curated market data (bars, trades, quotes, book, funding, OI, prices)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bars (
  instrument_id   TEXT    NOT NULL REFERENCES instruments(instrument_id),
  interval        TEXT    NOT NULL,           -- '60','240','900','1D' ...
  open_time       INTEGER NOT NULL,           -- venue bar open, ms UTC
  close_time      INTEGER NOT NULL,
  o REAL NOT NULL, h REAL NOT NULL, l REAL NOT NULL, c REAL NOT NULL,
  v REAL NOT NULL,                            -- base volume
  qv REAL NOT NULL,                           -- quote volume
  trades          INTEGER NOT NULL,
  taker_buy_qv    REAL NOT NULL,
  is_final        INTEGER NOT NULL DEFAULT 0, -- 0 = provisional (never decision-eligible)
  revision        INTEGER NOT NULL DEFAULT 0,
  source          TEXT NOT NULL,              -- WS | REST
  first_ingest_ts INTEGER NOT NULL,           -- availability stamp (AX-03 §3.4)
  last_update_ts  INTEGER NOT NULL,
  raw_hash        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, interval, open_time),
  CHECK (is_final IN (0,1)),
  CHECK (h >= l), CHECK (o > 0), CHECK (c > 0)
);
CREATE INDEX IF NOT EXISTS ix_bars_lookup ON bars(instrument_id, interval, open_time DESC);

CREATE TABLE IF NOT EXISTS trades (
  instrument_id  TEXT NOT NULL REFERENCES instruments(instrument_id),
  trade_id       TEXT NOT NULL,               -- venue trade id (or hash for WS-fallback)
  ts             INTEGER NOT NULL,
  price          TEXT NOT NULL,
  qty            TEXT NOT NULL,
  quote_qty      TEXT NOT NULL,
  taker_side     TEXT,                        -- may be NULL: venue WS flag not trusted (AMB-02)
  first_ingest_ts INTEGER NOT NULL,
  source         TEXT NOT NULL,
  raw_hash       TEXT NOT NULL,
  PRIMARY KEY (instrument_id, trade_id)
);
CREATE INDEX IF NOT EXISTS ix_trades_ts ON trades(instrument_id, ts);

CREATE TABLE IF NOT EXISTS book_snapshots (
  instrument_id  TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts             INTEGER NOT NULL,
  version        TEXT,                        -- venue depth version string
  bids           TEXT NOT NULL,               -- JSON [[price, qty], ...]
  asks           TEXT NOT NULL,
  depth          INTEGER NOT NULL,            -- number of levels per side stored
  digest         TEXT NOT NULL,               -- SHA-256 of the canonical JSON (AX-03 §5.2)
  first_ingest_ts INTEGER NOT NULL,
  source         TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts, digest)
);

CREATE TABLE IF NOT EXISTS quotes (
  instrument_id  TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts             INTEGER NOT NULL,
  bid            TEXT NOT NULL,
  ask            TEXT NOT NULL,
  bid_qty        TEXT,
  ask_qty        TEXT,
  spread_bps     REAL NOT NULL,
  mid            REAL NOT NULL,
  microprice     REAL,
  first_ingest_ts INTEGER NOT NULL,
  source         TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts, source)
);
CREATE INDEX IF NOT EXISTS ix_quotes_ts ON quotes(instrument_id, ts);

CREATE TABLE IF NOT EXISTS mark_prices (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,
  mark          TEXT NOT NULL,
  index_price   TEXT,
  est_settle    TEXT,
  next_funding_time INTEGER,
  funding_rate  TEXT,
  first_ingest_ts INTEGER NOT NULL,
  source        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts)
);

CREATE TABLE IF NOT EXISTS index_prices (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,
  price         TEXT NOT NULL,
  components    TEXT,                         -- JSON ['BINANCE','OKX',...] (AMB-09)
  first_ingest_ts INTEGER NOT NULL,
  source        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts)
);

CREATE TABLE IF NOT EXISTS open_interest (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,
  oi            TEXT NOT NULL,                -- contracts
  oi_value      TEXT,                         -- quote units
  first_ingest_ts INTEGER NOT NULL,
  source        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts)
);

CREATE TABLE IF NOT EXISTS funding_rate_obs (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,             -- observation time (current rate)
  rate          TEXT NOT NULL,
  next_funding_time INTEGER,
  period        TEXT,                         -- e.g. '8H' verbatim (never assumed)
  first_ingest_ts INTEGER NOT NULL,
  source        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts)
);

CREATE TABLE IF NOT EXISTS funding_settlements (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  settled_ts    INTEGER NOT NULL,
  rate          TEXT NOT NULL,
  amount        TEXT NOT NULL,                -- signed cash flow in quote units
  position_ref  TEXT,
  source        TEXT NOT NULL,                -- 'venue.history' | 'derived'
  raw_hash      TEXT NOT NULL,
  PRIMARY KEY (instrument_id, settled_ts, position_ref)
);

CREATE TABLE IF NOT EXISTS long_short_ratio (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,
  period        TEXT NOT NULL,
  long_account  REAL, short_account REAL,
  long_position REAL, short_position REAL,
  first_ingest_ts INTEGER NOT NULL,
  source        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts, period)
);

CREATE TABLE IF NOT EXISTS taker_buy_sell_vol (
  instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
  ts            INTEGER NOT NULL,
  period        TEXT NOT NULL,
  buy_vol       TEXT NOT NULL,
  sell_vol      TEXT NOT NULL,
  first_ingest_ts INTEGER NOT NULL,
  source        TEXT NOT NULL,
  PRIMARY KEY (instrument_id, ts, period)
);

-- ---------------------------------------------------------------------------
-- 4. Universe, snapshots, health, repair
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS universe_records (
  day          TEXT PRIMARY KEY,              -- 'YYYY-MM-DD' (UTC) of the freeze
  frozen_ts    INTEGER NOT NULL,
  rule_hash    TEXT NOT NULL,                 -- hash of the rule set + parameters used
  digest       TEXT NOT NULL,                 -- manifest digest of the member list (AX-03 §5.2)
  members      INTEGER NOT NULL,
  source       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS universe_members (
  day              TEXT NOT NULL REFERENCES universe_records(day),
  instrument_id    TEXT NOT NULL REFERENCES instruments(instrument_id),
  rank             INTEGER NOT NULL,
  qv_median        REAL,
  spread_median_bps REAL,
  cluster          TEXT,
  eligible         INTEGER NOT NULL,
  ineligibility_code TEXT,
  metrics          TEXT NOT NULL,             -- JSON: the full evidence snapshot
  PRIMARY KEY (day, instrument_id)
);

CREATE TABLE IF NOT EXISTS snapshots (
  snapshot_id    TEXT PRIMARY KEY,            -- ULID
  as_of          INTEGER NOT NULL,
  manifest_digest TEXT NOT NULL,
  param_set_hash TEXT NOT NULL,
  code_commit    TEXT NOT NULL,
  model_hashes   TEXT NOT NULL,               -- JSON array
  profile_hash   TEXT NOT NULL,
  created_ts     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS snapshot_partitions (
  snapshot_id  TEXT NOT NULL REFERENCES snapshots(snapshot_id),
  partition    TEXT NOT NULL,                 -- logical name (bars.900, funding, universe, features...)
  digest       TEXT NOT NULL,
  rows         INTEGER NOT NULL,
  PRIMARY KEY (snapshot_id, partition)
);

CREATE TABLE IF NOT EXISTS data_health (
  ts            INTEGER NOT NULL,
  instrument_id TEXT NOT NULL,
  state         TEXT NOT NULL,                -- OK | WARN | FAIL | HALT (AX-04 §10)
  gate_id       TEXT,
  value         REAL,
  threshold_ref TEXT,
  detail        TEXT,
  PRIMARY KEY (ts, instrument_id)
);

CREATE TABLE IF NOT EXISTS repairs (
  repair_id   TEXT PRIMARY KEY,
  started_ts  INTEGER NOT NULL,
  finished_ts INTEGER,
  scope       TEXT NOT NULL,
  method      TEXT NOT NULL,
  rows        INTEGER,
  digests     TEXT,                           -- JSON: before/after digests
  evidence    TEXT,                           -- JSON: pages/endpoints used
  outcome     TEXT NOT NULL                   -- COMPLETE | PARTIAL | IMPOSSIBLE
);

-- ---------------------------------------------------------------------------
-- 5. L2 — derived: features, forecasts, decisions, targets
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS features (
  feature_id    TEXT NOT NULL,                -- F-*
  version       TEXT NOT NULL,
  instrument_id TEXT NOT NULL,
  ts            INTEGER NOT NULL,             -- tape time of the value
  horizon       TEXT,
  value         REAL,
  state         TEXT NOT NULL,                -- OK | NOT_AVAILABLE
  computed_ts   INTEGER NOT NULL,
  input_digest  TEXT NOT NULL,
  PRIMARY KEY (feature_id, version, instrument_id, ts, horizon)
);
CREATE INDEX IF NOT EXISTS ix_features_ts ON features(feature_id, ts);

CREATE TABLE IF NOT EXISTS forecasts (
  forecast_id      TEXT PRIMARY KEY,          -- ULID
  snapshot_id      TEXT NOT NULL REFERENCES snapshots(snapshot_id),
  decision_id      TEXT,
  instrument_id    TEXT NOT NULL,
  horizon_bars     INTEGER NOT NULL,
  mu_raw           REAL, mu_net REAL,
  sigma_model      REAL, sigma_market REAL,
  p_net            REAL, n_eff REAL,
  model_hash       TEXT NOT NULL,
  calibration_hash TEXT NOT NULL,
  created_ts       INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_forecasts_dec ON forecasts(decision_id);

CREATE TABLE IF NOT EXISTS decisions (
  decision_id    TEXT PRIMARY KEY,            -- ULID
  snapshot_id    TEXT NOT NULL REFERENCES snapshots(snapshot_id),
  created_ts     INTEGER NOT NULL,
  gov_state      TEXT NOT NULL,
  multipliers    TEXT NOT NULL,               -- JSON {m_gov,m_data,m_regime,m_exec}
  universe_day   TEXT REFERENCES universe_records(day),
  n_candidates   INTEGER NOT NULL,
  n_targets      INTEGER NOT NULL,
  n_refusals     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS targets (
  target_id     TEXT PRIMARY KEY,             -- ULID
  decision_id   TEXT NOT NULL REFERENCES decisions(decision_id),
  instrument_id TEXT NOT NULL,
  side          TEXT NOT NULL,                -- OPEN_LONG | OPEN_SHORT | CLOSE_LONG | CLOSE_SHORT
  qty           TEXT NOT NULL,
  entry_ref     REAL NOT NULL,
  stop_price    REAL,
  horizon_bars  INTEGER NOT NULL,
  notional      REAL NOT NULL,
  binding_cap   TEXT NOT NULL,                -- RISK | VOL | KELLY | LIQUIDITY | MARGIN | NONE
  r_consumed    REAL NOT NULL,
  created_ts    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS refusals (
  refusal_id    TEXT PRIMARY KEY,
  decision_id   TEXT REFERENCES decisions(decision_id),
  instrument_id TEXT,
  stage         TEXT NOT NULL,                -- FEATURE | FORECAST | COMBINE | PORTFOLIO | KERNEL | GATE
  check_id      TEXT,                         -- RK-mm, QC-mm, gate name
  reason_code   TEXT NOT NULL,
  detail        TEXT NOT NULL,                -- JSON: the numbers that produced the refusal
  created_ts    INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_refusals_code ON refusals(reason_code, created_ts);

-- ---------------------------------------------------------------------------
-- 6. Execution: intents, venue orders, fills, protection, reconciliation
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS intents (
  intent_id        TEXT PRIMARY KEY,          -- ULID
  idempotency_key  TEXT NOT NULL UNIQUE,      -- 'ax<env><purpose><instrument><epoch36><counter>'
  decision_id      TEXT REFERENCES decisions(decision_id),
  purpose          TEXT NOT NULL,             -- ENTRY | PROTECT | EXIT | FLATTEN | CANCEL | MODIFY | LEVERAGE | MARGIN_TYPE
  instrument_id    TEXT NOT NULL,
  side             TEXT NOT NULL,
  qty              TEXT NOT NULL,
  limit_price      TEXT,
  status           TEXT NOT NULL,             -- AX-13 §3 OrderState
  attempts         INTEGER NOT NULL DEFAULT 0,
  created_ts       INTEGER NOT NULL,
  sent_ts          INTEGER,
  resolved_ts      INTEGER,
  resolution       TEXT,                      -- adopted state from the ladder (AX-08 §5.2)
  evidence_refs    TEXT,                      -- JSON array of journal seqs / raw hashes
  CHECK (status IN ('WRITTEN','SENT','ACKED','PARTIAL','FILLED','REJECTED','UNKNOWN',
                    'RESOLVED_FILLED','RESOLVED_WORKING','RESOLVED_ABSENT','RESOLVED_ESCALATED','ABANDONED'))
);

CREATE TABLE IF NOT EXISTS venue_orders (
  order_id        TEXT PRIMARY KEY,
  client_order_id TEXT NOT NULL,
  intent_id       TEXT REFERENCES intents(intent_id),
  instrument_id   TEXT NOT NULL,
  status          TEXT NOT NULL,
  side            TEXT NOT NULL,
  type            TEXT NOT NULL,
  price           TEXT, stop_price TEXT, trigger_by TEXT,
  qty             TEXT NOT NULL, executed_qty TEXT NOT NULL DEFAULT '0',
  avg_price       TEXT,
  reduce_only     INTEGER,
  is_protective   INTEGER NOT NULL DEFAULT 0,
  created_ts      INTEGER NOT NULL,
  last_update_ts  INTEGER NOT NULL,
  raw             TEXT NOT NULL,              -- JSON of the last venue payload
  raw_hash        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_orders_intent ON venue_orders(intent_id);
CREATE INDEX IF NOT EXISTS ix_orders_open ON venue_orders(status) WHERE status IN ('NEW','PARTIALLY_FILLED');

CREATE TABLE IF NOT EXISTS fills (
  fill_id       TEXT PRIMARY KEY,             -- venue fill id (or content hash when absent)
  order_id      TEXT REFERENCES venue_orders(order_id),
  intent_id     TEXT REFERENCES intents(intent_id),
  instrument_id TEXT NOT NULL,
  qty           TEXT NOT NULL,
  price         TEXT NOT NULL,
  fee           TEXT NOT NULL,
  fee_asset     TEXT,
  is_maker      INTEGER,
  realized_pnl  TEXT,
  event_ts      INTEGER NOT NULL,
  received_ts   INTEGER NOT NULL,
  decision_mid  REAL, arrival_mid REAL,       -- TCA inputs (AX-08 §8)
  adverse_move  REAL,                         -- measured after P-EXE-050 seconds
  raw_hash      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_fills_ts ON fills(instrument_id, event_ts);

CREATE TABLE IF NOT EXISTS position_snapshots (
  ts             INTEGER NOT NULL,
  instrument_id  TEXT NOT NULL,
  side           TEXT NOT NULL,               -- LONG | SHORT | FLAT
  qty            TEXT NOT NULL,
  entry_price    TEXT,
  mark_price     TEXT,
  leverage       INTEGER,
  margin_used    TEXT,
  margin_type    TEXT,
  unrealized_pnl TEXT,
  liq_price      TEXT,
  account_leverage INTEGER,
  source         TEXT NOT NULL,               -- WS | REST | ADOPTED
  raw_hash       TEXT NOT NULL,
  PRIMARY KEY (ts, instrument_id)
);
CREATE INDEX IF NOT EXISTS ix_positions_recent ON position_snapshots(instrument_id, ts DESC);

CREATE TABLE IF NOT EXISTS protections (
  ts            INTEGER NOT NULL,
  instrument_id TEXT NOT NULL,
  state         TEXT NOT NULL,                -- NONE | PENDING | ACTIVE | FAILED
  stop_price    TEXT,
  trigger_by    TEXT,
  qty           TEXT,
  order_id      TEXT,
  unprotected_ms INTEGER,
  source        TEXT NOT NULL,
  PRIMARY KEY (ts, instrument_id)
);

CREATE TABLE IF NOT EXISTS reconciliations (
  reconc_id    TEXT PRIMARY KEY,
  started_ts   INTEGER NOT NULL,
  finished_ts  INTEGER NOT NULL,
  reason       TEXT NOT NULL,                 -- BOOT | PERIODIC | AFTER_UNKNOWN | PRE_ENTRY | GOV_TRANSITION
  result       TEXT NOT NULL,                 -- CLEAN | DIVERGENT
  divergences  TEXT NOT NULL,                 -- JSON [{class, detail, evidence}]
  evidence_refs TEXT
);

CREATE TABLE IF NOT EXISTS corrections (
  correction_id TEXT PRIMARY KEY,
  ts            INTEGER NOT NULL,
  object        TEXT NOT NULL,                -- 'position:BTCUSDT:USDT'
  adopted_value TEXT NOT NULL,
  previous_value TEXT,
  evidence_refs TEXT NOT NULL,                -- JSON: raw payload hashes
  cause         TEXT,
  reconc_id     TEXT REFERENCES reconciliations(reconc_id)
);

-- ---------------------------------------------------------------------------
-- 7. Control: journal, governor, parameters, models, gates, incidents
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS journal (
  seq            INTEGER PRIMARY KEY AUTOINCREMENT,
  ts             INTEGER NOT NULL,
  event_type     TEXT NOT NULL,               -- EV-* (AX-13 §5)
  correlation_id TEXT,
  payload        TEXT NOT NULL,               -- canonical JSON (AX-03 §5.1)
  payload_hash   TEXT NOT NULL,               -- SHA-256 of payload
  prev_hash      TEXT NOT NULL,               -- chain_hash of seq-1 (genesis: 64 zeros)
  chain_hash     TEXT NOT NULL                -- SHA-256(prev_hash || payload_hash || ts || event_type)
);
CREATE INDEX IF NOT EXISTS ix_journal_type_ts ON journal(event_type, ts);

-- Append-only enforcement (AX-03 §5.3 / ADR-004)
CREATE TRIGGER IF NOT EXISTS trg_journal_no_update
BEFORE UPDATE ON journal
BEGIN SELECT RAISE(ABORT, 'journal is append-only (AX-03 §5.3)'); END;

CREATE TRIGGER IF NOT EXISTS trg_journal_no_delete
BEFORE DELETE ON journal
BEGIN SELECT RAISE(ABORT, 'journal is append-only (AX-03 §5.3)'); END;

CREATE TABLE IF NOT EXISTS chain_checkpoints (
  seq         INTEGER PRIMARY KEY REFERENCES journal(seq),
  chain_hash  TEXT NOT NULL,
  verified_ts INTEGER NOT NULL,
  method      TEXT NOT NULL DEFAULT 'full'
);

CREATE TABLE IF NOT EXISTS gov_state_history (
  ts          INTEGER PRIMARY KEY,
  state       TEXT NOT NULL,
  trigger_ids TEXT,                           -- JSON array
  multipliers TEXT NOT NULL,                  -- JSON
  dwell_until INTEGER,
  actor       TEXT NOT NULL                   -- AUTO | operator id
);

CREATE TABLE IF NOT EXISTS kills (
  ts        INTEGER NOT NULL,
  kill_id   TEXT NOT NULL,                    -- K1..K8
  scope     TEXT NOT NULL,
  active    INTEGER NOT NULL,
  actions   TEXT NOT NULL,
  actor     TEXT,
  PRIMARY KEY (ts, kill_id)
);

CREATE TABLE IF NOT EXISTS param_history (
  ts             INTEGER PRIMARY KEY,
  param_id       TEXT NOT NULL,
  old_value      TEXT,
  new_value      TEXT NOT NULL,
  class          TEXT NOT NULL,               -- V | D | C | O
  calibration_ref TEXT,
  actor          TEXT NOT NULL,
  reason         TEXT,
  confirmed_by   TEXT
);
CREATE INDEX IF NOT EXISTS ix_param_id_ts ON param_history(param_id, ts DESC);

CREATE TABLE IF NOT EXISTS param_sets (
  param_set_hash TEXT PRIMARY KEY,
  ts             INTEGER NOT NULL,
  values_json    TEXT NOT NULL,               -- canonical JSON of the resolved values
  file_digest    TEXT NOT NULL,
  registry_hash  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_registry (
  model_id       TEXT NOT NULL,
  version        TEXT NOT NULL,
  kind           TEXT NOT NULL,               -- FORECAST | CALIBRATION | REGIME | COST_MODEL | FEATURE_SET
  artifact_path  TEXT NOT NULL,
  artifact_hash  TEXT NOT NULL,
  card           TEXT NOT NULL,               -- JSON ModelCard (AX-10 §5)
  status         TEXT NOT NULL,               -- RESEARCH | SHADOW | CHAMPION | RETIRED
  created_ts     INTEGER NOT NULL,
  retired_ts     INTEGER,
  PRIMARY KEY (model_id, version)
);

CREATE TABLE IF NOT EXISTS calibrations (
  calibration_id       TEXT PRIMARY KEY,      -- CAL-*
  ts                   INTEGER NOT NULL,
  methodology_version  TEXT NOT NULL,
  inputs_hash          TEXT NOT NULL,
  outputs              TEXT NOT NULL,         -- JSON
  metrics              TEXT NOT NULL,         -- JSON
  applied              INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS gate_records (
  gate_record_id TEXT PRIMARY KEY,
  ts             INTEGER NOT NULL,
  gate           TEXT NOT NULL,               -- G0..G6
  rung_from      TEXT,
  rung_to        TEXT,
  evidence_refs  TEXT NOT NULL,               -- JSON array of artifact hashes
  metrics        TEXT NOT NULL,
  decision       TEXT NOT NULL,               -- PASS | FAIL
  decided_by     TEXT NOT NULL                -- AUTO | owner id
);

CREATE TABLE IF NOT EXISTS deployments (
  deployment_id  TEXT PRIMARY KEY,
  ts             INTEGER NOT NULL,
  mode           TEXT NOT NULL,               -- Env
  code_commit    TEXT NOT NULL,
  param_set_hash TEXT NOT NULL REFERENCES param_sets(param_set_hash),
  model_hashes   TEXT NOT NULL,               -- JSON array
  profile_hash   TEXT NOT NULL,
  gates          TEXT NOT NULL,               -- JSON array of gate_record_id
  evidence_refs  TEXT
);

CREATE TABLE IF NOT EXISTS incidents (
  incident_id    TEXT PRIMARY KEY,
  opened_ts      INTEGER NOT NULL,
  closed_ts      INTEGER,
  severity       TEXT NOT NULL,               -- SEV-1..4
  trigger_codes  TEXT NOT NULL,
  evidence_refs  TEXT NOT NULL,
  status         TEXT NOT NULL,               -- OPEN | MITIGATED | CLOSED
  postmortem_ref TEXT,
  summary        TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
  ts        INTEGER NOT NULL,
  kind      TEXT NOT NULL,                    -- OPERATOR | COMMAND | APPROVAL
  actor     TEXT NOT NULL,
  command   TEXT NOT NULL,
  args_digest TEXT NOT NULL,
  result    TEXT NOT NULL,
  PRIMARY KEY (ts, kind, actor)
);

-- ---------------------------------------------------------------------------
-- 8. Venue knowledge: profile, probes, drift, clock
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS venue_profiles (
  ts            INTEGER NOT NULL,
  profile_hash  TEXT NOT NULL,
  profile       TEXT NOT NULL,                -- JSON of the full VenueProfile artifact
  probes_total  INTEGER NOT NULL,
  probes_passed INTEGER NOT NULL,
  probes_failed INTEGER NOT NULL,
  status        TEXT NOT NULL,                -- CURRENT | STALE | INVALID
  PRIMARY KEY (ts, profile_hash)
);

CREATE TABLE IF NOT EXISTS venue_probes (
  ts         INTEGER NOT NULL,
  probe_id   TEXT NOT NULL,                   -- VCH-mm
  status     TEXT NOT NULL,                   -- PASSED | FAILED | SKIPPED | STALE
  blocking   INTEGER NOT NULL,
  value      TEXT,                            -- JSON observation
  evidence_ref TEXT,                          -- raw payload hash
  expires_ts INTEGER,
  PRIMARY KEY (ts, probe_id)
);

CREATE TABLE IF NOT EXISTS venue_drift (
  drift_id   TEXT PRIMARY KEY,
  detected_ts INTEGER NOT NULL,
  field      TEXT NOT NULL,
  old_hash   TEXT NOT NULL,
  new_hash   TEXT NOT NULL,
  affected   TEXT NOT NULL,                   -- JSON array of probe ids / clauses
  resolved_ts INTEGER,
  resolution TEXT
);

CREATE TABLE IF NOT EXISTS clock_samples (
  ts        INTEGER NOT NULL,
  offset_ms INTEGER NOT NULL,
  rtt_ms    INTEGER NOT NULL,
  samples   INTEGER NOT NULL,
  PRIMARY KEY (ts)
);

-- ---------------------------------------------------------------------------
-- 9. Views used by the operator surface (AX-12 §7.3)
-- ---------------------------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_open_positions AS
SELECT p.instrument_id, p.side, p.qty, p.entry_price, p.mark_price, p.leverage,
       p.margin_used, p.unrealized_pnl, p.liq_price, p.ts AS as_of
FROM position_snapshots p
JOIN (SELECT instrument_id, MAX(ts) AS mts FROM position_snapshots GROUP BY instrument_id) m
  ON m.instrument_id = p.instrument_id AND m.mts = p.ts
WHERE CAST(p.qty AS REAL) <> 0;

CREATE VIEW IF NOT EXISTS v_protection_state AS
SELECT pr.instrument_id, pr.state, pr.stop_price, pr.qty, pr.unprotected_ms, pr.ts AS as_of
FROM protections pr
JOIN (SELECT instrument_id, MAX(ts) AS mts FROM protections GROUP BY instrument_id) m
  ON m.instrument_id = pr.instrument_id AND m.mts = pr.ts;

CREATE VIEW IF NOT EXISTS v_unprotected AS
SELECT p.instrument_id, p.qty, p.mark_price, s.state
FROM v_open_positions p
LEFT JOIN v_protection_state s ON s.instrument_id = p.instrument_id
WHERE s.state IS NULL OR s.state <> 'ACTIVE';

CREATE VIEW IF NOT EXISTS v_today_pnl AS
SELECT COALESCE(SUM(CAST(realized_pnl AS REAL)), 0.0) AS realized_today
FROM fills
WHERE event_ts >= (CAST(strftime('%s','now','start of day') AS INTEGER) * 1000);

CREATE VIEW IF NOT EXISTS v_refusal_mix AS
SELECT reason_code, COUNT(*) AS n, MIN(created_ts) AS first_ts, MAX(created_ts) AS last_ts
FROM refusals GROUP BY reason_code;

-- ---------------------------------------------------------------------------
-- 10. Integrity routines implemented outside SQL (contract notes)
-- ---------------------------------------------------------------------------
-- VERIFY_CHAIN(seq0)          : recompute chain_hash forward from a checkpoint (AX-04 §9 check 6)
-- REBUILD_L1(day)             : drop and rebuild L1 rows for a day from l0_segments; digests must match
-- SNAPSHOT_MANIFEST(snapshot) : compute per-partition digests; a mismatch refuses trading (T-SNAP-001)
-- CAPACITY_GUARD()            : enforce data.retention_days_* and the free-space floor (AX-04 §7)
