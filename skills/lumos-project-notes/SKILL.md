---
name: lumos-project-notes
description: 維護專案知識圖譜（docs/{project}-knowledge/）— 追蹤進行中/待辦工作、系統關聯、Issue、會話交接。當專案工作開始、結束、遇到 issue、或需要掌握現況時觸發。
---

# 專案知識圖譜系統（lumos）

## 一眼看懂

- **金科玉律**:所有改動/調研/計畫都**同一次工作內**同步進圖譜。查知識**優先讀圖譜**;與其他文件/記憶/臆測衝突以圖譜為準、向人確認。**但與行為事實(測試結果/實際執行/生產觀測)衝突時不自動判圖譜為真**——那是有東西壞了,查清哪邊錯並立事故節點(2026-07-29 外審吸收)。
- **主工具 = `lumos`**(python3 零依賴,`find_vault` 自動鎖定 `docs/*-knowledge/`)。**禁止**用 Grep/Read/Edit/Write 直接碰 vault 的 .md——繞過寫後自驗與鐵則防護。需讀節點**完整 body**(決策全文/章節內文)→ `lumos show <節點> [--body-only]`(2026-07-21 新增,補「context 只給 summary 索引」的全文讀取缺口);context 仍是進場導航首選。
- **進場三步**:`lumos search <關鍵字>` 定位 → `lumos context <節點>` 掃脈絡(頭部攤 ⚠ 合約) → `lumos contracts <節點>` 查硬合約。**然後**才 grep code / 查 DB 驗證。
- **寫完一個節點**:`lumos lint <節點>`(單檔快檢) → 收尾 `lumos doctor`(全圖)。
- **紅燈不過夜**：main 上出現 CI 紅燈時，修不完也要在收尾報告明講「main 上有紅燈未解」，不得靜默收工。
- **rich 節點** = Write/Edit 內文 + `summary` block;**純量/list/decisions 一律走 `lumos set`/`append`/`decision-add`**(別手改 frontmatter)。

> ### ⤵ 何時去翻 `reference.md`（本 skill 目錄下,權威展開版 824 行）
> 本頭版給「做什麼 + 紀律」;**細節/模板/完整規格/邊角在 reference.md**。撞到下列情境**動手前先 `Read` 它對應段**,別只憑 167 行摘要硬幹:
>
> | 你正要做 | Read reference.md 的 |
> |---|---|
> | 綁合約 `[test:]`/`[audit:]`/`[kill:]`、跑 `lumos guard` scaffold/bind/kill、或不確定會不會**帶風向** | 「合約鏈深規 + guard 工作流 + 防帶風向鐵則」段 |
> | 寫**重大決策**要填 ADR 四欄、或某欄不知怎麼填 | 「decisions ADR 完整版」段 |
> | 建/改 Verification（`valid_under`/`revalidate_when`/雙向 `verified_by` 細節） | 「Verification 完整規格」段 |
> | 跑**自足性審計**要 prompt 模板 / 無主脈絡時的交叉審計變體 B | 「圖譜更新後審計」段 |
> | 查某 lumos 子命令的**完整旗標** | 「操作方式」段(或 `lumos <cmd> --help`) |
> | 需要 Obsidian GUI / 權威解析驗證 / File Recovery（少數場景） | 「Obsidian CLI」段 |
>
> **拿不準就 Read**——漏翻深規的代價 > 多讀一次的成本。

---

## Vault 偵測

```bash
ls -d docs/*-knowledge/Projects/ 2>/dev/null   # 存在即 lumos doctor 確認鎖得到
```
vault 名 = 資料夾 basename,lumos 自動解析。**全程無需 Obsidian**(僅 obsidian-only 功能才註冊,見 `reference.md`)。**本精簡版不含建立新圖譜的指令**——vault 是既有專案本來就有的,精簡版只負責讀寫既有圖譜。

## 核心圖譜接點(唯讀說明)

看到 frontmatter `core_refs:` 或 summary `CORE:` 行 → **該主題權威可能在跨專案核心圖譜,本專案筆記殘留描述不可當權威**(疑似快照 = drift)。★本精簡版不含核心圖譜維護 skill/工具★,語意異動需另外處理,不在本 skill 範圍內。

---

## 常用指令(速查;完整旗標見 `reference.md` 或 `lumos --help`)

**讀 / 巡檢**
| 要做的事 | 指令 |
|---|---|
| 進場掃脈絡(頭部突顯 ⚠ 合約 + valid_under 過期標紅) | `lumos context <節點> [--brief]` |
| 全文搜尋(預設 BM25F 相關性排序) | `lumos search <詞> [--path Systems] [--top N]` |
| 動模組前查硬合約 | `lumos contracts [節點]` |
| 健康巡檢(orphans/verified_by 同步/合約綁定/鐵則 lint…) | `lumos doctor [--ci]` |
| 單檔快檢(寫完立刻自驗,比 doctor 快) | `lumos lint <節點>` |
| 反查連入/連出 | `lumos backlinks <節點>` / `links` |
| 讀決策 / 掃被推翻 | `lumos decisions <節點>` / `--superseded` |
| 該重驗哪幾篇 / stale 清單 / 最近異動 | `lumos stale [--candidate --match ..]` / `recent --days 7` |

**寫入**(一律 tmp→自驗→atomic rename;BOM/CRLF 拒寫)
| 操作 | 指令 |
|---|---|
| 改純量 status/updated/type | `lumos set <note> <key> <value>`(日期 bare 不加引號) |
| list 追加 verified_by/related/tags | `lumos append <note> <key> "[[x]]"`(安全格式+dedup) |
| 依模板建檔 | `lumos new <type> <name>` |
| 新增/翻盤決策(巢狀,非 ruamel) | `lumos decision-add` / `decision-supersede` |
| rename/移檔(連結改寫) | `scripts/graph-rename.sh <舊> <新>` |
| 歸檔老 Verification | `lumos archive [--days N] [--apply]` |

> ⛔ **禁用 `notesmd-cli` 的 `frontmatter --edit`**(只准 `move`):實測會把整篇 frontmatter 鍵序重排字母序、縮排 2→4、**日期加引號(date→text 靜默損傷)**——一碰整篇 diff 不可審、pre-commit 擋。frontmatter 合法寫入只有 lumos T1 + obsidian `processFrontMatter`。
> body 段落/checkbox/表格 → 用 **Edit**(非 lumos T1 範圍);版本歷史 → git。
---

## Frontmatter 鐵則(違反 = 長 ghost 節點或整篇 frontmatter 報廢)

血換來的四條,**不可犯**:

1. **多 wikilink 必須是 YAML list,一項一行**。❌ `verified_by: "[[A]], [[B]]"`(單字串)→ 貪婪吃成一個超長連結 → ghost 節點 + 垃圾檔。✅ list 一項一連結。
2. **block scalar(`summary: |`)內的 wikilink 不被索引**。summary 裡的 `[[X]]` 只是文字;要建關聯必須同時在內文或 list 型 property 放一份。
3. **含 `: `(冒號+空格)的長文必須 block scalar 或引號**。❌ `- content: 處置 SQL: UPDATE`(未引號)→ 整篇 frontmatter 解析失敗、所有 property 隱性失效。✅ `- content: |-` 換行縮排。
4. **同層禁重複鍵**。`decided:`/`valid:` 出現兩次 → Obsidian js-yaml 整篇 fail(CLI ruby 寬鬆放行,**CLI 過不代表 Obsidian 讀得到**)。

> 純量/list/decisions 走 lumos T1 天生避開這些雷;手改 frontmatter 才要盯。巡檢偵測指令見 `reference.md`。

---

## summary block(Systems/Issues 必有;掃一眼掌握全貌)

每行一個前綴。Systems 重 `FLOW`+`KEY`+`DEP`+`TEST`;Issues 重 `FLAG`+`DECISION`+`KEY`;Verification 重 `TEST`+`VERIFY`。

★位置是 frontmatter 的 `summary:` 欄位(`summary: |-` 底下逐行),不是 body 裡開一個 `## Summary` 標題★——寫錯位置的症狀很陰:`search` 照樣命中、標籤照樣解析出 `[★INVARIANT★]`,但 `contracts`／`guard` 會回「(無合約標記)」,讀的人因此以為這個節點沒有硬合約。這是靜默給錯答案,不是報錯。

| 前綴 | 用途 | 前綴 | 用途 |
|---|---|---|---|
| `FLOW:` | 核心流程 `a→b→c` | `VERIFY:` | 驗證紀錄 `[[..]]` |
| `KEY:` | 關鍵概念/欄位 | `DECISION:` | 決策簡版 `[日期]內容(valid)` |
| `DEP:` | 依賴模組 `[[..]]` | `FLAG:` | 語意標記 TECHNICAL/DECISION/ORIGIN |
| `TEST:` | 測試狀態 | `AUTH:` | 認證方式 |

分隔:`→` 流程方向、`｜` 分隔同類、`,` 分隔同欄。

---

## 合約性標記(合約 vs 偶然;最重要,動筆前掃一眼)

Systems 記的是「現在長怎樣」,分不出哪些是**合約**(改=breaking)哪些是**偶然**(可改)。用 KEY 行前綴聲明:

```
KEY:★INVARIANT★ <業務合約,改=breaking> [test:測試名] [audit:模型/日期] [kill:recipes]
KEY:★DEBT★ <已知偶然行為,可改不算 breaking>
```
- **未標 = 未聲明**;**不確定就不標**(寧漏勿錯)。**嚴禁從現況 code 反推「應該是合約吧」**——把偶然合約化會鎖死重構,比沒標更毒。只有業務語意明確或 decisions[] 載明意圖才配 ★INVARIANT★。

**合約鏈(行尾指針,遞增嚴格;深度規格見 `reference.md`)**:
- `[test:方法名]` — 綁一個真實測試(doctor Check T 強制,裸合約擋)。**綁定走指令**:`lumos guard bind <node> "<KEY子字串>" <測試名>`。
- `[audit:模型/日期]` — 綁測試後,合法性須經**無脈絡獨立 agent** 審過(prompt 中立「試圖反駁」,不帶風向;**判準=五問 rubric 逐條打勾,五項全過才 legal**——意圖證據/合約vs偶然/測試夠格/可證偽/爆炸半徑,含穩定性探針與防應試化兩道,完整規格見 reference.md〈[audit:] 獨立合法性審計〉段)。`lumos guard audit <node> "<KEY子字串>"`。
- `[kill:recipes]`(選配,金流建議)— 沙盒真弄壞、綁定測試必翻紅。`lumos guard kill-add` / `kill`。
- **天花板**:[test:] 只買 verification;「這規則現在還符不符合真實業務」是 validation,要對業務現實的人確認。

**可逆性(危險動作動手前先寫好收回,僅 Systems)**:
```
KEY:★IRREVERSIBLE★ <收不回:上架/prod遷移> [rollback:decisions]   # 必綁,否則 doctor Check R 擋
KEY:★CHECKPOINT★   <改了難救>                                     # 建議補 [rollback:],缺=提醒不擋
```
外部不可逆(信已送/下游已消費)→ 改用 `[guard:decisions]`(事前冪等鍵/核可閘)。`[rollback:]` 證「有寫 undo」≠「驗過能跑」。

**重生標記(from-scratch 重建的節點必蓋,Check J 守衛)**:
- **何時**:目擊記錄佚失/接手無人 legacy/整篇重寫——由 AI 看 code「重建」筆記時(≠平常 incremental 更新)。重建=逆向工程,可能編出自信的假 why/假合約,故課更嚴檢查。
- **蓋章**:`lumos set <節點> regen from-scratch/<日期>`(不蓋=Check J 不看;蓋了才守)。
- **summary 每條 claim 標身分**(四選一):`[src:路徑(:行號)]` code 作證(Tier A)/`[git:sha]` 提交作證(Tier B)/`推測:` 前綴=沒證據的猜(接在 KEY:/DECISION: 後)/`佚失:` 前綴=查不到,不編。
- **Check J 擋什麼**(lint/doctor 自動):★INVARIANT★ 無 [src:]/[git:] 意圖證據→擋(拒發明合約);DECISION 裸寫→擋;證據指針假的(檔案不存在/行號越界/git 查無)→擋;`推測:` 行承載 ★合約→擋。無標記 KEY 行只提醒不擋。
- **升級**:查證後補 [src:]/[git:];**佚失的 why 正確輸出是「佚失:」,嚴禁編一個合理的**。深規見 `reference.md`〈重生守衛〉段。

---

## 決策(ADR)· 驗證 · 雙向同步(要點;完整見 `reference.md`)

- **重大決策**(架構/技術/流程/安全選型)`decisions[]` 必填四欄:`context`/`alternatives_considered`(≥2)/`why_chosen`/`trade_offs`——**缺資訊就問人,不可編造**污染學習資產。翻盤:舊條 `valid:false`+`superseded_by`+`ended`,新條重填完整四欄。
- **Verification** 必填 `valid_under`(有效條件:版本/規模/schema)+ `revalidate_when`(重驗觸發)。建 Verification **同步**把 wikilink 加進相關 Systems 的 `verified_by`(雙向,缺一不可;漏寫 `lumos sync-verified-by --apply` 補)。
- **plan_refs**:落地某計劃的 Verification(含後續迭代)填 `plan_refs` 反指計劃節點(意圖鏈,doctor Check 4 把關)。
- **計劃/設計一律寫圖譜計劃節點**(`Projects/<主題>_計劃`,`type:project`),**不寫 `docs/superpowers/specs/`、`openspec/` 等 repo 路徑**——覆寫任何 SDD 工具的預設落點。

---

## 自足性審計(圖譜實質更新後必做)

派**乾淨 sonnet agent 只讀圖譜**還原脈絡 → 主對話比對「還原結果 vs 腦中現存脈絡」:有出入 = 圖譜當下不健全,補缺後**重審到一致**。純格式修正可豁免。
> 無主對話脈絡時(定期巡檢/接手陌生專案)→ 改用「圖譜×程式碼交叉審計」(以 code 為真值),做法見 `reference.md`。

---

## 常見工作流

```bash
# 開工:掌握現況
lumos search "status/doing"; lumos recent --days 7; lumos context Systems/<模組>

# 改完 code:更新圖譜
lumos set Systems/<模組> updated <日期>
lumos append Systems/<模組> verified_by "[[Verification/<日期>_xxx]]"
# body 進度/表格 → Edit;寫完 → lumos lint <節點>

# 環境變動後:掃該重驗的
lumos stale --match "<變更關鍵字>"
```

## 資料夾 / 位置

`docs/{slug}-knowledge/{Projects,Systems,Issues,Verification,MOC}`(隨 git 版控)。某主題筆記 >5 份 → 建/更新 MOC 索引。
