# 整合与验证记录

主要阅读入口：[代码分类与合并台账](../../CODE_STATUS.md)。

接手AI先读根目录[AGENTS.md](../../AGENTS.md)，再读[分类与提交规则](../../CONTRIBUTING_ASCEND.md)。登记结构为v2，具体枚举见`REGISTRY_RULES.json`；新条目与run模板在`examples/`，真实验证记录放`runs/`。

- `items.json`：功能目的、历史证据、当前合并决定、整合顺序、对应验证项。
- `file-classification.json`：69个Python文件的主要归属、SHA和运行角色（原68个及新增登记检查器）；列出两个直接同目标冲突。
- `verification-plan.json`：尚未执行的统一验证计划；CPU检查不替代真实服务验证。
- `evidence/flash-record-index.json`：Flash原始证据文件的逻辑位置、SHA和范围。
- `REVIEW_MANIFEST.json`：本次新增记录的完整性清单，和原始源码归档清单分别维护。

历史源码继续保留原路径和字节内容。分类是索引，不是搬动文件或已经完成引擎整合。每个文件只登记一个主要归属，复杂共享caller仍需差异级审查。候选与参考不能因被记录而自动启用。

提交前运行`python3 ascend_tuning/tools/verify_package.py`及`python3 ascend_tuning/tools/check_registry.py`。运行时修改另用`--base-ref`检查本次变动源码是否登记；记录内容变动后刷新REVIEW_MANIFEST，原始归档清单保持独立。
