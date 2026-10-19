# Ascend tuning source collection

本目录归并多个独立任务的代码、配置和证据。官方SGLang源码仍在仓库原目录；这里的模型代码快照按profile显式导出，不会在import SGLang时自动叠加。

## 包含内容

| 目录 | 内容 | 验证范围 |
|---|---|---|
| profiles/glm53-flash-eager | 47个实际诊断运行的Flash适配源码 | 两个indexer修改的真实模型早/中段采样6.31x/7.71x；不是完整C32或完整Graph/MTP资格 |
| profiles/glm53-w8a8-historical | 原GLM的SDMA、nativeHiCache/MemCache、targetGraph/MTP支持代码 | 历史功能及C32证据；新节点角色、ABI、源文件校验条件待移植 |
| profiles/glm53-w8a8c8-buffers | 普通HCCL与DeepEP分离配置 | 启动显存改善；没有端到端提速结论 |
| experiments | NoCopy、CPU描述符和分词队列候选 | 不默认启用；NoCopy未达到解码改善目标 |
| references/vllm950 | vLLM-Ascend/DSpark、950DT兼容范围 | 参考项，不是SGLang或910C支持证明 |
| patches | Flash两个性能修改的实际diff | 依赖历史私有Flash基线，不可直接用于任意新版caller |

源码包含既有实现和诊断支持，不把每个历史overlay文件都称作优化。旧的审计角色ID、source pins、支持脚本入口和SDK扩展依赖仍明确保留，不自动转换成新服务器部署配置。旧控制器、一次性启动器、实际节点argv及密码不在本包中。

## 使用

```bash
python3 ascend_tuning/tools/verify_package.py
python3 ascend_tuning/tools/export_profile.py --profile glm53-flash-eager --output /path/to/empty-export
```

第二条只导出文件，不修改官方源码、不启动模型、不访问服务器。将来构建镜像时，把选定profile移植到匹配底座，再按模型配置验证。新服务器的Docker/驱动/互联/权重尚未核验，也尚无新的镜像digest。

四处历史审计地址被改为显式环境参数，避免发布资产地址。BASELINE及各file manifest保留原SHA和发布SHA；对应模块不是逐字节原件，尚未做这次参数化后的NPU复测。数值计算未在这次归并中修改。历史结果只证明原有测试条件。

## 后续维护

- 每项优化一个可追溯commit，记录适用模型、底座、依赖和正确性/性能范围。
- 只选择适用的profile，不把不同模型/精度或实验候选直接叠加。
- 官方更新先在独立分支处理兼容，再最小正确性和性能验证。
- Git管理源码和构建配方；镜像由registry/离线包分发，权重独立挂载。
