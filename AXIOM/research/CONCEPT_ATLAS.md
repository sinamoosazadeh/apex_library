# AXIOM — Concept Atlas (اطلس مفاهیم برای دایرةالمعارف)

> **وضعیت: غیر‑هنجاری (non-normative).** این سند و پوشهٔ `research/` بخشی از مجموعهٔ طراحی AXIOM نیستند،
> هیچ بندی از `docs/AX-00…AX-18` را تغییر نمیدهند و هیچ آزمون/دروازهای به آن ارجاع نمیدهد
> (ثبت رسمی: `AX-18` — ADR-026). هدفش یک چیز است: **ساخت یک لِکسیکون جستوجو** برای مالک، تا بتواند
> دایرةالمعارف منابع (مقالات، کتابها، مقررات، مستندات مؤسسهای) را حول مفاهیم واقعی بازارهای کوانت/مؤسسهای
> بسازد. هر ورودی در این سند یک **بردار جستوجو** است، نه یک استناد نهایی؛ دقت سال/ژورنال/نویسنده باید در
> مرحلهٔ جمعآوری از منبع اصلی تأیید شود (این همان قانون `AX-10` بند ۲ است: هیچ چیزی بدون منبع اولیه وارد
> سیستم نمیشود).

---

## ۰) چرا این سند به این شکل نوشته شده

سه واقعیت که شکل این اطلس را تعیین کردهاند:

1. **الگوریتمهای واقعی Tier A منتشر نمیشوند.** چیزی که در دسترس عموم است، چهار جنس سند است:
   (الف) **مقالات علمی** (JF, JFE, RFS, Management Science, Quantitative Finance, arXiv q-fin),
   (ب) **کتابهای درسی/حرفهای** نوشتهٔ معاملهگران و پژوهشگران مؤسسهای، (ج) **مقررات و راهنمای ناظران**
   (SEC 15c3-5، MiFID II RTS 6، SR 11-7، BIS)، (د) **مستندات عمومی زیرساخت** (FIX، بورسها، صرافیها).
   دایرةالمعارف واقعبینانه = همین چهار جنس. هر چیزی خارج از اینها (ویدیوهای «استراتژی صندوقها»)
   شواهد کلاس `L-CLAIM` ضعیف است، نه `[V]`/`[D]` (کلاسهای شواهد: `AX-00` بند ۳).
2. **دو دایرهٔ واژگانی وجود دارد که یکدیگر را نمیشناسند.** دایرهٔ خردهفروشی/پرایساکشن (ICT, FVG,
   Order Block, Wyckoff, SMC) و دایرهٔ مؤسسهای/آکادمیک (order-flow imbalance, liquidity provision,
   change-point detection, market impact, inventory models). **پدیدهها یکی هستند؛ نامها نه.**
   بخش A همین نقشهٔ ترجمه است.
3. **۱۲ موتور `apex_gen5` ساختار AXIOM نیست** (`AX-00` بند ۶، `AX-17` بند ۶). بخش A فقط برای
   آرشیو دانش و ترجمهٔ واژگانی است؛ در AXIOM معادلِ *قابل‌اندازه‌گیری* آنها بهصورت `F-*` در `AX-05` زندگی
   میکند و هیچ موتوری از GEN5 وارد نشده است.

---

## بخش A — آن ۱۲ موتور (E01–E12) و مفهومِ مؤسسهایِ هرکدام

نامهای زیر از فایل `APEX_GEN5.md` (خط ۱۲۰۲ به بعد) استخراج شدهاند و **فقط به‌عنوان مرجع تاریخی** آمدهاند.

| # | موتور (GEN5) | مفهومی که ادعا میکند | معادل مؤسسهای/آکادمیک — **واژگان جستوجو** | وضعیت واقعی |
|---|---|---|---|---|
| E01 | Structure | ساختار بازار (BOS/CHoCH/سوینگ) | **Change-point detection** · **Trend filtering** · **Piecewise linear segmentation** · **Swing/ZigZag detection** · **Dow theory** · **Optimal stopping** | زبان پرایساکشن؛ معادل ریاضی آن «تشخیص نقطهٔ تغییر» است |
| E02 | Liquidity | استخرهای نقدینگی و «جمع‌آوری» (sweep) | **Liquidity provision/consumption** · **Predatory trading** · **Stop-loss cascades** · **Order-flow imbalance (OFI)** · **Liquidity resilience/recovery** · **Depth elasticity** | پدیده واقعی است؛ نام مؤسسهای آن «نقدینگی و شکار حدضرر» است |
| E03 | Volume / Participation | حجم و مشارکت | **Volume clock** · **VPIN (volume-synchronized probability of informed trading)** · **Order flow toxicity** · **Participation rate (POV)** · **VWAP/TWAP** · **Trade-size clustering** | کاملاً معتبر؛ ادبیات غنی (Easley–López de Prado–O'Hara) |
| E04 | Volatility | فشردگی→انبساط | **Volatility clustering** · **GARCH family** · **Realized volatility / HAR-RV** · **Volatility-of-volatility** · **Range expansion / opening-range breakout** · **Volatility regime switching** | معتبر؛ هستهٔ ادبیات volatility |
| E05 | Imbalance / FVG | شکاف ارزش منصفانه | **Limit-order-book imbalance** · **Liquidity void / gap** · **Jump risk (Merton jump-diffusion)** · **Price impact & resilience** · **Post-trade reversion** | «FVG» = روایت پرایساکشنِ «شکاف نقدینگی در دفتر سفارش» |
| E06 | Order Block | ناحیهٔ عرضه/تقاضا | **Hidden/iceberg liquidity** · **Order anticipation** · **Large-order detection** · **Accumulation/distribution** · **Iceberg & reserve orders** | ناحیهٔ سفارش = مفهوم واقعی «نقدینگی پنهان» با نام مؤسسهای |
| E07 | RTM/ICT | پول هوشمند | **Informed trading (Kyle, Glosten–Milgrom)** · **PIN** · **Order flow toxicity** · **Trade classification (Lee–Ready, tick rule)** · **Market manipulation & surveillance** | ICT زبان خردهفروشی است؛ معادل: «سمّیت جریان سفارش» |
| E08 | Wyckoff / Auction | حراج و انبارش | **Double auction** · **Price discovery / information share (Hasbrouck)** · **Market Profile / TPO** · **Dealer inventory models (Ho–Stoll, Avellaneda–Stoikov)** · **Auction theory** | کلاسیک است؛ نسخهٔ دانشگاهی آن «نظریهٔ حراج و کشف قیمت» است |
| E09 | Trend | روند | **Time-series momentum** · **Trend following (managed futures)** · **State-space/Kalman trend** · **MA crossover evidence** · **Hurst exponent** | معتبر و پرمنبع (Moskowitz–Ooi–Pedersen) |
| E10 | Momentum | مومنتوم و واگرایی | **Cross-sectional momentum** · **Momentum crashes** · **Residual momentum** · **52-week high** · **Divergence/exhaustion** · **Momentum ignition** | معتبر؛ نسخهٔ واگرایی، ضعیف‌ترین بخش آن است |
| E11 | Regime | تشخیص رژیم | **Markov-switching models (Hamilton)** · **Hidden Markov Models** · **CUSUM change-points** · **Volatility regimes** · **Risk-on/risk-off** · **Clustering-based regimes** | کاملاً مؤسسهای |
| E12 | Temporal Context | زمینهٔ زمانی | **Intraday periodicity** · **Time-of-day liquidity** · **Seasonality & calendar effects** · **Overnight vs intraday returns** · **Funding-settlement timing (crypto)** | مؤسسهای است اما به‌عنوان *فیلتر*، نه به‌عنوان موتور مستقل |

**نتیجهٔ صریح برای شما:** ۵ مورد از این ۱۲ (E02, E03, E07, E08, E11) با ترجمهٔ واژگانی به ادبیات
Tier A وصل میشوند؛ ۴ مورد (E01, E04, E09, E10) معادل روشنِ آکادمیک دارند؛ و ۳ مورد (E05, E06 با روایت
پرایساکشن، و بخش «واگرایی» E10) **در دایرةالمعارف با درجهٔ شواهد پایین** ثبت میشوند، چون ادبیات مؤسسهای
برای آنها یا وجود ندارد یا اثرشان بعد از هزینه تکرارنیذیر است.

---

## بخش B — ۱۲ موتورِ واقعیِ یک استک مؤسسهای (ستون فقرات دایرةالمعارف)

این ۱۲ «موتور عملیاتی» همان چیزی است که یک تیم کوانت Tier A واقعاً میسازد و می‌گرداند. برای هر کدام:
زیرمفاهیم (واژگان جستوجو)، منبع کانونی، و محلِ آن در AXIOM.

### B01 — اتصال به بازار و ثبت داده (Market Connectivity & Data Capture)
**زیرمفاهیم:** market data feed handler · FIX 4.4/5.0 protocol · WebSocket market data · snapshot vs incremental
entropy · tick store · point-in-time capture · sequence gap detection · replay determinism · nanosecond timestamps ·
colocation · PTP (Precision Time Protocol) · venue session/schedule.
**منابع کانونی:** مستندات FIX Trading Community؛ Lehalle & Laruelle, *Market Microstructure in Practice*؛
Hasbrouck, *Empirical Market Microstructure*.
**در AXIOM:** `AX-02` (Venue Truth) + `AX-04` (Data Plane) + `AX-03` (زمان/هویت).

### B02 — دادهٔ مرجع و شناسنامهٔ ابزار (Reference Data & Instrument Master)
**زیرمفاهیم:** instrument master · contract specification · tick size / step size / multiplier · notional limits ·
contract rollover · **survivorship bias** · backfill bias · universe construction rule-based · corporate-action
analogs (crypto: re-listing, contract migration) · delisting bias · static vs dynamic universe.
**منابع کانونی:** Elton–Gruber–Blake (1996) survivorship؛ Fung & Hsieh (2000) backfill bias؛
`AX-04` بند ۴ (قانون یخ‌بستن یونیورس).
**در AXIOM:** `AX-04` §4 + `T-DATA-004` (ضد جان‌به‌دربردن).

### B03 — کیفیت، یکپارچگی و ترمیم داده (Data Quality, Integrity & Repair)
**زیرمفاهیم:** data quality gate · outlier detection (Hampel/MAD) · staleness detection · missing-bar detection ·
**bitemporal modeling** · late-arriving data · availability lag / PIT correctness · **look-ahead bias** ·
**data snooping (Sullivan–Timmermann–White)** · gap repair / backfill policy · reconciliation of data vs venue ·
audit trail of corrections · point-in-time vs as-reported.
**منابع کانونی:** López de Prado, *AFML* (بخش داده)؛ Snodgrass (bitemporal)؛ مستندات Compustat PIT (به‌عنوان
نمونهٔ صنعتی «زمان دسترسی»).
**در AXIOM:** `AX-04` §3 (QC-01…20) + §8 (Repair) + `AX-03` §3 (TapeCursor/PIT).

### B04 — پژوهش آلفا و کارخانهٔ ویژگی (Alpha Research & Feature Factory)
**زیرمفاهیم:** **alpha factor library** · **101 Formulaic Alphas** · **alpha decay** · **factor zoo** ·
**cross-sectional standardization** · winsorization · neutralization · **IC / IR / fundamental law of active
management** · **orthogonalization** · **multiple-testing in factor search** · **replicating anomalies** ·
feature store · capacity of a signal.
**منابع کانونی:** Kakushadze (2016) *101 Formulaic Alphas*؛ Grinold & Kahn, *Active Portfolio Management*؛
Harvey–Liu–Zhu (2016) *…and the Cross-Section of Expected Returns*؛ Hou–Xue–Zhang (2020) *Replicating Anomalies*.
**در AXIOM:** `AX-05` (Signal Library) + چارچوب پذیرش §2.

### B05 — ترکیب سیگنال‌ها (Signal Combination & Shrinkage)
**زیرمفاهیم:** forecast combination · **combining forecasts (Bates–Granger)** · **Bayesian model averaging** ·
**meta-labeling** · model ensembling · shrinkage of weights · weights under correlation · **forecast pooling in
practice** · model crowding · decorrelation.
**منابع کانونی:** Timmermann (2006) *Forecast Combinations* (Handbook of Economic Forecasting)؛
López de Prado *AFML* (meta-labeling)؛ Grinold–Kahn (سرمایه‌گذاری سیگنال‌ها).
**در AXIOM:** `AX-06` §5 (ترکیب با انقباض و سقف وزن).

### B06 — کالیبراسیون احتمال و کمّی‌سازی عدم‌قطعیت (Probabilistic Calibration & Uncertainty)
**زیرمفاهیم:** **reliability diagram** · **Platt scaling** · **isotonic regression** · **Brier score
decomposition (Murphy)** · **sharpness** · **conformal prediction** · **block bootstrap** · **prediction
intervals** · **expected shortfall of a forecast** · uncertainty propagation to position size.
**منابع کانونی:** Platt (1999)؛ Zadrozny & Elkan (2002)؛ Murphy (1973)؛ Brier (1950)؛ Vovk/Shafer (conformal)؛
Politis & Romano (1994) stationary bootstrap.
**در AXIOM:** `AX-06` §3 (`p_net`, `σ_model`, BSS) + `AX-08` §3.4 (استفادهٔ صریح از `σ` در دروازهٔ معامله).

### B07 — برآورد رژیم و وضعیت (Regime & State Estimation)
**زیرمفاهیم:** **Markov-switching models** · **Hidden Markov Models** · **filtered vs smoothed state
probabilities** · **change-point detection (CUSUM, PELT, Bayesian online changepoint)** · **structural break
tests** · **volatility regimes** · **correlation regimes** · **entropy of regime posterior** · regime-conditional
risk scaling.
**منابع کانونی:** Hamilton (1989)؛ Ang & Timmermann (2012) *Regime Changes and Financial Markets*؛
Page (1954) CUSUM؛ Killick et al. (2012) PELT.
**در AXIOM:** `AX-06` §6 + `AX-09` §4 (آستانه‌های فرماندار بر پایهٔ کوانتیل توزیع خودِ آماره).

### B08 — ساخت پرتفوی (Portfolio Construction & Optimization)
**زیرمفاهیم:** **mean–variance optimization (Markowitz)** · **robust portfolio optimization** ·
**shrinkage covariance (Ledoit–Wolf)** · **random matrix theory / Marchenko–Pastur denoising** ·
**factor risk models (Barra/Axioma-style)** · **Black–Litterman** · **risk parity** · **hierarchical risk
parity (HRP)** · **turnover-penalized optimization (Gârleanu–Pedersen)** · **no-trade band** ·
constraint set (gross/net/instrument/sector) · solver determinism.
**منابع کانونی:** Markowitz (1952)؛ Ledoit & Wolf (2003, 2004, 2017)؛ López de Prado (2016) HRP؛
Gârleanu & Pedersen (2013)؛ Roncalli *Introduction to Risk Parity and Budgeting*.
**در AXIOM:** `AX-07` §5–§6 (زنجیرهٔ کوواریانس + QP محدود + باند بی‌معامله).

### B09 — مدیریت ریسک و کنترل مواجهه (Risk Management & Exposure Control)
**زیرمفاهیم:** **VaR / Expected Shortfall** · **coherent risk measures** · **CVaR optimization** ·
**drawdown-based risk measures** · **stress testing / scenario analysis** · **liquidity risk (L-VaR)** ·
**pre-trade risk controls** · **kill switch** · **fat-finger checks** · **max order size / price band checks** ·
**limit hierarchy** · **risk budgeting** · **risk of ruin**.
**منابع کانونی:** Artzner et al. (1999) coherent risk؛ Rockafellar & Uryasev (2000) CVaR؛
Chekhlov–Uryasev–Zabarankin (2005) drawdown measures؛ **SEC Rule 15c3-5 (Market Access Rule)** و
**MiFID II RTS 6** به‌عنوان مرجع *مقرراتی* کنترل‌های پیش‌معاملاتی و الزام kill switch؛
**Federal Reserve SR 11-7** (Model Risk Management)؛ BIS/FSB stress-testing guidance.
**در AXIOM:** `AX-07` §2/§7 + `AX-09` (کرنل ۲۵ بررسی + K1–K8).

### B10 — تعیین حجم و تخصیص سرمایه (Sizing & Capital Allocation)
**زیرمفاهیم:** **Kelly criterion** · **fractional Kelly** · **continuous-time Kelly (Merton)** ·
**volatility targeting** · **volatility-managed portfolios (Moreira–Muir)** · **risk budgeting across bets** ·
**drawdown control (Grossman–Zhou)** · **optimal f** · position-level vs portfolio-level sizing · leverage policy ·
margin/collateral optimization.
**منابع کانونی:** Kelly (1956)؛ MacLean–Thorp–Ziemba *The Kelly Capital Growth Investment Criterion*؛
Moreira & Muir (2017)؛ Grossman & Zhou (1993)؛ Merton (1969/1971).
**در AXIOM:** `AX-07` §7 (پنج سقف: ریسک، نوسان، کلی با کران پایین، نقدینگی، مارجین).

### B11 — اجرا و تحلیل هزینهٔ معاملات (Execution & Transaction Cost Analysis)
**زیرمفاهیم:** **implementation shortfall (Perold)** · **Almgren–Chriss optimal execution** ·
**VWAP/TWAP/POV algorithms** · **arrival price** · **smart order routing** · **dark pools / ATS** ·
**market impact models (Kyle lambda, square-root law)** · **temporary vs permanent impact** ·
**execution risk vs timing risk** · **opportunity cost of non-execution** · **TCA decomposition** ·
**adverse selection** · **slippage buckets** · **order placement aggressiveness** · **iceberg/reduce-only** ·
**limit-order placement optimization (Guéant–Lehalle)**.
**منابع کانونی:** Perold (1988)؛ Almgren & Chriss (2000)؛ Bertsimas & Lo (1998)؛ Obizhaeva & Wang (2013)؛
Kyle (1985)؛ Gatheral (2010)؛ Tóth et al. (2011) square-root law؛ Kissell, *The Science of Algorithmic
Trading and Portfolio Management*؛ Johnson, *Algorithmic Trading and DMA*.
**در AXIOM:** `AX-08` §3–§4 (مدل هزینه، دروازهٔ اقتصادی، قیمت‌گذاری سفارش) + §8 (TCA).

### B12 — عملیات، حاکمیت مدل و پس‌معاملات (Operations, Model Governance & Post-Trade)
**زیرمفاهیم:** **OMS/EMS** · order lifecycle state machine · **idempotency / duplicate order protection** ·
**reconciliation (position, cash, fills)** · **trade breaks** · allocation & booking · **performance attribution
(Brinson)** · **transaction cost attribution** · **model risk management (SR 11-7)** · **model registry /
champion–challenger** · **MLOps / experiment tracking / reproducibility** · audit trail · **incident
postmortem** · regulatory reporting (MiFID II, CAT in US) · **disaster recovery / RTO-RPO**.
**منابع کانونی:** Bacon, *Practical Portfolio Performance Measurement and Attribution*؛
Menchero/Orr/Wang (attribution)؛ **SR 11-7**؛ مستندات FIX برای چرخهٔ سفارش؛ Narang, *Inside the Black Box*.
**در AXIOM:** `AX-08` §5/§7 (پروتکل عدم‌قطعیت + مغایرت‌زدایی) + `AX-12` (عملیات/امنیت/رانبوک) + `AX-10` §5
(رجیستر مدل).

---

## بخش C — ستون‌های کتابخانه‌ای (Canon): ۴۰ منبعِ پایه که بقیه به آنها ارجاع می‌دهند

**C1) ریزساختار بازار و اجرا**
Hasbrouck, *Empirical Market Microstructure* · O'Hara, *Market Microstructure Theory* ·
Bouchaud, Bonart, Donier, Gould, *Trades, Quotes and Prices* · Cartea, Jaimungal, Penalva,
*Algorithmic and High-Frequency Trading* · Lehalle & Laruelle, *Market Microstructure in Practice* ·
Kyle (1985) · Glosten & Milgrom (1985) · Amihud (2002) · Roll (1984) · Lee & Ready (1991) ·
Cont, Kukanov & Stoikov (2014) · Tóth et al. (2011) · Avellaneda & Stoikov (2008) · Ho & Stoll (1981).

**C2) پرتفوی، ریسک و تخصیص سرمایه**
Markowitz (1952) · Grinold & Kahn, *Active Portfolio Management* · Ang, *Asset Management* ·
Ilmanen, *Expected Returns* · Pedersen, *Efficiently Inefficient* · Ledoit & Wolf (2003/2004/2017) ·
López de Prado (2016) HRP · Roncalli, *Introduction to Risk Parity and Budgeting* · Meucci,
*Risk and Asset Allocation* · Artzner et al. (1999) · Rockafellar & Uryasev (2000) · Kelly (1956) ·
MacLean–Thorp–Ziemba · Grossman & Zhou (1993) · Moreira & Muir (2017) · Gârleanu & Pedersen (2013).

**C3) آمار، یادگیری و اعتبارسنجی**
López de Prado, *Advances in Financial Machine Learning* · López de Prado, *Machine Learning for Asset
Managers* · Bailey & López de Prado (2014) deflated Sharpe · Bailey et al. (2014) PBO/CSCV ·
White (2000) Reality Check · Hansen (2005) SPA · Politis & Romano (1994) · Harvey, Liu & Zhu (2016) ·
Sullivan, Timmermann & White (1999) · Chan, *Algorithmic Trading* / *Quantitative Trading* ·
Sinclair, *Volatility Trading*.

**C4) مقررات، حاکمیت و زیرساخت (منابع مؤسسهایِ واقعی)**
SEC **Rule 15c3-5** (Market Access Rule) · **MiFID II RTS 6** (الزامات الگوریتمی، kill switch، تست) ·
**Federal Reserve SR 11-7** (Model Risk Management) · **BIS/FSB** گزارش‌های ریسک و استرس ·
FIX Trading Community specifications · مستندات تغییر ساختار بازار (SEC Market Structure) ·
**قانون ورشکستگی/ریسک عملیاتی (Basel)**.

**C5) مخصوص کریپتو (برای صرافی مورد استفادهٔ شما)**
He, Manela, Ross & von Beschwitz — *Fundamentals of Perpetual Futures* (perpetual/funding) ·
Makarov & Schoar (2020) *Trading and Arbitrage in Cryptocurrency Markets* (JFE) ·
Cong, Li, Tang & Yang — *Crypto Wash Trading* (کیفیت دادهٔ صرافی‌های کریپتو) ·
ادبیات **funding-rate basis / cash-and-carry** · **liquidation cascades / deleveraging spirals** ·
**stablecoin & margin mechanics** · مستندات صرافی مورد استفاده (که در `AX-02` سند شده است).

---

## بخش D — راهنمای شکار منابع (Search Playbook)

**D1) محل‌های جستوجو (به ترتیب بازده):**

| منبع | چه چیزی دارد | چطور جستوجو کنیم |
|---|---|---|
| **SSRN** | مقالات کاری مالی/کوانت با کیفیت بالا؛ پیش از ژورنال | جستوجوی عنوان + author؛ فیلتر «Financial Economics» و «Capital Markets» |
| **arXiv (q-fin.TR / q-fin.PM / q-fin.RM / q-fin.ST / q-fin.MF)** | نسخهٔ preprint مقالات ریزمحاسباتی و اجرا | `site:arxiv.org q-fin.TR <concept>` |
| **NBER / RePEc / Fed working papers / BIS** | مقالات مؤسسهای و مقرراتی | `site:nber.org`, `site:bis.org`, `site:federalreserve.gov` |
| **Journal sites** (JF, JFE, RFS, Management Science, Quantitative Finance, JPM, JFQA) | مقالات مرجع | جستوجو با نام نویسندهٔ کانونی + مفهوم |
| **SEC / ESMA / MiFID / FIX** | مقررات و مشخصات فنی | `site:sec.gov 15c3-5`, `MiFID II RTS 6 killing functionality` |
| **Risk.net / QuantStart / Hudson & Thames / blog های مؤسسهای** | ترجمهٔ عملی مفاهیم | برای ایده، نه برای استناد |
| **گزارش‌های مؤسسهای (AQR, Man Group, Two Sigma, Robeco, MSCI, WorldQuant)** | کاربرد صنعتی | `site:aqr.com`, `site:msci.com research` |

**D2) نحو جستوجو (نمونه‌های آماده):** در فایل `research/search_queries.txt` یک بستهٔ آماده با
~۱۲۰ کوئری خط‌به‌خط (قابل کپی/پیست یا اسکریپت‌شدن) قرار دارد؛ هر کوئری با شناسهٔ مفهوم شروع می‌شود.

**D3) قاعدهٔ سه‌گذری برای هر مفهوم (تا دایرةالمعارف بی‌کیفیت نشود):**
1. **منبع اولیه:** مقالهٔ اصلی/مقرره/مستندات → ثبت با کلاس `[L-CLAIM]` (یا `[V-DOC]` برای صرافی/مقرره).
2. **منبع درجه‌دوم:** کتاب یا مقالهٔ مروری که آن را توضیح می‌دهد → ثبت به‌عنوان «تفسیر».
3. **شاهد تجربی مستقل:** اگر مقالهٔ *تکرار* (replication) یا نقد وجود دارد، حتماً ثبت شود.
   اگر مفهوم فقط در منبع اولیه تأیید شده و تکرار مستقل ندارد، در دایرةالمعارف با برچسب **«تأییدنشدهٔ مستقل»**
   می‌نشیند — همان اصلی که در `AX-10` بند ۳ به‌صورت «تکرارپذیری و کنترل چندآزمونی» عملیاتی شده است.

---

## بخش E — چطور خروجی جستوجو به یک دایرةالمعارف واقعی تبدیل شود

### E1) اسکیمای هر ورودی (پیشنهاد)
```
id            : CONCEPT-<nn>            # شناسهٔ مفهوم (مطابق research/concept_index.json)
title_fa      : عنوان فارسی
title_en      : عنوان/واژگان انگلیسی (کانونیکال)
aliases       : مترادفها و واژههای خردهفروشی معادل (مثلاً FVG ↔ liquidity void)
family        : micro | data | alpha | risk | portfolio | exec | ops | research | crypto
engine        : B01..B12                 # موتور میزبان
status        : CORE | ADJACENT | SPECULATIVE
evidence      : L-CLAIM(primary) | L-CLAIM(replication) | V-DOC | SPEC-MEASURED
sources[]     : {type: paper|book|regulation|spec|crypto-doc, cite: "...", url}
axiom_refs[]  : بندهای AX که این مفهوم در آنها عملیاتی شده (یا «—» اگر وارد طراحی نشده)
notes         : نکتهٔ مهم: محدودیت، شرط اعتبار، خطر سوءتفسیر
```
قالب ماشین‌خوان همین اسکیما در `research/concept_index.json` با ۲۴ مفهوم پرشده است — قابل بارکردن
توسط برچسب‌گذاری، اسکریپت جستوجو، یا ابزار مدیریت دایرةالمعارف.

### E2) قانون طلایی ورود به طراحی
هر چیزی که در جستوجوها پیدا می‌کنید **ابتدا در دایرةالمعارف می‌نشیند (لایهٔ دانش)** و برای ورود به
طراحی AXIOM باید از مسیرهای موجود عبور کند:
مفهوم جدید → `AX-05` بند ۲ (الزام مکانیزم + آزمون اطلاعات حاشیه‌ای + FDR) → `AX-10` (پیش‌ثبت و نردبان) →
اگر پارامتری اضافه شد: `AX-15` (شناسه، کلاس، بازه) → اگر رفتار تغییر کرد: `AX-18` (ADR، کلاس ۱–۴).
**هیچ چیزی مستقیم از دایرةالمعارف وارد کد نمیشود** (`AX-16` بند ۹، بند ۱).

---

## بخش F — دام‌ها (چه چیزهایی را در دایرةالمعارف نگذارید)

1. **مفاهیمِ بی‌مکانیزم با آمار قوی:** «۹۵٪ وین‌ریت» بدون مکانیزم = `SPECULATIVE` (اصل A9).
2. **نتایج بک‌تستِ بدون کنترل چندآزمونی:** هر عددی که با `DSR/PBO` اعتبارسنجی نشده، «ادعا» است نه «شاهد».
3. **سوگیری بقا/جان‌به‌دربردن:** هر مقاله‌ای که یونیورس را با نمادهای امروز می‌سازد، معتبر نیست
   (`T-DATA-004`).
4. **ادبیات HFT/کولوکیشن:** برای AXIOM مفید است اما **خارج از دامنهٔ اجرایی ما** است (ADR-007)؛
   فقط به‌عنوان دانش جمع شود، هرگز به‌عنوان هدف.
5. **مفاهیم مقرراتی که فقط به بازار سهام مربوط‌اند** (مثل CAT): از منظر *طراحی کنترل* درس بگیرید
   (pre-trade controls، kill switch، تست الگوریتم)، نه از منظر انطباق که برای کریپتو معنا ندارد.
6. **مطالب «استراتژی صندوق‌ها» بدون منبع اولیه:** کلاس شواهد ضعیف؛ ثبت در بخش «شایعات صنعتی» یا حذف.

---

## بخش G — ۱۲ نکته‌ای که در جستوجو کمتر پیدا می‌شود (و ارزش طلا دارد)

1. هر مقالهٔ **اجرا** را با فرض *impact موقت در برابر دائمی* بخوانید؛ اکثر بک‌تست‌های کریپتو موقت را
   حس نمی‌کنند و همین یک خطا کل آلفا را می‌خورد.
2. **Capacity** را جدا از Sharpe ثبت کنید: سیگنالی که در ۱ میلیون دلار کار می‌کند در ۱۰۰ میلیون نه
   (منابع: Gârleanu–Pedersen؛ ادبیات «capacity of strategies»).
3. **Momentum crash** و **factor crowding** دو رویداد واقعی‌اند؛ هر استراتژی مومنتومی بدون سنجهٔ
   crowding ناقص است.
4. **Regime posterior entropy** مبنای منطقی «کوچک‌کردن در ابهام» است، نه آستانه‌های دستی.
5. **Funding** در کریپتو معادل dividend/borrow در سهام است: کسی که آن را در برچسب درست حس نکند،
   بک‌تستش سراب است (در AXIOM: `AX-06` §2.1).
6. **Wash trading** در صرافی‌های کریپتو واقعی و گسترده است ⇒ بازیابی «حجم واقعی» یک مسئلهٔ داده است
   (منبع کانونی: Cong et al.).
7. **PM/MM inventory models** (Avellaneda–Stoikov, Ho–Stoll) ریاضیات «پشتوانهٔ» مفاهیمی مثل
   Order Block و Liquidity Pool هستند.
8. **Predatory trading** (Brunnermeier–Pedersen) نسخهٔ دانشگاهی «جمع‌آوری نقدینگی/شکار استاپ» است.
9. **Reality Check / SPA** را قبل از DSR بخوانید: کدام آزمون به چه سؤالی جواب می‌دهد، متفاوت است.
10. **متون مقرراتی** (RTS 6، 15c3-5، SR 11-7) بهترین طراحی‌های *کنترل* را دارند و مکمل مقالات آلفا هستند.
11. **بازسازی نتایج (replication)** ارزشمندترین منبع است: مقالاتی که آنومالی‌های قبلی را رد می‌کنند
    (Hou–Xue–Zhang؛ Harvey–Liu–Zhu) به شما یاد می‌دهند کدام آلفا احتمالاً واقعی است.
12. **لاگ و پس‌معاملات** را از روز اول جدی بگیرید: بدون TCA و attribution، «چرا پول درآمد/از دست رفت»
    برای همیشه حدس باقی می‌ماند (`AX-08` §8، `AX-12` §9).

---

### پیوست — فایل‌های همراه
- `research/concept_index.json` — ۲۴ مفهوم (۱۲ ترجمهٔ GEN5 + ۱۲ موتور مؤسسهای) با مترادف‌ها، منابع کانونی،
  شناسه‌های AXIOM و برچسب وضعیت؛ قابل بارکردن برای اجرای خودکار کوئری‌ها.
- `research/search_queries.txt` — بستهٔ آمادهٔ کوئری (~۱۲۰ خط) برای گوگل/گوگل‌اسکالر/arXiv/SSRN.
- `research/README.md` — قانون استفاده و نحوهٔ افزودن ورودی جدید به دایرةالمعارف.
