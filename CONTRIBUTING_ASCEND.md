# 分类、登记、验证与提交规则

本文件是接手AI与维护者的操作说明。规则机器定义见[REGISTRY_RULES.json](ascend_tuning/integration/REGISTRY_RULES.json)，现有范围见[CODE_STATUS.md](CODE_STATUS.md)。登记结构已升级为v2；原来23项的历史范围保留，没有因此晋升运行资格。

当前登记以`integration/items.json`及`file-classification.json`为准。根说明中的`CODE_STATUS.md`是人类阅读摘要，同步维护；`catalog.json`是初次归档清单，`SOURCE_INDEX.json`及`PACKAGE_MANIFEST.json`是归档身份，不把它们当作独立的现行准入表。`verification-plan.json`是计划，`runs/`才是新候选的真实结果记录。

## 1. 按什么单位登记

一项独立目的一个ID。例如“页表步长不再触发重复编译”是`F-STRIDE`，“按attention组分配查询”是`F-QUERY`。多个文件可以属于同一项；同一文件可能服务多项，文件清单登记主要归属，其他关系写入说明。不要把每个文件称为一项优化，也不要把整场对话塞进一个无边界条目。

先搜索已有ID和源码路径。目的相同就在原项下补实现/证据；目的不同才新建。既有ID不改名、不复用。Flash用`F-`，普通W8A8用`G-`，C8用`C8-`，通用引擎用`CORE-`，实验用`X-`，资料用`R-`；既有工具项`TOOLS`保留。跨模型记录在`model`中明确所有影响对象，并在`scope.profiles`列实际配置。

## 2. 分类只说明用途

| category | 用途 | 示例 |
|---|---|---|
| adaptation | 模型或后端接入 | Flash加载、SDMA PD |
| correctness | 数值、状态、布局、生命周期修复 | FP32尾部、取消回收 |
| performance | 保持正确性前提下提速 | 步长去特化、查询并行 |
| configuration | 仅参数、缓冲、拓扑变化 | HCCL/DeepEP大小 |
| observability_test | 审计、采样、测试门控 | payload核对、测试等待 |
| deployment_support | 构建、预检和启动支持 | SDK扩展构建 |
| tooling | 仓库管理工具 | 记录检查、profile导出 |
| reference | 其他框架/硬件参考 | 950DT/vLLM资料 |

以主要目的选择一个分类。候选、实验、失败和通过由独立状态表达。修复顺便提速时主要归`correctness`，收益另记；能独立验证的性能改动拆出独立提交和ID。必须一起改变的接口/实现可同提交，但说明耦合原因。

## 3. 怎么填写登记表

从[新条目模板](ascend_tuning/integration/examples/new-item.json)复制对象到`items.json`的`items`数组，替换示例ID及内容。模板不是已实现功能。至少填写：

| 字段 | 规则 |
|---|---|
| id / title / summary | 稳定编号、名称、具体触发问题与期望行为 |
| model / category | 适用模型和主要用途 |
| source_presence | 源码是否在归档、部分存在、尚未收录、仅计划、仅配置或参考 |
| source_paths | 仓库内的实际源码路径；尚无实现可为空，但不能宣称已整合 |
| configuration_paths / reference_paths | 如适用，列配置或参考文件 |
| scope | 基础源码提交、硬件范围、profile及限制；未知值留null或空数组并解释 |
| integration_after | 本次整合顺序，引用真实ID；不是声称物理算法必然依赖 |
| required_validation | 引用verification-plan中验证项；按影响增加，不机械照搬全部压测 |
| evidence_refs | 仓库内证据索引或摘要路径；外部证据先写可追溯摘要与SHA，不上传私有原文 |
| validation_runs | 新候选的真实run记录路径；没有新实测保持空数组 |
| validation_state | 验证到什么范围，见下一节 |
| integration_state / merge_policy | 源码整合状态及允许如何合并 |
| rollback | 旧运行提交、profile及回退说明；尚无运行版写null并说明 |
| upstream | 是否核查官方目标提交、保留/改写/已被官方覆盖的决定及证据 |
| notes | 风险、配置限制、不能外推的结论及其他消费者 |

现有`historical_evidence`保留为历史摘要，`development_merge`保留为详细行动建议。机器准入以新的验证状态、merge_policy及真实run记录为准。全局source_collection_commit指归档来源，不是所有功能都在该提交实机通过。

## 4. 状态如何变化

`validation_state`：

- `pending`：未验证。
- `source_only`：仅源码/记录或CPU完整性审查，未获运行资格。
- `component_pass`：组件通过；必须说明CPU或NPU、形状、dtype和并行组。
- `historical_scoped_pass`：旧冻结环境的有限范围通过；新组合/新机器不自动继承。
- `candidate_pass`：精确候选及声明配置通过相应联合验证，须链接真实run记录。
- `failed`：当前候选未过；原始失败保留，新修复另起run。
- `not_applicable`：纯参考项，不适用资格。

`integration_state`：`planned`、`archived`、`in_progress`、`integrated`、`verified`、`released`、`retired`。`integrated`只说明实现接入；`verified`或`released`必须有候选通过证据。纯工具可用对应CPU验证，不强求NPU测试。

`merge_policy`：`development_candidate`可按受影响正确性整合；`hold_integration`待解决明确缺口；`experimental_only`只保留隔离实验且默认关闭；`reference_only`仅资料；`tooling_only`只涉及工具。实验或参考不能直接标为稳定发布。性能负收益不删除历史数据，应保持实验状态或说明取舍。

状态可以因回归失败降级，但保留旧run。检查器不能证明真实硬件与数字真实性，AI必须检查原始证据。

候选通过的检查结果必须绑定同一源码及同一目标模型、配置和运行环境，不能把Graph关闭时的功能结果与Graph开启时的性能结果拼成一次完整通过。组件或CPU静态证据可作为来源复用，联合运行记录仍需说明这些证据适用当前组合。

## 5. 源文件与证据怎么放

- `profiles`、`SOURCE_INDEX.json`、原`PACKAGE_MANIFEST.json`承载归档源码身份，保持原件；已有归档文件不能悄悄变更字节或SHA。
- 新引擎整合写标准`python/sglang/`等对应模块，只引入必要差异；模型专属模块与公共入口分清。公共conn/transfer或caller需同时审查受影响模型。
- 在`file-classification.json`登记新修改的自定义源码、SHA、主要ID、角色；不是要求登记全部官方源文件。变更SHA与实际文件同步。删除或移动的旧实现记录在`retired_paths`与条目notes，Git历史保留旧内容。
- `source_paths`可多项复用文件，但每个清单文件有一个primary_item。测试门控、逐层CPU审计、历史sitecustomize都要明确角色，不默认进入生产路径。
- 新的真实验证记录放`ascend_tuning/integration/runs/`，从[run模板](ascend_tuning/integration/examples/validation-run.json)填写。模板`example=true`、`verdict=not_run`，不能直接作为通过证据。
- run绑定实际被测candidate_commit，或绑定源文件清单路径和SHA；另记硬件、镜像/SDK、权重/量化、拓扑/开关、数据协议、时间、检查结果、指标范围、原始制品SHA、失败和限制。预热口径、实际命中与真实running/queue按模型合同保存。
- 报告提交可以晚于被测源码提交；不要为了填提交号制造自引用。只改报告时，以运行时源码清单相同证明被测实现未变。
- 大型或私有原始制品保存在受控位置；公开记录用脱敏逻辑制品标识和SHA，禁止凭证、资产地址或原始业务文本。

## 6. 一次提交怎么做

1. 读AGENTS与台账，确认当前用户范围和已有授权；定位已有条目或登记新ID。
2. 修改前记录基础提交与适用配置；源码准备和记录审查可以先做。
3. 一个独立目的形成一份最小差异，同提交更新条目、文件清单和相关说明。不要夹带另一模型、整树格式化、SDK升级或旧launcher。
4. 文档/台账修改跑CPU检查；运行时修改按影响范围补正确性。没有硬件就保留待验证，仍可提交源码候选，不冒充已运行。
5. 在有Git历史的工作区，检查本次实际差异与文件归属：

   ```bash
   git diff --stat
   python3 ascend_tuning/tools/verify_package.py
   python3 ascend_tuning/tools/check_registry.py
   python3 ascend_tuning/tools/check_registry.py --base-ref <本次工作起点提交>
   ```

   `check_registry`检查字段、枚举、引用、依赖循环、路径和SHA、候选证据及变动源码登记。最后一条是只读Git差异检查；将占位符替换为实际提交。
6. 改动既有记录文件时更新`REVIEW_MANIFEST.json`；它排除自身，原归档PACKAGE_MANIFEST不动。可运行`check_registry.py --refresh-review-manifest`刷新记录清单，再正常检查。该选项只更新记录清单，不改源码SHA或资格状态。
7. 由用户指定的本机ZCode DeepSeek执行Git/GitHub写入。提交信息格式：`类型(范围): [ID] 具体行为`，例如`perf(flash): [F-QUERY] partition prefill query rows`。类型用feat/fix/perf/config/test/build/docs/chore，范围用flash/glm53/c8/common/registry等。多个紧密相关ID可并列。
8. 正文写问题、最终行为、适用模型/底座、验证命令及范围、未验证项、风险和回退方式。正文不要只写“优化完成”或对话过程。
9. 发布前确认远端目标分支没有被别的任务更新；有变化先审查并合入，不能强推覆盖。提交后回读实际提交和关键文件SHA，登记结果。PR形式提交时，创建后把PR附加到当前任务。

Git写入的执行偏好不要求每次重复请求用户许可。已有授权足够就继续；如果入口或资源缺失，先完成本地可审查内容，再清楚报告具体缺口。

## 7. 开发合并、统一验证与稳定发布

小改动在独立临时分支开发，完成后向`ascend-tuned`提出合并。分支不是每模型/每月一份全量副本，完成后可删除临时分支，提交与Tag保留。当前归档允许按profile保留历史实现，但正式引擎需要解决冲突，不能把两份文件互相覆盖。

纯说明、登记与仓库工具的低影响修改，可以在已有用户授权下直接提交维护主线；不为每次补记录强制创建分支或新增人工审批。运行时代码的开发、合并和部署依照实际任务范围及上述验证要求。

开发主线可以记录未实测候选，但必须隔离、默认关闭且标清范围。会影响已启用路径的整合，先完成受影响正确性；不以“代码能合并”替代运行验证。

统一验证按每模型一个冻结组合组织，复用仍匹配的组件证据与一次服务生命周期，不为每个文件重复长预热。功能通过后按代表性合同验证性能；新改变、失败或跨模型公共路径才扩大检查。

稳定发布只包含声明支持且通过的组合。用户自行安排月度版本和2026-11-20目标；本规则不创建定时、不自动发版、不移动旧Tag。官方升级按[UPSTREAM_UPDATES.md](UPSTREAM_UPDATES.md)另建候选；官方已覆盖的补丁经证据核实后退役，不叠加重复修复。
