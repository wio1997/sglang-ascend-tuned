# SGLang Ascend Tuned

基于官方SGLang的公开维护分支，归并Ascend上的模型适配、已测优化和配置。官方基础源码、历史与许可证保留；[官方README](README.upstream.md)。本分支从实际使用过的commit `ce0a8fea5f4245839d174b2b8c55692be1810a7f` 建立，不冒充官方最新版。

**当前是研究代码归并版。没有发布新的容器镜像，也没有完成新服务器验证。**

- [源码和使用说明](ascend_tuning/README.md)
- [补丁及验证范围清单](ascend_tuning/catalog.json)
- [模型代码profile](ascend_tuning/profiles/index.json)
- [性能证据摘要](ascend_tuning/evidence/)
- [Flash实际补丁](ascend_tuning/patches/glm53-flash/indexer-performance.patch)
- [实验候选](ascend_tuning/experiments/)
- [来源与基础版本](ascend_tuning/BASELINE.json)

## 已知成果

Flash两处indexer修改消除了反复编译与TP重复查询，匹配的真实模型早/中段窗口分别改善6.31x和7.71x。完整预热、SGLangC32吞吐、完整数值/Graph/MTP资格仍未完成。

原GLM-5.3的nativeSDMA/MemCache/Graph/MTP相关代码及普通W8A8历史结果保留。最新NoCopy未达到解码改善目标，单列实验。W8A8C8通信缓冲调整单列配置，不能当作普通W8A8或端到端性能结论。950DT/DeepSeek材料来自vLLM-Ascend/DSpark，单列参考。

## 更新方式

```bash
git clone --branch ascend-tuned https://github.com/wio1997/sglang-ascend-tuned.git
cd sglang-ascend-tuned
python3 ascend_tuning/tools/verify_package.py
# 后续更新同一分支
git pull --ff-only
```

各对话的代码在独立分支修改，按适用范围验证后合并。新机器镜像需另经匹配底座构建、最小实机验证后发布digest。密码、资产地址、权重、镜像二进制、provider及原始业务请求不进入仓库。
