# Quantitative & Institutional Trading — Concept Taxonomy for Literature Search

**Purpose.** A categorized index of the concepts, methods and vocabulary used by quantitative and
institutional trading systems, built to drive systematic literature search.

**Entry format.** `Name (abbreviation)` — short gloss — `q:` search phrases — `r:` landmark references.
Each entry is a search seed, not a conclusion: expand it with the sub-terms of its own domain and with
the expansion patterns at the end of this document.

**Numbering.** `D<domain>.<entry>` — cite an id (e.g. "expand D03.4 into queries") to request a
concept's deeper expansion or cross-linking.

**Coverage.** Financial theory · market microstructure · order flow · market impact and execution ·
data engineering and data quality · time-series econometrics · volatility · regime and change
detection · alpha research and factors · alternative data · forecasting and calibration · machine
learning · reinforcement learning · portfolio construction · covariance estimation · risk management ·
sizing and capital allocation · backtesting and validation · simulation · derivatives, futures and
funding · crypto market structure · venue mechanics and regulation · operations and governance ·
performance measurement · decision theory · trading systems engineering · search venues.

---

## Domain index

| # | Domain |
|---|---|
| D01 | Market Microstructure & the Limit Order Book |
| D02 | Liquidity, Order Flow & Informed Trading |
| D03 | Market Impact & Execution |
| D04 | Market Data: Capture, Quality, Point-in-Time |
| D05 | Time-Series Econometrics & Statistical Foundations |
| D06 | Volatility & Risk Measurement |
| D07 | Regimes, State Estimation & Change Detection |
| D08 | Alpha Research, Factors & Anomalies |
| D09 | Alternative Data, Text & NLP Signals |
| D10 | Forecasting, Calibration & Uncertainty |
| D11 | Machine Learning in Finance |
| D12 | Reinforcement Learning & Optimal Control |
| D13 | Portfolio Construction & Optimization |
| D14 | Covariance Estimation & Robust Statistics |
| D15 | Risk Management, Tail Risk & Stress |
| D16 | Sizing, Capital Allocation & Leverage |
| D17 | Backtesting, Validation & Overfitting |
| D18 | Simulation, Synthetic Markets & Agent-Based Models |
| D19 | Derivatives: Futures, Perpetuals, Funding & Options |
| D20 | Crypto Market Structure |
| D21 | Venue Mechanics, Order Types & Market Regulation |
| D22 | Operations, Governance, Controls & Compliance |
| D23 | Performance Measurement & Attribution |
| D24 | Decision Theory, Behavioral Finance & Research Epistemology |
| D25 | Trading Systems Engineering |
| D26 | Where to Search: Venues, Journals & Source Types |

---

## D01 — Market Microstructure & the Limit Order Book

- **D01.1 Limit order book (LOB)** — ساختار صف قیمتی پیشنهاد/درخواست و قواعد تطبیق. `q:` "limit order book" dynamics · order book event data · LOB reconstruction. `r:` Gould et al. (2013) *Limit order books*; Bouchaud, Bonart, Donier & Gould (2018).
- **D01.2 Order-driven vs quote-driven markets** — تفاوت بازارهای سفارشمحور و بازارساز-محور و اثرشان بر اطلاعات. `q:` dealer market vs order-driven market quality · market structure comparison. `r:` Madhavan (2000) *Market microstructure: a survey*.
- **D01.3 Quoted, effective and realized spread** — سه تعریف فاصلهٔ خرید-فروش و کاربرد هرکدام. `q:` quoted vs effective spread decomposition · realized spread estimation. `r:` Roll (1984); Huang & Stoll (1997).
- **D01.4 Spread decomposition: order processing, inventory, adverse selection** — اجزای اقتصادی فاصله و سهم اطلاعات نابرابر. `q:` "components of the bid-ask spread" · adverse selection component estimation. `r:` Glosten & Milgrom (1985); Stoll (1989).
- **D01.5 Market depth and book slope** — عمق در هر سطح قیمت و کشش دفتر سفارش. `q:` order book depth elasticity · "book slope" liquidity. `r:` Bouchaud et al. (2018); Cont, Kukanov & Stoikov (2014).
- **D01.6 Microprice / weighted mid** — قیمت میانی وزنی بر پایهٔ عدمتوازن صف. `q:` "micro-price" imbalance fair value · weighted mid price predictability. `r:` Stoikov (2018) *The micro-price*.
- **D01.7 Queue position and queue value** — ارزش اقتصادی جایگاه در صف و مدلسازی آن. `q:` "queue position" limit order value · queueing model limit order book. `r:` Cont & de Larrard (2013); Cartea, Jaimungal & Penalva (2015).
- **D01.8 Tick size and price grid** — حداقل گام قیمت و اثر آن بر نقدینگی و رقابت سفارش. `q:` "tick size" market quality · tick size pilot study evidence. `r:` SEC Tick Size Pilot (2016–2018) evaluation; Harris (1994).
- **D01.9 Price clustering and discreteness** — خوشهشدگی قیمتها روی اعداد خاص و اثر گسستگی. `q:` "price clustering" trading · discrete prices microstructure. `r:` Ball, Torous & Tschoegl (1985); Harris (1991).
- **D01.10 Order arrival intensity and Hawkes processes** — خودبرانگیختگی ورود سفارشها و معاملات. `q:` "Hawkes process" order flow model · self-exciting point process trades. `r:` Hawkes (1971); Bacry, Mastromatteo & Muzy (2015).
- **D01.11 Queue-reactive model** — مدل تصادفی صفهای دفتر سفارش. `q:` "queue-reactive" limit order book simulation. `r:` Huang, Lehalle & Rosenbaum (2015).
- **D01.12 Stochastic order book models** — مدلهای تصادفی حالت دفتر برای قیمتگذاری و شبیهسازی. `q:` "stochastic model for order book dynamics" · diffusion limit order book. `r:` Cont, Stoikov & Talreja (2010).
- **D01.13 Zero-intelligence order book models** — دفتر سفارش بدون عامل هوشمند؛ پایهٔ شبیهسازی. `q:` "zero-intelligence" limit order book model · statistical properties order book. `r:` Smith, Farmer, Gillemot & Krishnamurthy (2003).
- **D01.14 Hidden and iceberg liquidity** — سفارشهای پنهان، اندازهٔ نمایشدادهشده و اثرشان. `q:` "iceberg orders" market quality · "hidden liquidity" empirical. `r:` Hautsch & Huang (2012); Anand & Venkataraman (2013).
- **D01.15 Limit vs market order choice** — نظریهٔ انتخاب نوع سفارش توسط معاملهگر. `q:` "limit versus market order" choice theory · optimal order type submission. `r:` Cohen et al. (1981); Foucault (1999).
- **D01.16 Fleeting liquidity and cancellations** — عمر کوتاه سفارشها و پیامد آن برای نقدینگی. `q:` "fleeting orders" liquidity · order cancellation rates high frequency. `r:` Hasbrouck & Saar (2009); van Kervel (2015).
- **D01.17 Trade classification algorithms** — استنباط سمت معاملهکننده از دادههای معاملات. `q:` "trade classification" Lee-Ready · tick rule bulk classification accuracy. `r:` Lee & Ready (1991); Chakrabarty, Pascual & Shkilko (2007).
- **D01.18 Trade size distribution and volume clocks** — توزیع اندازهٔ معاملات و نمونه‌گیری بر پایهٔ حجم. `q:` "volume clock" sampling · trade size distribution power law. `r:` Easley, López de Prado & O'Hara (2011); Gopikrishnan et al. (2000).
- **D01.19 Price discovery and information share** — سهم هر بازار از کشف قیمت. `q:` "price discovery" "information share" Hasbrouck · Gonzalo-Granger permanent-transitory. `r:` Hasbrouck (1995); Gonzalo & Granger (1995).
- **D01.20 Lead-lag and cross-market information** — تقدم-تأخر میان بازارها و اندازهگیری همبستگی ناهمزمان. `q:` lead-lag cross-market high frequency · Hayashi-Yoshida estimator. `r:` Hayashi & Yoshida (2005); Huth & Abergel (2014).
- **D01.21 Probability of informed trading (PIN), VPIN** — سنجههای احتمال معاملهٔ آگاهانه و سمّیت جریان. `q:` "PIN" probability informed trading estimation · "VPIN" flow toxicity. `r:` Easley, Kiefer, O'Hara & Paperman (1996); Easley, López de Prado & O'Hara (2012).
- **D01.22 Adverse selection cost** — هزینهٔ انتخاب نامطلوب برای تأمینکنندهٔ نقدینگی. `q:` "adverse selection" limit order fill · informed traders liquidity providers. `r:` Copeland & Galai (1983); Glosten & Milgrom (1985).
- **D01.23 Dealer inventory models** — قیمتگذاری بازارساز با ریسک موجودی. `q:` "dealer inventory" pricing model · inventory risk market maker spread. `r:` Ho & Stoll (1981); Amihud & Mendelson (1980).
- **D01.24 Latency and the speed of trading** — اثر تأخیر بر نقدینگی، رقابت و کیفیت بازار. `q:` "low-latency trading" market quality · speed competition limit order book. `r:` Hasbrouck & Saar (2013); Budish, Cramton & Shim (2015).
- **D01.25 Market fragmentation and smart order routing** — تکهتکهشدگی و مسیریابی سفارش. `q:` "smart order routing" fragmentation · market fragmentation price discovery. `r:` Foucault & Menkveld (2008); O'Hara & Ye (2011).
- **D01.26 Dark pools and alternative trading systems (ATS)** — معاملات خارج از دفتر عمومی و اثر اطلاعاتی. `q:` "dark pool" price discovery · ATS trading volume information. `r:` Zhu (2014); Buti, Rindi & Werner (2011).
- **D01.27 Clearing, settlement and central counterparties** — تسویه، ضمانت و ساختار ریسک پایاپای. `q:` central counterparty clearing risk · settlement cycle T+1 market quality. `r:` BIS/CPMI-IOSCO PFMI; Duffie & Zhu (2011).

## D02 — Liquidity, Order Flow & Informed Trading

- **D02.1 Dimensions of liquidity** — تنگness، عمق، بازگشتپذیری و فوریت بهعنوان چهار بُعد جدا. `q:` "dimensions of liquidity" measurement · liquidity definition market microstructure. `r:` Kyle (1985); Sarr & Lybek (2002).
- **D02.2 Amihud illiquidity and variants** — سنجهٔ اثر قیمت بهازای حجم. `q:` "illiquidity and stock returns" Amihud · Amihud measure cross-section. `r:` Amihud (2002).
- **D02.3 Commonality in liquidity** — حرکت همزمان نقدینگی در بازار. `q:` "commonality in liquidity" Chordia · systematic liquidity risk. `r:` Chordia, Roll & Subrahmanyam (2000); Pastor & Stambaugh (2003).
- **D02.4 Funding liquidity vs market liquidity** — تعامل تأمین مالی و نقدینگی بازار. `q:` "market liquidity and funding liquidity" · margin spiral theory. `r:` Brunnermeier & Pedersen (2009).
- **D02.5 Liquidity and margin spirals** — حلقهٔ تشدید افت قیمت و افزایش مارجین. `q:` "margin spiral" deleveraging · liquidity spiral mechanism. `r:` Brunnermeier & Pedersen (2009); BIS (2010).
- **D02.6 Fire sales and forced deleveraging** — فروش اجباری و اثر قیمت آن. `q:` "fire sales" asset prices · forced liquidation price pressure. `r:` Shleifer & Vishny (1992); Coval & Stafford (2007).
- **D02.7 Predatory trading** — سوءاستفادهٔ آگاهانه از وضعیت پرمخاطرهٔ دیگری. `q:` "predatory trading" Brunnermeier Pedersen · front-running distressed traders. `r:` Brunnermeier & Pedersen (2005).
- **D02.8 Stop-loss cascades and liquidity vacuums** — زنجیرهٔ فعالشدن حدضررها و خلأ نقدینگی. `q:` stop-loss cascade liquidity · "stop hunting" empirical evidence. `r:` Osler (2003) currency stop-loss orders; Easley, López de Prado & O'Hara (2011) the microstructure of the flash crash.
- **D02.9 Order-flow toxicity** — ترکیب جریان سفارش از منظر خطر برای تأمینکنندهٔ نقدینگی. `q:` "flow toxicity" measurement · toxic order flow prediction. `r:` Easley, López de Prado & O'Hara (2012).
- **D02.10 Order anticipation and front-running** — پیشدستی روی سفارش بزرگ دیگران. `q:` "order anticipation" institutional orders · detection front-running order flow. `r:` SEC/CFTC enforcement actions; Brunnermeier & Pedersen (2005).
- **D02.11 Spoofing and layering** — سفارشهای جعلی و دستکاری دفتر. `q:` "spoofing" detection market manipulation · layering order book. `r:` CFTC/SEC enforcement actions; Yang, Paddrik, Hayes, Todd, Kirilenko, Beling & Scherer (2012).
- **D02.12 Wash trading and fake volume** — حجم صوری و روشهای تشخیص آن. `q:` "wash trading" detection · fake volume cryptocurrency exchange. `r:` Cong, Li, Tang & Yang (2023); Amiram, Lyandres & Rabetti (2021).
- **D02.13 Momentum ignition and marking the close** — دستکاری برای برانگیختن مومنتوم یا قیمت پایانی. `q:` "momentum ignition" manipulation · "marking the close" evidence. `r:` CFTC/SEC enforcement; Comerton-Forde & Putniņš (2011).
- **D02.14 Liquidity provision as a strategy** — بازارسازی، تخفیف کارمزد و ریسک موجودی. `q:` "liquidity provision" returns · high frequency market making profitability. `r:` Menkveld (2013); Avellaneda & Stoikov (2008).
- **D02.15 Crowded trades and deleveraging** — ازدحام پوزیشنها و ریسک خروج همزمان. `q:` "crowded trades" measurement · hedge fund crowding performance. `r:` Lou & Polk (2022) comomentum; IMF GFSR crowding studies.
- **D02.16 Short interest, borrow and squeezes** — موقعیت فروش استقراضی، قرض و فشار کوتاهشدن. `q:` "short interest" return predictability · short squeeze mechanics. `r:` Asquith, Pathak & Ritter (2005); Boehmer, Jones & Zhang (2008).
- **D02.17 Flow-driven price pressure: index and ETF effects** — فشار تقاضای ناشی از جریان صندوقها و بازآرایی شاخصها. `q:` "index effect" inclusion addition returns · ETF flows price impact. `r:` Shleifer (1986); Ben-David, Franzoni & Moussawi (2018).
- **D02.18 Price–volume relationship** — رابطهٔ حجم و تغییر قیمت، اطلاعاتی یا مکانیکی. `q:` "price-volume" relationship evidence · volume and volatility mixture of distributions. `r:` Karpoff (1987); Clark (1973).
- **D02.19 Trade informativeness and market efficiency measures** — سنجش محتوای اطلاعاتی معاملات. `q:` "information content of trades" Hasbrouck · informed trading measure. `r:` Hasbrouck (1991); Easley & O'Hara (1987).
- **D02.20 Large-order detection from public data** — شناسایی سفارشهای بزرگ از دادههای عمومی. `q:` large order detection trade prints · institutional order identification. `r:` Easley, López de Prado & O'Hara (2012); Bouchaud et al. (2018).

## D03 — Market Impact & Execution

- **D03.1 Implementation shortfall** — شکاف میان بازده تصمیم و بازده اجراشده. `q:` "implementation shortfall" paper versus reality · IS decomposition. `r:` Perold (1988).
- **D03.2 Optimal execution (Almgren–Chriss)** — مسیر بهینهٔ اجرا با مصالحهٔ اثر بازار و ریسک زمانبندی. `q:` "optimal execution of portfolio transactions" · Almgren Chriss closed form. `r:` Almgren & Chriss (2000).
- **D03.3 Temporary vs permanent impact** — تفکیک اثر گذرا و ماندگار و پیامدهای مدلسازی. `q:` "temporary and permanent price impact" · impact decay estimation. `r:` Almgren & Chriss (2000); Bouchaud et al. (2004).
- **D03.4 Square-root law of market impact** — اثر بازار متناسب با جذر نسبت حجم به نقدینگی. `q:` "square root law" market impact · impact universality metaorder. `r:` Tóth et al. (2011); Grinold & Kahn (capacity chapters).
- **D03.5 Transient impact and propagator models** — مدلهای اثر گذرا و پاسخ قیمت به جریان سفارش. `q:` "propagator model" price impact · transient impact kernel estimation. `r:` Bouchaud, Gefen, Potters & Wyart (2004); Bouchaud et al. (2018).
- **D03.6 No-dynamic-arbitrage constraints on impact kernels** — محدودیت تحلیلی بر شکل تابع اثر. `q:` "no-dynamic-arbitrage and market impact" · impact kernel admissibility. `r:` Gatheral (2010); Gatheral, Hansen & Karlsmark (2013).
- **D03.7 Kyle's lambda** — شیب اثر قیمتی سفارش و سنجهٔ نقدینگی/اطلاعات. `q:` "Kyle's lambda" estimation · price impact coefficient estimation. `r:` Kyle (1985).
- **D03.8 Order-flow imbalance (OFI) impact** — رابطهٔ خطی عدمتوازن جریان و بازده کوتاهمدت. `q:` "order flow imbalance" price impact · OFI linear impact model. `r:` Cont, Kukanov & Stoikov (2014).
- **D03.9 Cross-impact between assets** — اثر متقابل معاملات یک دارایی بر دارایی دیگر. `q:` "cross-impact" price impact assets · cross-impact no-dynamic-arbitrage. `r:` Schneider & Lillo (2019); Benzaquen, Mastromatteo, Eisler & Bouchaud (2017).
- **D03.10 Metaorder impact and decay** — برچسب «فرا-سفارش» و شکل اثر آن. `q:` "metaorder" impact decay · large order execution empirical. `r:` Bershova & Rakhlin (2013); Zarinelli et al. (2015).
- **D03.11 Execution algorithms: VWAP, TWAP, POV, IS** — خانوادهٔ الگوریتمهای استاندارد اجرا. `q:` "VWAP algorithm" execution benchmark · "percentage of volume" execution strategy. `r:` Berkowitz, Logue & Noser (1988); Kissell (2013).
- **D03.12 Adaptive execution and limit placement** — تعیین مکان و لحظهٔ سفارش بهصورت پویا. `q:` "limit order placement" optimization · adaptive execution algorithm design. `r:` Guéant (2016) *The Financial Mathematics of Market Liquidity*; Lehalle & Neuman (2019).
- **D03.13 Participation rate and strategy capacity** — سهم بازار و مرز ظرفیت سرمایه. `q:` "strategy capacity" market impact · capacity analysis trading strategy. `r:` Gârleanu & Pedersen (2013); Frazzini, Israel & Moskowitz (2018).
- **D03.14 Execution risk vs timing risk** — مصالحهٔ ریسک اجرا و ریسک تأخیر. `q:` "execution risk" versus "timing risk" · trade-off optimal liquidation. `r:` Almgren & Chriss (2000); Kissell & Glantz (2003).
- **D03.15 Opportunity cost of non-execution** — هزینهٔ سفارشهای پرنشده. `q:` opportunity cost unfilled order execution · non-execution risk measurement. `r:` Perold (1988); Kissell (2013).
- **D03.16 Transaction cost analysis (TCA)** — تجزیهٔ هزینهٔ معامله به اجزا و پایش آن. `q:` "transaction cost analysis" decomposition · TCA implementation practice. `r:` Kissell (2013) *The Science of Algorithmic Trading and Portfolio Management*; Johnson (2010).
- **D03.17 Benchmark choice in execution** — انتخاب معیار اجرا و اثر آن بر تصمیم. `q:` arrival price versus VWAP benchmark · implementation shortfall benchmark choice. `r:` Kissell (2013); Perold (1988).
- **D03.18 Closing auction and imbalance execution** — اجرا در حراج پایانی و سوءاستفاده از عدمتوازن. `q:` closing auction execution strategy · "who trades at the close". `r:` Bogousslavsky & Muravyev (2023); Comerton-Forde & Putniņš (2011).
- **D03.19 Execution in dark venues and information leakage** — اجرا در بازارهای تاریک و ریسک افشا. `q:` "dark pool" execution information leakage · order splitting dark venues. `r:` Zhu (2014); Kratz & Schöneborn (2014).
- **D03.20 Machine learning for execution** — یادگیری ماشین/تقویت برای زمانبندی و مکان سفارش. `q:` "deep reinforcement learning" order execution · machine learning trade scheduling. `r:` Nevmyvaka, Feng & Kearns (2006); Ning, Lin & Jaimungal (2020).
- **D03.21 Market impact of derivatives hedging** — اثر پوشش ریسک با آپشن و فیوچرز بر قیمت پایه. `q:` "delta hedging" price impact · gamma exposure market impact. `r:` Barbon & Buraschi (2021) gamma fragility; Gârleanu, Pedersen & Poteshman (2009) demand-based option pricing.

## D04 — Market Data: Capture, Quality, Point-in-Time

- **D04.1 Market data feeds and message types** — جریان دادهٔ بازار: snapshot، incremental، depth. `q:` market data feed handler architecture · exchange data message types. `r:` FIX Trading Community specs; exchange data manuals.
- **D04.2 Sequence numbers and gap recovery** — تشخیص شکاف پیام و بازیابی وضعیت بازار. `q:` sequence gap detection market data · snapshot plus incremental recovery. `r:` exchange data manuals; ITCH/OUCH specifications.
- **D04.3 Event time vs receive time** — دو مبدأ زمانی داده و پیامد آن برای بکتست. `q:` exchange timestamp versus receive timestamp · event time processing finance. `r:` Aït-Sahalia, Mykland & Zhang (2005); Hasbrouck (2007).
- **D04.4 Clock synchronization (NTP, PTP, IEEE 1588)** — همزمانسازی ساعت و خطای پنهان آن. `q:` "precision time protocol" trading timestamping · clock skew measurement trading. `r:` IEEE 1588; Mills (1991) NTP.
- **D04.5 Tick storage and columnar formats** — ذخیرهسازی دادهٔ tick و فرمتهای ستونی. `q:` "tick data" storage compression · Parquet Apache Arrow financial data. `r:` industry data engineering references; open-source format specs.
- **D04.6 Time-series and analytical databases for markets** — پایگاهدادههای سریزمانی و تحلیلی مناسب دادهٔ بازار. `q:` time-series database comparison trading · kdb+ q language tick database. `r:` kdb+/q documentation; ClickHouse/QuestDB/TimescaleDB documentation.
- **D04.7 Point-in-time (PIT) data and vintages** — دادهٔ «آنگونه که در آن زمان معلوم بود». `q:` "point-in-time" data vintages · real-time macro database ALFRED. `r:` ALFRED/FRED documentation; Compustat PIT methodology notes.
- **D04.8 Bitemporal data modelling** — مدلسازی دو-زمانی (زمان رویداد و زمان ثبت). `q:` "bitemporal" data model finance · slowly changing dimensions audit. `r:` Snodgrass (1999); DAMA-DMBOK.
- **D04.9 Survivorship bias** — سوگیری حذف نمادهای ازمیانرفته از نمونه. `q:` "survivorship bias" performance measurement · delisting bias returns. `r:` Elton, Gruber & Blake (1996); Brown et al. (1992).
- **D04.10 Backfill and look-ahead bias** — سوگیری ناشی از پرکردن گذشته و اطلاع از آینده. `q:` "backfill bias" database returns · "look-ahead bias" detection backtest. `r:` Fung & Hsieh (2000); López de Prado (2018).
- **D04.11 Data snooping and p-hacking in finance** — سوءاستفادهٔ آماری از دادههای موجود. `q:` "data snooping" bootstrap trading rules · p-hacking financial research. `r:` Sullivan, Timmermann & White (1999); Harvey (2017).
- **D04.12 Outlier detection and robust filtering** — شناسایی دادهٔ پرت و صافیهای مقاوم. `q:` Hampel filter outlier detection financial data · robust statistics median absolute deviation. `r:` Huber & Ronchetti (2009); Hampel (1974).
- **D04.13 Missing data and imputation policy** — سیاست برخورد با دادهٔ گمشده و هزینهٔ پرکردن آن. `q:` missing data imputation time series finance · imputation bias trading. `r:` Little & Rubin (2019); López de Prado (2018).
- **D04.14 Corporate actions and price adjustments** — تعدیل قیمت برای رویدادهای شرکتی و معادلهای کریپتو. `q:` corporate action price adjustment methodology · total return index construction. `r:` index-provider methodology documents; CRSP/Compustat guides.
- **D04.15 Data quality dimensions and gates** — ابعاد کیفیت داده و دروازههای کنترلی. `q:` data quality dimensions framework · data quality rules market data validation. `r:` DAMA-DMBOK; BCBS 239.
- **D04.16 Reference data and instrument master** — دادهٔ مرجع، مشخصات قرارداد و شناسنامهٔ ابزار. `q:` instrument master reference data architecture · contract specification management. `r:` FIX/ISO 20022 reference data standards; BCBS 239.
- **D04.17 Symbology and financial identifiers** — سیستمهای شناسه و نگاشت نمادها. `q:` financial instrument identifiers FIGI ISIN symbology mapping · ticker symbol changes handling. `r:` ISO 6166 (ISIN); OMG FIGI standard.
- **D04.18 Alternative data governance and evaluation** — مجوز، ماندگاری، نیمهعمر و شفافیت دادههای جایگزین. `q:` alternative data governance framework · alternative data desirability framework. `r:` Denev & Amen (2020); SEC/ESMA guidance on data vendors.
- **D04.19 Data vendor landscape and market data licensing** — تأمینکنندگان، مجوزها و هزینهٔ توزیع داده. `q:` market data licensing exchange fees · data vendor evaluation trading. `r:` exchange fee schedules; FISD/industry reports.
- **D04.20 Rebuild, replay and reproducibility of datasets** — بازسازی قطعی داده و اثبات یکسانی. `q:` deterministic data pipeline replay finance · dataset versioning reproducibility research. `r:` reproducibility literature (Pimentel et al. 2019); MLOps references.

## D05 — Time-Series Econometrics & Statistical Foundations

- **D05.1 Stationarity and unit-root tests** — ایستایی و آزمونهای ریشهٔ واحد. `q:` augmented Dickey-Fuller unit root test · KPSS Phillips-Perron stationarity. `r:` Dickey & Fuller (1979); Kwiatkowski et al. (1992).
- **D05.2 Spurious regression** — رگرسیون کاذب میان سریهای ناایستا. `q:` "spurious regression" Granger Newbold · cointegration versus spurious regression. `r:` Granger & Newbold (1974).
- **D05.3 Cointegration** — رابطهٔ بلندمدت پایدار میان سریهای ناایستا. `q:` "cointegration" Engle Granger · Johansen cointegration rank test. `r:` Engle & Granger (1987); Johansen (1988).
- **D05.4 ARIMA, ARFIMA and long memory** — مدلهای خودبازگشت و حافظهٔ بلندمدت. `q:` ARFIMA long memory finance · fractional integration estimation. `r:` Granger & Joyeux (1980); Hosking (1981).
- **D05.5 GARCH family** — خانوادهٔ مدلهای نوسان شرطی. `q:` GARCH volatility clustering survey · EGARCH GJR asymmetric volatility. `r:` Engle (1982); Bollerslev (1986); Nelson (1991).
- **D05.6 Stochastic volatility models** — نوسان بهعنوان فرایند پنهان. `q:` stochastic volatility model estimation · Bayesian stochastic volatility Kim Shephard Chib. `r:` Taylor (1986); Kim, Shephard & Chib (1998).
- **D05.7 Realized volatility and realized measures** — اندازهگیری نوسان از دادهٔ پرفرکانس. `q:` "realized volatility" estimation theory · realized variance high frequency. `r:` Andersen & Bollerslev (1998); Barndorff-Nielsen & Shephard (2002).
- **D05.8 HAR and extensions** — مدل سلسلهمراتبی نوسان تحققیافته. `q:` "HAR" realized volatility model · HARQ semivariance extensions. `r:` Corsi (2009); Bollerslev, Patton & Quaedvlieg (2016).
- **D05.9 Jumps and jump tests** — تشخیص پرشها از مسیر قیمت. `q:` jump detection high frequency test · bipower variation Barndorff-Nielsen Shephard. `r:` Barndorff-Nielsen & Shephard (2006); Lee & Mykland (2008).
- **D05.10 Microstructure noise and optimal sampling** — نویز مشاهدهای و فرکانس بهینهٔ نمونهگیری. `q:` "microstructure noise" realized volatility · optimal sampling frequency volatility. `r:` Aït-Sahalia, Mykland & Zhang (2005); Zhang, Mykland & Aït-Sahalia (2005).
- **D05.11 State-space models and Kalman filtering** — مدل حالت-فضا و صافی کالمن. `q:` "Kalman filter" time-varying parameter finance · state space model estimation. `r:` Kalman (1960); Durbin & Koopman (2012).
- **D05.12 Particle filters and sequential Monte Carlo** — صافیهای ذرهای برای مدلهای غیرخطی. `q:` particle filter financial time series · sequential Monte Carlo filtering. `r:` Gordon, Salmond & Smith (1993); Doucet, de Freitas & Gordon (2001).
- **D05.13 Bayesian inference, MCMC and priors** — استنباط بیزی و نمونهگیری زنجیرهٔ مارکوف. `q:` Bayesian inference finance MCMC · Hamiltonian Monte Carlo Neal. `r:` Gelman et al. (2013); Neal (2011).
- **D05.14 Bootstrap methods** — روشهای خودگردان و نسخههای وابسته به دادههای مالی. `q:` bootstrap confidence interval time series · block bootstrap stationary bootstrap. `r:` Efron (1979); Künsch (1989); Politis & Romano (1994).
- **D05.15 Quantile regression** — رگرسیون چندکی و کاربرد در دنبالهٔ توزیع. `q:` quantile regression financial returns · tail regression risk. `r:` Koenker & Bassett (1978).
- **D05.16 Extreme value theory (EVT)** — نظریهٔ مقادیر فرین و مدلسازی دنباله. `q:` "extreme value theory" risk management · peaks over threshold generalized Pareto. `r:` Pickands (1975); McNeil & Frey (2000).
- **D05.17 Copulas and tail dependence** — مدلسازی وابستگی غیرخطی و دنبالهای. `q:` copula tail dependence finance · vine copula portfolio. `r:` Sklar (1959); Embrechts, McNeil & Straumann (2002).
- **D05.18 Dynamic correlation models** — همبستگی متغیر با زمان. `q:` DCC-GARCH dynamic correlation · exponentially weighted covariance RiskMetrics. `r:` Bollerslev (1990); Engle (2002).
- **D05.19 Hurst exponent and long-range dependence** — حافظهٔ بلندمدت و روندپذیری/بازگشتی بودن. `q:` "Hurst exponent" financial time series · rescaled range analysis Lo. `r:` Hurst (1951); Lo (1991).
- **D05.20 Predictive regressions and Stambaugh bias** — سوگیری در رگرسیونهای پیشبین با رگرسور ماندگار. `q:` "Stambaugh bias" predictive regression · return predictability in-sample bias. `r:` Stambaugh (1999); Campbell & Yogo (2006).
- **D05.21 Market-timing tests and sign predictability** — آزمون توان پیشبینی علامت بازده. `q:` market timing test sign predictability · Pesaran Timmermann market timing. `r:` Pesaran & Timmermann (1992); Henriksson & Merton (1981).
- **D05.22 Granger causality and transfer entropy** — جهت اطلاعات میان سریها. `q:` Granger causality financial markets · transfer entropy information flow markets. `r:` Granger (1969); Schreiber (2000).
- **D05.23 Spectral and wavelet analysis** — تحلیل فرکانسی و موجکی سریهای مالی. `q:` wavelet analysis financial volatility · spectral analysis market cycles. `r:` Percival & Walden (2000); Gençay, Selçuk & Whitcher (2001).
- **D05.24 Panel data methods** — دادههای تابلویی برای مقطعی-زمانی. `q:` panel regression fixed effects finance · clustered standard errors panel. `r:` Wooldridge (2010); Petersen (2009).
- **D05.25 HAC and robust standard errors** — خطای استاندارد مقاوم به خودهمبستگی و ناهمسانی. `q:` Newey-West standard errors · HAC covariance estimation. `r:` Newey & West (1987); White (1980).
- **D05.26 High-frequency econometrics** — اقتصادسنجی دادهٔ پرفرکانس و محدودیتهای آن. `q:` high-frequency econometrics survey · Andersen Bollerslev Diebold high frequency. `r:` Aït-Sahalia & Jacod (2014); Andersen et al. (2009).
- **D05.27 Bayesian model comparison and evidence** — مقایسه و انتخاب مدل با شواهد بیزی. `q:` Bayesian model comparison finance · Bayes factor model selection. `r:` Kass & Raftery (1995); Geweke (2005).

## D06 — Volatility & Risk Measurement

- **D06.1 Volatility targeting and scaling** — هدفگذاری نوسان و مقیاسدهی پوزیشن. `q:` "volatility targeting" evidence Sharpe · volatility scaling portfolio. `r:` Harvey et al. (2018); Moreira & Muir (2017).
- **D06.2 Implied vs realized volatility** — تفاوت نوسان ضمنی و تحققیافته و کاربرد آن. `q:` implied versus realized volatility spread · volatility forecast comparison. `r:` Christensen & Prabhala (1998); Busch, Christensen & Nielsen (2011).
- **D06.3 Variance risk premium** — صرف ریسک فروش نوسان. `q:` "variance risk premium" evidence · volatility risk premium harvesting. `r:` Carr & Wu (2009); Bollerslev, Tauchen & Zhou (2009).
- **D06.4 Volatility of volatility and vol-of-vol** — نوسانِ نوسان و اثرش بر قیمتگذاری. `q:` "vol of vol" modeling · VVIX volatility of VIX. `r:` CBOE VVIX methodology; Park (2015) volatility-of-volatility returns.
- **D06.5 Stylized facts of returns** — واقعیتهای تجربی بازده: دنبالهٔ سنگین، خوشهبندی، اثر اهرمی. `q:` "stylized facts" asset returns Cont · empirical properties financial returns. `r:` Cont (2001); Mandelbrot (1963).
- **D06.6 Low-volatility anomaly** — بازده مازاد سهام کم‌نوسان. `q:` "low volatility anomaly" evidence · betting against beta. `r:` Ang, Hodrick, Xing & Zhang (2006); Frazzini & Pedersen (2014).
- **D06.7 Volatility-managed portfolios** — کاهش مواجهه در نوسان بالا. `q:` "volatility-managed portfolios" Moreira Muir · volatility timing evidence. `r:` Moreira & Muir (2017).
- **D06.8 Value at Risk (VaR)** — ارزش در معرض خطر و روشهای محاسبه. `q:` value at risk methodologies comparison · historical simulation VaR critique. `r:` Jorion (2006); Christoffersen (2012).
- **D06.9 VaR backtesting and coverage tests** — آزمون کفایت مدل VaR. `q:` "backtesting value at risk" Kupiec · conditional coverage Christoffersen test. `r:` Kupiec (1995); Christoffersen (1998).
- **D06.10 Expected shortfall (ES) and coherence** — کوتاهترین انتظار دنباله و خصوصیات نظری. `q:` "expected shortfall" coherent risk measure · ES backtesting. `r:` Artzner, Delbaen, Eber & Heath (1999); Acerbi & Tasche (2002).
- **D06.11 CVaR optimization** — بهینهسازی با محدودیت ریسک دنباله. `q:` "conditional value at risk" optimization Rockafellar · CVaR portfolio linear programming. `r:` Rockafellar & Uryasev (2000).
- **D06.12 Drawdown-based risk measures** — معیارهای مبتنی بر افت سرمایه. `q:` "drawdown measure" portfolio optimization · conditional drawdown at risk. `r:` Chekhlov, Uryasev & Zabarankin (2005); Grossman & Zhou (1993).
- **D06.13 Stress testing and scenario analysis** — آزمون فشار و تحلیل سناریو. `q:` stress testing framework portfolios · reverse stress testing. `r:` BIS/FSB stress testing principles; ECB stress test methodology.
- **D06.14 Fat tails and extreme risk modelling** — دنبالهٔ سنگین و مدلسازی ریسک فرین. `q:` fat tails financial returns statistical consequences · Taleb fat tails. `r:` Taleb (2020); Embrechts, Klüppelberg & Mikosch (1997).
- **D06.15 Tail risk hedging** — پوشش ریسک دنباله با ابزار مشتقه. `q:` tail risk hedging cost benefit · tail hedging program design. `r:` Bhansali & Davis (2010); Ilmanen (2011).
- **D06.16 Correlation breakdown and contagion** — شکست همبستگیها در بحران و سرایت. `q:` "correlation breakdown" crisis · contagion financial markets measurement. `r:` Longin & Solnik (2001); Forbes & Rigobon (2002).
- **D06.17 Liquidity-adjusted risk measures** — واردکردن ریسک نقدینگی در سنجههای ریسک. `q:` liquidity adjusted value at risk · liquidity risk measurement portfolio. `r:` Bangia, Diebold, Schuermann & Stroughair (1999); Amihud (2002).
- **D06.18 Margin models and procyclicality** — مدلهای مارجین، SPAN و اثر چرخهای. `q:` SPAN margin methodology · margin procyclicality BIS. `r:` CME SPAN documentation; BIS (2010) *The role of margin requirements and haircuts in procyclicality*.
- **D06.19 Risk decomposition and contribution** — تجزیهٔ ریسک پرتفوی به سهم اجزا. `q:` risk contribution decomposition portfolio · marginal contribution to risk. `r:` Roncalli (2013); Meucci (2009).
- **D06.20 Model risk** — ریسک خطای مدل و مدیریت آن. `q:` "model risk management" SR 11-7 · model validation framework banks. `r:` Federal Reserve SR 11-7 (2011); OCC 2011-12.

## D07 — Regimes, State Estimation & Change Detection

- **D07.1 Markov-switching models** — مدلهای تغییر رژیم با زنجیرهٔ مارکوف. `q:` "Markov switching" model Hamilton · regime switching volatility estimation. `r:` Hamilton (1989); Kim & Nelson (1999).
- **D07.2 Hidden Markov models (HMM)** — مدل پنهان گسسته و استنتاج وضعیت. `q:` "hidden Markov model" market regime · Baum-Welch forward-backward algorithm. `r:` Baum & Petrie (1966); Rabiner (1989).
- **D07.3 Filtered vs smoothed state probabilities** — تفاوت اطلاعات لحظهای و گذشتهنگر در حالت. `q:` filtered versus smoothed regime probabilities · online state inference caution. `r:` Hamilton (1994); Kim & Nelson (1999).
- **D07.4 Regime-based asset allocation** — تخصیص دارایی وابسته به رژیم. `q:` regime based asset allocation evidence · regime switching portfolio choice. `r:` Ang & Bekaert (2002); Guidolin & Timmermann (2007).
- **D07.5 Change-point detection (CUSUM, PELT, BOCPD)** — تشخیص نقطهٔ تغییر بهصورت برخط و پسرو. `q:` "change point detection" algorithms survey · Bayesian online changepoint detection. `r:` Page (1954); Killick, Fearnhead & Eckley (2012); Adams & MacKay (2007).
- **D07.6 Structural break tests** — آزمونهای شکست ساختاری در پارامترها. `q:` structural break test Bai Perron · Chow test parameter stability. `r:` Chow (1960); Bai & Perron (1998).
- **D07.7 Statistical process control (SPC) and monitoring** — نمودارهای کنترل و تشخیص انحراف فرایند. `q:` statistical process control trading monitoring · EWMA control chart. `r:` Montgomery (2019) *Introduction to Statistical Quality Control*.
- **D07.8 Regime uncertainty and entropy** — عدمقطعیت وضعیت و کوچکسازی در ابهام. `q:` regime uncertainty entropy allocation · model uncertainty shrinkage. `r:` Ang & Timmermann (2012); Hansen & Sargent (2008).
- **D07.9 Trend vs mean-reversion regime indicators** — سنجههای تفکیک رژیم روندی و بازگشتی. `q:` variance ratio test regime · Hurst exponent regime classification. `r:` Lo & MacKinlay (1988); Lo (1991).
- **D07.10 Turbulence and systemic-risk indices** — شاخصهای آشفتگی و ریسک سیستمی. `q:` "financial turbulence" Kritzman index · absorption ratio systemic risk. `r:` Kritzman & Li (2010); Kritzman, Li, Page & Rigobon (2011).
- **D07.11 Connectedness and spillover measures** — سرریز نوسان و بازده میان بازارها. `q:` volatility connectedness Diebold Yilmaz · spillover index framework. `r:` Diebold & Yılmaz (2014); Diebold & Yılmaz (2012).
- **D07.12 Clustering of market states** — خوشهبندی حالتهای بازار بدون برچسب. `q:` clustering market regimes machine learning · unsupervised regime detection. `r:` Nystrup, Madsen & Lindström (2017); Hamilton (2016) macroeconomic regimes and regime shifts.

## D08 — Alpha Research, Factors & Anomalies

- **D08.1 CAPM and multi-factor models** — مدلهای عاملی قیمتگذاری دارایی. `q:` Fama-French five factor model · multifactor model specification. `r:` Sharpe (1964); Fama & French (1993, 2015).
- **D08.2 Cross-sectional momentum** — مومنتوم در مقطع داراییها. `q:` "returns to buying winners and selling losers" · cross-sectional momentum evidence. `r:` Jegadeesh & Titman (1993); Carhart (1997).
- **D08.3 Time-series momentum and trend following** — مومنتوم سریزمانی و پیروی روند. `q:` "time series momentum" Moskowitz Ooi Pedersen · century of evidence trend following. `r:` Moskowitz, Ooi & Pedersen (2012); Hurst, Ooi & Pedersen (2017).
- **D08.4 Momentum crashes and dynamic momentum** — فروپاشی مومنتوم و مدیریت ریسک آن. `q:` "momentum crashes" Daniel Moskowitz · momentum has its moments. `r:` Daniel & Moskowitz (2016); Barroso & Santa-Clara (2015).
- **D08.5 Value and value-momentum combination** — ارزش، ترکیب آن با مومنتوم در همهجا. `q:` "value and momentum everywhere" · value factor implementation choices. `r:` Asness, Moskowitz & Pedersen (2013); Fama & French (1998).
- **D08.6 Carry** — صرف حمل و ساختار ترم. `q:` "carry" Koijen Moskowitz Pedersen Vrugt · carry across asset classes. `r:` Koijen, Moskowitz, Pedersen & Vrugt (2018).
- **D08.7 Betting against beta and leverage constraints** — صرف بتا و محدودیت اهرم. `q:` "betting against beta" · leverage constraints anomaly. `r:` Frazzini & Pedersen (2014).
- **D08.8 Quality, profitability and investment factors** — کیفیت، سودآوری و سرمایهگذاری. `q:` "quality minus junk" · profitability factor Novy-Marx. `r:` Novy-Marx (2013); Asness, Frazzini & Pedersen (2019).
- **D08.9 Short-term reversal and liquidity provision** — بازگشت کوتاهمدت و چرخهٔ نقدینگی. `q:` short-term reversal returns Nagel · liquidity provision returns reversal. `r:` Lehmann (1990); Nagel (2012).
- **D08.10 Long-term reversal and overreaction** — بازگشت بلندمدت و بیشواکنشی. `q:` "does the stock market overreact" · long-term reversal evidence. `r:` De Bondt & Thaler (1985).
- **D08.11 Seasonality and calendar anomalies** — الگوهای فصلی و تقویمی. `q:` stock market seasonality evidence · "Halloween indicator" sell in May. `r:` Rozeff & Kinney (1976); Bouman & Jacobsen (2002).
- **D08.12 Post-earnings announcement drift (PEAD)** — دریفت پس از اعلام سود. `q:` "post-earnings announcement drift" · earnings surprise drift persistence. `r:` Bernard & Thomas (1989); Ball & Brown (1968).
- **D08.13 Accruals, earnings quality and fundamentals** — اقلام تعهدی و کیفیت سود. `q:` "accruals anomaly" Sloan · earnings quality replication. `r:` Sloan (1996); Green, Hand & Zhang (2017).
- **D08.14 Analyst revisions and expectations data** — بازنگری تحلیلگران و دادهٔ انتظارات. `q:` analyst revision return predictability · recommendation changes performance. `r:` Womack (1996); Jegadeesh, Kim, Krische & Lee (2004).
- **D08.15 Sentiment and attention measures** — سنجههای احساسات و توجه بازار. `q:` investor sentiment index Baker Wurgler · "in search of attention" search volume. `r:` Baker & Wurgler (2006); Da, Engelberg & Gao (2011).
- **D08.16 The factor zoo, multiplicity and replication** — انبوه عوامل و بحران تکرارپذیری. `q:` "factor zoo" multiple testing · "replicating anomalies" Hou Xue Zhang · replication crisis finance. `r:` Harvey, Liu & Zhu (2016); Hou, Xue & Zhang (2020); Jensen, Kelly & Pedersen (2023).
- **D08.17 Factor timing** — زمانبندی عوامل و ظرفیت آن. `q:` "factor timing" difficulty evidence · factor momentum and timing. `r:` Asness (2016); Haddad, Kozak & Santosh (2020).
- **D08.18 Anomaly decay after publication** — افت اثر آنومالی پس از انتشار. `q:` "does academic research destroy stock return predictability" · anomaly decay post publication. `r:` McLean & Pontiff (2016).
- **D08.19 Statistical arbitrage** — آربیتراژ آماری و سبدهای مقطعی. `q:` "statistical arbitrage" survey · statistical arbitrage US equities Avellaneda Lee. `r:` Gatev, Goetzmann & Rouwenhorst (2006); Avellaneda & Lee (2010); Krauss (2017).
- **D08.20 Pairs trading and relative value** — معاملات جفتی و ارزش نسبی. `q:` pairs trading performance · Ornstein-Uhlenbeck pairs trading optimal. `r:` Elliott, van der Hoek & Malcolm (2005); Do & Faff (2010).
- **D08.21 Fundamental law of active management** — رابطهٔ مهارت، گستردگی و محدودیتها. `q:` "fundamental law of active management" · transfer coefficient theory. `r:` Grinold (1989); Clarke, de Silva & Thorley (2002).
- **D08.22 Alpha decay and signal half-life** — نیمهعمر سیگنال و افق بهرهبرداری. `q:` alpha decay horizon trading signal · signal half-life estimation. `r:` Grinold & Kahn (2000); Chinco, Clark-Joseph & Ye (2019).
- **D08.23 Capacity, scalability and impact of size** — ظرفیت استراتژی و اثر بزرگشدن. `q:` capacity of trading strategies · diseconomies of scale hedge funds. `r:` Frazzini, Israel & Moskowitz (2018); Gârleanu & Pedersen (2016).
- **D08.24 Machine-learned factors** — عوامل استخراجشده با یادگیری ماشین. `q:` "empirical asset pricing via machine learning" · "taming the factor zoo". `r:` Gu, Kelly & Xiu (2020); Feng, Giglio & Xiu (2020).
- **D08.25 Option-implied return signals** — سیگنالهای بازده از بازار آپشن. `q:` option implied volatility return predictability · volatility smirk future returns. `r:` Xing, Zhang & Zhao (2010); Bali & Murray (2013).
- **D08.26 Flow-based signals** — سیگنالهای مبتنی بر جریان وجوه و موقعیتها. `q:` mutual fund flow return predictability · ETF flow price impact. `r:` Coval & Stafford (2007); Ben-David, Franzoni & Moussawi (2018).

## D09 — Alternative Data, Text & NLP Signals

- **D09.1 Alternative data landscape** — طبقهبندی دادههای جایگزین و زنجیرهٔ ارزش. `q:` alternative data taxonomy asset management · alt data landscape survey. `r:` Denev & Amen (2020).
- **D09.2 Web scraping and panel data** — استخراج وب و دادهٔ پنلی مصرفکننده. `q:` web scraping alternative data alpha · credit card panel data signals. `r:` industry case studies; SEC enforcement on scraping.
- **D09.3 Geospatial and satellite imagery** — تصاویر ماهوارهای و دادهٔ مکانی. `q:` satellite imagery hedge fund alpha · geospatial data commodity forecasting. `r:` industry studies (e.g. parking lot, oil storage).
- **D09.4 Shipping and supply-chain data** — دادهٔ حملونقل و زنجیرهٔ تأمین. `q:` AIS shipping data trading signals · supply chain disruption nowcasting. `r:` commodity nowcasting literature.
- **D09.5 Internet search data** — دادهٔ جستوجوی اینترنتی بهعنوان توجه/تقاضا. `q:` Google Trends stock returns · search volume market attention. `r:` Da, Engelberg & Gao (2011); Preis, Moat & Stanley (2013).
- **D09.6 Social media sentiment** — احساسات شبکههای اجتماعی. `q:` "Twitter mood predicts the stock market" · social media sentiment trading. `r:` Bollen, Mao & Zeng (2011); Renault (2017).
- **D09.7 News analytics and machine-readable news** — خبر، سرعت و واکنش قیمت. `q:` machine readable news trading strategies · news sentiment price reaction latency. `r:` Tetlock (2007); Tetlock, Saar-Tsechansky & Macskassy (2008).
- **D09.8 NLP for finance: embeddings and transformers** — متون مالی و مدلهای زبانی. `q:` FinBERT financial sentiment · large language models financial text. `r:` Araci (2019); Yang, UY & Huang (2020).
- **D09.9 Earnings calls and disclosure tone** — لحن و محتوای تماسهای سوددهی. `q:` earnings call tone deception detection · textual analysis conference calls. `r:` Larcker & Zakolyukina (2012); Hassan et al. (2019).
- **D09.10 Filings analysis and document similarity** — تحلیل صورتهای مالی و شباهت اسناد. `q:` "lazy prices" 10-K changes · textual similarity annual reports returns. `r:` Cohen, Malloy & Nguyen (2020); Loughran & McDonald (2011).
- **D09.11 Event extraction and entity linking** — استخراج رویداد و پیوند موجودیتها. `q:` event extraction financial text · entity linking news securities. `r:` NLP/IE conference literature (ACL/EMNLP finance tracks).
- **D09.12 Data decay, exclusivity and crowding in alt data** — افت ارزش داده و ازدحام مصرفکنندگان. `q:` alternative data decay half-life · data exclusivity alpha decay. `r:` industry practitioner studies.

## D10 — Forecasting, Calibration & Uncertainty

- **D10.1 Forecast evaluation and comparison tests** — آزمون برتری پیشبینیها. `q:` Diebold-Mariano test forecast comparison · Giacomini-White conditional predictive ability. `r:` Diebold & Mariano (1995); Giacomini & White (2006).
- **D10.2 Proper scoring rules** — قواعد نمرهدهی درست برای احتمال و چگالی. `q:` "strictly proper scoring rules" Gneiting Raftery · Brier score log score. `r:` Gneiting & Raftery (2007); Brier (1950).
- **D10.3 Reliability, resolution and calibration plots** — تشخیص اینکه «۷۰٪» واقعاً یعنی ۷۰٪. `q:` reliability diagram Murphy decomposition · calibration curve classifier. `r:` Murphy (1973); Niculescu-Mizil & Caruana (2005).
- **D10.4 Probability calibration methods** — پلات، ایزوتونیک و مقیاسدهی دما. `q:` Platt scaling isotonic regression calibration · temperature scaling neural networks. `r:` Platt (1999); Zadrozny & Elkan (2002); Guo et al. (2017).
- **D10.5 Conformal prediction and distribution-free intervals** — بازههای معتبر بدون فرض توزیعی. `q:` "conformal prediction" time series · distribution-free predictive inference. `r:` Vovk, Gammerman & Shafer (2005); Lei et al. (2018).
- **D10.6 Forecast combination** — ترکیب پیشبینیها و بهینهسازی وزنها. `q:` "forecast combinations" Timmermann survey · combination weights estimation. `r:` Bates & Granger (1969); Timmermann (2006).
- **D10.7 Bayesian model averaging and shrinkage of forecasts** — میانگینگیری مدل و انقباض پیشبینی. `q:` Bayesian model averaging forecasting · shrinkage forecast weighting. `r:` Raftery, Madigan & Hoeting (1997); Diebold & Shin (2019).
- **D10.8 Return predictability and its fragility** — پیشبینیپذیری بازده و شکنندگی آن. `q:` "comprehensive look at the empirical performance of equity premium prediction" · return predictability out-of-sample failure. `r:` Welch & Goyal (2008); Goyal, Welch & Zafirov (2024).
- **D10.9 Forecast horizons and information decay** — افق پیشبینی و افت اطلاعات با زمان. `q:` forecasting horizon information decay · short versus long horizon predictability. `r:` Grinold & Kahn (2000); Chinco, Clark-Joseph & Ye (2019).
- **D10.10 Nowcasting and mixed-frequency models** — اکنوننگری و دادهٔ با فرکانس متفاوت. `q:` "nowcasting" Giannone Reichlin Small · MIDAS mixed data sampling. `r:` Giannone, Reichlin & Small (2008); Ghysels, Santa-Clara & Valkanov (2004).
- **D10.11 Density forecasts and predictive distributions** — پیشبینی توزیع کامل بهجای نقطه. `q:` density forecast evaluation Berkowitz · predictive distribution finance. `r:` Berkowitz (2001); Diebold, Gunther & Tay (1998).
- **D10.12 Model confidence sets** — مجموعهٔ مدلهای قابل اعتماد. `q:` "model confidence set" Hansen Lunde Nason · superior set of models. `r:` Hansen, Lunde & Nason (2011).
- **D10.13 Uncertainty quantification and prediction intervals** — کمّیسازی عدمقطعیت پیشبینی. `q:` prediction intervals machine learning finance · epistemic versus aleatoric uncertainty. `r:` Kendall & Gal (2017); Meinshausen (2006) quantile forests.
- **D10.14 Value of information and experiment design** — ارزش اطلاعات و طراحی آزمون. `q:` "value of information" decision analysis · experiment design finance. `r:` Howard (1966); Gelman et al. (2013).

## D11 — Machine Learning in Finance

- **D11.1 Supervised learning for return prediction** — پیشبینی بازده با یادگیری نظارتشده. `q:` machine learning asset pricing survey · cross-sectional return prediction ML. `r:` Gu, Kelly & Xiu (2020); Kelly & Xiu (2023).
- **D11.2 Regularization: ridge, lasso, elastic net, group lasso** — جریمههای پارامتری و انتخاب ویژگی. `q:` elastic net high-dimensional finance · group lasso factor selection. `r:` Tibshirani (1996); Zou & Hastie (2005); Yuan & Lin (2006).
- **D11.3 Tree ensembles: random forests, boosting** — جنگل تصادفی و تقویت گرادیانی. `q:` gradient boosting tabular finance · random forest return prediction. `r:` Breiman (2001); Chen & Guestrin (2016); Ke et al. (2017).
- **D11.4 Feature importance and SHAP** — اهمیت ویژگی و تفسیر مدل. `q:` SHAP values finance interpretability · feature importance pitfalls correlated. `r:` Lundberg & Lee (2017); Strobl et al. (2007).
- **D11.5 Deep learning on tabular data** — یادگیری عمیق روی دادهٔ جدولی. `q:` why tree-based models outperform deep learning tabular · tabular deep learning benchmark. `r:` Grinsztajn, Oyallon & Varoquaux (2022); Gorishniy et al. (2021).
- **D11.6 Sequence models for order books (DeepLOB-type)** — مدلهای توالی برای دفتر سفارش. `q:` "DeepLOB" limit order book deep learning · CNN LSTM order book prediction. `r:` Zhang, Zohren & Roberts (2019); Sirignano & Cont (2019).
- **D11.7 Autoencoders and factor extraction** — استخراج عاملهای پنهان. `q:` autoencoder asset pricing models · conditional factor model neural network. `r:` Gu, Kelly & Xiu (2021); Kelly, Pruitt & Su (2019).
- **D11.8 Representation learning for assets** — بازنمایی داراییها و شباهت آنها. `q:` asset embeddings representation learning finance · similarity learning securities. `r:` machine learning finance conference literature.
- **D11.9 Graph neural networks for markets** — شبکههای گرافی برای روابط داراییها. `q:` graph neural network stock prediction · relational modeling financial markets GNN. `r:` Feng et al. (2019); Chen, Wei & Huang (2018).
- **D11.10 Transfer learning and pretraining in finance** — انتقال دانش بین بازارها و دورانها. `q:` transfer learning financial time series · domain adaptation regime shift. `r:` Pan & Yang (2010); finance applications literature.
- **D11.11 Meta-learning and few-shot adaptation** — یادگیری سریع در رژیمهای نو. `q:` meta-learning time series finance · few-shot learning market regimes. `r:` Hospedales et al. (2021); Finn, Abbeel & Levine (2017).
- **D11.12 Causal inference and double machine learning** — استنباط علّی و یادگیری ماشین دوگانه. `q:` double machine learning causal finance · causal inference asset prices. `r:` Chernozhukov et al. (2018); Athey & Imbens (2019).
- **D11.13 Data leakage in ML pipelines** — نشتی اطلاعات در خط لوله و اثر آن بر نتایج. `q:` "leakage in data mining" · target leakage cross-validation финансовые. `r:` Kaufman, Rosset & Perlich (2012); López de Prado (2018).
- **D11.14 Hyperparameter tuning and nested cross-validation** — تنظیم فراپارامتر و اعتبارسنجی تودرتو. `q:` nested cross-validation model selection bias · hyperparameter optimization overfitting finance. `r:` Cawley & Talbot (2010); Bergstra & Bengio (2012).
- **D11.15 Deep hedging** — پوشش ریسک با شبکههای عصبی. `q:` "deep hedging" Buehler · neural network hedging derivatives. `r:` Buehler, Gonon, Teichmann & Wood (2019).
- **D11.16 Generative models for market data** — تولید دادهٔ مصنوعی بازار. `q:` "Quant GANs" financial time series generation · diffusion models market data. `r:` Wiese et al. (2020); Ni et al. (2020) Sig-Wasserstein GANs.
- **D11.17 Model selection under non-stationarity** — انتخاب مدل در شرایط ناپایا. `q:` model selection non-stationary financial data · rolling window model selection. `r:` Pesaran & Timmermann (2002); Inoue, Jin & Rossi (2017).
- **D11.18 Explainability and regulatory expectations for ML models** — تفسیرپذیری و انتظارات ناظران. `q:` explainable AI financial services regulation · model documentation machine learning finance. `r:` SR 11-7; EU AI Act risk management provisions; Mitchell et al. (2019) model cards.

## D12 — Reinforcement Learning & Optimal Control

- **D12.1 Markov decision processes for trading** — صورت‌بندی MDP برای معامله و اجرا. `q:` Markov decision process trading formulation · state action reward trading. `r:` Sutton & Barto (2018); Bertsekas (2012).
- **D12.2 Value-based and policy-gradient RL** — روشهای مقدارمحور و گرادیان سیاست. `q:` policy gradient methods trading · DQN deep reinforcement learning finance. `r:` Mnih et al. (2015); Schulman et al. (2017).
- **D12.3 RL for optimal execution** — یادگیری تقویتی برای اجرای بهینه. `q:` "reinforcement learning for optimized trade execution" · RL liquidation scheduling. `r:` Nevmyvaka, Feng & Kearns (2006); Ning, Lin & Jaimungal (2020).
- **D12.4 RL for market making** — یادگیری تقویتی برای بازارسازی. `q:` reinforcement learning market making limit order book · inventory control RL. `r:` Chan & Shelton (2001); Spooner, Fearnley, Savani & Koukorinis (2018).
- **D12.5 RL for portfolio allocation** — تخصیص پرتفوی با یادگیری تقویتی. `q:` deep reinforcement learning portfolio management · RL asset allocation. `r:` Jiang, Xu & Liang (2017); Kolm & Ritter (2019).
- **D12.6 Offline / batch RL** — یادگیری تقویتی خارج از خط و ریسکهای آن. `q:` "offline reinforcement learning" tutorial · batch RL finance evaluation. `r:` Levine, Kumar, Tucker & Fu (2020).
- **D12.7 Sim-to-real gap in trading RL** — فاصلهٔ محیط شبیهسازی و بازار واقعی. `q:` sim-to-real transfer reinforcement learning trading · environment fidelity RL finance. `r:` RL-finance workshop literature; ABIDES-based studies.
- **D12.8 Optimal stopping and timing problems** — مسائل توقف بهینه در معاملات. `q:` optimal stopping trading strategy · American option stopping theory application. `r:` Dixit & Pindyck (1994); Bertsekas (2005).
- **D12.9 Stochastic control and dynamic programming** — کنترل تصادفی و برنامهریزی پویا. `q:` stochastic control portfolio Merton · Hamilton-Jacobi-Bellman numerical solution. `r:` Merton (1971); Fleming & Soner (2006).
- **D12.10 Transaction costs in dynamic portfolio problems** — هزینهٔ معامله در مسائل پویا. `q:` dynamic portfolio choice transaction costs · no-trade region optimal. `r:` Magill & Constantinides (1976); Gârleanu & Pedersen (2013).
- **D12.11 Inverse RL and imitation of order flow** — یادگیری از رفتار مشاهدهشده. `q:` inverse reinforcement learning market participants · imitation learning trading. `r:` Ng & Russell (2000); finance applications literature.
- **D12.12 Evaluation of RL policies in markets** — ارزیابی سیاستها بدون امکان آزمون مکرر. `q:` off-policy evaluation finance · counterfactual evaluation trading strategies. `r:` Precup, Sutton & Singh (2000); Thomas & Brunskill (2016).

## D13 — Portfolio Construction & Optimization

- **D13.1 Mean-variance optimization** — بهینهسازی میانگین-واریانس و بحران خطای برآورد. `q:` "portfolio selection" Markowitz · estimation error portfolio optimization Michaud. `r:` Markowitz (1952); Michaud (1989).
- **D13.2 Black–Litterman model** — تلفیق دیدگاهها با تعادل بازار. `q:` "Black-Litterman" model implementation · prior views portfolio Bayesian. `r:` Black & Litterman (1992); Idzorek (2004).
- **D13.3 Robust portfolio optimization** — بهینهسازی مقاوم نسبت به خطای پارامتر. `q:` "robust portfolio optimization" uncertainty sets · worst-case portfolio allocation. `r:` Goldfarb & Iyengar (2003); Tütüncü & Koenig (2004).
- **D13.4 Resampled efficiency** — بازنمونهگیری بهینهسازی برای پایداری وزنها. `q:` resampled efficiency portfolio · Michaud resampling implementation. `r:` Michaud (1998).
- **D13.5 Risk parity and equal risk contribution** — برابری ریسک و سهم برابر ریسک. `q:` "risk parity" controversy · equal risk contribution portfolio properties. `r:` Maillard, Roncalli & Teïletche (2010); Asness, Frazzini & Pedersen (2012).
- **D13.6 Hierarchical risk parity (HRP)** — خوشهبندی سلسلهمراتبی و تخصیص بدون وارون ماتریس. `q:` "building diversified portfolios that outperform out of sample" · hierarchical clustering allocation. `r:` López de Prado (2016).
- **D13.7 Maximum diversification and minimum variance** — تنوع حداکثری و واریانس حداقلی. `q:` "toward maximum diversification" · minimum variance portfolio anomaly. `r:` Choueifaty & Coignard (2008); Clarke, de Silva & Thorley (2011).
- **D13.8 Turnover-penalized optimization** — جریمهٔ گردش در بهینهسازی پویا. `q:` "dynamic trading with predictable returns and transaction costs" · turnover penalty portfolio. `r:` Gârleanu & Pedersen (2013); Gârleanu & Pedersen (2016).
- **D13.9 Multi-period convex portfolio optimization** — بهینهسازی چنددورهای مقید محدب. `q:` "multi-period trading via convex optimization" · convex optimization trading Boyd. `r:` Boyd, Busseti, Diamond et al. (2017).
- **D13.10 Convex optimization foundations for portfolios** — ابزارهای محدب و حلکنندهها. `q:` convex optimization applications finance · disciplined convex programming CVXPY. `r:` Boyd & Vandenberghe (2004); Diamond & Boyd (2016).
- **D13.11 Integer and cardinality constraints** — محدودیتهای گسسته و تعداد دارایی. `q:` cardinality constrained portfolio optimization · mixed integer portfolio optimization. `r:` Bertsimas & Shioda (2009); Chang et al. (2000).
- **D13.12 Bayesian portfolio choice and estimation risk** — انتخاب پرتفوی بیزی با ریسک برآورد. `q:` Bayes-Stein estimation portfolio · parameter uncertainty portfolio choice. `r:` Jorion (1986); Kan & Zhou (2007).
- **D13.13 Factor risk models in optimization** — مدلهای ریسک عاملی (Barra-style). `q:` Barra risk model construction · fundamental factor risk model optimization. `r:` Grinold & Kahn (2000); Connor (1995).
- **D13.14 Naive diversification and 1/N benchmarks** — تنوع ساده و معیار ۱/N. `q:` "optimal versus naive diversification" · 1/N portfolio performance. `r:` DeMiguel, Garlappi & Uppal (2009).
- **D13.15 Correlation clustering and network-based allocation** — خوشهبندی داراییها بر پایهٔ همبستگی. `q:` correlation clustering assets portfolio · network based portfolio construction. `r:` Mantegna (1999); Tola et al. (2008).
- **D13.16 Kelly portfolios and growth-optimal allocation** — پرتفوی رشد بهینه و کسر کلی. `q:` Kelly criterion portfolio continuous time · growth optimal portfolio. `r:` Kelly (1956); MacLean, Thorp & Ziemba (2011).
- **D13.17 Portfolio insurance and CPPI** — بیمهٔ پرتفوی و پوشش پویا. `q:` "constant proportion portfolio insurance" · portfolio insurance strategies comparison. `r:` Black & Jones (1987); Perold & Sharpe (1988).
- **D13.18 Multi-strategy capital allocation** — تخصیص سرمایه میان استراتژیها. `q:` multi-strategy allocation framework · capital allocation across trading strategies. `r:` Grinold & Kahn (2000); Roncalli (2013); Gârleanu & Pedersen (2016).
- **D13.19 Constraints, leverage limits and regulatory capital** — قیود، سقف اهرم و سرمایهٔ نظارتی. `q:` leverage constraints portfolio choice · margin requirements portfolio implementation. `r:` Frazzini & Pedersen (2012); Basel/FRTB margin frameworks.
- **D13.20 Turnover, rebalancing and implementation shortfall of allocation** — گردش، بازآرایی و هزینهٔ اجرای آن. `q:` rebalancing frequency performance · turnover cost portfolio implementation. `r:` Perold & Sharpe (1988); Gârleanu & Pedersen (2013).

## D14 — Covariance Estimation & Robust Statistics

- **D14.1 Sample covariance pathologies** — مشکلات ماتریس کوواریانس نمونهای در بُعد بالا. `q:` sample covariance estimation error large N · ill-conditioned covariance portfolio. `r:` Michaud (1989); Ledoit & Wolf (2004).
- **D14.2 Random matrix theory cleaning** — پاکسازی با نظریهٔ ماتریس تصادفی. `q:` "noise dressing of financial correlation matrices" · Marchenko-Pastur eigenvalue distribution finance. `r:` Laloux, Cizeau, Bouchaud & Potters (1999); Plerou et al. (2002).
- **D14.3 Ledoit–Wolf shrinkage** — انقباض تحلیلی کوواریانس. `q:` "honey I shrunk the sample covariance matrix" · nonlinear shrinkage covariance Ledoit Wolf. `r:` Ledoit & Wolf (2003, 2004, 2017, 2020).
- **D14.4 Factor-model covariance** — کوواریانس بر پایهٔ مدل عاملی. `q:` single index model covariance Sharpe · factor model covariance estimation. `r:` Sharpe (1963); Connor & Korajczyk (1993).
- **D14.5 Exponentially weighted and DCC covariance** — کوواریانس وزنی و پویا. `q:` exponentially weighted moving average covariance · DCC covariance forecasting. `r:` RiskMetrics (1996); Engle (2002).
- **D14.6 Robust covariance estimation** — برآورد مقاوم در برابر دادهٔ پرت. `q:` robust covariance estimation finance · minimum covariance determinant. `r:` Rousseeuw & Van Driessen (1999); Huber & Ronchetti (2009).
- **D14.7 Positive-definiteness repair** — ترمیم ماتریس نامعین مثبت. `q:` nearest positive semidefinite matrix Higham · correlation matrix repair. `r:` Higham (1988); Rebonato & Jäckel (1999).
- **D14.8 Sparse covariance and graphical models** — کوواریانس تُنُک و مدلهای گرافی. `q:` graphical lasso covariance estimation · sparse precision matrix finance. `r:` Friedman, Hastie & Tibshirani (2008); Meinshausen & Bühlmann (2006).
- **D14.9 Implied covariance and implied correlations** — کوواریانس و همبستگی استخراجشده از بازار مشتقه. `q:` option implied correlation index · implied covariance matrix extraction. `r:` CBOE implied correlation index methodology; Driessen, Maenhout & Vilkov (2009).
- **D14.10 Non-stationarity and regime-dependent covariance** — ناپایداری کوواریانس در رژیمها. `q:` time-varying covariance regimes · regime dependent correlation. `r:` Ang & Chen (2002); Pelletier (2006).
- **D14.11 Shrinkage toward structured targets** — انقباض به سمت هدفهای ساختاریافته. `q:` shrinkage target covariance matrix choice · shrinkage toward factor model. `r:` Ledoit & Wolf (2003); Schäfer & Strimmer (2005).
- **D14.12 Estimation of higher moments** — برآورد گشتاورهای سوم و چهارم. `q:` coskewness cokurtosis estimation · higher moment portfolio optimization. `r:` Harvey & Siddique (2000); Jondeau & Rockinger (2006).

## D15 — Risk Management, Tail Risk & Stress

- **D15.1 Risk limits and limit hierarchies** — ساختار سلسلهمراتبی حدود ریسک. `q:` risk limit framework trading desk · limit hierarchy implementation. `r:` industry risk policy references; Basel market risk framework.
- **D15.2 Pre-trade risk controls** — کنترلهای پیش از ارسال سفارش. `q:` "pre-trade risk" controls architecture · fat finger check order rejection. `r:` SEC Rule 15c3-5 (2010); CFTC (2013) concept release on risk controls.
- **D15.3 Kill switches and algorithmic trading controls** — کلید قطع و الزامات کنترلی الگوریتمها. `q:` MiFID II RTS 6 kill functionality · algorithmic trading risk controls requirement. `r:` EU Delegated Regulation 2017/589 (RTS 6).
- **D15.4 Concentration and exposure limits** — حدود تمرکز در نماد، صنعت و عامل. `q:` concentration limits portfolio risk · exposure limit setting practice. `r:` risk policy references; Grinold & Kahn (2000).
- **D15.5 Stop-loss theory and design** — نظریهٔ طراحی حدضرر. `q:` "when do stop-loss rules stop losses" · stop loss optimal strategy theory. `r:` Kaminski & Lo (2014); Han, Zhou & Zhu (2016).
- **D15.6 Gap risk and overnight risk** — ریسک شکاف قیمتی و نگهداری بینروزی. `q:` gap risk measurement trading · overnight return risk management. `r:` Barro (2006) disaster risk; futures gap literature.
- **D15.7 Liquidation risk and margin calls** — ریسک بستهشدن اجباری پوزیشن. `q:` margin call liquidation mechanics · forced liquidation risk management. `r:` exchange margin documentation; BIS margin studies.
- **D15.8 Leverage and margin policy** — سیاست اهرم، مارجین اولیه و نگهداری. `q:` optimal leverage policy trading · initial versus maintenance margin. `r:` exchange margin rules; Frazzini & Pedersen (2012).
- **D15.9 Tail hedging and convexity** — پوشش دنباله و ریسک نامتقارن. `q:` tail risk hedging equity portfolios · convexity hedging cost. `r:` Ilmanen (2011); Bhansali (2014).
- **D15.10 Stress testing and reverse stress testing** — آزمون فشار و کشف سناریوهای شکست. `q:` reverse stress testing methodology · stress testing trading portfolios. `r:` ECB/CBES stress testing frameworks; BIS (2005).
- **D15.11 Liquidity risk management** — مدیریت ریسک نقدینگی در سطح پرتفوی. `q:` liquidity risk management framework funds · liquidity stress testing portfolios. `r:` IOSCO recommendations on liquidity risk management; Bangia et al. (1999).
- **D15.12 Systemic risk measures** — سنجههای ریسک سیستمی. `q:` "CoVaR" systemic risk measure · marginal expected shortfall systemic. `r:` Adrian & Brunnermeier (2016); Acharya et al. (2017).
- **D15.13 Risk model validation and backtesting** — اعتبارسنجی مدل ریسک. `q:` risk model validation practices · VaR backtesting regulatory. `r:` BCBS traffic light approach; SR 11-7.
- **D15.14 Insurance fund and loss mutualization mechanisms** — صندوق بیمه و تسهیم زیان در صرافیها. `q:` exchange insurance fund liquidation mechanism · auto-deleveraging ADL design. `r:` crypto exchange documentation; BIS crypto reports.
- **D15.15 Wrong-way risk and counterparty exposure** — ریسک جهت اشتباه و مواجههٔ متقابل. `q:` wrong-way risk counterparty exposure · CVA credit valuation adjustment. `r:` Basel counterparty credit risk framework; Gregory (2012).
- **D15.16 Model-driven risk misestimation failures** — نمونههای شکست مدلهای ریسک و درسهای آن. `q:` risk model failure case studies · lessons from risk management failures. `r:` Taleb (2007); Basel Committee reviews of the financial crisis.

## D16 — Sizing, Capital Allocation & Leverage

- **D16.1 Kelly criterion** — معیار کلی و نرخ رشد بهینهٔ سرمایه. `q:` "a new interpretation of information rate" Kelly · Kelly criterion gambling investing. `r:` Kelly (1956); Thorp (2006).
- **D16.2 Fractional Kelly and estimation error** — کسر کلی و اصلاح خطای برآورد لبه. `q:` fractional Kelly estimation error · Kelly criterion uncertainty edge. `r:` MacLean, Thorp & Ziemba (2011); Baker & McHale (2013).
- **D16.3 Optimal f and money management** — مدیریت سرمایه و بهینهسازی اندازهٔ معامله. `q:` Ralph Vince optimal f · money management trading systems. `r:` Vince (1990, 1992); Pardo (2008).
- **D16.4 Volatility targeting in position sizing** — هدفگذاری نوسان در تعیین اندازهٔ پوزیشن. `q:` volatility targeting position sizing · risk targeting implementation. `r:` Harvey et al. (2018).
- **D16.5 Risk budgeting across strategies** — بودجهبندی ریسک میان استراتژیها. `q:` risk budgeting multi-strategy · risk allocation portfolio of strategies. `r:` Roncalli (2013); Grinold & Kahn (2000).
- **D16.6 Position sizing under drawdown control** — اندازهگیری پوزیشن با کنترل افت سرمایه. `q:` drawdown control investment strategy · drawdown based position scaling. `r:` Grossman & Zhou (1993); Chekhlov et al. (2005).
- **D16.7 Leverage efficiency and margin optimization** — بهرهوری اهرم و بهینهسازی مارجین. `q:` leverage efficiency portfolio margin · funding cost leverage optimization. `r:` Frazzini & Pedersen (2012); exchange margin documentation.
- **D16.8 Risk of ruin and survivability analysis** — ریسک ورشکستگی و تحلیل بقا. `q:` "risk of ruin" trading capital · gambler's ruin trading strategy. `r:` Feller (1968); Pardo (2008).
- **D16.9 Compounding, path dependence and non-ergodicity** — مرکبشدن، وابستگی به مسیر و ناارگودیسیتی. `q:` non-ergodicity wealth dynamics · path dependence compounding returns. `r:` Peters (2019); MacLean et al. (2011).
- **D16.10 Sizing with uncertain edge and short samples** — اندازهگیری با لبهٔ نامعلوم و نمونهٔ کم. `q:` Bayesian Kelly uncertainty · position sizing estimation risk. `r:` Baker & McHale (2013); Kan & Zhou (2007).
- **D16.11 Capital allocation across correlated strategies** — تخصیص سرمایه میان استراتژیهای همبسته. `q:` capital allocation correlated strategies · portfolio of trading strategies allocation. `r:` Roncalli (2013); Grinold & Kahn (2000).
- **D16.12 Bet sizing and bankroll management analogies** — قیاسهای اندازهٔ شرط و مدیریت موجودی. `q:` bankroll management betting Kelly · bet sizing theory. `r:` Thorp (2006); MacLean, Ziemba & Blazenko (1992).

## D17 — Backtesting, Validation & Overfitting

- **D17.1 Backtest design principles** — اصول طراحی بکتست قابل اعتماد. `q:` "backtesting protocol" machine learning era · backtest design best practice. `r:` Arnott, Harvey & Markowitz (2019); Harvey & Liu (2015).
- **D17.2 Backtest overfitting** — بیشبرازش در بکتست و سنجش آن. `q:` "probability of backtest overfitting" CSCV · pseudo-mathematics financial charlatanism. `r:` Bailey, Borwein, López de Prado & Zhu (2014); Bailey et al. (2017).
- **D17.3 Deflated Sharpe ratio (DSR)** — شارپ تعدیلشده برای تعداد آزمونها. `q:` "deflated Sharpe ratio" · Sharpe ratio multiple testing correction. `r:` Bailey & López de Prado (2014).
- **D17.4 Sharpe ratio statistics** — آمارهٔ شارپ: خطا، خودهمبستگی، افق. `q:` "statistics of Sharpe ratios" Lo · Sharpe ratio autocorrelation annualization. `r:` Lo (2002); Bailey & López de Prado (2012).
- **D17.5 Purged K-fold cross-validation and embargo** — اعتبارسنجی متقاطع با پاکسازی و ممنوعیت همسایگی. `q:` "purged" cross validation financial machine learning · embargo leakage labels overlap. `r:` López de Prado (2018); López de Prado (2020) CPCV.
- **D17.6 Combinatorial purged cross-validation (CPCV)** — اعتبارسنجی ترکیبی برای مسیرهای چندگانه. `q:` "combinatorial purged cross-validation" backtest paths. `r:` López de Prado (2018, 2020).
- **D17.7 Walk-forward and rolling-window analysis** — پیشروی زمانی و پنجرهٔ غلتان. `q:` walk-forward optimization trading system · rolling window out-of-sample testing. `r:` Pardo (2008); Hansen & Timmermann (2012).
- **D17.8 Multiple-testing control methods** — کنترل آزمونهای چندگانه. `q:` Benjamini-Hochberg false discovery rate · Holm Bonferroni finance applications. `r:` Benjamini & Hochberg (1995); Storey (2002).
- **D17.9 Reality Check and SPA tests** — آزمونهای جستوجوگری داده. `q:` "reality check for data snooping" White · "superior predictive ability" Hansen test. `r:` White (2000); Hansen (2005); Romano & Wolf (2005).
- **D17.10 Minimum backtest length and track-record requirements** — حداقل طول لازم برای نتیجهگیری. `q:` minimum track record length Sharpe · minimum backtest length deflated Sharpe. `r:` Bailey & López de Prado (2014); Bailey et al. (2014).
- **D17.11 Out-of-sample degradation and live-vs-backtest gap** — افت عملکرد خارج از نمونه. `q:` out-of-sample performance degradation trading · backtest to live performance gap. `r:` Harvey & Liu (2015); Pardo (2008).
- **D17.12 Paper trading and shadow deployment** — معاملهٔ کاغذی و استقرار سایه. `q:` paper trading evaluation methodology · shadow trading validation strategy. `r:` practitioner methodology references.
- **D17.13 Robustness and sensitivity analysis** — تحلیل حساسیت پارامتر و پایداری زیردورهها. `q:` parameter sensitivity trading strategy robustness · strategy perturbation tests. `r:` Pardo (2008); Harvey & Liu (2015).
- **D17.14 Regime-wise and stress-path validation** — اعتبارسنجی به تفکیک رژیم و مسیرهای پرتنش. `q:` regime specific strategy validation · stress period strategy testing. `r:` Ang & Timmermann (2012); practitioner literature.
- **D17.15 Data-snooping in technical analysis** — جستوجوگری داده در قواعد تحلیل تکنیکال. `q:` "data-snooping" technical trading rule performance bootstrap · universe of trading rules. `r:` Sullivan, Timmermann & White (1999); Bajgrowicz & Scaillet (2012).
- **D17.16 Replication and falsification studies** — مطالعات تکرار و ابطال. `q:` "replicating anomalies" · false and missed discoveries financial economics. `r:` Hou, Xue & Zhang (2020); Harvey & Liu (2020); Jensen, Kelly & Pedersen (2023).
- **D17.17 Researcher degrees of freedom** — درجات آزادی پژوهشگر و باغ مسیرهای دوشاخه. `q:` "garden of forking paths" · researcher degrees of freedom finance. `r:` Gelman & Loken (2014); Simmons, Nelson & Simonsohn (2011).
- **D17.18 Publication bias and p-hacking** — سوگیری انتشار و دستکاری معنیداری. `q:` "why most published research findings are false" · p-hacking financial research. `r:` Ioannidis (2005); Harvey (2017).
- **D17.19 Preregistration and research protocols** — پیشثبت پروتکل پژوهش. `q:` preregistration empirical finance research · pre-registered hypothesis testing trading. `r:` Nosek et al. (2018); López de Prado (2018, 2020).
- **D17.20 Simulation-based validation and Monte Carlo robustness** — اعتبارسنجی مبتنی بر شبیهسازی. `q:` Monte Carlo validation trading strategies · synthetic data robustness testing. `r:` Pardo (2008); ABIDES-based studies.

## D18 — Simulation, Synthetic Markets & Agent-Based Models

- **D18.1 Agent-based models of financial markets** — مدلهای عاملبنیان بازار. `q:` "agent-based models" financial markets survey · heterogeneous agents asset pricing. `r:` LeBaron (2006); Hommes (2006).
- **D18.2 Zero-intelligence and statistical market models** — بازارهای بدون هوش و خواص آماری. `q:` "zero-intelligence" traders double auction · statistical mechanics of markets. `r:` Gode & Sunder (1993); Smith et al. (2003).
- **D18.3 Order book simulators and matching engines** — شبیهساز دفتر سفارش و موتور تطبیق. `q:` limit order book simulator implementation · matching engine design. `r:` exchange documentation; ABIDES (Byrd et al. 2020).
- **D18.4 Multi-agent simulation platforms** — بسترهای شبیهسازی چندعاملی. `q:` ABIDES agent based interactive discrete event simulation · market simulation platform. `r:` Byrd, Hybinette & Balch (2020).
- **D18.5 Impact-aware market simulation** — شبیهسازی با اثر بازار درونزا. `q:` market impact simulation endogenous · relaxational impact model simulation. `r:` Bouchaud et al. (2018); Cont & Wang (2021).
- **D18.6 Synthetic data generation for markets** — تولید دادهٔ مصنوعی. `q:` synthetic financial data generation quality · generative adversarial networks market data. `r:` Wiese et al. (2020); Assefa et al. (2020).
- **D18.7 Signature methods and rough paths** — روشهای امضا و مسیرهای زبر برای سریهای مالی. `q:` "signature methods" financial time series · rough path theory machine learning finance. `r:` Lyons (1998); Kidger et al. (2019).
- **D18.8 Monte Carlo methods and variance reduction** — مونتکارلو و کاهش واریانس. `q:` variance reduction Monte Carlo finance · quasi-Monte Carlo risk. `r:` Glasserman (2004).
- **D18.9 Market replay and scenario resampling** — بازپخش بازار و بازنمونهگیری سناریو. `q:` market replay backtesting engine · historical scenario resampling. `r:` practitioner engineering literature.
- **D18.10 Stress scenario generation** — تولید سناریوهای بحرانی. `q:` scenario generation copula stress · tail scenario construction. `r:` Embrechts et al. (2002); ECB stress methodology.
- **D18.11 Simulator calibration and validation** — کالیبراسیون و اعتبارسنجی شبیهساز. `q:` market simulator calibration stylized facts · validating simulation models trading. `r:` Cont (2001); Bouchaud et al. (2018).
- **D18.12 Adversarial and robustness testing of algorithms** — آزمون مخرب و مقاومسازی. `q:` adversarial testing trading algorithms · fault injection trading systems. `r:` Basiri et al. (2016); Nygard (2018).

## D19 — Derivatives: Futures, Perpetuals, Funding & Options

- **D19.1 Futures pricing and cost of carry** — قیمتگذاری آتی و هزینهٔ نگهداری. `q:` futures pricing cost of carry model · theory of storage convenience yield. `r:` Hull (2017); Working (1949).
- **D19.2 Basis, contango and backwardation** — پایه و ساختار بازار. `q:` futures basis behaviour · contango backwardation determinants. `r:` Gorton & Rouwenhorst (2006); Keynes (1930) normal backwardation.
- **D19.3 Term structure and roll yield** — ساختار ترم و بازده رول. `q:` roll yield futures term structure · commodity term structure risk premia. `r:` Erb & Harvey (2006); Szymanowska et al. (2014).
- **D19.4 Futures risk premia** — صرف ریسک در بازار آتی. `q:` commodity futures risk premia anatomy · time series momentum futures. `r:` Szymanowska, de Roon, Nijman & van den Goorbergh (2014); Moskowitz et al. (2012).
- **D19.5 Hedging pressure and positioning** — فشار پوششدهندگان و موقعیتها. `q:` hedging pressure futures returns · open interest positioning predictive. `r:` de Roon, Nijman & Veld (2000); Hong & Yogo (2012).
- **D19.6 Commitments of Traders (COT) data** — دادهٔ موقعیت معاملهگران و کاربرد آن. `q:` CFTC Commitments of Traders analysis · speculative positioning signal. `r:` CFTC COT documentation; Sanders, Irwin & Merrin (2010).
- **D19.7 Perpetual futures and funding rate mechanics** — فیوچرز دائمی و سازوکار نرخ بهره. `q:` "fundamentals of perpetual futures" · perpetual swap funding rate mechanism. `r:` He, Manela, Ross & von Beschwitz (2022); exchange perpetual contract documentation.
- **D19.8 Mark price, index price and liquidation price** — قیمت علامت، شاخص و بستهشدن اجباری. `q:` mark price versus last price liquidation · index price construction derivatives. `r:` exchange contract specifications; BIS (2022) crypto derivatives notes.
- **D19.9 Auto-deleveraging and insurance funds** — تخصیص خودکار و صندوق بیمه. `q:` auto-deleveraging mechanism crypto exchange · insurance fund liquidation waterfall. `r:` exchange documentation; BIS crypto working papers.
- **D19.10 Funding arbitrage and cash-and-carry** — آربیتراژ نرخ و نقدی-آتی. `q:` cash and carry basis trade crypto · funding rate arbitrage strategy. `r:` Makarov & Schoar (2020); practitioner literature.
- **D19.11 Options pricing and the Black-Scholes-Merton framework** — قیمتگذاری آپشن و مبانی آن. `q:` Black-Scholes-Merton derivation assumptions · option pricing critique. `r:` Black & Scholes (1973); Merton (1973).
- **D19.12 Volatility surface, smile and skew** — سطح نوسان و لبخند. `q:` implied volatility surface modelling · volatility skew explanation. `r:` Derman & Kani (1994); Dupire (1994); Gatheral (2006).
- **D19.13 Stochastic and local volatility models** — مدلهای نوسان تصادفی و محلی. `q:` Heston stochastic volatility calibration · SABR model implied volatility. `r:` Heston (1993); Hagan, Kumar, Lesniewski & Woodward (2002).
- **D19.14 Variance and volatility swaps** — سواپ واریانس و نوسان. `q:` variance swap replication theory · VIX methodology calculation. `r:` Carr & Madan (1998); CBOE VIX white paper.
- **D19.15 Option-implied moments and crash risk** — گشتاورهای استخراجی از آپشن و ریسک سقوط. `q:` option implied skewness kurtosis · volatility smirk future returns. `r:` Bakshi, Kapadia & Madan (2003); Xing, Zhang & Zhao (2010).
- **D19.16 Delta hedging and gamma scalping** — پوشش دلتا و کسب گاما. `q:` delta hedging transaction costs · gamma scalping profitability. `r:` Hull (2017); Taleb (1997) dynamic hedging.
- **D19.17 Crypto options and inverse contracts** — آپشنهای کریپتو و قراردادهای معکوس. `q:` crypto options Deribit implied volatility · inverse option pricing quanto. `r:` Alexander & Imeraj (2021); venue (Deribit) contract documentation.
- **D19.18 Margin models for derivatives (SPAN and VaR-based)** — مدلهای مارجین ابزار مشتقه. `q:` SPAN margin methodology CME · VaR based margining exchange. `r:` CME SPAN documentation; BIS margin requirements literature.
- **D19.19 Calendar spreads and relative value in futures** — اسپرد تقویمی و ارزش نسبی. `q:` calendar spread trading futures · term structure relative value strategy. `r:` Szymanowska et al. (2014); practitioner literature.
- **D19.20 Delta-neutral and basis-neutral positioning** — موضعگیری دلتا-خنثی و پایه-خنثی. `q:` delta neutral basis trade · hedged carry position construction. `r:` Koijen et al. (2018); practitioner literature.

## D20 — Crypto Market Structure

- **D20.1 Crypto market microstructure** — ریزساختار بازار ارز دیجیتال. `q:` cryptocurrency market microstructure survey · crypto liquidity measurement. `r:` Brauneis, Mestel, Riordan & Theissen (2021); Makarov & Schoar (2020).
- **D20.2 Price discovery across crypto venues** — کشف قیمت میان بازار نقدی و مشتقهٔ کریپتو. `q:` bitcoin price discovery spot versus futures · information share crypto markets. `r:` Baur & Dimpfl (2019); Alexander, Choi, Park & Sohn (2020).
- **D20.3 Arbitrage and market segmentation** — آربیتراژ و جدایی بازارها. `q:` "trading and arbitrage in cryptocurrency markets" · cross-exchange arbitrage spreads. `r:` Makarov & Schoar (2020).
- **D20.4 Wash trading and fake volume detection** — حجم صوری و تشخیص آن. `q:` "crypto wash trading" detection · fake volume exchange ranking. `r:` Cong, Li, Tang & Yang (2023); Amiram, Lyandres & Rabetti (2021).
- **D20.5 Exchange counterparty and solvency risk** — ریسک طرف مقابل و ورشکستگی صرافی. `q:` crypto exchange failure analysis · centralized exchange solvency risk. `r:` BIS (2022) crypto reports; post-2022 exchange failure literature.
- **D20.6 Stablecoins and peg dynamics** — استیبلکوینها و پایداری پگ. `q:` "is bitcoin really untethered" · stablecoin peg deviation arbitrage. `r:` Griffin & Shams (2020); BIS stablecoin reports.
- **D20.7 Funding rates and perpetual pricing literature** — ادبیات نرخ بهره و قیمتگذاری دائمی. `q:` perpetual futures funding rate research · perpetual swap pricing model. `r:` He, Manela, Ross & von Beschwitz (2022).
- **D20.8 Liquidation cascades and leverage cycles in crypto** — آبشار بستهشدن اجباری و چرخهٔ اهرم. `q:` crypto liquidation cascade analysis · deleveraging spiral crypto markets. `r:` BIS (2022) "Crypto shocks and retail losses"; exchange data studies.
- **D20.9 MEV, DEX microstructure and AMM mechanics** — ارزش قابل استخراج، ریزساختار DEX و سازوکار AMM. `q:` "Flash Boys 2.0" maximal extractable value · constant function market maker analysis. `r:` Daian et al. (2019); Angeris et al. (2021).
- **D20.10 Loss-versus-rebalancing and LP economics** — اقتصاد تأمینکنندهٔ نقدینگی در AMM. `q:` "loss-versus-rebalancing" AMM · impermanent loss analysis. `r:` Milionis, Moallemi, Roughgarden & Zhang (2022).
- **D20.11 Oracle design and manipulation risk** — اوراکل قیمت و ریسک دستکاری. `q:` price oracle manipulation DeFi · oracle design attacks. `r:` Angeris & Chitra (2020); Daian et al. (2019).
- **D20.12 On-chain analytics and flows** — تحلیلهای زنجیرهای و جریانها. `q:` on-chain analytics exchange flows · address clustering heuristics. `r:` Meiklejohn et al. (2013); Ron & Shamir (2013).
- **D20.13 Crypto factor models and cross-sectional returns** — عوامل و بازده مقطعی کریپتو. `q:` "common risk factors in cryptocurrency" · cross-section cryptocurrency returns. `r:` Liu, Tsyvinski & Wu (2022); Liu & Tsyvinski (2021).
- **D20.14 Crypto volatility and jump behaviour** — نوسان و پرشهای کریپتو. `q:` "high-frequency jump analysis of the bitcoin market" · bitcoin volatility stylized facts. `r:` Scaillet, Treccani & Trevisan (2020); Katsiampa (2017).
- **D20.15 Crypto regulation and market integrity** — مقررات و تمامیت بازار کریپتو. `q:` MiCA regulation crypto markets · crypto market integrity surveillance. `r:` EU MiCA (2023/1114); IOSCO crypto recommendations.
- **D20.16 Retail behaviour and loss patterns in crypto** — رفتار خرد و الگوهای زیان. `q:` retail investor losses cryptocurrency · leverage retail trading outcomes. `r:` BIS Bulletin (2022); Hasso, Pelster & Breitmayer (2019) who trades cryptocurrencies.
- **D20.17 Mining economics and hashrate signals** — اقتصاد استخراج و سیگنالهای هشریت. `q:` bitcoin mining economics profitability · hashrate price relationship. `r:` Hayes (2017); Cong, He & Li (2021) decentralized mining in centralized pools.
- **D20.18 Token liquidity, listings and delistings** — نقدینگی توکن، عرضه و حذف از فهرست. `q:` exchange listing effect cryptocurrency returns · token delisting impact. `r:` Benedetti & Kostovetsky (2021) ICO returns; exchange announcement event studies.
- **D20.19 Decentralized exchange and CEX-DEX interactions** — تعامل صرافی متمرکز و غیرمتمرکز. `q:` centralized decentralized exchange arbitrage · DEX CEX price transmission. `r:` Lehar & Parlour (2023); Capponi & Jia (2021).
- **D20.20 Stress events and flash crash studies in crypto** — رویدادهای تنش و سقوطهای ناگهانی کریپتو. `q:` crypto flash crash event study · March 2020 bitcoin crash liquidity. `r:` BIS and academic event studies.

## D21 — Venue Mechanics, Order Types & Market Regulation

- **D21.1 FIX protocol and order lifecycle** — پروتکل FIX و چرخهٔ عمر سفارش. `q:` "FIX protocol" specification order messages · order lifecycle state machine. `r:` FIX Trading Community specification; exchange FIX guides.
- **D21.2 Order type taxonomy** — طبقهبندی کامل انواع سفارش. `q:` order types reference market limit stop · advanced order types guide. `r:` exchange rulebooks; Harris (2003) *Trading and Exchanges*.
- **D21.3 Time-in-force semantics** — معنای دقیق GTC/IOC/FOK و اثر آن بر پر شدن. `q:` time in force IOC FOK semantics · fill or kill implementation. `r:` exchange rulebooks; Harris (2003).
- **D21.4 Post-only, reduce-only and self-trade prevention** — قیود سفارش در بازارهای مشتقه. `q:` "post-only" order rejection logic · "reduce-only" order semantics. `r:` exchange contract documentation.
- **D21.5 Batch operations and mass cancel** — عملیات دستهای و ابطال گروهی. `q:` batch order placement API · mass cancel orders exchange. `r:` exchange API documentation.
- **D21.6 Circuit breakers, price bands and volatility interruptions** — توقفها و باندهای قیمتی. `q:` "circuit breaker" market design effects · price band limit up limit down. `r:` SEC/CFTC circuit breaker rules; exchange price band rules.
- **D21.7 Tick size regimes and minimum increments** — رژیمهای گام قیمت و حداقل افزایش. `q:` tick size regime effects liquidity · minimum price increment policy. `r:` SEC Tick Size Pilot; exchange tick rules.
- **D21.8 Order-to-trade ratio limits and message throttling** — محدودیت نسبت سفارش به معامله. `q:` "order to trade ratio" regulation · message throttling exchange. `r:` MiFID II RTS 9; exchange throttling rules.
- **D21.9 Market structure regulation (Reg NMS and analogues)** — مقررات ساختار بازار و حمایت از سفارش. `q:` "Regulation NMS" order protection rule · market structure regulation framework. `r:` SEC Reg NMS (2005); SEC equity market structure concept releases.
- **D21.10 Best execution obligations** — الزام اجرای بهترین. `q:` best execution obligation MiFID II · best execution policy evidence. `r:` MiFID II Article 27; SEC/FINRA best execution guidance.
- **D21.11 Market abuse: spoofing, layering, wash, marking** — تخلفات بازار و تشخیص آنها. `q:` "market abuse" detection algorithms · spoofing enforcement actions. `r:` Dodd-Frank Act §747; EU Market Abuse Regulation 596/2014.
- **D21.12 Settlement cycles and clearing mechanics** — چرخهٔ تسویه و سازوکار پایاپای. `q:` T+1 settlement impact market · central clearing novation mechanics. `r:` DTCC/CCP documentation; BIS CPMI reports.
- **D21.13 Short selling and securities lending mechanics** — فروش استقراضی و قرض اوراق. `q:` short sale mechanics locate requirement · securities lending market structure. `r:` SEC Regulation SHO (2004); Duffie, Gârleanu & Pedersen (2002).
- **D21.14 Position limits and accountability levels** — حدود موقعیت و سطوح پاسخگویی. `q:` "position limits" derivatives regulation · accountability levels exchange. `r:` CFTC Part 150; exchange position limit rules.
- **D21.15 Large trader reporting** — گزارش معاملهگران بزرگ. `q:` large trader reporting rule · position reporting requirements exchange. `r:` CFTC Part 17/18; SEC Rule 13h-1.
- **D21.16 Exchange fees, rebates and fee tiers** — ساختار کارمزد و رِبیت صرافیها. `q:` maker taker fee structure effect · exchange fee tiers algorithmic trading. `r:` exchange fee schedules; SEC/ESMA fee studies.
- **D21.17 Auction mechanics: open, close and intraday auctions** — حراجهای پایانی و میانروزی. `q:` closing auction design effects · call auction price efficiency. `r:` Biais, Hillion & Spatt (1999); Bogousslavsky & Muravyev (2023).
- **D21.18 Index construction, rebalancing and provider effects** — ساخت شاخص و اثر بازآرایی. `q:` index rebalancing effects prices · index provider methodology changes. `r:` Beneish & Whaley (1996); index methodology documents.
- **D21.19 Crypto venue mechanics** — سازوکار اختصاصی صرافیهای کریپتو. `q:` crypto exchange contract specification · perpetual funding interval implementation. `r:` exchange API/contract documentation; BIS crypto market structure reports.
- **D21.20 Exchange and API operational risk** — ریسک عملیاتی صرافی و رابط برنامهنویسی. `q:` exchange API rate limit handling · venue outage risk trading systems. `r:` exchange status/incident documentation; BIS operational risk reports.

## D22 — Operations, Governance, Controls & Compliance

- **D22.1 Model risk management (SR 11-7)** — حاکمیت ریسک مدل. `q:` "model risk management" SR 11-7 framework · model validation independence. `r:` Federal Reserve SR 11-7 / OCC 2011-12.
- **D22.2 Algorithmic trading governance** — حاکمیت معاملات الگوریتمی. `q:` MiFID II RTS 6 testing requirements · algorithmic trading governance framework. `r:` EU Delegated Regulation 2017/589 (RTS 6); FCA algorithmic trading guidance.
- **D22.3 Change management and segregation of duties** — مدیریت تغییر و تفکیک وظایف. `q:` change management financial controls · segregation of duties trading operations. `r:` COSO internal control framework; operational risk standards.
- **D22.4 Incident management and blameless postmortems** — مدیریت رخداد و تحلیل بدون سرزنش. `q:` "blameless postmortem" engineering culture · incident response process finance. `r:` Google SRE book; NIST incident handling guide.
- **D22.5 Business continuity and disaster recovery** — تداوم کسبوکار و بازیابی از فاجعه. `q:` business continuity RTO RPO financial · disaster recovery planning trading. `r:` BCBS (2005) *High-level principles for business continuity*; ISO 22301.
- **D22.6 Reconciliation and break management** — مغایرتزدایی و مدیریت اختلافها. `q:` trade reconciliation breaks management · position reconciliation process. `r:` industry operations references; DTCC reconciliation guidance.
- **D22.7 Trade lifecycle and settlement operations** — چرخهٔ عمر معامله در عملیات. `q:` trade lifecycle straight through processing · post-trade operations workflow. `r:` FIX/ISO 20022 post-trade standards.
- **D22.8 Audit trails, immutability and tamper-evident logs** — رد حسابرسی و لاگ دستنخورده. `q:` tamper-evident audit log hash chain · immutable ledger compliance trading. `r:` NIST SP 800-92 (log management); Merkle (1988).
- **D22.9 Data governance (BCBS 239 and analogues)** — حاکمیت داده و گزارشدهی ریسک. `q:` "BCBS 239" risk data aggregation principles · data lineage governance finance. `r:` BCBS 239 (2013); DAMA-DMBOK.
- **D22.10 Key management, secrets and API access control** — مدیریت کلید، رمز و دسترسی API. `q:` API key management trading system · least privilege secrets management. `r:` NIST SP 800-57 (key management); OWASP secrets management guidance.
- **D22.11 Access control and dual control (four-eyes)** — کنترل دسترسی و کنترل دوگانه. `q:` "four-eyes principle" financial controls · maker checker workflow trading. `r:` COSO/SOX control frameworks.
- **D22.12 Monitoring, alerting and alert fatigue** — پایش، هشدار و خستگی هشدار. `q:` alert fatigue design monitoring · SLO SLI alerting best practice. `r:` Google SRE book; Nygard (2018).
- **D22.13 Trade surveillance systems** — سیستمهای نظارت بر معاملات. `q:` trade surveillance market abuse detection systems · surveillance alert tuning. `r:` regulatory technical standards on surveillance; vendor methodology literature.
- **D22.14 Regulatory reporting** — گزارشدهی ناظرتی. `q:` MiFID II transaction reporting requirements · CFTC large trader reporting systems. `r:` MiFIR Article 26; CFTC Parts 17/18.
- **D22.15 Vendor and outsourcing risk** — ریسک تأمینکننده و برونسپاری. `q:` third party risk management finance · vendor due diligence data providers. `r:` EBA outsourcing guidelines; BCBS outsourcing principles.
- **D22.16 Reproducibility, experiment tracking and MLOps** — تکرارپذیری و ردیابی آزمایشها. `q:` reproducibility machine learning experiments tracking · MLOps model versioning finance. `r:` Pimentel et al. (2019); Sculley et al. (2015) hidden technical debt.
- **D22.17 Testing in production: canary and shadow deployments** — انتشار تدریجی و سایه. `q:` canary deployment risk control · shadow mode deployment trading system. `r:` Humble & Farley (2010) continuous delivery.
- **D22.18 Capacity, cost and resource planning** — ظرفیت، هزینه و برنامهریزی منابع. `q:` infrastructure cost optimization trading systems · capacity planning market data volumes. `r:` industry engineering references.
- **D22.19 Documentation standards and model cards** — استاندارد مستندسازی و کارت مدل. `q:` "model cards for model reporting" · model documentation standards finance. `r:` Mitchell et al. (2019); SR 11-7 documentation expectations.
- **D22.20 Operational risk frameworks and loss data** — چارچوب ریسک عملیاتی و دادهٔ زیان. `q:` operational risk framework Basel · loss event data collection standards. `r:` Basel II/III operational risk framework; ORX industry data.

## D23 — Performance Measurement & Attribution

- **D23.1 Sharpe and related ratios** — شارپ و نسبتهای مرتبط. `q:` "Sharpe ratio" definition issues · risk-adjusted performance measures comparison. `r:` Sharpe (1966, 1994); Sortino & Price (1994).
- **D23.2 Omega, Kappa and gain-to-pain measures** — سنجههای مبتنی بر توزیع کامل. `q:` "omega function" performance measure · Kappa ratio performance. `r:` Keating & Shadwick (2002); Kaplan & Knowles (2004).
- **D23.3 Information ratio and active risk** — نسبت اطلاعات و ریسک فعال. `q:` information ratio active management · tracking error optimization. `r:` Goodwin (1998); Grinold & Kahn (2000).
- **D23.4 Performance attribution (Brinson-style)** — تجزیهٔ عملکرد بر پایهٔ تخصیص و انتخاب. `q:` Brinson attribution allocation selection · performance attribution methodology. `r:` Brinson, Hood & Beebower (1986); Brinson, Singer & Beebower (1991).
- **D23.5 Factor-based attribution** — تجزیهٔ عملکرد بر پایهٔ عوامل. `q:` factor based performance attribution · risk factor attribution portfolio. `r:` Fama & French (1993); Menchero, Orr & Wang (2011).
- **D23.6 Time-weighted vs money-weighted returns** — بازده وزنی-زمان و وزنی-پول. `q:` time weighted versus money weighted return · IRR versus TWR performance. `r:` GIPS standards; Bacon (2008).
- **D23.7 GIPS and performance presentation standards** — استانداردهای ارائهٔ عملکرد. `q:` "GIPS" standards composite construction · performance presentation requirements. `r:` CFA Institute GIPS standards.
- **D23.8 Drawdown metrics and recovery analysis** — سنجههای افت سرمایه و زمان بازیابی. `q:` maximum drawdown duration recovery · ulcer index performance. `r:` Chekhlov et al. (2005); Bacon (2008).
- **D23.9 Risk-adjusted measures for non-normal returns** — سنجههای متناسب با بازده غیرنرمال. `q:` performance measurement non-normal returns · "beyond mean-variance" performance measures. `r:` Leland (1999); Amin & Kat (2003).
- **D23.10 Luck vs skill and statistical significance of performance** — تفکیک شانس از مهارت. `q:` "luck versus skill" mutual fund performance · significance of alpha estimates. `r:` Fama & French (2010); Barras, Scaillet & Wermers (2010).
- **D23.11 Style analysis and peer benchmarking** — تحلیل سبک و مقایسه با همتا. `q:` returns based style analysis Sharpe · peer group benchmarking methodology. `r:` Sharpe (1992); Fama & French (2010).
- **D23.12 Capacity and scalability metrics** — سنجههای ظرفیتپذیری. `q:` strategy capacity estimation methodology · capacity constrained performance decay. `r:` Frazzini, Israel & Moskowitz (2018); Gârleanu & Pedersen (2016).
- **D23.13 Turnover, holding period and breakeven cost analysis** — گردش، دورهٔ نگهداری و نقطهٔ سربهسر هزینه. `q:` breakeven cost trading strategy · turnover impact performance. `r:` Perold (1988); Frazzini, Israel & Moskowitz (2018).
- **D23.14 Trade-level and strategy-level P&L decomposition** — تجزیهٔ سود و زیان در سطح معامله و استراتژی. `q:` P&L attribution trading strategies · alpha beta decomposition returns. `r:` Grinold & Kahn (2000); practitioner references.

## D24 — Decision Theory, Behavioral Finance & Research Epistemology

- **D24.1 Risk versus uncertainty (Knightian)** — تفکیک ریسک قابل اندازهگیری از عدمقطعیت. `q:` "risk uncertainty and profit" Knight · Knightian uncertainty economics. `r:` Knight (1921).
- **D24.2 Expected utility and subjective probability** — نظریهٔ مطلوبیت و احتمال ذهنی. `q:` subjective expected utility Savage · expected utility axioms critique. `r:` Savage (1954); von Neumann & Morgenstern (1944).
- **D24.3 Prospect theory and loss aversion** — نظریهٔ چشمانداز و زیانگریزی. `q:` "prospect theory" decision under risk · cumulative prospect theory parameters. `r:` Kahneman & Tversky (1979, 1992).
- **D24.4 Ambiguity aversion and robust control** — گریز از ابهام و کنترل مقاوم. `q:` ambiguity aversion model · "robust control and model uncertainty" Hansen Sargent. `r:` Gilboa & Schmeidler (1989); Hansen & Sargent (2001).
- **D24.5 Value of information and experimentation** — ارزش اطلاعات و آزمایش. `q:` expected value of information decision analysis · bandit problems exploration. `r:` Howard (1966); Gittins (1979).
- **D24.6 Behavioral biases in trading** — سوگیریهای رفتاری در معامله. `q:` overconfidence trading volume · disposition effect evidence. `r:` Barber & Odean (2000); Odean (1998).
- **D24.7 Limits of arbitrage** — محدودیتهای آربیتراژ. `q:` "limits of arbitrage" Shleifer Vishny · arbitrage capital constraints mispricing. `r:` Shleifer & Vishny (1997).
- **D24.8 Noise trader risk and sentiment feedback** — ریسک معاملهگر نویزی و بازخورد احساسات. `q:` noise trader approach asset pricing · sentiment feedback prices. `r:` De Long, Shleifer, Summers & Waldmann (1990).
- **D24.9 Superforecasting and human calibration** — کالیبراسیون انسانی و پیشبینی خبره. `q:` "superforecasting" calibration training · expert judgment calibration. `r:` Tetlock & Gardner (2015); Kahneman & Tversky (1973).
- **D24.10 Base rates and reference class forecasting** — نرخ پایه و پیشبینی بر پایهٔ کلاس مرجع. `q:` reference class forecasting Flyvbjerg · base rate neglect decision making. `r:` Flyvbjerg (2006); Kahneman & Tversky (1973).
- **D24.11 Pre-mortems and decision journals** — پیشمرگ و ژورنال تصمیم. `q:` "premortem" prospective hindsight technique · decision journal practice. `r:` Klein (2007); Kahneman (2011).
- **D24.12 Scientific method in finance: falsification and replication** — روش علمی در مالی: ابطال و تکرار. `q:` falsification economics research · replication crisis in finance. `r:` Popper (1959); Harvey (2017); Ioannidis (2005).
- **D24.13 Reflexivity, crowding and self-defeating strategies** — بازتابندگی و استراتژیهای خودشکن. `q:` reflexive market dynamics · self-defeating trading strategies crowding. `r:` Soros (1987); Lou & Polk (2022).
- **D24.14 Ensemble judgment and wisdom of crowds** — قضاوت جمعی و ترکیب نظرها. `q:` wisdom of crowds markets aggregation · prediction markets accuracy. `r:` Surowiecki (2004); Wolfers & Zitzewitz (2004).
- **D24.15 Decision under deep uncertainty: scenarios and robust decisions** — تصمیم در عدمقطعیت عمیق. `q:` decision making under deep uncertainty methods · robust decision making framework. `r:` Lempert, Popper & Bankes (2003); Walker, Lempert & Kwakkel (2013).

## D25 — Trading Systems Engineering

- **D25.1 Event-driven architecture for trading** — معماری رویدادمحور در معاملات. `q:` event-driven architecture trading systems · event sourcing CQRS finance. `r:` Fowler (2005) event sourcing; Vernon (2013).
- **D25.2 Determinism, idempotency and exactly-once semantics** — قطعیت، خودتوانی و یکبار-دقیقاً. `q:` idempotency keys order submission · exactly-once processing stream. `r:` Kleppmann (2017) *Designing Data-Intensive Applications*.
- **D25.3 Append-only logs and hash chains** — لاگ فقط-افزودنی و زنجیرهٔ هش. `q:` append-only log design · hash chain tamper evidence. `r:` Merkle (1988); Kleppmann (2017).
- **D25.4 Write-ahead logging and durability semantics** — لاگ پیشنوشتنی و تضمین دوام. `q:` write-ahead logging durability · fsync semantics database. `r:` SQLite WAL documentation; Kleppmann (2017).
- **D25.5 Stream processing for market data** — پردازش جریانی دادهٔ بازار. `q:` stream processing market data Kafka · exactly-once stream processing financial. `r:` Kafka/Flink documentation; industry architecture papers.
- **D25.6 Distributed consensus (Paxos, Raft)** — اجماع توزیعشده و کاربرد آن. `q:` Raft consensus algorithm · Paxos made simple. `r:` Lamport (1998); Ongaro & Ousterhout (2014).
- **D25.7 Timekeeping: monotonic vs wall clocks** — زمانسنجی در سیستم و مخاطرات آن. `q:` monotonic versus wall clock programming · leap second handling systems. `r:` POSIX time specifications; Mills (1991).
- **D25.8 Tail latency and performance engineering** — تأخیر دنباله و مهندسی کارایی. `q:` "the tail at scale" latency · p99 latency engineering. `r:` Dean & Barroso (2013).
- **D25.9 Resilience patterns: circuit breaker, bulkhead, backpressure** — الگوهای تابآوری. `q:` circuit breaker pattern resilience · backpressure bulkhead design. `r:` Nygard (2018) *Release It!*.
- **D25.10 Chaos engineering and fault injection** — مهندسی آشوب و تزریق خطا. `q:` "chaos engineering" principles · fault injection testing distributed. `r:` Basiri et al. (2016); Netflix chaos engineering resources.
- **D25.11 Observability: metrics, logs, traces** — مشاهدهپذیری سیستم. `q:` observability three pillars metrics logs traces · distributed tracing finance systems. `r:` Google SRE book; OpenTelemetry specification.
- **D25.12 Configuration as code and parameter registries** — پیکربندی بهعنوان کد و رجیستر پارامترها. `q:` configuration as code best practices · parameter registry experiment management. `r:` Humble & Farley (2010); MLOps references.
- **D25.13 Schema evolution and interface contracts** — تکامل اسکیما و قراردادهای رابط. `q:` schema evolution compatibility Avro Protobuf · API contract versioning. `r:` Kleppmann (2017); Avro/Protobuf documentation.
- **D25.14 Feature stores and point-in-time correctness** — فروشگاه ویژگی و درستی نقطهای. `q:` "feature store" point-in-time correctness · training serving skew prevention. `r:` MLOps platform documentation; Sculley et al. (2015).
- **D25.15 Market data normalization and time alignment** — یکسانسازی و همراستاسازی زمانی داده. `q:` market data normalization timestamp alignment · data alignment as-of joins. `r:` industry data engineering references.
- **D25.16 Latency measurement and benchmarking** — اندازهگیری تأخیر و بنچمارک. `q:` latency benchmarking trading systems · tick to trade latency measurement. `r:` exchange latency statistics; industry benchmark reports.
- **D25.17 Backtest-live parity engineering** — مهندسی همسانی بکتست و معاملهٔ زنده. `q:` backtest live parity code architecture · same code path simulation production. `r:` practitioner engineering literature.
- **D25.18 Security engineering for trading systems** — امنیت سیستمهای معاملاتی. `q:` trading system security architecture · API security financial applications. `r:` NIST CSF; OWASP guidance.

## D26 — Where to Search: Venues, Journals & Source Types

- **D26.1 Preprint and working-paper repositories** — مخازن پیشچاپ و مقالات کاری. `q:` SSRN financial economics working papers · arXiv q-fin sections (TR, PM, RM, ST, MF, EC). `r:` ssrn.com; arxiv.org/list/q-fin.
- **D26.2 Academic journals (finance and economics)** — مجلات دانشگاهی مالی و اقتصادی. `q:` Journal of Finance Journal of Financial Economics Review of Financial Studies · Journal of Financial and Quantitative Analysis. `r:` JF, JFE, RFS, JFQA, Review of Finance, Journal of Monetary Economics.
- **D26.3 Quantitative and operations journals** — مجلات کمّی و تحقیق در عملیات. `q:` Quantitative Finance journal · Mathematical Finance Operations Research Management Science. `r:` Quantitative Finance; Mathematical Finance; Operations Research; Management Science; Journal of Financial Econometrics.
- **D26.4 Practitioner journals** — مجلات حرفهای صنعت. `q:` Journal of Portfolio Management · Financial Analysts Journal · Journal of Trading. `r:` JPM; FAJ; Journal of Financial Data Science; Journal of Investment Management.
- **D26.5 Conferences and workshops** — کنفرانسها و کارگاهها. `q:` AFA WFA EFA annual meeting finance · NeurIPS ICML workshops machine learning finance · ICAIF ACM conference AI in finance. `r:` AFA/WFA/EFA; NeurIPS & ICML finance workshops; ACM ICAIF.
- **D26.6 Regulators, central banks and standard setters** — ناظران، بانکهای مرکزی و نهادهای استانداردگذار. `q:` SEC rule 15c3-5 market access · MiFID II RTS 6 algorithmic trading · BIS working papers markets · Federal Reserve SR letters. `r:` sec.gov; cftc.gov; esma.europa.eu; bis.org; federalreserve.gov; iosco.org.
- **D26.7 Industry research and asset-manager publications** — پژوهش صنعتی و انتشارات مؤسسات. `q:` AQR research library · Robeco research · MSCI research papers · Man Group insights. `r:` aqr.com; robeco.com; msci.com/research; man.com.
- **D26.8 Standards bodies and technical specifications** — نهادهای استاندارد و مشخصات فنی. `q:` FIX Trading Community specification · ISO 20022 financial messaging · IEEE 1588 precision time protocol. `r:` fixtrading.org; iso20022.org; IEEE standards.
- **D26.9 Open-source libraries and frameworks** — کتابخانهها و چارچوبهای متنباز. `q:` backtesting frameworks comparison (vectorbt, backtrader, zipline) · market simulation ABIDES · quantitative research libraries (statsmodels, arch, PyMC). `r:` project repositories and documentation.
- **D26.10 Critical appraisal and replication sources** — منابع نقد و تکرار. `q:` replication crisis finance papers · critical finance review · anomaly replication databases. `r:` Critical Finance Review; Chen & Zimmermann open-source asset pricing database.

---

## Expansion patterns (query construction)

Combine any concept `X` with these modifiers to reach the right literature layer:

| Pattern | Purpose | Example |
|---|---|---|
| `"X" survey` / `"X" review` | state of the art and open problems | `"market impact" survey` |
| `"X" out-of-sample` / `"X" robustness` | whether the effect survives honestly | `"momentum" out-of-sample robustness` |
| `"X" replication` / `"X" fails to replicate` | falsification layer | `"low volatility anomaly" replication` |
| `"X" transaction costs` / `"X" net of costs` | tradability filter | `"factor timing" transaction costs` |
| `"X" capacity` / `"X" at scale` | capital limits | `"statistical arbitrage" capacity` |
| `"X" regime` / `"X" non-stationary` | stability across states | `"volatility targeting" regime dependence` |
| `"X" crypto` / `"X" bitcoin` / `"X" perpetual futures` | market-specific transfer | `"order flow imbalance" crypto perpetual` |
| `"X" high frequency` / `"X" intraday` | horizon narrowing | `"price discovery" high frequency` |
| `"X" regulation` / `"X" compliance` | constraints layer | `"best execution" regulation` |
| `"X" implementation` / `"X" production` | engineering layer | `"backtest overfitting" implementation` |
| `site:` filters | restrict to source class | `site:arxiv.org "limit order book"`, `site:bis.org margin procyclicality`, `site:ssrn.com "funding rate"` |
| `filetype:pdf` | reach full texts | `"market impact" filetype:pdf` |
| `author:+year` | landmark papers | `Kyle 1985 continuous auctions insider trading` |

**Source-class grading (apply to every result before filing):**
`primary research` (refereed/working paper) · `independent replication or refutation` ·
`regulation or official standard` · `venue/technical documentation` · `industry white paper` ·
`practitioner claim`. Two entries with the same claim but different classes are not equivalent;
record the class with the entry.

**Saturation rule.** A domain is adequately covered when new searches return (a) re-citations of the
same primary sources, (b) no new independent replication, and (c) the same vocabulary variants already
recorded. At that point move to the next domain rather than deepening the same one.
