# APEX Engine Encyclopedia — Master Index

## Included engines

1. Structure
2. Liquidity
3. Volume
4. Volatility
5. FVG
6. Order Block
7. Correlation
8. Regime
9. Momentum
10. Trend
11. Context
12. Divergence
13. Pattern & Setup & Webhook & Framework
14. Wyckoff
15. RTM

## Dependency principle

```text
Canonical Data / Quality / Time
                |
                +--> Structure
                +--> Volatility
                +--> Volume
                +--> Liquidity
                +--> Momentum --> Trend
                +--> Correlation
                +--> Divergence
                +--> FVG
                +--> OrderBlock
                         |
                         +--> Context / Regime
                         |
                         +--> Wyckoff / RTM
                                   |
                                   v
                         Pattern / Setup / Framework
                                   |
                              Decision
                                   |
                           Independent Risk Veto
                                   |
                          Execution / Ledger
```

This is a conceptual DAG. Concrete runtime dependencies must be declared in schema-level contracts and checked for cycles.

## Important architectural distinction

The 15 engines are not 15 independent indicators. They form an evidence system. Outputs must preserve provenance and uncertainty so APEX can combine orthogonal information while controlling double-counting and correlation.

## Quality target

The goal is not “maximum complexity.” The goal is maximum defensible coverage: complete domain ontology, explicit assumptions, deterministic algorithms, point-in-time correctness, empirical validation, explainability, governance, and controlled evolution.
