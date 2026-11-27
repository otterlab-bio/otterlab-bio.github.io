---
title: "資料準備"
weight: 11
showDate: false
showAuthor: false
showWordCount: false
showReadingTime: false
showTableOfContents: true
---

成功執行 `otter create` 需要每個樣本都具備可識別的一對 FASTQ 檔案。pdata 檔案為可選項；傳入 `--pdata` 時，其中的 `sampleid` 值必須與 FASTQ 樣本名稱一致。

## FASTQ 命名

預設的配對字尾為：

```text
sample1_R1.fastq.gz
sample1_R2.fastq.gz
```

也可以顯式指定其他字尾：

```bash
otter create \
  --fastq ./fastq \
  --mode RRBS \
  --suffix1 _1.fq.gz \
  --suffix2 _2.fq.gz
```

樣本匹配對掃描器識別到的字尾及由此解析出的樣本名稱敏感。請在檔名與 pdata 中保持樣本 ID 一致（包括大小寫）。

## pdata

`--pdata` 接受 Excel 或 CSV 檔案。必需列為 `sampleid`。用於分組與下游比較時，請使用 `sample_group` 或 `condition`。

支援的別名包括：

| 規範欄位 | 常見別名 |
| --- | --- |
| `sampleid` | `样本编号`, `样本ID`, `sample_id` |
| `sample_group` | `样本分组`, `分组`, `group` |
| `condition` | `条件`, `treatment` |

CSV 範例：

```csv
sampleid,sample_group,condition
sample1,control,control
sample2,control,control
sample3,treated,treated
sample4,treated,treated
```

`create` 會驗證配對樣本，並在提供 pdata 時驗證其對應關係。執行前應修正重複的 ID 與空的分組值。

## 專案目錄結構

推薦的輸入目錄結構如下：

```text
my_analysis/
├── fastq/
│   ├── sample1_R1.fastq.gz
│   ├── sample1_R2.fastq.gz
│   └── ...
└── samples.xlsx
```

`otter init my_project` 會建立工作流資產目錄結構。條件允許時儘量將原始資料儲存在專案目錄之外，並在受控生產環境中使用絕對路徑。

## 執行前檢查

```bash
ls fastq/*_R1.fastq.gz
ls fastq/*_R2.fastq.gz
otter create \
  --output my_project \
  --fastq ./fastq \
  --mode RRBS \
  --pdata ./samples.xlsx \
  --reference-root "$OTTER_REFERENCE_ROOT" \
  --reference-primary hg38@GRCh38.p14
```

規範流程始終會指定一個參考釋出版本（release），因此執行前檢查需要一個已釋出該版本的參考登錄檔（reference registry）（參見[快速開始](03-quickstart.md)）。

若配對失敗，請先比對實際檔案字尾、樣本名大小寫以及 pdata 中的 `sampleid` 值。若有其他流程依賴當前檔名，請向 `otter create` 傳入匹配的 `--suffix1` 與 `--suffix2` 參數，而不要重新命名檔案。

[返回手冊目錄](README.md) · [下一章：快速開始](03-quickstart.md)
