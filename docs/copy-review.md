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

## 繁体版本：由 OpenCC 生成，术语表校正

`content/docs/manual/*.zh-tw.md` 此前只是简体正文的副本（九个章节都是），
`README.md` 却写着「已用 OpenCC 转成繁体并人工校正」。本轮补上这一步：

- 新增 `scripts/convert-zh-tw.py`：以 `zh-cn` 为源，先用 `s2twp` 转字形，再套一层术语表。
  代码块、内联代码与 URL 在转换前会被占位符保护，因为手册里写的是程序真实匹配的列名
  （`样本编号`、`样本分组`、`条件`），转了就和 `internal/input/pdata.go` 的别名表对不上。
- 术语表来自 `data/home/zh-tw.yaml`（此前逐字校对过的那份），保证首页与手册用词一致：
  `釋出`（非 `發佈`）、`執行`（非 `運行`）、`登錄檔`（非 `註冊表`）、`運算元`（非 `算子`）、
  `儲存庫`、`安裝程式`、`驗證`（`校驗和` 除外）、`欄位`、`帳戶`、`後台`。
- `--check` 子命令会扫描代码之外的简体专用字，防止以后改完简体忘了同步。

顺带修正了两处原文事实性错误：`可加密审计` 应为 `密码学可审计`（英文原文
"Cryptographically Auditable"），`运行器` 在英文原文里是 CI runner，与 OTTER 自己的
`executor`（执行器）不是同一个东西，中文统一写作 `runner` 以免混淆。

## 繁体用词：文檔 / 檔案

`s2twp` 把 `文档` 和 `文件` 都转成 `文件`，两者在繁体里就此撞车。按你的决定，繁体统一为
「文档 = 文檔、file = 檔案」，所以 `scripts/convert-zh-tw.py` 在转字形之前先把 `文档`
换成占位符，转换完再还原成 `文檔`；`文件` 则照常走 `檔案`。导航栏、`/docs/` 标题、手册
侧栏、页脚与章节内的「文档中心」入口都已统一为 `文檔`。

同一轮还修掉了三处只在 `$isZh` 分支上的 UI 文案（`主导航`、`语言`、页脚 `数据`），
它们此前让繁体页面混入简体字。

## 术语审查：生信与计算机专用词

按生信与计算机的通行译法逐词核对了两份中文，发现三类问题，均已修正。

### 一、生信术语误译或大陆/台湾混用

| 英文 | 改前 | 改后 | 依据 |
| :--- | :--- | :--- | :--- |
| bisulfite | 重亚硫酸盐（与「亚硫酸氢盐」并存） | 统一为「亚硫酸氢盐」 | 化学名 sodium bisulfite 是亚硫酸氢钠；「重亚硫酸盐」是 metabisulfite 的旧称，与 WGBS/RRBS 的 bisulfite 不是同一物质 |
| Reduced Representation Bisulfite Sequencing | 简化代表测序 | 简化基因组亚硫酸氢盐测序 | 通行译法是「简化基因组」；同一页的 RRBS 词条原为两种写法 |
| genome | 基因组（zh-tw） | 基因體 | 台湾标准 |
| transcriptome | 转录组（zh-tw） | 轉錄體 | 台湾标准 |
| sequencing | 测序（zh-tw） | 定序 | 台湾标准 |
| QC | 质控（zh-tw） | 品管 | 台湾标准 |
| annotation | 注释（zh-tw） | 註解 | 台湾标准 |
| normalization | 归一化（zh-tw） | 正規化 | 台湾标准 |

### 二、计算机术语错译

| 英文 | 改前 | 改后 | 说明 |
| :--- | :--- | :--- | :--- |
| operator（系统组件） | 運算元（zh-tw） | 運算子 | 台湾把 operand 译作「運算元」，operator 是「運算子」；原译文把两者对调了 |
| build（CI 编译） | 構建（zh-tw） | 建置 | 台湾把软件构建叫「建置」；「建構」指从零构造，用于「建構甲基化矩陣」这类语义，两者已分开 |
| binary | 二進位制（zh-tw） | 二進位 | 台湾标准简写 |
| configuration | 配置（zh-tw） | 設定 | 台湾把 config 与 configure 都叫「設定」 |
| checker（SLURM 作业提交检查） | 检查器 | 作业检查程序（checker） | 原文指 SLURM 的 job submission checker，不是通用「检查器」 |
| schema | 模式（schema） | schema | schema 不同于 mode，中文「模式」会与分析模式混淆，保留英文 |

### 三、同一概念多种译法

| 概念 | 改前 | 改后 |
| :--- | :--- | :--- |
| dry-run | 试运行 / 空运行 / 预演 | 统一为「试运行」 |
| executor（作为层） | 执行层 | 执行器（与章节正文一致） |
| validate / verify | 混用「校验」「验证」 | 按英文区分：validate → 校验，verify → 验证 |

`--dry-run` 是 CLI 参数，其余三处是正文，混用会让读者以为是不同机制。执行器同理：`craftmake` 是 executor，不是抽象「执行层」。

### 已确认无需改动的项

- `快照`（snapshot）、`清单`（manifest）、`校验和`（checksum）、`契约`（contract）、`资源边界`（envelope）：均为该领域已通行的译法，简繁一致。
- `分區`（SLURM partition）：台湾 SLURM 社区也用「分區」或直接用 partition，保留。
- `執行緒`（thread）、`快取`（cache）、`變數`（variable）：台湾标准用法，本就正确。
