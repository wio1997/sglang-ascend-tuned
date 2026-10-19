# 接手AI的入口

这是用户维护的SGLang Ascend调优仓库。会话中用户最新指示优先；以下规则用于保持代码、证据和提交可追溯，不构成额外审批要求。

开始修改前依次阅读：

1. `CONTRIBUTING_ASCEND.md`：分类、登记字段、验证状态、提交与合并规则。
2. `CODE_STATUS.md`：已有改动、范围、冲突和待办。
3. `ascend_tuning/integration/items.json`与`file-classification.json`：找已有ID，避免重复实现或覆盖别的模型。
4. `ascend_tuning/integration/verification-plan.json`：受影响配置的联合验证计划。升级底座时再读`UPSTREAM_UPDATES.md`。

核心要求：

- 一个独立目的一个稳定ID；分类描述用途，验证状态描述证据，不把“候选”当功能类别。
- 原GLM W8A8、Flash、W8A8C8分别记录配置和资格；跨模型修改列出受影响模型。
- 先登记，再修改。提交包含必要源码差异和同步更新的记录；未知或未测填`null`/`pending`，不补造结果。
- 历史全文件快照保留为归档；新引擎适配提取最小差异，不能整目录覆盖或直接复用旧launcher。
- 提交前运行`python3 ascend_tuning/tools/verify_package.py`和`python3 ascend_tuning/tools/check_registry.py`。运行时修改还按影响范围验证；CPU记录检查不等于NPU或性能通过。
- 实际资源、编译、部署、服务、模型、压测/profile及Git/GitHub写入使用用户指定的本机ZCode DeepSeek；读取与本地源码准备、CPU记录检查可由主控完成。执行入口从当前会话和本地配置获取，不把私有路径或凭证写入公开仓库。已有明确授权继续有效，不因为本文件重复索要许可。
- 用户自行安排月度版本，目标日期为2026-11-20；本文件不授权创建自动化、恢复暂停任务、操作其他服务或自动发布。
- 不修改系统SDK/驱动/BIOS/时钟或重启整机。公开网站使用HTTP/API/Web Search；需要浏览器时遵循用户许可。
- 不提交凭证、资产地址、权重、镜像二进制、provider或原始业务文本。原始失败及旧Tag不覆盖；有新证据就新增记录。

下一项工作由当前用户任务决定。不要仅因本文件或台账存在就启动模型实验、发消息给其他对话或创建新agent。
