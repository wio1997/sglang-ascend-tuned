# New-node porting and image publication

1. Inventory Docker, CPU architecture, accelerator model/count/HBM, driver, CANN compatibility, available storage, weights and actual interconnect. Old910C/A3 topology does not establish new-node connectivity.
2. Recover or obtain a compatible immutable base image. Historical image ID is not a pullable registry manifest digest. Match runtime source and paired MemFabric/MemCache13 ABI.
3. Export a single profile. Port historical role IDs and source-identity assertions, explicitly configure parameterized audit endpoints, keep source changes separate from configuration. Do not load historical sitecustomize from this archive as an unreviewed system hook.
4. Validate minimal real model correctness, precision, cache ownership, MTP/Graph and SDMA as applicable; remeasure representative performance. The catalog is evidence scope, not automatic deployment qualification.
5. Build once from source and a recorded Dockerfile/dependency lock. Publish a versioned image digest or hash-checked offline package, preload it on selected nodes, and select the model configuration at launch. Model weights remain external.

Actual deployment/build/profile work follows the user's local ZCode/DeepSeek execution preference. No old-server launcher or infrastructure credentials are bundled. No new image build, remote connection or NPU test was performed for this source consolidation.

## Upstream changes

The official source is preserved in this fork. Add/fetch an upstream remote, prepare upgrades on a separate branch, resolve module/profile conflicts and validate the affected cases before publishing a new image. Do not replace a newer MTP caller using the older eager diagnostic diff.950DT/vLLM code is a reference and requires its own SGLang/910C port.
