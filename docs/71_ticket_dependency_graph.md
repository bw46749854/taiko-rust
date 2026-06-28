# 71. Ticket Dependency Graph

Status: canonical

```text
TKT-0000
  -> GATE-0000
  -> GATE-0010
  -> GATE-0020
  -> TKT-0001 Loop CLI MVP
      -> GATE-0030
      -> TKT-0002 Fixture validation MVP
          -> GATE-0040
          -> TKT-0003 Headless autoplay MVP
              -> GATE-0050
              -> TKT-0004 Timing analyzer MVP
                  -> GATE-0060
                  -> TKT-0040 Failure feedback loop MVP
                      -> GATE-0070
                      -> TKT-0050 QA regression gate MVP
                          -> GATE-0080
                          -> TKT-0060 Phase1 feature loop entry
                              -> GATE-0090
                              -> TKT-0005 BPM / MEASURE / DELAY / OFFSET timeline
                                  -> TKT-0006 Roll / balloon / BalloonEx
                                  -> TKT-0007 GOGO / BARLINE
                                  -> TKT-0010 Headless autoplay baseline expansion
                                      -> TKT-0011 Score / gauge / clear
                                      -> TKT-0012 SCROLL / NMSCROLL / BMSCROLL / HBSCROLL
                                          -> TKT-0013 SUDDEN / DIRECTION / JPOSSCROLL parse/report
                                      -> TKT-0014 Timing log schema expansion
                                          -> TKT-0015 Timing log analyzer expansion
                                              -> TKT-0035 Synthetic fixture coverage pack
                                                  -> TKT-0075 User-selected song validation harness
                                  -> TKT-0008 Branch parser
                                      -> TKT-0009 Branch condition evaluator
```

## Critical path

The critical path is:

```text
TKT-0000 -> gates -> TKT-0001 -> GATE-0030 -> TKT-0002 -> GATE-0040 -> TKT-0003 -> GATE-0050 -> TKT-0004 -> GATE-0060 -> TKT-0040 -> GATE-0070 -> TKT-0050 -> GATE-0080 -> TKT-0060 -> GATE-0090 -> TKT-0005 -> TKT-0010 -> TKT-0011/TKT-0012 -> TKT-0014 -> TKT-0015 -> TKT-0035 -> TKT-0075
```

## Parallelization

After `TKT-0060` and `GATE-0090`, `TKT-0005` begins as the first gameplay ticket. After `TKT-0005`, the following can proceed in parallel under separate implementation worktrees when their dependency rows are satisfied:

- roll/balloon work,
- GOGO/BARLINE work,
- scroll work,
- branch parser work.

Plan review and QA remain separate for every branch.
