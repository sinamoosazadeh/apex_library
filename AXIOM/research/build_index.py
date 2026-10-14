#!/usr/bin/env python3
"""AXIOM research — concept atlas index builder (non-normative).

Emits two artifacts from one table:
  * research/concept_index.json  — machine-readable concept index (24 concepts)
  * research/search_queries.txt  — ready-to-paste search-query pack

This file is NOT part of the AXIOM design suite (see AX-18 ADR-026): it creates no
obligation on the system and is excluded from the design gates. Its only purpose is to
drive the owner's literature-collection campaign (CONCEPT_ATLAS.md).

Run:  python3 research/build_index.py [--check]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# id, title_fa, title_en, aliases, family, engine, status, axiom_refs, sources, queries
C: list[tuple] = [
    # ---------------- Part A: the 12 GEN5 engines, translated ----------------
    ("A01", "ساختار بازار / تشخیص نقطهٔ تغییر", "Market Structure & Change-Point Detection",
     ["swing detection", "trend filtering", "zigzag", "BOS/CHoCH (retail)"], "alpha", "B04", "ADJACENT",
     ["AX-05 §3.1 (F-DONJ,F-ER)"],
     ["Page (1954) CUSUM", "Killick et al. (2012) PELT", "Tibshirani (2014) trend filtering",
      "Dow theory (classic)", "Lo, Mamaysky, Wang (2000) Foundations of Technical Analysis"],
     ['"change-point detection" financial time series', '"trend filtering" L1 signal extraction',
      '"optimal changepoint detection" PELT paper', '"swing detection" OR "pivot detection" market structure',
      '"technical analysis" "foundations" Lo Mamaysky Wang']),

    ("A02", "نقدینگی، عمق و شکار حدضرر", "Liquidity, Depth and Predatory Trading",
     ["liquidity pools (retail)", "stop runs", "sweeps"], "micro", "B01", "CORE",
     ["AX-05 §3.3 (F-SPR,F-D1)", "AX-07 §7 (سقف نقدینگی)"],
     ["Kyle (1985)", "Amihud (2002)", "Brunnermeier & Pedersen (2005) Predatory Trading",
      "Cont, Kukanov & Stoikov (2014)", "Brunnermeier & Pedersen (2009) funding liquidity"],
     ['"predatory trading" Brunnermeier Pedersen', '"liquidity resilience" limit order book',
      '"order flow imbalance" price impact', '"stop-loss" cascade fire sales',
      '"liquidity" "depth elasticity" market impact']),

    ("A03", "حجم، مشارکت و سمّیت جریان سفارش", "Volume, Participation and Order-Flow Toxicity",
     ["volume profile (retail)", "POV", "participation rate"], "micro", "B11", "CORE",
     ["AX-05 §3.4 (F-TAKER)", "AX-08 §4.2 (slicing)"],
     ["Easley, Lopez de Prado & O'Hara (2012) VPIN", "Easley et al. (2011) The Volume Clock",
      "Easley et al. (1996) PIN", "Admati & Pfleiderer (1988) intraday patterns"],
     ['"volume clock" Easley Lopez de Prado', '"VPIN" flow toxicity liquidity',
      '"probability of informed trading" PIN estimation', '"participation rate" "POV" execution algorithm',
      '"volume-synchronized" sampling trading']),

    ("A04", "نوسان: خوشه‌بندی، فشردگی و انبساط", "Volatility: Clustering, Compression and Expansion",
     ["volatility squeeze", "range expansion", "ATR"], "alpha", "B04", "CORE",
     ["AX-05 §3.2 (F-RV,F-EWMA,F-HAR-RV)", "AX-07 §4 (هدف نوسان)"],
     ["Engle (1982) ARCH", "Bollerslev (1986) GARCH", "Andersen & Bollerslev (1998) realized vol",
      "Corsi (2009) HAR", "Crabel (1990) opening range breakout"],
     ['"volatility clustering" GARCH survey', '"realized volatility" HAR model Corsi',
      '"volatility of volatility" forecasting', '"range expansion" OR "opening range breakout"',
      '"volatility regime" switching model']),

    ("A05", "شکاف ارزش منصفانه ↔ شکاف نقدینگی", "Fair Value Gap ↔ Liquidity Void / Jump Risk",
     ["FVG (retail)", "imbalance", "gap"], "micro", "B01", "ADJACENT",
     ["AX-05 §3.3 (F-QIMB,F-MICRO)"],
     ["Merton (1976) jump-diffusion", "Cont et al. (2014) price impact of order book events",
      "Toth et al. (2011) square-root law", "Hasbrouck (1991) information content of trades"],
     ['"liquidity void" order book gap', '"jump risk" "jump diffusion" derivatives pricing',
      '"price impact" "resilience" order book', '"post-trade reversion" microstructure',
      '"order book imbalance" predictor']),

    ("A06", "بلوک سفارش ↔ نقدینگی پنهان", "Order Blocks ↔ Hidden / Iceberg Liquidity",
     ["supply-demand zone (retail)", "iceberg", "hidden orders"], "micro", "B01", "ADJACENT",
     ["AX-05 §3.3 (F-D1,F-KYLE)"],
     ["Hautsch & Huang (hidden orders)", "Anand & Venkataraman (iceberg orders)",
      "Easley, Lopez de Prado & O'Hara (large-order detection)", "Bouchaud et al. Trades, Quotes and Prices"],
     ['"hidden orders" OR "iceberg orders" market quality', '"order anticipation" institutional trading',
      '"large order" detection trade data', '"accumulation" "distribution" institutional order flow',
      '"undisclosed liquidity" empirical']),

    ("A07", "پول هوشمند ↔ معاملات مطلع", "Smart Money ↔ Informed Trading",
     ["ICT (retail)", "smart money concepts", "order flow"], "micro", "B01", "CORE",
     ["AX-05 §3.4 (F-TAKER,F-CASCADE)"],
     ["Kyle (1985) continuous auctions", "Glosten & Milgrom (1985)", "Easley et al. (1996) PIN",
      "Lee & Ready (1991) trade classification", "Cong et al. Crypto Wash Trading"],
     ['"informed trading" Kyle model', '"trade classification" Lee Ready tick rule',
      '"order flow toxicity" measurement', '"wash trading" crypto exchanges detection',
      '"smart money" institutional order flow evidence']),

    ("A08", "حراج، کشف قیمت و انبارش تاجر", "Auction, Price Discovery and Dealer Inventory",
     ["Wyckoff (retail)", "market profile", "auction theory"], "micro", "B01", "CORE",
     ["AX-05 §3.3 (F-MICRO)"],
     ["Hasbrouck (1995) information share", "Ho & Stoll (1981) dealer pricing",
      "Avellaneda & Stoikov (2008) high-frequency market making", "Steidlmayer Market Profile (CBOT)",
      "Wyckoff (1931)"],
     ['"price discovery" "information share" Hasbrouck', '"dealer inventory" optimal pricing model',
      '"high-frequency market making" Avellaneda Stoikov', '"market profile" TPO auction theory',
      '"double auction" microstructure theory']),

    ("A09", "روند و مومنتوم سری‌زمانی", "Trend & Time-Series Momentum",
     ["trend following", "CTA", "managed futures"], "alpha", "B04", "CORE",
     ["AX-05 §3.1 (F-TS-MOM,F-TS-SLOPE)", "AX-06 §4 (M1)"],
     ["Moskowitz, Ooi & Pedersen (2012) Time Series Momentum",
      "Hurst, Ooi & Pedersen (2017) A Century of Trend Following",
      "Brock, Lakonishok & LeBaron (1992)", "Neely et al. (2014) technical indicators"],
     ['"time series momentum" Moskowitz Ooi Pedersen', '"trend following" century of evidence',
      '"moving average" rules stochastic properties Brock', '"Hurst exponent" trend persistence',
      '"managed futures" performance attribution']),

    ("A10", "مومنتوم مقطعی، واگرایی و فروپاشی", "Cross-Sectional Momentum, Divergence and Crashes",
     ["relative strength", "RSI divergence"], "alpha", "B04", "CORE",
     ["AX-05 §3.5 (F-XS-MOM)", "AX-06 §2 (labels)"],
     ["Jegadeesh & Titman (1993)", "Daniel & Moskowitz (2016) Momentum Crashes",
      "Blitz, Huij & Martens (2011) residual momentum", "Wilder (1978) RSI/ADX"],
     ['"cross-sectional momentum" Jegadeesh Titman', '"momentum crashes" Daniel Moskowitz',
      '"residual momentum" Blitz', '"52-week high" momentum', '"RSI" divergence predictive power evidence']),

    ("A11", "رژیم‌های بازار و تشخیص نقطهٔ شکست", "Market Regimes & Structural Breaks",
     ["regime classification", "risk-on/risk-off"], "alpha", "B07", "CORE",
     ["AX-06 §6", "AX-09 §4.1 (آستانه‌ها از توزیع‌های صفر)"],
     ["Hamilton (1989) Markov switching", "Ang & Timmermann (2012) Regime Changes",
      "Calvet & Fisher (2004) multifractal", "Page (1954) CUSUM"],
     ['"regime switching" financial markets Ang Timmermann', '"Markov switching" volatility state',
      '"hidden Markov model" trading regime detection', '"structural break" test time series finance',
      '"change point" online detection Bayesian']),

    ("A12", "زمینهٔ زمانی، فصل‌بودن و تقویم", "Temporal Context, Seasonality and Calendar Effects",
     ["session bias (retail)", "killzones", "time-of-day"], "data", "B01", "ADJACENT",
     ["AX-05 §3.6 (تقویم)", "AX-08 §3.2 (funding window)"],
     ["Andersen & Bollerslev (1997) intraday periodicity", "Admati & Pfleiderer (1988)",
      "Heston, Korajczyk & Sadka (2010) intraday patterns", "crypto funding-rate literature"],
     ['"intraday periodicity" volatility Andersen Bollerslev', '"time-of-day" liquidity patterns',
      '"day of week effect" OR "turn of the month" anomaly', '"overnight vs intraday" returns decomposition',
      '"funding rate" perpetual futures settlement']),

    # ---------------- Part B: the 12 institutional engines ----------------
    ("B01", "اتصال به بازار و ثبت داده", "Market Connectivity & Data Capture",
     ["feed handler", "FIX", "tick store", "replay"], "data", "—", "CORE",
     ["AX-02", "AX-04 §2", "AX-03 §3"],
     ["FIX Trading Community specs", "Lehalle & Laruelle Market Microstructure in Practice",
      "Hasbrouck Empirical Market Microstructure"],
     ['FIX protocol specification 4.4 5.0', '"feed handler" market data architecture low latency',
      '"sequence gap" market data recovery exchange', '"replay" deterministic market data simulation',
      '"PTP" precision time protocol timestamping trading']),

    ("B02", "دادهٔ مرجع و شناسنامهٔ ابزار", "Reference Data & Instrument Master",
     ["instrument master", "contract spec", "universe"], "data", "—", "CORE",
     ["AX-04 §4", "T-DATA-004"],
     ["Elton, Gruber & Blake (1996) survivorship bias", "Fung & Hsieh (2000) backfill bias",
      "instrument master design (industry)"],
     ['"survivorship bias" mutual fund performance', '"backfill bias" hedge fund databases',
      '"instrument master" reference data architecture', '"point-in-time" data vs restated fundamentals',
      '"delisting bias" return calculation']),

    ("B03", "کیفیت، یکپارچگی و ترمیم داده", "Data Quality, Integrity and Repair",
     ["data gates", "bitemporal", "PIT", "repair"], "data", "—", "CORE",
     ["AX-04 §3 (QC-01..20)", "AX-04 §8", "AX-03 §3"],
     ["Lopez de Prado AFML (data section)", "Snodgrass (1999) bitemporal SQL",
      "Sullivan, Timmermann & White (1999) data snooping"],
     ['"data snooping" bootstrap technical trading', '"look-ahead bias" backtest correction',
      '"bitemporal" database point-in-time modeling', '"outlier detection" Hampel filter MAD',
      '"data quality" gate financial market data pipeline']),

    ("B04", "پژوهش آلفا و کارخانهٔ ویژگی", "Alpha Research & Feature Factory",
     ["factor library", "alpha decay", "IC/IR", "feature store"], "research", "—", "CORE",
     ["AX-05 §2 (چارچوب پذیرش)", "AX-15 (رجیستر)"],
     ["Kakushadze (2016) 101 Formulaic Alphas", "Grinold & Kahn Active Portfolio Management",
      "Harvey, Liu & Zhu (2016) cross-section of expected returns", "Hou, Xue & Zhang (2020) replicating anomalies"],
     ['"101 formulaic alphas" Kakushadze', '"factor zoo" multiple testing anomalies',
      '"fundamental law of active management" information coefficient',
      '"replicating anomalies" Hou Xue Zhang', '"alpha decay" signal half-life capacity']),

    ("B05", "ترکیب سیگنال‌ها و انقباض", "Signal Combination & Shrinkage",
     ["forecast combination", "meta-labeling", "ensembling"], "research", "—", "CORE",
     ["AX-06 §5"],
     ["Timmermann (2006) Forecast Combinations", "Lopez de Prado AFML (meta-labeling)",
      "Bates & Granger (1969) combination of forecasts"],
     ['"forecast combination" survey Timmermann', '"meta-labeling" Lopez de Prado',
      '"Bayesian model averaging" forecasting finance', '"forecast pooling" correlation shrinkage weights',
      '"ensemble" trading signals weighting scheme']),

    ("B06", "کالیبراسیون احتمال و کمّی‌سازی عدم‌قطعیت", "Probabilistic Calibration & Uncertainty",
     ["reliability", "isotonic", "conformal", "bootstrap"], "research", "—", "CORE",
     ["AX-06 §3", "AX-08 §3.4"],
     ["Platt (1999) probabilistic outputs", "Zadrozny & Elkan (2002) isotonic",
      "Murphy (1973) Brier decomposition", "Vovk/Shafer conformal prediction",
      "Politis & Romano (1994) stationary bootstrap"],
     ['"probability calibration" reliability diagram finance',
      '"isotonic regression" classifier probability calibration', '"Brier score" decomposition Murphy',
      '"conformal prediction" time series finance', '"stationary bootstrap" dependent data']),

    ("B07", "برآورد رژیم و وضعیت", "Regime & State Estimation",
     ["HMM", "change-point", "filtered state"], "research", "—", "CORE",
     ["AX-06 §6", "AX-09 §4.1"],
     ["Hamilton (1989)", "Ang & Timmermann (2012)", "Killick et al. (2012) PELT",
      "Nystrup et al. (regime-based asset allocation)"],
     ['"regime based asset allocation" hidden Markov', '"filtered" vs "smoothed" state probability online',
      '"online changepoint detection" Bayesian', '"volatility regime" risk scaling',
      '"regime entropy" model uncertainty allocation']),

    ("B08", "ساخت پرتفوی و بهینه‌سازی مقاوم", "Portfolio Construction & Robust Optimization",
     ["mean-variance", "shrinkage", "HRP", "risk parity", "factor model"], "portfolio", "—", "CORE",
     ["AX-07 §5", "AX-07 §6", "ADR-013/ADR-014"],
     ["Markowitz (1952)", "Ledoit & Wolf (2003, 2004, 2017)",
      "Lopez de Prado (2016) HRP", "Garleanu & Pedersen (2013)",
      "Roncalli Introduction to Risk Parity and Budgeting"],
     ['"honey I shrunk the sample covariance matrix" Ledoit Wolf',
      '"building diversified portfolios" hierarchical risk parity',
      '"dynamic trading with predictable returns and transaction costs" Garleanu Pedersen',
      '"risk parity" portfolio construction theory', '"robust portfolio optimization" estimation error']),

    ("B09", "مدیریت ریسک و کنترل‌های پیش‌معاملاتی", "Risk Management & Pre-Trade Controls",
     ["VaR", "expected shortfall", "kill switch", "stress testing"], "risk", "—", "CORE",
     ["AX-07 §2", "AX-09 §2 (RK-01..25)", "AX-09 §5 (K1..K8)"],
     ["Artzner et al. (1999) coherent risk measures", "Rockafellar & Uryasev (2000) CVaR",
      "Chekhlov, Uryasev & Zabarankin (2005) drawdown", "SEC Rule 15c3-5 Market Access Rule",
      "MiFID II RTS 6 algorithmic trading", "Federal Reserve SR 11-7"],
     ['"coherent measures of risk" Artzner', '"conditional value at risk" optimization Rockafellar',
      '"market access rule" 15c3-5 pre-trade controls', 'MiFID II RTS 6 "kill functionality" algorithmic trading',
      '"model risk management" SR 11-7 guidance']),

    ("B10", "تعیین حجم و تخصیص سرمایه", "Sizing & Capital Allocation",
     ["Kelly", "vol targeting", "risk budgeting", "drawdown control"], "risk", "—", "CORE",
     ["AX-07 §7", "AX-07 §3.2 (R)"],
     ["Kelly (1956)", "MacLean, Thorp & Ziemba The Kelly Capital Growth Investment Criterion",
      "Moreira & Muir (2017) volatility-managed portfolios", "Grossman & Zhou (1993) drawdown control",
      "Merton (1969/1971) continuous-time portfolio"],
     ['"Kelly criterion" fractional Kelly risk of ruin', '"volatility managed portfolios" Moreira Muir',
      '"controlling drawdowns" optimal investment strategy Grossman Zhou',
      '"risk budgeting" portfolio allocation framework', '"volatility targeting" evidence Sharpe improvement']),

    ("B11", "اجرا و تحلیل هزینهٔ معاملات", "Execution & Transaction Cost Analysis",
     ["implementation shortfall", "Almgren-Chriss", "VWAP/TWAP", "TCA", "market impact"], "exec", "—", "CORE",
     ["AX-08 §3", "AX-08 §4", "AX-08 §8 (TCA)"],
     ["Perold (1988) implementation shortfall", "Almgren & Chriss (2000)",
      "Bertsimas & Lo (1998)", "Obizhaeva & Wang (2013)", "Gatheral (2010)",
      "Toth et al. (2011) square-root law", "Kissell The Science of Algorithmic Trading"],
     ['"implementation shortfall" Perold paper vs reality',
      '"optimal execution of portfolio transactions" Almgren Chriss',
      '"optimal control of execution costs" Bertsimas Lo', '"square root law" market impact liquidity',
      '"no dynamic arbitrage" market impact Gatheral', '"transaction cost analysis" TCA decomposition slippage']),

    ("B12", "عملیات، حاکمیت مدل و پس‌معاملات", "Operations, Model Governance & Post-Trade",
     ["OMS/EMS", "reconciliation", "attribution", "model registry", "MLOps"], "ops", "—", "CORE",
     ["AX-08 §5", "AX-08 §7", "AX-12", "AX-10 §5"],
     ["Bacon Practical Portfolio Performance Measurement and Attribution",
      "Menchero, Orr & Wang attribution", "Federal Reserve SR 11-7",
      "FIX order lifecycle specification", "Narang Inside the Black Box"],
     ['"performance attribution" Brinson multi-factor',
      '"model risk management" model inventory validation governance',
      '"trade reconciliation" breaks operations asset manager',
      '"order management system" EMS OMS architecture buy side',
      '"champion challenger" model deployment governance quant']),
]

HEADER = """# AXIOM — search query pack (generated by research/build_index.py)
#
# How to use: paste a line into Google / Google Scholar / SSRN / arXiv.
#   * For arXiv only:  append   site:arxiv.org
#   * For papers only: append   filetype:pdf
#   * For scholar:     use the quoted phrase as-is
# Every line starts with the concept id (see research/concept_index.json) so results
# can be filed back into the encyclopedia under the right concept.
#
# Reminder (AX-10 §2): a hit is a SEARCH VECTOR, not evidence. Grade it before it
# enters the encyclopedia: primary paper / replication / regulation / industry claim.
"""


def main() -> int:
    entries = []
    for (cid, fa, en, aliases, family, engine, status, refs, sources, queries) in C:
        entries.append({
            "id": cid,
            "title_fa": fa,
            "title_en": en,
            "aliases": aliases,
            "family": family,
            "engine": engine,
            "status": status,
            "axiom_refs": refs,
            "sources": sources,
            "queries": queries,
        })

    index = {
        "$comment": ("AXIOM research concept index (non-normative, ADR-026). "
                     "Feeds the owner's literature-collection campaign; creates no design obligation."),
        "schema_version": 1,
        "concepts": entries,
        "id_ranges": {
            "A01..A12": "the twelve apex_gen5 engines (E01..E12), translated to institutional vocabulary",
            "B01..B12": "the twelve operational engines of an institutional quant stack"
        },
        "status_legend": {
            "CORE": "established concept with a real institutional/academic literature",
            "ADJACENT": "the retail concept maps onto a real phenomenon, but the retail formulation is not evidence",
            "SPECULATIVE": "no independent literature; record as a hypothesis only"
        },
    }
    idx_text = json.dumps(index, indent=2, ensure_ascii=False) + "\n"

    lines = [HEADER]
    for e in entries:
        lines.append(f"# --- {e['id']} · {e['title_en']} ({e['title_fa']})")
        lines.extend(e["queries"])
        lines.append("")
    q_text = "\n".join(lines)

    idx = HERE / "concept_index.json"
    qp = HERE / "search_queries.txt"
    if "--check" in sys.argv:
        ok = True
        if not idx.exists() or idx.read_text(encoding="utf-8") != idx_text:
            print("DRIFT: concept_index.json", file=sys.stderr); ok = False
        if not qp.exists() or qp.read_text(encoding="utf-8") != q_text:
            print("DRIFT: search_queries.txt", file=sys.stderr); ok = False
        print("research index check:", "OK" if ok else "FAILED")
        return 0 if ok else 1
    idx.write_text(idx_text, encoding="utf-8")
    qp.write_text(q_text, encoding="utf-8")
    print(f"wrote {idx.name} ({len(entries)} concepts) and {qp.name} "
          f"({sum(len(e['queries']) for e in entries)} queries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
