[English](REPRODUCE.md) | **简体中文**

# 复现有限预算核查

以下所有命令都应从本资料包根目录运行。需要 Python 3.9 或更新版本。发布版在 Python 3.9.6、macOS arm64 和 `pynauty==2.8.8.1` 环境下经过测试。`triangulations.py` 和 `verify_certificates.py` 只使用标准库；其他完整枚举和审计命令使用 pynauty。如果没有可用的 wheel，安装可能需要 C 编译器。不要使用 Python 的 `-O` 选项：断言是检查的一部分。

## 检查随附文件

在 macOS 上：

```sh
shasum -a 256 -c MANIFEST.sha256
```

在使用 GNU coreutils 的 Linux 上，使用 `sha256sum -c MANIFEST.sha256`。清单检查字节完整性，不检查数学有效性。清单不包括其自身、环境、缓存、本地验证日志和用户重新运行的产物。

仅依赖标准库的快速检查会验证报告的数量、类型元数据、一致性标志，以及软件审计绑定的哈希：

```sh
python3 -B code/verify_certificates.py
```

若要实际重新计算每个纯坏见证和每条证书记录，请安装依赖并运行补充审计：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements.txt
.venv/bin/python -B code/independent_predicates.py
.venv/bin/python -B code/audit_checks.py --results certificates
```

除非提供 `--output`，否则审计只读。它会用两套谓词实现核查 11,504 个去重前见证，同时检查原子守恒、欧拉关系、全部 658 条记录的重建和标识符、658 次确定性随机半边重标号，以及五个手工构造的合法性正反例。它共用 `Host` 和单独的谓词检查器；它不会独立重新生成宿主。

可使用从一开始计数的行号检查单条记录，也可以改用标识符前缀：

```sh
.venv/bin/python -B code/inspect_case.py --line 1
.venv/bin/python -B code/inspect_case.py --line 658
```

## 跨模型检查（仅使用标准库）

两个分别编写的脚本无需依赖，也不导入本资料包的其他模块：

```sh
python3 -B code/claude_host_census.py --small-cases
python3 -B code/claude_budget_check.py
```

第一个脚本验证 191 个宿主，确认它们两两不同构，并检查所有宿主的自同构加权计数 24/|Aut+| 之和等于 4096 = A002005 a(4)；`--small-cases` 在同一嵌入图族上以暴力枚举检验 a(1) = 4 和 a(2) = 32。第二个脚本针对全部 782,145 个子集重新计算纯坏性，对其中 11,504 个纯坏见证检查引理 9.11、9.14 和 9.15、推论 9.16 及辅助推论 9.13，重新检查宿主合法性并打印敏感性对照。两者均以状态码零退出，且末尾输出 `passed=True`；已记录的输出位于 `certificates/claude-crosscheck.txt`。在记录所用环境中，第二个脚本耗时约一分钟。

## 重建完整的有限计算

每次运行都请选择新的输出目录。以下命令写入 `reproduced/`；重复执行会覆盖该目录中的文件。它们不会更改随附的 `certificates/` 目录。依赖安装完成后无需联网。

```sh
mkdir reproduced
.venv/bin/python -B code/triangulations.py --output reproduced/hosts.json
.venv/bin/python -B code/flip_crosscheck.py --hosts reproduced/hosts.json --output reproduced/host-crosscheck.json
.venv/bin/python -B code/independent_predicates.py
.venv/bin/python -B code/subsets.py --hosts reproduced/hosts.json --out reproduced
.venv/bin/python -B code/audit_checks.py --results reproduced --output reproduced/software-audit.json
.venv/bin/python -B code/verify_certificates.py --results reproduced --export-strata reproduced/strata.csv --compare certificates
```

完整发布版的重新运行在记录的本地环境中耗时约 27 秒；这是一次观测结果，并非运行时间保证。完整运行时不要使用 `--limit`。前缀诊断会明确标记为不完整。

## 验收标准

所有命令都必须以状态码零退出。预期结果如下：

| 检查 | 预期结果 |
|---|---|
| 宿主生成 | `complete=true`，60,060 次构造，191 个宿主 |
| 翻转交叉核查 | `complete=true`，191 个宿主，1,924 次转移，两组集合差均为零，`agree=true` |
| 子集 | `complete=true`，782,145 个候选，770,641 个非纯坏，11,504 个纯坏见证，658 个唯一类型，无失败 |
| 完整审计 | `passed=true`，115,040 次字段比较，658 次记录重建，658 次重标号，5 个合法性示例 |
| 按边数 1-12 划分的唯一类型 | `2,10,26,69,114,164,142,95,30,6,0,0` |
| 按已用标记点数 1-6 划分的唯一类型 | `32,238,303,85,0,0` |
| 使用 5 和 6 个标记点的候选 | 295,711 和 165,188；两个区间均经过测试 |
| 最终比较 | `stable_rerun_comparison=true` |

`strata.csv` 包含全部 72 个边数／已用标记点数单元，包括稀疏 JSON 统计中省略的零单元。`types.jsonl` 每种定向类型包含一个代表；每条记录都包含宿主置换、选中边掩码、嵌入／区域数据、主谓词、单独实现的谓词，以及间隙数据。

对于此固定版本的实现及经过测试的架构，重新生成的 `types.jsonl` 与随附记录逐字节一致。计时字段自然会变化，绑定含有计时信息的文件的审计哈希也会随之变化。结构比较仅排除 `seconds`、`elapsed_seconds` 和审计哈希映射；每个映射仍会与对应文件核对。规范证书字节和派生标识符可能依赖 pynauty/nauty 的版本及架构。不同平台可以保留相同的数学类集合与数量，而不复现这些标识符；此时需要调查逐字节比较失败的原因，不能直接置之不理。

数值检查不会独立验证几何完备性输入、完整的超椭圆对应、交数公式或几何锥引理。有限归约、重建规范及准确范围请阅读[预算投稿正文](proof/submission.zh-CN.md)。关于原论文其他证明路线的论证不在本资料包范围内。
