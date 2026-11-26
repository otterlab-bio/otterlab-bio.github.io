# 文案会审记录（Antigravity / Gemini）

两轮会审，模型为 `gemini-4-hydrogen-high`，通过 Antigravity CLI（`agy --print`，`--mode advise`）执行，输入为自包含 brief，未读取仓库以避免事实污染。

## 第一轮

产出三套 Hero 方向：

| 方向 | 角度 | 英文 H1 |
| :--- | :--- | :--- |
| A | 执行层重构与 HPC 确定性 | Compiled workflow binaries. Deterministic HPC runs. |
| B | 移植/宿主判定与读段保真 | Strand-aware xenograft sorting. Verified read fidelity. |
| C | 跨多组学端到端可复现性 | Reproducible multi-omics CLI. Locked end to end. |

推荐 A，理由是它把主页立论落在真实集群上暴露的三类失效模式，而不是把 OTTER 窄化为读段分选工具。

它同时指出 brief 的计数缺口：只显式列出 11 个代码组件，却要求 12 个卡片，建议核对第 12 个。核对结果是 `holt`（容器化工作台），已补入。

## 第二轮

在已实现的英文文案上做判定，给出四点有效意见，均已采纳：

1. `Host reads out. / Biology in.` 把五种分析模式窄化为去宿主一步，且 `Biology in.` 属空泛口号。改为 `Compiled pipelines. / Reproducible runs.`，中文 `编译型管线。可复现运行。`。
2. `Eleven repositories` 与列表不符，改为 `Twelve repositories`。
3. 统一使用 Slurm 官方拼写，替换正文中混用的 `SLURM`。
4. 比较差值明确写作 `percentage points` 而不是裸的 `points`，避免把绝对差值读成相对变化；这一处已采纳。Gemini 同时建议把 `full-genome eRRBS` 改成 `genome-wide eRRBS`，未采纳：`manuscript.typ` §2.3 与 §S4.4 的原文就是 `full-genome eRRBS data`，主页应与稿件逐字一致。

## 未采纳的意见及原因

| 意见 | 原因 |
| :--- | :--- |
| 中文 H1 用 `编译级测序管线，确定运行零漂移` | 「编译级」不是通行术语；「零漂移」在稿件中无对应证据。改为「编译型管线。可复现运行。」 |
| 把终端输出改写为五行中文叙述（「校验样本元数据并锁定参考注册表版本」等） | 终端里是真实命令与日志，翻译后既不再是可复现的输出，也与 `cmd/build.go` 的实际日志不符。改为保留英文原样输出。 |
| 把阶段状态改为「已解析 / 运行中 / 已完成」 | `otter-run/v1` schema 不定义运行期状态；快照只有阶段顺序与资源边界。改为只显示阶段名、backend 与序号。 |
| 数据卡改写为「获取参考注册表 SHA-256 校验清单」 | Hugging Face 数据集是评测 fixture 与溯源记录，不是参考注册表清单。按原意保留。 |
| 统计卡换用 BAM 记录数（92,205,522）与离线阶段数（99 / 99） | 四个统计卡已覆盖构建速度、内存、调度、召回四个维度，正好对应读者选型时的四类疑问。99 阶段演练保留在快速开始的要点里；BAM 位级保真的数字未上首页，因为它在稿件里是 Gate A 的单次生产审计，放进统计卡会被误读为常规性能指标。 |

## 事实核验

所有数字回到 `manuscript.typ` 与 release 元数据逐条比对：

| 首页数值 | 稿件位置 |
| :--- | :--- |
| 2.41× / 91.6 s vs 221.0 s / 18.62 → 6.42 GiB | §2.3, §S4.4 |
| 4.213 s vs 19.819 s（n = 3） | §S4.2 |
| 51.61%–54.03%（+0.575–1.200 个百分点） | §3.2, §S5.3 |
| 99 个阶段、0 失败 | `scripts/e2e/otter_e2e.sh` 输出 |
| MIT、v1.3.0、Linux/macOS × amd64/arm64 | release v1.3.0 资产清单 |
| DOI 10.64898/2026.10.24.761506 | bioRxiv |
