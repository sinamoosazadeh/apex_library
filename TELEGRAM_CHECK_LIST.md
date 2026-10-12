بله. برای طراحی UI/UX ربات تلگرام APEX بهتر است موضوع را فقط به «متن و دکمه‌های هر صفحه» محدود نکنیم؛ باید یک Telegram Bot UI Design System کامل طراحی شود که تمام پنجره‌ها، اجزای ثابت، وضعیت‌ها، ناوبری، سلسله‌مراتب اطلاعات، رنگ/اموجی/تایپوگرافی، خطاها، Loading، Confirmation، جزئیات بازار و وضعیت خود سیستم را پوشش دهد.

در مرحله اول، فهرست زیر را به‌عنوان Master Design Checklist در نظر بگیر. فعلاً برای هر مورد توضیح را عمداً کوتاه نگه داشته‌ام تا بعداً بتوانیم هر بخش را جداگانه با جزئیات طراحی کنیم.


---

APEX Telegram Bot — Complete UI/UX Design Checklist

1. Global Design System

1.1 Visual Identity

[ ] نام و هویت بصری APEX

[ ] لوگو / آیکون

[ ] نمادهای اختصاصی APEX

[ ] زبان بصری کلی

[ ] سبک Institutional / Professional

[ ] میزان استفاده از تزئینات

[ ] سطح تراکم اطلاعات

[ ] قواعد استفاده از فضای خالی


1.2 Color System

[ ] رنگ Primary

[ ] رنگ Secondary

[ ] رنگ Accent

[ ] رنگ Success

[ ] رنگ Warning

[ ] رنگ Danger

[ ] رنگ Neutral

[ ] رنگ Disabled

[ ] رنگ Bullish

[ ] رنگ Bearish

[ ] رنگ Neutral Market

[ ] رنگ System Health

[ ] رنگ Risk

[ ] رنگ Execution

[ ] رنگ Data Quality

[ ] رنگ Forecast Confidence


1.3 Typography

[ ] متن عادی

[ ] عنوان

[ ] Subtitle

[ ] Label

[ ] Value

[ ] Numeric value

[ ] Percentage

[ ] Price

[ ] Timestamp

[ ] Status

[ ] Warning

[ ] Error

[ ] Caption

[ ] Monospace برای داده‌های فنی

[ ] Bold

[ ] Italic

[ ] Code formatting

[ ] Inline code

[ ] Strikethrough در صورت نیاز


1.4 Emoji System

[ ] Emojiهای مجاز

[ ] Emojiهای ممنوع

[ ] معنی هر Emoji

[ ] Emoji برای Market

[ ] Emoji برای Long

[ ] Emoji برای Short

[ ] Emoji برای Risk

[ ] Emoji برای Health

[ ] Emoji برای Data

[ ] Emoji برای Forecast

[ ] Emoji برای Execution

[ ] Emoji برای Warning

[ ] Emoji برای Error

[ ] Emoji برای Settings

[ ] Emoji برای Navigation

[ ] Emoji برای Refresh

[ ] Emoji برای Back

[ ] Emoji برای Home

[ ] Emoji برای Help


اصل مهم: هر Emoji باید semantic role مشخص داشته باشد؛ استفاده تزئینی و تصادفی ممنوع.


---

2. Message Architecture

برای هر پیام باید مشخص شود:

[ ] Header

[ ] Breadcrumb / Location

[ ] Context line

[ ] Main content

[ ] Metrics

[ ] Status

[ ] Warning

[ ] Footer

[ ] Navigation

[ ] Timestamp

[ ] Data freshness

[ ] Source

[ ] Confidence

[ ] Action area



---

3. User Location / Breadcrumb System

مثلاً:

🏠 APEX
└─ 📊 Market
   └─ ₿ BTCUSDT
      └─ 🔎 Analysis

باید مشخص شود:

[ ] آیا Breadcrumb در تمام صفحات وجود دارد؟

[ ] سطح فعلی کاربر

[ ] Parent screen

[ ] Current screen

[ ] Current asset

[ ] Current timeframe

[ ] Current mode

[ ] Current operation



---

4. Navigation System

4.1 Permanent Navigation

[ ] 🏠 Home

[ ] ◀️ Back

[ ] 🔄 Refresh

[ ] ❓ Help

[ ] ⚙️ Settings


مشخص شود کدام‌ها:

همیشه وجود دارند

فقط در صفحات خاص ظاهر می‌شوند

در صفحات حساس حذف می‌شوند.


4.2 Navigation Hierarchy

[ ] Home

[ ] Main Menu

[ ] Category Menu

[ ] Detail View

[ ] Sub-detail

[ ] Action View

[ ] Confirmation View

[ ] Result View



---

5. Main / Home Screen

باید مشخص شود:

[ ] Greeting

[ ] APEX status

[ ] Current market

[ ] Current asset

[ ] Current timeframe

[ ] Current system mode

[ ] System health

[ ] Active position

[ ] Latest signal

[ ] Market regime

[ ] Data freshness

[ ] Last update

[ ] Main navigation

[ ] Quick actions



---

6. Main Menu

گزینه‌های احتمالی:

[ ] 📊 Market

[ ] 🔎 Analysis

[ ] 🎯 Signals

[ ] 📈 Forecast

[ ] 💼 Portfolio

[ ] ⚠️ Risk

[ ] ⚙️ Settings

[ ] 🧠 Intelligence

[ ] 🩺 System Health

[ ] 📡 Data

[ ] 📋 Reports

[ ] 🧪 Research

[ ] ℹ️ About

[ ] ❓ Help


باید hierarchy نهایی تعیین شود.


---

7. Market Selection

[ ] Asset selector

[ ] Symbol selector

[ ] Market type

[ ] Exchange

[ ] Futures/Spot state

[ ] Current price

[ ] 24h change

[ ] Volume

[ ] Open Interest

[ ] Funding اگر در architecture مجاز باشد

[ ] Market status



---

8. Timeframe Selection

تمام Timeframeهای مجاز پروژه:

[ ] 1m

[ ] 3m

[ ] 5m

[ ] 15m

[ ] 30m

[ ] 1H

[ ] 2H

[ ] 4H

[ ] 6H

[ ] 12H

[ ] 1D

[ ] 3D

[ ] 1W

[ ] 1M


همچنین:

[ ] Current TF indicator

[ ] Multi-TF selection

[ ] MTF status

[ ] Synchronization status



---

9. Market Overview Window

[ ] Price

[ ] Price change

[ ] Volume

[ ] OI

[ ] Volatility

[ ] Regime

[ ] Trend

[ ] Momentum

[ ] Structure

[ ] Liquidity

[ ] Data quality

[ ] Snapshot timestamp



---

10. Market Structure Window

[ ] Trend state

[ ] HH

[ ] HL

[ ] LH

[ ] LL

[ ] BOS

[ ] CHOCH

[ ] Structure strength

[ ] Structural bias

[ ] Swing information

[ ] MTF structure

[ ] Confirmation state



---

11. Liquidity Window

[ ] BSL

[ ] SSL

[ ] EQH

[ ] EQL

[ ] Liquidity pools

[ ] Liquidity sweep

[ ] Liquidity grab

[ ] Liquidity void

[ ] Distance to liquidity

[ ] Liquidity strength

[ ] Liquidity status



---

12. FVG Window

[ ] Active FVGs

[ ] Bullish FVG

[ ] Bearish FVG

[ ] FVG size

[ ] FVG age

[ ] FVG mitigation

[ ] FVG fill %

[ ] FVG strength

[ ] FVG timeframe

[ ] FVG status

[ ] Nearest FVG



---

13. Order Block Window

[ ] Bullish OB

[ ] Bearish OB

[ ] OB timeframe

[ ] OB origin

[ ] OB size

[ ] OB strength

[ ] Mitigation state

[ ] Retest state

[ ] Freshness

[ ] Distance

[ ] Validity

[ ] Expiration



---

14. Wyckoff Window

[ ] Phase

[ ] Event

[ ] Composite structure

[ ] Accumulation

[ ] Distribution

[ ] Spring

[ ] Upthrust

[ ] SOS

[ ] SOW

[ ] Sign of Strength

[ ] Sign of Weakness

[ ] Wyckoff confidence

[ ] Phase maturity



---

15. Analyst Dashboard

برای هر Analyst:

[ ] Analyst name

[ ] Status

[ ] Direction

[ ] Evidence count

[ ] Confidence

[ ] Reliability

[ ] Independence

[ ] Freshness

[ ] Agreement

[ ] Conflict

[ ] Degradation state



---

16. Evidence Fabric Window

[ ] Evidence events

[ ] Evidence source

[ ] Analyst

[ ] Timestamp

[ ] Snapshot ID

[ ] Evidence type

[ ] Direction

[ ] Strength

[ ] Confidence

[ ] Validity

[ ] Expiry

[ ] Contradictions



---

17. Confluence Window

[ ] Number of agreeing analysts

[ ] Independent evidence

[ ] Correlated evidence

[ ] Confluence score

[ ] Conflict score

[ ] Evidence density

[ ] Zone overlap

[ ] Directional consensus

[ ] Quality-adjusted consensus



---

18. Context Window

[ ] Market regime

[ ] Volatility regime

[ ] Trend

[ ] Structure

[ ] Liquidity

[ ] Volume

[ ] Momentum

[ ] Correlation

[ ] MTF context

[ ] Anomaly state

[ ] Context confidence



---

19. Forecast Window

[ ] Forecast direction

[ ] Forecast horizon

[ ] Probability

[ ] Confidence

[ ] Calibration state

[ ] Forecast health

[ ] OOD status

[ ] Scenario

[ ] Alternative scenario

[ ] Forecast invalidation

[ ] Forecast timestamp



---

20. Signal Window

[ ] Signal direction

[ ] Signal type

[ ] Confidence

[ ] Evidence

[ ] Context

[ ] Forecast

[ ] Risk approval

[ ] Execution readiness

[ ] Signal age

[ ] Signal validity

[ ] Invalidation



---

21. Decision Window

تفکیک بسیار مهم:

Evidence
   ↓
Context
   ↓
Forecast
   ↓
Opportunity
   ↓
Risk Veto
   ↓
Decision

برای UI:

[ ] Evidence state

[ ] Opportunity state

[ ] Forecast state

[ ] Risk state

[ ] Veto state

[ ] Final decision

[ ] Decision rationale



---

22. Risk Window

[ ] Risk state

[ ] Risk score

[ ] Exposure

[ ] Concentration

[ ] Correlation risk

[ ] Volatility risk

[ ] Drawdown state

[ ] Circuit breaker

[ ] Veto

[ ] Risk budget

[ ] Position constraints



---

23. Portfolio Window

[ ] Portfolio state

[ ] Open positions

[ ] Exposure

[ ] Long exposure

[ ] Short exposure

[ ] Concentration

[ ] Correlation

[ ] Unrealized PnL

[ ] Realized PnL

[ ] Portfolio risk

[ ] Portfolio health



---

24. Position Window

برای هر Position:

[ ] Symbol

[ ] Side

[ ] Entry

[ ] Current price

[ ] Size

[ ] Exposure

[ ] PnL

[ ] PnL %

[ ] Duration

[ ] Position state

[ ] Risk state

[ ] Execution state

[ ] Last reconciliation



---

25. Execution Window

[ ] Execution state

[ ] Order state

[ ] Requested price

[ ] Executed price

[ ] Quantity

[ ] Execution latency

[ ] Execution deviation

[ ] Fees

[ ] Partial fill

[ ] Rejection

[ ] Retry

[ ] Reconciliation



---

26. System Health Window

Health Domains

[ ] Observation

[ ] Snapshot

[ ] Intelligence

[ ] Forecast

[ ] Risk

[ ] Portfolio

[ ] Execution

[ ] Resource

[ ] Recovery


هرکدام:

[ ] Healthy

[ ] Degraded

[ ] Critical

[ ] Unknown



---

27. Data Health Window

[ ] Connection

[ ] Source health

[ ] Freshness

[ ] Missing candles

[ ] Duplicate candles

[ ] Timestamp validity

[ ] OHLC validity

[ ] OI quality

[ ] Schema validity

[ ] Quarantine state

[ ] Data completeness



---

28. Snapshot Window

[ ] Snapshot ID

[ ] as_of

[ ] Creation timestamp

[ ] Market timestamp

[ ] Timeframes

[ ] Data sources

[ ] Data hash

[ ] Completeness

[ ] Immutability

[ ] Replayability



---

29. MTF Dashboard

برای هر TF:

1m    ↑ Bullish
5m    ↑ Bullish
15m   → Neutral
1H    ↑ Bullish
4H    ↑ Bullish
1D    → Neutral

همچنین:

[ ] Alignment

[ ] Conflict

[ ] Dominant TF

[ ] Higher-TF bias

[ ] Lower-TF trigger

[ ] MTF confidence



---

30. Alerts / Notifications

[ ] Signal notification

[ ] Position notification

[ ] Risk notification

[ ] Execution notification

[ ] Data failure

[ ] System degradation

[ ] Circuit breaker

[ ] Recovery

[ ] Forecast degradation



---

31. Status Indicators

استاندارد واحد برای:

[ ] 🟢 Active

[ ] 🟡 Degraded

[ ] 🔴 Critical

[ ] ⚪ Unknown

[ ] 🔵 Informational

[ ] ⏳ Pending

[ ] ✓ Confirmed

[ ] ✕ Rejected

[ ] ⛔ Vetoed



---

32. Vertical Indicator / Quote Block System

همان چیزی که اشاره کردی باید به‌صورت Design Primitive تعریف شود.

مثلاً:

│ Market Regime
│
│ Trending
│ Confidence: 82%
│ Volatility: Elevated

باید مشخص شود:

[ ] کاربرد

[ ] رنگ

[ ] ضخامت

[ ] hierarchy

[ ] چه زمانی استفاده شود

[ ] چه زمانی استفاده نشود

[ ] تفاوت Info / Warning / Critical

[ ] آیا برای Context استفاده شود یا Status



---

33. Cards

[ ] Metric Card

[ ] Status Card

[ ] Signal Card

[ ] Position Card

[ ] Analyst Card

[ ] Risk Card

[ ] Forecast Card

[ ] Health Card

[ ] Evidence Card

[ ] Error Card



---

34. Tables

[ ] Market table

[ ] MTF table

[ ] Analyst table

[ ] Evidence table

[ ] Position table

[ ] Execution table

[ ] Risk table

[ ] System health table



---

35. Buttons

Navigation

[ ] Home

[ ] Back

[ ] Close

[ ] Cancel


Action

[ ] Analyze

[ ] Refresh

[ ] Retry

[ ] Confirm

[ ] Reject

[ ] Apply

[ ] Reset


Context

[ ] Details

[ ] More

[ ] Explain

[ ] Evidence

[ ] History



---

36. Button States

برای هر Button:

[ ] Normal

[ ] Selected

[ ] Disabled

[ ] Loading

[ ] Error

[ ] Success

[ ] Expired

[ ] Permission denied



---

37. Loading States

[ ] Initial loading

[ ] Data loading

[ ] Analysis loading

[ ] Forecast loading

[ ] Refresh loading

[ ] Execution loading


و مشخص شود آیا:

⏳ Updating market data...

یا:

⏳
Analyzing...

نمایش داده شود.


---

38. Empty States

[ ] No position

[ ] No signal

[ ] No FVG

[ ] No OB

[ ] No liquidity

[ ] No forecast

[ ] No evidence

[ ] No data

[ ] No history



---

39. Error States

[ ] Data unavailable

[ ] Timeout

[ ] Invalid snapshot

[ ] Analyst failure

[ ] Forecast failure

[ ] Risk engine failure

[ ] Execution failure

[ ] Permission failure

[ ] Internal error



---

40. Degradation States

این بخش برای APEX بسیار مهم است.

[ ] Normal

[ ] Partial degradation

[ ] Intelligence degradation

[ ] Forecast degradation

[ ] Risk degradation

[ ] Execution degradation

[ ] Data degradation

[ ] Safe mode

[ ] Recovery



---

41. Confirmation Windows

برای عملیات حساس:

[ ] Action

[ ] Reason

[ ] Consequence

[ ] Current state

[ ] Requested state

[ ] Confirm

[ ] Cancel



---

42. Explanation / Why Window

برای پاسخ به:

> Why did APEX produce this decision?



نمایش:

[ ] Evidence

[ ] Context

[ ] Forecast

[ ] Risk

[ ] Veto

[ ] Final rationale



---

43. Evidence Drill-Down

Signal
 ↓
Decision
 ↓
Context
 ↓
Evidence
 ↓
Analyst
 ↓
Raw Observation

کاربر باید بتواند از نتیجه به شواهد underlying برسد.


---

44. History

[ ] Signal history

[ ] Decision history

[ ] Position history

[ ] Execution history

[ ] Forecast history

[ ] Risk history

[ ] System events

[ ] Configuration history



---

45. Audit View

[ ] Event ID

[ ] Snapshot ID

[ ] Decision ID

[ ] Timestamp

[ ] Actor

[ ] State before

[ ] State after

[ ] Reason

[ ] Evidence

[ ] Version



---

46. System Event Log

[ ] Startup

[ ] Shutdown

[ ] Data reconnect

[ ] Snapshot creation

[ ] Analyst execution

[ ] Decision

[ ] Risk veto

[ ] Execution

[Recovery

[ ] Configuration change



---

47. Settings

User Settings

[ ] Language

[ ] Timezone

[ ] Notifications

[ ] Display density

[ ] Numeric precision


Market Settings

[ ] Symbol

[ ] Timeframe

[ ] MTF profile


System Settings

[ ] Mode

[ ] Refresh

[ ] Data source

[ ] Diagnostics



---

48. Display Preferences

[ ] Compact

[ ] Standard

[ ] Detailed

[ ] Expert


این مورد برای رباتی با حجم اطلاعات APEX بسیار ارزشمند است.


---

49. Information Density

برای هر صفحه مشخص شود:

[ ] Minimal

[ ] Normal

[ ] Detailed

[ ] Diagnostic



---

50. Precision Rules

[ ] Price decimals

[ ] Percentage decimals

[ ] Volume decimals

[ ] OI decimals

[ ] Confidence

[ ] Probability

[ ] Timestamp precision

[ ] Duration



---

51. Timestamp System

[ ] Exchange time

[ ] UTC

[ ] Local time

[ ] Relative time

[ ] as_of

[ ] Last update

[ ] Data age



---

52. Freshness Indicators

مثلاً:

Data: ✓ Fresh
Updated: 4s ago

و:

Data: ⚠ Stale
Age: 43s


---

53. Confidence Visualization

[ ] Confidence %

[ ] Confidence tier

[ ] Reliability

[ ] Calibration

[ ] Uncertainty

[ ] OOD


نباید Confidence و Probability بدون تعریف دقیق به‌جای هم استفاده شوند.


---

54. Market Regime UI

[ ] Trending

[ ] Ranging

[ ] High Volatility

[ ] Low Volatility

[ ] Transition

[ ] Uncertain



---

55. Signal Lifecycle UI

Detected
→ Validated
→ Confirmed
→ Active
→ Invalidated
→ Expired
→ Closed


---

56. Position Lifecycle UI

Requested
→ Accepted
→ Submitted
→ Partially Filled
→ Filled
→ Managed
→ Closing
→ Closed
→ Reconciled


---

57. Forecast Lifecycle

[ ] Generated

[ ] Active

[ ] Updated

[ ] Invalidated

[ ] Expired

[ ] Evaluated



---

58. Risk Lifecycle

[ ] Approved

[ ] Restricted

[ ] Vetoed

[ ] Emergency

[ ] Recovered



---

59. System Mode

[ ] LIVE

[ ] PAPER

[ ] RESEARCH

[ ] SAFE

[ ] DEGRADED

[ ] MAINTENANCE

[ ] RECOVERY



---

60. Environment Indicator

هر صفحه در صورت نیاز مشخص کند:

ENV: LIVE

یا:

ENV: PAPER

تا ambiguity ایجاد نشود.


---

61. Asset Context Persistence

مشخص شود آیا انتخاب:

BTCUSDT
4H

در تمام صفحات حفظ می‌شود یا خیر.


---

62. User Context Persistence

[ ] Current screen

[ ] Current symbol

[ ] Current TF

[ ] Current mode

[ ] Last action

[ ] Navigation stack



---

63. Refresh Architecture

[ ] Manual refresh

[ ] Automatic refresh

[ ] Last refresh

[ ] Refresh state

[ ] Refresh failure

[ ] Retry



---

64. Retry Architecture

[ ] Retry button

[ ] Retry count

[ ] Retry reason

[ ] Retry cooldown

[ ] Automatic retry

[ ] Escalation



---

65. Back Behavior

باید دقیقاً تعریف شود:

[ ] Back به parent

[ ] Back به previous state

[ ] Back به Home

[ ] Back after action

[ ] Back after error

[ ] Back during loading



---

66. Home Behavior

[ ] Always available

[ ] State reset یا حفظ state

[ ] Navigation stack reset

[ ] Context preservation



---

67. Help System

[ ] Contextual Help

[ ] Global Help

[ ] Glossary

[ ] FAQ

[ ] Command reference

[ ] Error explanations



---

68. Glossary

برای اصطلاحات تخصصی:

[ ] BOS

[ ] CHOCH

[ ] FVG

[ ] OB

[ ] BSL

[ ] SSL

[ ] OI

[ ] MTF

[ ] OOD

[ ] PIT

[ ] Confluence

[ ] Snapshot

[ ] Evidence

[ ] Forecast

[ ] Veto



---

69. Command System

[ ] /start

[ ] /home

[ ] /market

[ ] /analysis

[ ] /signal

[ ] /portfolio

[ ] /risk

[ ] /health

[ ] /settings

[ ] /help


البته commandهای نهایی باید با architecture واقعی APEX منطبق شوند.


---

70. Deep-Linking

[ ] Symbol link

[ ] Signal link

[ ] Position link

[ ] Report link

[ ] Event link



---

71. Notification Design System

برای هر Notification:

[ ] Severity

[ ] Title

[ ] Event

[ ] Context

[ ] Timestamp

[ ] Action

[ ] Dismiss

[ ] Details



---

72. Notification Priority

[ ] INFO

[ ] LOW

[ ] MEDIUM

[ ] HIGH

[ ] CRITICAL



---

73. Critical Alerts

مثلاً:

🔴 CRITICAL

Execution state cannot be reconciled.

System entered SAFE mode.

باید برای Critical Alertها layout کاملاً مشخص داشته باشی.


---

74. Risk/Veto Messaging

به‌جای:

> Signal rejected.



بهتر است ساختار:

⛔ ENTRY VETOED

Opportunity: VALID
Forecast: VALID
Risk: BLOCKED

Reason:
Portfolio concentration exceeds limit.

به‌صورت Design Pattern تعریف شود.


---

75. Decision Transparency

هر Decision مهم:

[ ] What

[ ] Why

[ ] Evidence

[ ] Confidence

[ ] Risk

[ ] Constraint

[ ] Final state



---

76. Data Provenance UI

[ ] Source

[ ] Timestamp

[ ] Snapshot

[ ] Data version

[ ] Transformation

[ ] Validation state



---

77. Research UI

[ ] Research status

[ ] Hypothesis

[ ] Dataset

[ ] Experiment

[ ] Result

[ ] Confidence

[ ] Promotion state



---

78. Configuration Version UI

[ ] Active configuration

[ ] Version

[ ] Effective date

[ ] Previous version

[ ] Change reason

[ ] Approval



---

79. System Version UI

[ ] APEX version

[ ] Architecture revision

[ ] Intelligence version

[ ] Risk version

[ ] Execution version

[ ] Configuration version



---

80. Health Score

[ ] Overall health

[ ] Data health

[ ] Intelligence health

[ ] Forecast health

[ ] Risk health

[ ] Execution health

[ ] Resource health



---

81. Resource Monitor

[ ] CPU

[ ] RAM

[ ] Disk

[ ] Network

[ ] Queue

[ ] Processing latency

[ ] API latency

[ ] Event backlog



---

82. Diagnostics

[ ] Connectivity

[ ] Data

[ ] Snapshot

[ ] Analyst

[ ] Forecast

[ ] Risk

[ ] Execution

[ ] Storage

[ ] Resource



---

83. Maintenance Mode

[ ] Maintenance banner

[ ] Reason

[ ] Start

[ ] Expected duration

[ ] Current state



---

84. Safe Mode

[ ] Why activated

[ ] What is disabled

[ ] What remains operational

[ ] Recovery condition

[ ] Current health



---

85. Recovery UI

Recovery in progress

✓ Data connection
✓ Snapshot integrity
✓ Analyst health
⏳ Execution reconciliation
○ Normal operation


---

86. Auditability

برای هر خروجی حساس:

[ ] Unique ID

[ ] Timestamp

[ ] Snapshot

[ ] Version

[ ] Evidence

[ ] Decision

[ ] Actor

[ ] Result



---

87. Accessibility

[ ] Emoji-only meaning ممنوع

[ ] متن جایگزین برای status

[ ] رنگ به‌تنهایی معیار نباشد

[ ] خوانایی روی موبایل

[ ] خطوط کوتاه

[ ] جلوگیری از پیام‌های بیش از حد متراکم

[ ] سازگاری با screen reader تا حد امکان



---

88. Mobile Optimization

[ ] Message width

[ ] Button width

[ ] تعداد دکمه در هر ردیف

[ ] طول متن

[ ] Scroll burden

[ ] Deep navigation burden

[ ] اطلاعات ضروری در بالای صفحه



---

89. Message Length Policy

[ ] Short message

[ ] Standard message

[ ] Detailed message

[ ] Diagnostic message

[ ] Pagination strategy



---

90. Pagination

برای:

[ ] History

[ ] Evidence

[ ] Signals

[ ] Positions

[ ] Events

[ ] Analysts

[ ] Research



---

91. Expand / Collapse

[ ] Summary

[ ] Details

[ ] Advanced details

[ ] Raw data

[ ] Diagnostics


در Telegram معمولاً با navigation به صفحه جزئیات پیاده‌سازی می‌شود.


---

92. Progressive Disclosure

اصل:

Summary
   ↓
Details
   ↓
Evidence
   ↓
Raw technical information

کاربر عادی نباید مجبور شود تمام جزئیات فنی را در صفحه اول ببیند.


---

93. Expert Mode

برای کاربر حرفه‌ای:

[ ] Raw metrics

[ ] Analyst IDs

[ ] Snapshot IDs

[ ] Evidence IDs

[ ] Model metadata

[ ] Latency

[ ] Health

[ ] Diagnostics



---

94. Debug Mode

[ ] Raw events

[ ] Internal state

[ ] IDs

[ ] Timing

[ ] Errors

[ ] Stack/reference

[ ] Data validation



---

95. Security UI

[ ] Authentication state

[ ] Authorization state

[ ] Session

[ ] Sensitive action confirmation

[ ] Admin-only screens

[ ] Permission denied

[ ] Session expiry



---

96. Admin UI

[ ] System control

[ ] Health

[ ] Configuration

[ ] Users

[ ] Audit

[ ] Research

[ ] Diagnostics

[ ] Maintenance



---

97. Role-Based UI

مثلاً:

[ ] Viewer

[ ] Trader

[ ] Analyst

[ ] Researcher

[ ] Operator

[ ] Administrator


هر role باید UI مجاز خودش را داشته باشد.


---

98. State Machine Design

برای هر پنجره:

ENTER
 ↓
LOADING
 ↓
READY
 ↓
ACTION
 ↓
RESULT
 ↓
EXIT

و تمام transitionهای exception نیز تعریف شوند.


---

99. Global UI State Model

باید مشخص شود:

USER
 ├── Navigation State
 ├── Market Context
 ├── Display Preferences
 └── Permission State

SYSTEM
 ├── Runtime State
 ├── Health State
 ├── Data State
 ├── Intelligence State
 ├── Risk State
 └── Execution State


---

100. UI Contract

برای هر Screen یک قرارداد استاندارد تعریف کن:

screen:
  id:
  name:
  purpose:
  entry_points:
  exit_points:

context:
  symbol:
  timeframe:
  mode:

data:
  inputs:
  outputs:

visual:
  header:
  body:
  footer:

navigation:
  parent:
  children:
  back:
  home:

states:
  loading:
  ready:
  empty:
  degraded:
  error:

actions:
  primary:
  secondary:

permissions:

refresh:

audit:

localization:


---

101. Screen Inventory

در نهایت باید یک Registry مرکزی داشته باشی:

SCREEN_REGISTRY

که تمام پنجره‌های ربات در آن ثبت باشند.

برای هر Screen:

ID

Name

Purpose

Parent

Children

Inputs

Outputs

State

Actions

Permissions

Dependencies

Navigation

Error states



---

102. Component Registry

همین کار برای اجزای UI:

COMPONENT_REGISTRY

مثلاً:

Header

Breadcrumb

Metric

Status

SignalCard

RiskCard

HealthCard

EvidenceBlock

NavigationBar

AlertBlock

ErrorBlock

Timestamp

RefreshButton



---

103. Emoji Registry

یک registry رسمی:

EMOJI_REGISTRY

مثلاً:

success: "✓"
warning: "⚠️"
critical: "🔴"
home: "🏠"
back: "◀️"
refresh: "🔄"
market: "📊"
risk: "🛡️"

تا developer در هر فایل Emoji دلخواه انتخاب نکند.


---

104. Text / Copy Registry

تمام متن‌های UI باید قابل مدیریت باشند:

UI_COPY_REGISTRY

شامل:

titles

labels

buttons

warnings

errors

confirmations

help text

status messages



---

105. Formatting Registry

قواعد واحد برای:

[ ] Bold

[ ] Italic

[ ] Code

[ ] Quote

[ ] Headers

[ ] Separators

[ ] Emoji

[ ] Numbers

[ ] Percentages

[ ] Dates

[ ] Prices



---

106. Separator System

مثلاً:

━━━━━━━━━━━━━━

یا:

──────────────

یا:

┄┄┄┄┄┄┄┄┄┄┄

اما باید فقط یک سیستم استاندارد انتخاب شود و کاربرد هر نوع separator تعریف شود.


---

107. Header Patterns

مثلاً:

📊 MARKET OVERVIEW
BTCUSDT · 4H

یا:

🏠 APEX
› Market
› BTCUSDT

باید pattern رسمی انتخاب شود.


---

108. Footer Patterns

مثلاً:

Updated 12s ago · Snapshot #A91F

یا:

APEX GEN5 · LIVE


---

109. Data Source Footer

برای داده‌های حساس:

Source: Toobit
As of: 19:42:18 UTC


---

110. Final UI Consistency Matrix

در پایان باید یک ماتریس داشته باشی که برای تمام صفحات مشخص کند:

Screen	Header	Breadcrumb	Context	Status	Refresh	Back	Home	Timestamp	Footer

Home	✓	—	✓	✓	✓	—	—	✓	✓
Market	✓	✓	✓	✓	✓	✓	✓	✓	✓
Analysis	✓	✓	✓	✓	✓	✓	✓	✓	✓
Signal	✓	✓	✓	✓	✓	✓	✓	✓	✓
Risk	✓	✓	✓	✓	✓	✓	✓	✓	✓
Health	✓	✓	✓	✓	✓	✓	✓	✓	✓


این ماتریس باید در نهایت برای تک‌تک Screenهای واقعی APEX تکمیل شود.


---

پیشنهاد من برای مرحله بعد

به‌نظر من نباید هنوز وارد طراحی تک‌تک صفحات شویم. ابتدا همین Master Checklist را به یک APEX Telegram UI/UX Design Specification تبدیل کنیم و آن را به ۶ لایه تقسیم کنیم:

L0 — DESIGN TOKENS
     ↓
L1 — UI PRIMITIVES
     ↓
L2 — COMPONENTS
     ↓
L3 — SCREEN TEMPLATES
     ↓
L4 — SCREEN/SYSTEM REGISTRY
     ↓
L5 — USER FLOWS & STATE MACHINES
     ↓
L6 — FINAL TELEGRAM UI SPEC

بعد برای هر پنجره‌ای که تو طراحی می‌کنی، من آن را صرفاً از نظر «زیبا بودن» بررسی نمی‌کنم؛ بلکه آن را علیه این قرارداد بررسی می‌کنم:

Visual consistency → Information hierarchy → Navigation → State coverage → Data semantics → APEX architecture alignment → Error/degradation handling → Mobile usability → Telegram constraints → Implementation ambiguity

این روش باعث می‌شود در نهایت چیزی که به تیم برنامه‌نویسی می‌دهی صرفاً مجموعه‌ای از mockupها نباشد، بلکه یک UI Contract قابل پیاده‌سازی و بدون ابهام باشد.