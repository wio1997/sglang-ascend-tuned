# 整合与验证记录

主要阅读入口：[代码分类与合并台账](../../CODE_STATUS.md)。

- `items.json`：功能目的、历史证据、当前合并决定、整合顺序、对应验证项。
- `file-classification.json`：68个现有Python文件的主要归属、SHA和运行角色；列出两个直接同目标冲突。
- `verification-plan.json`：尚未执行的统一验证计划；CPU检查不替代真实服务验证。
- `evidence/flash-record-index.json`：Flash原始证据文件的逻辑位置、SHA和范围。
- `REVIEW_MANIFEST.json`：本次新增记录的完整性清单，和原始源码归档清单分别维护。

历史源码继续保留原路径和字节内容。分类是索引，不是搬动文件或已经完成引擎整合。每个文件只登记一个主要归属，复杂共享caller仍需差异级审查。候选与参考不能因被记录而自动启用。
