# OTTER 主页设计方案 (v0.1)

参考站点：`https://music.egoist.dev/zh/`（MyGo Music 产品主页）
技术栈：Hugo 0.170 + Blowfish v3.11.0 + GitHub Pages
状态：待确认（文案由 Antigravity/Gemini 会审后定稿）

---

## 1. 目标与受众

| 项 | 结论 |
| :--- | :--- |
| 主页定位 | OTTER 项目主页，同时承担 otterlab-bio 组织的入口 |
| 第一受众 | 做 PDX/CDX 多组学的生信分析人员、HPC 平台管理员 |
| 第二受众 | 审稿人、期刊编辑、潜在合作方（需要有可核验的引用与数据链接） |
| 第三受众 | 中文实验室内部成员与国内同行 |
| 核心动作 | (1) 复制安装命令；(2) 打开 GitHub 仓库；(3) 打开文档/Colab；(4) 引用 DOI |
| 语气 | 参考站点是"产品发布会"，OTTER 需要收敛为"系统说明"：克制、量化、可核验。禁用 revolutionary / game-changing / unprecedented 一类词汇 |

参考站点真正值得复刻的不是配色，而是**信息节奏**：一张巨大的衬线标题、一句克制的解释、一个可信的界面实证、然后把功能拆成可扫读的卡片网格。

---

## 2. 参考站设计拆解（实测值）

以下数值由 Playwright 在 1440×900 下读取 computed style 得到，作为我们的基线。

### 2.1 色彩

| Token | 亮色 | 暗色 |
| :--- | :--- | :--- |
| `--paper` 页面底色 | `#FBF7F1` | `#141214` |
| `--paper-2` 次级底 | `#F4EDE3` | `#1B181B` |
| `--raised` 卡片面 | `#FFFFFF` | `#201D20` |
| `--ink` 正文 | `#1D1D1F` | `#F5F5F7` |
| `--ink-2` 次级文字 | `rgba(60,60,67,.66)` | `rgba(235,235,245,.62)` |
| `--line` 描边 | `rgba(0,0,0,.08)` | `rgba(255,255,255,.08)` |
| `--accent` 强调 | `oklch(60% .21 24)`（朱红） | `oklch(66% .2 22)` |

### 2.2 排版

| 层级 | 字体 | 字号 / 行高 | 字重 | 字距 |
| :--- | :--- | :--- | :--- | :--- |
| H1 主标题 | Fraunces Variable + Noto Serif SC | 92px / 97.5px | 900 | -0.92px |
| H2 区块标题 | 同上 | 52px / 58px | 900 | -0.52px |
| Eyebrow 眉标 | 系统无衬线 | 13px / 21px | 600 | +1.04px，全大写路径以中文小字+字距替代 |
| 导语 | 系统无衬线 | 20–24px / 1.5 | 400 | normal |
| 正文 | 系统无衬线 | 16px / 26.4px | 400 | normal |

### 2.3 形状与质感

- 卡片：圆角 22px，内边距 28px，描边 1px `rgba(0,0,0,.08)`，阴影 `0 10px 30px -22px rgba(80,50,20,.14)`。
- 栅格：内容最大宽度约 1128px；功能区为 3 列，首卡跨 2 列（747px + 365px + 365px），形成非对称节奏。
- 顶栏：悬浮胶囊，距顶 20px，半透明 + `backdrop-blur`，最大宽度 1280px。
- 背景：极淡的同心圆纹理，随滚动几乎不可察觉。
- 动效：`cubic-bezier(.22,1,.36,1)`，hero 四级 90ms 阶梯上浮（0.65s），`prefers-reduced-motion` 下整体禁用。

---

## 3. 视觉方向：把"暖纸 + 朱红"换成"暖纸 + 深海蓝 + 水獭青"

不复刻参考站的红色。理由：参考站的红是音乐产品的品牌色，OTTER 已有稳定品牌资产（`figures/logo.png` / `logo.svg`），主色为深海蓝 `#002B49`，辅色为水獭与水面青 `#64B2CE`，并带棕色毛发 `#AD8561`。沿用手稿标题色可以保证主页、README、PDF 三处视觉连续。

### 3.1 自定义色板 `assets/css/schemes/otter.css`

```
primary（深海蓝）  50 #EFF5F9  100 #DCE8F1  200 #B9D3E4  300 #8FB8D1  400 #5C97BA
                   500 #33789F 600 #1B5C80  700 #0B4461  800 #002B49  900 #001D33
secondary（水獭青）50 #F0F9FC 100 #DCF1F7  200 #B7E3EF  300 #85CFE2  400 #64B2CE
                   500 #3F97B7 600 #2C7B99  700 #24617A  800 #1E4C5F  900 #193D4C
neutral（暖纸）    50 #FAF7F2  100 #F5F0E8  200 #E9E1D4  300 #D8CCB9  400 #B5A691
                   500 #8E8071 600 #6B5F52  700 #4B4238  800 #2B2723  900 #1A1815
```

暗色背景取 `#131518`（略带蓝的黑），比参考站的 `#141214`（暖黑）更贴合深海蓝主色；卡片面 `#1C2024`。

### 3.2 字体策略（性能优先）

- 拉丁展示字体：自托管 Fraunces 可变字体 latin 子集（woff2，单文件约 40–70 KB），仅用于 H1/H2 与统计数字。
- 中文展示字体：**不加载网络 CJK 字体**，回退 `"Songti SC", "Noto Serif SC", "Source Han Serif SC", serif`。理由：一个完整 CJK Serif 子集动辄数 MB，与"零依赖、加载快"的项目气质冲突。
- 正文：`-apple-system, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif`。
- 代码：`ui-monospace, "SF Mono", "JetBrains Mono", Menlo, monospace`。

### 3.3 关键约束：只用预编译的 Tailwind

Blowfish 发布包内已带编译好的 `assets/css/compiled/main.css`，站点构建**不运行 Node**。因此：

1. 所有自定义视觉写进 `assets/css/custom.css` 的普通 CSS（含自定义属性与媒体查询）；
2. 页面 Markdown/短代码里只使用主题已知的 utility class；
3. 不在模板里写 `text-[92px]` 一类任意值类，因为预编译产物里没有对应规则。

这条约束决定 hero 的排版必须由 `custom.css` 提供 `.ot-hero-title` 等语义类，而不是堆 Tailwind。

---

## 4. 信息架构

```
/                 English（默认，面向国际读者）
/zh/              简体中文
/docs/            文档入口（列表页，链到 GitHub 手册各章）
/zh/docs/
/benchmarks/      评测汇总（可选，第二阶段）
/changelog/       版本与发布（可选，由 GitHub Release 手工同步）
```

参考站点用客户端脚本按 `navigator.language` 跳转 `/zh/`，我们沿用同一策略（Blowfish 自带 `languageRedirect`，默认关闭，需要显式开启）。

---

## 5. 首页区块规格

页面总长约 5 屏（桌面），区块顺序对齐参考站，但内容换成 OTTER 的真实证据。

### 5.1 Hero

- 眉标：`开源 · MIT 许可 · Go 与 Rust`
- H1：两段式短句，每段 2–3 个词（参考站节奏：`你的音乐，原生地播放。`）。定稿为 `Compiled pipelines. / Reproducible runs.`，中文 `编译型管线。可复现运行。`
- 导语：2–3 行，交代"做什么 + 凭什么不同 + 代价/边界"
- 两个按钮：`安装 OTTER`（primary，滚动到快速开始）与 `查看源码`（outline，GitHub，带 star 数）
- 元信息行：`MIT 开源 · Linux 与 macOS · amd64 与 arm64`
- 视觉主体：**纯 HTML/CSS 绘制的终端与项目面板**（不使用位图），内容为真实命令与真实输出：
  - 左：`otter build --project-root demo ...` 命令与 6 行日志，逐字取自 `cmd/build.go` 与 `cmd/create_v1.go` 的 logger 输出
  - 右：快照中的阶段表（phase、backend、序号），状态字符串一律不写，因为 `otter-run/v1` schema 不定义运行期状态
  - 该面板在暗色模式切换配色，并随滚动轻微上浮（不做视差）

### 5.2 体系区（对应参考站"该有的，都在。"）

- Eyebrow：`体系`
- H2：`一条命令，四层编译。`
- 导语：说明 `otter → craftmake → enva → operators → bamdriver` 的职责边界
- 视觉：四张并列的层卡片（otter / craftmake / enva / operators），每张一句职责。原仓库的 `otter-workflow-stack.svg` 为深色底示意图，与本页浅色纸面冲突，未采用；四层职责改由 HTML 卡片承载，暗色模式下自动换色

### 5.3 能力卡网格（对应参考站"功能"）

1 张宽卡 + 5 张标准卡，全部为真实机制，不写"易用""强大"：

| 卡 | 标题方向 | 证据 |
| :--- | :--- | :--- |
| 宽卡 | 七个原生算子取代 R 脚本 | fastqcx / xenofilx / pairbam / seq2mat / matsrun / qctb / methx |
| 卡 | 无锁的单写者状态机 | craftmake 单写连接 + rollback journal，Lustre 上 256 次重叠事务零丢失 |
| 卡 | 不可变参考注册表 | `$OTTER_REFERENCE_ROOT` + sha256 清单，run 快照绑定身份 |
| 卡 | 环境只装一次 | enva 以 rattler 解析，安装延迟从小时级降到分钟级 |
| 卡 | 静态二进制 | Linux 为 static 构建，不依赖 glibc 版本 |
| 卡 | 本地与 SLURM 同一份快照 | backend 与资源边界在 resolve 时固定 |

### 5.4 评测区（对应参考站"原生，而且安静"的位置）

三到四个统计卡，数字全部来自 `manuscript.typ`，并标注口径：

- `2.41×` 甲基化矩阵构建提速（91.6 s vs 221.0 s）
- `65.5%` 峰值内存下降（18.62 GiB → 6.42 GiB）
- `4.213 s / 19.819 s` BS-PDX 控制器对账中位数（craftmake / Snakemake）
- `51.61%–54.03%` RRBS 梯度上的可用召回

下方一行小字：`n = 3 配对重复；完整梯度见 Supplementary Tables S11/S12。`

### 5.5 快速开始（对应参考站代码面板）

三标签：`安装脚本` / `容器` / `Colab`，标签由 15 行原生 JS 切换（`aria-selected` + `hidden`），不依赖主题脚本。每个标签内是可复制的真实命令；单行安装命令允许换行，避免横向滚动遮住尾部。右侧列 4 条要点（分析模式、参考基因组体量、离线演练、迁移路径）。

### 5.6 组件区（对应参考站"其余的一切，交给插件"）

12 个公开仓库做成 2 列或 3 列卡片，每张卡：名称、一句话职责、语言徽标、链接。数据用 Hugo data 文件维护（`data/components.yaml`），避免模板硬编码。

### 5.7 文档与引用

- 四张卡：文档、预印本、数据、演练，各自带完整 URL
- 文档正文落在站内 `/docs/` 与 `/zh-cn/docs/`，覆盖安装、数据准备、首次运行、五类模式，并跳到 GitHub 手册对应章节
- 引用：bioRxiv DOI `10.64898/2026.10.24.761506`
- 数据：Hugging Face `fallingstar10/otter-data`

### 5.8 页脚

单行：`OTTER · MIT 开源 · 由 Go 与 Rust 写成`，右侧 GitHub 与 DOI 图标。不放大段链接矩阵。

---

## 6. 动效档位：L2

| 动效 | 实现 | 参数 |
| :--- | :--- | :--- |
| Hero 入场 | 主题自带 `.landing-rise` 阶梯 | 0.65s，90ms 递增 |
| 卡片入场 | IntersectionObserver 加 `.is-in` | translateY(14px) → 0，opacity 0 → 1，0.5s |
| 卡片悬停 | CSS transform | -4px，阴影加深，0.2s |
| 顶栏 | 主题 `header.layout = "floating"` | 玻璃拟态，滚动后加深 |
| 背景纹理 | CSS `repeating-radial-gradient` | 极低对比，暗色自动降透明度 |

统一 `@media (prefers-reduced-motion: reduce)` 关闭位移与淡入；不使用 GSAP、Lenis、滚动 pin。

---

## 7. Blowfish 配置映射

```toml
# config/_default/params.toml
colorScheme = "otter"
defaultAppearance = "light"
autoSwitchAppearance = true

[header]
  layout = "floating"

[homepage]
  layout = "landing"
  showRecent = false
  homepageImage = ""          # 不用照片，hero 由 HTML/CSS 绘制

[footer]
  showMenu = true
  showCopyright = true
  showThemeAttribution = true
  showAppearanceSwitcher = true
  showScrollToTop = true
```

- hero 内容写在 `content/_index.md` 的 `heroCaption` / `heroLead` / `heroButtons` 前置字段。
- 正文主体使用主题短代码：`feature-grid`、`feature`、`stats`、`stat`、`steps`、`tabs`、`cta`。
- 定制样式：`assets/css/custom.css`（主题自动加载）。
- 自定义脚本：`layouts/partials/extend-footer.html`（滚动入场，约 15 行）。
- 字体预加载：`layouts/partials/extend-head.html`。

---

## 8. 双语策略

- 英文为默认语言（`defaultContentLanguage = "en"`），中文在 `content/*.zh-cn.md`。
- 两版文案同源：先定英文事实陈述，再写中文，不允许中文版新增未在英文版出现的数字。
- 术语统一：graft / host（移植/宿主），usable recall（可用召回），reference registry（参考注册表），snapshot（快照）。
- 遵循 AGENTS.md 语言规范：无句子级破折号，范围统一用 en-dash（`51.61%–54.03%`），复合词保留连字符（`read-pair`、`host–graft` 用 en-dash 表示对）。

---

## 9. 事实清单（唯一数据源）

所有数字只能来自以下位置，主页不得自行推导或四舍五入成更大口径：

| 事实 | 值 | 出处 |
| :--- | :--- | :--- |
| 最新发布 | v1.3.0（2026-11-23） | GitHub Release |
| 许可 | MIT | `LICENSE` |
| 平台 | Linux / macOS，amd64 / arm64 | Release 资产清单 |
| 甲基化构建 | 2.41×（91.6 s vs 221.0 s） | `manuscript.typ` §2.3, S4.4 |
| 峰值 RSS | 18.62 GiB → 6.42 GiB（-65.51%） | 同上 |
| 控制器对账 | BS-PDX 4.213 vs 19.819 s；RNA-PDX 2.651 vs 9.478 s | S4.2, Table S4 |
| RNA-seq 可用召回 | 92.13%–92.69% | §3.2 |
| RRBS 可用召回 | 51.61%–54.03% | §3.2 |
| 预印本 DOI | 10.64898/2026.10.24.761506 | bioRxiv |
| 数据 | huggingface.co/datasets/fallingstar10/otter-data | README |

---

## 10. 仓库与部署

### 10.1 仓库形态（待确认，见第 12 节）

推荐：独立公开仓库 `otterlab-bio/otterlab-bio.github.io`，即组织根站点，域名 `https://otterlab-bio.github.io/`。该目录当前作为 `website/` 存在于手稿工作区内，作为独立 git 仓库初始化，可选手稿仓库以 submodule 方式引用。

### 10.2 目录

```text
website/
├── config/_default/          hugo.toml, languages.{en,zh-cn}.toml, params.toml, menus.*.toml
├── content/                  _index.md, _index.zh-cn.md, docs/
├── data/components.yaml      12 个仓库的卡片数据
├── assets/
│   ├── css/custom.css
│   ├── css/schemes/otter.css
│   ├── fonts/fraunces-latin.woff2
│   └── img/{logo.svg,workflow-stack.svg,og.png}
├── layouts/partials/extend-head.html
├── layouts/partials/extend-footer.html
├── static/{favicon*,robots.txt}
├── .github/workflows/pages.yml
└── DESIGN.md
```

### 10.3 主题引入方式

使用 Hugo Module，锁定 `github.com/nunocoracao/blowfish/v3@v3.11.0`，不提交 200 MB 的主题副本：

```bash
hugo mod init github.com/otterlab-bio/otterlab-bio.github.io
hugo mod get github.com/nunocoracao/blowfish/v3@v3.11.0
```

CI 中 `actions/setup-go` 后直接 `hugo --minify`。若后续需要完全离线构建，再改为 git submodule。

### 10.4 Pages 工作流

`actions/configure-pages` + `actions/deploy-pages`，`HUGO_VERSION: 0.170.1`，`baseURL` 由 `actions/configure-pages` 注入。首次上线前需要在组织设置中把 Pages 来源设为 GitHub Actions。

### 10.5 域名与 SEO

- 生成 1200×630 OG 图（logo + 一句标题 + DOI）。
- `sitemap.xml`、`robots.txt`、`hreflang` 由主题与语言配置生成。
- 结构化数据：`SoftwareApplication`（name/applicationCategory/licenseCode/codeRepository）+ `ScholarlyArticle`（DOI）。

---

## 11. 验收标准

1. Lighthouse（移动）Performance ≥ 95、Accessibility ≥ 95、SEO ≥ 95。
2. 首屏无网络字体阻塞，LCP < 1.2 s（本地千兆、冷缓存）。
3. 320 / 390 / 768 / 1024 / 1440 / 1920 六档宽度无横向溢出，hero 字号按 `clamp()` 收缩。
4. 亮暗两套配色对比度均 ≥ 4.5:1（正文）与 ≥ 3:1（大标题）。
5. 键盘可达：跳过导航、按钮焦点环、标签页可切换。
6. `prefers-reduced-motion: reduce` 下无位移与淡入。
7. 所有统计数字可在第 9 节事实清单中逐条找到出处。
8. 全站无句子级破折号（`—` / `---`）。

---

## 12. 待确认决策

| # | 决策 | 选项 A（推荐） | 选项 B |
| :--- | :--- | :--- | :--- |
| 1 | 仓库与 URL | **已采用**：`otterlab-bio/otterlab-bio.github.io`，站点在根域 | `otterlab-bio/otter-website`，站点在 `/otter-website/` |
| 2 | 默认语言 | **已采用**：英文为默认（`/`），中文在 `/zh-cn/`；中文浏览器首次访问根域自动跳到中文，显式 URL 永不跳转 | 中文优先，`/en/` 为英文 |
| 3 | 强调色 | **已采用**：深海蓝主色 `#0B4461` + 水獭青 `#2C7B99` | 沿用参考站朱红 |
