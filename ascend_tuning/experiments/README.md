# Experiments — not enabled by default

- NoCopy: historicalC32 output411.96token/s vs389.87, but TPOT37.99ms vs36.66ms. The predefined decode improvement target failed. Included for reproducibility, not promoted.
- CPU descriptors: isolated fragmented fixture54.84->21.04ms; no model gain measured.
- Tokenizer queue: two short inputs3.718->1.639ms; no accepted long-input result.

These files are not imported by an enabled runtime profile. Hardware/service correctness and performance qualification must match the intended use.
