# 雅思词汇 100 短文记忆项目

把《雅思词汇 9400 词》的全部 **9389 个单词**编织进 **100 篇英文短文**里,每篇配中文翻译,并在英文原文和中文译文里把雅思单词用红色高亮,最终生成一本 **100 页的 PDF**(每页一篇),用于在语境中记忆词汇。

## 设计目标

- **全覆盖**:9389 个词全部出现在短文里,一个不漏(严格覆盖,接受较高词密度)。
- **可读性**:原始词表按固定随机种子打乱后再分组,使每篇短文混合不相关词汇,读起来更像自然文章而非词表堆砌。
- **双语红色高亮**:雅思单词在英文原文**和**中文译文里都标红,方便对照记忆。
- **中文不乱码**:PDF 同时内嵌拉丁字体与中日韩字体,逐字符切换。
- **无内容漂移**:去掉高亮标记后的文本必须与原文逐字一致(中文侧允许轻度润色,以保证每个词义都出现且可标记)。

## 数据流水线

```
雅思词汇9400词EXCEL版-顺序版.xls   (9389 词,B列=单词 C列=中文释义)
        │  打乱 + 分组(固定种子)
        ▼
word_chunks.json                  (100 组,每组约 94 词)
        │  人工创作英文短文 + 中文翻译
        ▼
passages.json                     (100 篇 {id, theme, text, translation})
        │  autopair.py 半自动标注
        ▼
marked/mark_*.json                (含 text_marked / translation_marked / pairs)
        │  build_pdf.py 渲染
        ▼
雅思词汇100短文.pdf                (100 页,每页一篇,双语红色高亮)
```

## 关键文件

| 文件 / 目录 | 说明 |
|---|---|
| `雅思词汇9400词EXCEL版-顺序版.xls` | 源词表,9389 词 |
| `word_chunks.json` | 打乱后的 100 组词块 |
| `passages.json` | 最终 100 篇短文 `{id, theme, text, translation}` |
| `passages/words_*.json` | 每篇的词表 `{id, words:[{word, def}]}` |
| `batches/batch_*.json` | 10 个批次清单,每批 10 篇 `{batch, passage_ids}` |
| `out/out_*.json` | 单篇原始短文(英文 + 中文),供标注与校验比对 |
| `marked/mark_*.json` | 标注结果(见下方格式) |
| `overrides/ov_*.json` | 人工覆盖:可改写译文并强制登记词→译文实际用词 |
| `雅思词汇100短文.pdf` | 输出 PDF |

## 标注文件格式 `marked/mark_*.json`

```json
{
  "id": 1,
  "theme": "...",
  "text_marked": "... ⟦physicist⟧ ...",
  "translation_plain": "...物理学家...",
  "translation_marked": "...⟦物理学家⟧...",
  "pairs": [{"word": "physicist", "zh": "物理学家"}]
}
```

- 高亮用 `⟦`(U+27E6)和 `⟧`(U+27E7)包裹,标记内的文字在 PDF 里渲染为红色。
- `pairs` 显式记录每个英文词对应的中文标记片段,使中文侧覆盖率可被校验。

## 核心脚本

- **`autopair.py`** — 半自动标注。英文侧把每个雅思词包上标记;中文侧用单词释义在译文里定位并标红,生成 `pairs`。匹配不到多字释义时,回退到「受控单字」(排除「的地得了和与」等虚词)。支持读取 `overrides/ov_*.json` 强制登记译文实际用词。
  - `python3 autopair.py` 重建全部 100 篇并打印覆盖率统计
  - `python3 autopair.py <id>` 重建单篇,并列出该篇匹配不到的词
- **`build_pdf.py`** — 渲染 PDF。拉丁字体用 DejaVuSans、中日韩字体用 DroidSansFallbackFull,逐字符切换(解决早期「英文不可见」的字体缺字形问题)。自动调节字号(约 7–10.5pt),保证每篇正好占一页。
- **`check_strict.py <batch>`** — 严格校验单个批次:去标记后无漂移、每个雅思词在英文侧已标、每个词在 `pairs` 里且其中文片段确实标在译文中。**只校验,不生成内容。**
- **`verify.py`** — 总词覆盖校验:确认全部 9389 词都出现在 `passages.json`。

## 字体说明

PDF 渲染必须同时使用两套字体并逐字符判断:

- `DejaVuSans.ttf` — 仅含拉丁字形,无中日韩
- `DroidSansFallbackFull.ttf` — 仅含中日韩字形,无拉丁

只用其中一个会导致英文或中文不可见,因此 `build_pdf.py` 通过 cmap 查表对每个字符选择对应字体。

## 当前状态

- 词覆盖:**9389 / 9389 全覆盖**(`verify.py` 通过)
- PDF:**100 页**,每页一篇,英文可见、中文不乱码、双语红色高亮可用
- 英文侧高亮:**100%**(全部 9389 词)
- 中文侧高亮:**约 96.6% 自动完成**;严格校验 10/100 篇完全通过
- 剩余约 **322 个词**需人工登记:这些词在译文里使用了近义表达(例如 `chicken` 释义「小鸡/鸡肉」而译文写「鸡」),纯字符串匹配无法定位,正按「译文实际用词」逐篇写入 `overrides/ov_*.json`

## 复现步骤

```bash
# 1. 重建全部标注(读取 overrides 覆盖)
python3 autopair.py

# 2. 严格校验全部批次
for b in $(seq 1 10); do python3 check_strict.py $b; done

# 3. 校验总词覆盖
python3 verify.py

# 4. 生成 PDF
python3 build_pdf.py
```
