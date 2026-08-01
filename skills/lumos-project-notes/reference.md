# lumos-project-notes · reference（權威展開版）

> 這是 SKILL.md（本精簡版頭版）的**完整細節版**。頭版給「做什麼 + 紀律」並用觸發表指你來讀對應段;此處放深規/模板/完整規格/邊角。**金科玉律 / vault 偵測 / 進場三步 / frontmatter 鐵則 / 合約標記快規等基礎已在頭版,不重複。**

## 跨專案核心圖譜接點(唯讀說明)

部分業務規則可能已**升格**到既有專案自己的跨專案核心圖譜(圖譜裡看到的 `core_refs:` 或 summary `CORE:` 行即是指標)。★本精簡版不含核心圖譜維護的 skill/工具★,以下只講「讀到這些標記代表什麼」:

1. **看到筆記 frontmatter `core_refs:` 或 summary `CORE:` 行** → 該主題權威可能在另一個核心圖譜,本專案筆記殘留描述**不可當權威**(疑似快照)
2. 語意/規則異動、雙向核對等維護動作不在本精簡版範圍——這些標記留著給有核心圖譜工具的人處理

## 操作方式

### 主要工具：lumos（讀 / 寫 / 巡檢 / 歸檔一律優先）

repo 內的 `scripts/lumos`（python3 標準庫，零 Obsidian 依賴）是**日常操作圖譜的主要工具**。讀取、寫入、巡檢、歸檔一律先用 lumos；Obsidian CLI 只保留給 lumos 沒有的少數場景（見下節）。

> **全域安裝**：本精簡版隨附 `install.sh`（不是 `lumos install`——那支子命令未交付），跑一次把 `lumos` 裝上 `~/.local/bin`，之後任何專案子目錄直接打 `lumos <cmd>`（find_vault 從 cwd 往上找 docs/*-knowledge）。下文一律用全域 `lumos`。★不要用 `python3 scripts/lumos`★——若你所在的專案本身 vendored 了完整版 `scripts/lumos`（checked in、非本精簡版安裝的），那個寫法會呼叫到**完整版 53 支指令**，不是本精簡版的 24 支子集；`init`/`update` 等本精簡版未交付的指令在那條路徑上會**真的執行**，可能動到專案層 `CLAUDE.md`。全域安裝是本包唯一保證等價的路徑。

**禁止用 Grep/Glob/Read/Edit/Write 直接操作 `docs/{vault-name}/` 下的 .md 檔案。**
lumos 提供圖譜感知能力（backlinks、links、orphans、contracts、合約測試綁定），是單純讀寫檔案做不到的；直接編輯也繞過寫後自驗與鐵則防護。

**讀取 / 巡檢**：

| 用途 | lumos 指令 |
|---|---|
| **單檔快檢（寫完一個節點立刻自驗標籤/格式，比 doctor 快）** | `lumos lint <筆記名>` — type/summary/★ 格式/裸合約/未審/ghost trap;node-local 不掃 repo |
| 健康巡檢（orphans / unresolved / verified_by 同步 / plan_refs 意圖鏈 / 同名守衛 / 鐵則 lint / ★INVARIANT★→測試綁定 + 獨立合法性審計；Check P 失效檔案認領(節點正文 inline-code 路徑指向已不存在的 repo 檔 → 軟提醒「圖譜指向死碼」)） | `lumos doctor [--ci]` |
| 讀單篇 decisions | `lumos decisions <筆記名>` |
| 全 vault 掃被推翻決策 | `lumos decisions --superseded` |
| 環境變更掃 valid_under / revalidate_when 命中 | `lumos stale --match "<條件字串>"` |
| **改某流程前查「該重驗哪幾篇」** | `lumos stale --candidate --match "<關鍵字>"` — 聚焦活躍 Verification 的 `revalidate_when`(未來重驗條件、排 Archive);比純 `--match` 窄(後者含 valid_under 快照 + Archive) |
| status=stale 清單 | `lumos stale` |
| 最近 N 天修改 | `lumos recent --days 7` |
| 資料夾統計 | `lumos stats` |
| 反查連入/連出 | `lumos backlinks <筆記名>`／`links` |
| 進場掃脈絡（節點 + 鄰居 closet 索引；頭部突顯 ⚠ 合約） | `lumos context <筆記名> [--brief]` |
| **合約登記簿（動模組前查硬合約）** | `lumos contracts [筆記名]` — 列 ★INVARIANT★(改=breaking)/★DEBT★(可改);只認 KEY 行前綴標準格式 |
| **全文搜尋** | `lumos search <詞> [--path Systems] [--regex] [--files-only] [--top N] [--json]` — frontmatter+body,大小寫不敏感 substring;**預設 BM25F 相關性排序**(2026-07-11 轉正,goldset 評測修正尺 nDCG@5 +58.1%;只重排既有候選不擴召回,預設全量+逐檔命中明細,--top N 才截);`--legacy` 走舊字母序全量,`--regex` 自動走舊路;**A1 型別先驗:MOC 索引頁 ×0.4 降權**(仍在結果內只是後移;要找索引頁用 `--path MOC` 直達) |
| 鄰域樹狀展開／畫圖 | `map <筆記名> --depth 2`／`export --folders Systems Projects` |

**寫入**：

| 操作 | 指令 | 說明 |
|---|---|---|
| 改純量 status/updated/created/type | `lumos set <note> <key> <value>` | 行級手術，構造性最小 diff（只改該行，其餘原樣）；日期 bare 不加引號 |
| list 追加 verified_by/plan_refs/related/tags | `lumos append <note> <key> "[[x]]"` | 鐵則1 安全格式、自動 dedup |
| 依模板建檔 | `lumos new <type> <name>` | system/verification/issue/project |
| rename / 移檔（連結改寫） | `scripts/graph-rename.sh <舊> <新>` | 封印 wrapper（notesmd move），含 frontmatter 字串 |
| 滾動歸檔老 Verification | `lumos archive [--days N] [--apply]` | 單遍移檔 + path 式入連結正規化成 basename；dry-run 預設；**活守衛護欄**：仍背書存活守衛(綁定測試在 code)的 Verification 不按年齡歸檔 |
| **巢狀:翻盤決策** | `lumos decision-supersede <note> "<content子字串>" --by "..." [--ended DATE]` | decisions[] 某條 valid:false + superseded_by;surgical 不碰子清單/其他條 |
| **巢狀:新增決策** | `lumos decision-add <note> "<content>" --decided DATE [--context ..] [--why ..]` | append ADR 決策(無 decisions 則建) |

- T1 寫入一律**寫 tmp → 自驗(值正確+無新指紋) → atomic rename**，失敗原檔不動；BOM/CRLF 檔拒寫
- **decisions 翻盤/新增** → `lumos decision-supersede` / `decision-add`（surgical 巢狀;**非 ruamel**——ruamel round-trip 會 reflow、破壞最小 diff）
- **白名單外的 frontmatter 寫入**（`summary` block 改某行、`alternatives_considered` 子清單編輯）→ lumos 目前無對應,走下節 obsidian `processFrontMatter` eval 或手動 Edit

**安裝 / 生命週期**：本精簡版的機器層安裝／解除不走 `lumos` 子命令（`install`/`uninstall`/`update`/`bootstrap`/`init`/`deinit`/`teardown` 皆未交付）。改用交付包隨附的 `install.sh`——用法見專案 README。

> ⚠ **`doctor`／`lint` 有些檢查會建議跑本精簡版沒交付的指令**——這是從完整版原封繼承的訊息文字，**看到請忽略、不用照做**（判準是「打了會得到『未知指令』錯誤」，不是背下一份清單）。已知會出現的至少有 `lumos init`／`lumos update`／`lumos self-audit`／`lumos signoff`（後者出現在 regen 節點的證據檢查訊息裡，`lint` 和 `doctor` 都會印，建議「走 signoff 升級」）——這份列舉不保證窮盡。最常見的是 `CLAUDE.md` 紀律區塊比對（Check D）：sentinel 損壞或與範本不同步時會建議跑 `init`/`update` 修復；`CLAUDE.md` 相關的檢查在本版**沒有修復路徑**，那是刻意的（本版不注入、不更新任何 `CLAUDE.md`，見專案 README〈怎麼裝〉）。

> **子命令全覽（本精簡版 24 支頂層命令；`lumos --help` 為現行權威）**：讀取/導航（`context` `show` `contracts` `search` `links` `backlinks` `map` `export` `decisions` `stale` `recent` `stats`）+ 巡檢/治理（`doctor` `lint` `sync-verified-by` `rel-cascade`）+ 寫入（`set` `append` `new` `archive` `decision-add` `decision-supersede` `decision-reindex`）+ 合約守衛（`guard` list/scaffold/bind/audit/trace/kill/kill-add）。

### Obsidian CLI：僅限 GUI 檢視場景（指令已刪,見文末〈Obsidian〉節）

### ⛔ 禁用工具：notesmd-cli 的 `frontmatter` 指令

第三方 `notesmd-cli`（原 Yakitrak/obsidian-cli，Go 單檔）**只准用 `move`**（rename 連結改寫含 frontmatter 字串,2026-06-13 驗收通過;即上方 `graph-rename.sh` 封的那層）。**`frontmatter --edit` 嚴禁對真實 vault 使用**：實測會把整篇 frontmatter 鍵序重排成字母序、縮排 2→4、**日期加引號（property 型別 date→text 靜默損傷）**——一碰整篇 diff 不可審,且 pre-commit 污染指紋會擋。frontmatter 寫入合法路徑只有：lumos T1（純量/list/decisions）、obsidian `processFrontMatter` eval（白名單外）。驗收證據：MyApp vault 的 `2026-06-13_Yakitrak三題驗收`。

### 降級模式（lumos 與 obsidian 都不可用時）
以下情況才允許 Read/Edit/Write 直接碰 .md：
- `scripts/lumos` 不存在 **且** Obsidian App 未執行 / vault 未註冊 / CLI 報錯
- lumos 無法精準替換特定內容時（如修改表格某一行），可用 Edit 輔助（這類 body 表格編輯本就不是 lumos T1 範圍）

## 知識庫位置

- **路徑**：`docs/{project-slug}-knowledge/`（專案 repo 內，隨 git 版控）— 新慣例
- **舊路徑**：`docs/knowledge/` — 舊專案維持相容
- **團隊共用**：clone repo 後用 Obsidian 開啟對應資料夾即為獨立 Vault

## 資料夾結構

```
docs/{project-slug}-knowledge/
├── Projects/          # 專案總覽筆記（一個專案一份）
├── Systems/           # 功能模組 / 系統元件筆記
├── Issues/            # 追蹤中的問題
├── Verification/      # 驗證紀錄（每個功能的測試結果）
└── MOC/               # Maps of Content（索引筆記）
```

## 標籤慣例

| 類別 | 標籤 | 用途 |
|------|------|------|
| 狀態 | `status/doing` | 正在進行 |
| 狀態 | `status/todo` | 待辦 |
| 狀態 | `status/done` | 已完成 |
| 狀態 | `status/blocked` | 被阻擋 |
| 類型 | `type/project` | 專案 |
| 類型 | `type/system` | 系統元件 |
| 類型 | `type/issue` | 問題追蹤 |
| 類型 | `type/verification` | 驗證紀錄 |
| 驗證 | `status/pass` | 測試通過 |
| 驗證 | `status/fail` | 測試失敗 |
| 驗證 | `status/stale` | 曾經 pass 但 `valid_under` 條件已變/`valid_until` 已過，需重跑 |
| 優先 | `priority/P0` | 緊急 |
| 優先 | `priority/P1` | 重要 |
| 優先 | `priority/P2` | 一般 |

## Properties（YAML Frontmatter）慣例

```yaml
---
status: doing
type: project
created: 2026-03-26
updated: 2026-03-26
related:
  - "[[系統A]]"
  - "[[系統B]]"
tags:
  - status/doing
  - type/project
summary: |
  FLOW:主要流程A→B→C | AUTH:認證方式
  KEY:關鍵概念1,關鍵概念2
  DEP:[[依賴模組A]][[依賴模組B]]
  TEST:通過數/總數(日期) | VERIFY:[[驗證紀錄]]
  DECISION:[日期]決策內容(valid)
verified_by:
  - "[[Verification/2026-04-07_API審計修復]]"
  - "[[Verification/2026-05-04_點數圈存顯示]]"
decisions:
  - content: "決策描述"
    context: "當時的背景／痛點／約束（為什麼非做不可）"
    alternatives_considered:
      - "選項A：說明 / 為何不選"
      - "選項B：說明 / 為何不選"
    why_chosen: "為什麼選了這個（vs alternatives）"
    trade_offs: "犧牲了什麼（成本／彈性／複雜度／學習曲線）"
    decided: 2026-03-26
    valid: true
---
```

### Frontmatter 鐵則（違反 = 圖譜長 ghost 節點或整篇 frontmatter 報廢）

2026-06-10 MyApp 圖譜健檢實際踩雷總結，四條鐵則：

1. **多個 wikilink 必須是 YAML list，一項一連結**。❌ `verified_by: "[[A]], [[B]]"`（單一字串）→ Obsidian 把整串從第一個 `[[` 貪婪吃到最後一個 `]]` 當成**一個**超長連結 → 圖譜長出亂碼灰色 ghost 節點；在 Obsidian 點到該節點還會**自動建立含 `]], [[` 的垃圾檔案**（檔名中的 `/` 切成巢狀資料夾）。✅ 寫法見上方 `related` / `verified_by` 範例。
2. **block scalar（`summary: |` 等）內的 wikilink 不會被索引**。寫在 summary 裡的 `[[X]]` 只是文字，不產生圖譜連結、不算 backlink——要建立關聯必須同時在內文（如「## 相關模組」）或 list 型 property 放一份，否則目標筆記可能變孤兒。
3. **含 `: `（冒號+空格）的長文必須用 block scalar 或引號**。❌ `- content: 處置 SQL: UPDATE ...`（未引號）→ YAML `mapping values are not allowed` → **整篇 frontmatter 解析失敗**，所有 property 查詢對此筆記隱性失效。✅ `- content: |-` 換行縮排放長文。
4. **同一層級禁止重複鍵**。`decided:` / `valid:` 在同一個 decision item 出現兩次 → Obsidian 的 js-yaml 直接整篇 fail（CLI 的 ruby/libyaml 寬鬆放行，**用 CLI 驗過不代表 Obsidian 讀得到**）。

**巡檢偵測指令**（健康巡檢時跑）：

```bash
# 偵測 frontmatter YAML 解析失敗（鐵則 3；macOS 內建 ruby，注意 libyaml 比 js-yaml 寬鬆，過了不代表 Obsidian 過）
ruby -ryaml -rdate -e 'Dir.glob("docs/{vault-name}/**/*.md").each { |p| t = File.read(p); next unless t.start_with?("---"); parts = t.split(/^---\s*$/, 3); next if parts.length < 3; begin; YAML.safe_load(parts[1], permitted_classes: [Date], aliases: true); rescue => e; puts "#{p} -> #{e.message[0,120]}"; end }; puts "scan done"'

# 偵測 Obsidian 端解析失敗（鐵則 3+4 都抓得到；對「有 frontmatter 卻讀不到」的筆記交叉確認）
obsidian vault="{vault}" eval code="app.vault.getMarkdownFiles().filter(f => { const c = app.metadataCache.getFileCache(f); return c?.sections?.[0]?.type === 'yaml' && !c.frontmatter; }).map(f => f.path).join('\n') || '全部可解析'"

# 偵測字串型多 wikilink（鐵則 1）與 ghost 垃圾檔案
grep -rln ']], \[\[' docs/{vault-name}/ --include='*.md' | head
find docs/{vault-name} -name '*\]\]*'
```

### summary 欄位（中文結構化摘要）

**所有 Systems 和 Issues 筆記必須有 `summary` 欄位。** 讓 Claude Code 掃一眼 frontmatter 就掌握模組全貌，不需要讀完整篇筆記。

符號規則：

| 符號 | 用途 | 範例 |
|------|------|------|
| `FLOW:` | 核心流程 | `reserve→complete→void` |
| `AUTH:` | 認證方式 | `HMAC-SHA256`, `JWT` |
| `KEY:` | 關鍵概念/欄位 | `transactionId貫穿三階段` |
| `DEP:` | 依賴模組（用 wikilink） | `[[Billing]][[Inventory]]` |
| `TEST:` | 測試狀態 | `12/12通過(2026-04-07)` |
| `VERIFY:` | 驗證紀錄連結 | `[[2026-04-07_API審計修復]]` |
| `DECISION:` | 重大決策（簡版） | `[日期]內容(valid/superseded)` |
| `FLAG:` | 語意標記 | `TECHNICAL`, `DECISION`, `ORIGIN` |
| `→` | 流程方向 | `A→B→C` |
| `｜` | 分隔同類項目 | `A｜B｜C` |
| `,` | 分隔同欄細項 | `a,b,c` |
| `(valid)` | 現行有效 | |
| `(superseded)` | 已被取代 | |
| `★INVARIANT★` | KEY 行前綴：業務合約，改動 = breaking | `KEY:★INVARIANT★ 自動型只派V` |
| `★DEBT★` | KEY 行前綴：已知偶然行為，可改不算 breaking | `KEY:★DEBT★ RetentionDays=7寫死非設定` |

不同筆記類型的重點：
- **Systems**: FLOW + KEY + DEP + TEST（流程、關鍵欄位、依賴、測試）
- **Issues**: FLAG + DECISION + KEY（標記、決策、關鍵發現）
- **Verification**: TEST + VERIFY（測試結果、驗證紀錄）

### ★INVARIANT★ / ★DEBT★ 合約性標記（合約 vs 偶然）

Systems 節點記錄的是「做完的功能描述」（現在是什麼），天生分不出哪些行為是**合約**（改了 = breaking）、哪些是**偶然**（實作副產物，可隨意改）——未來修改者只能猜。解法是 KEY 行的合約性前綴（2026-06-12 Sonnet 對抗審計選定：**不開「需求與邊界」H2 段**——那會是繼 KEY 行 / decisions[] / DECISION: 行之後第四個放不變量的位置，多軌必漂移；收進既有 KEY 行單一位置）：

- `KEY:★INVARIANT★ ...` — 業務合約。改動此行為 = breaking change，動之前必須先翻 decisions[] 確認意圖
- `KEY:★DEBT★ ...` — 已知偶然行為（實作副產物 / 暫定值 / 寫死常數）。可重構，不算 breaking
- **未標 = 未聲明**（合約性未知，動之前自行判斷）。不回溯大掃除；動到節點時若當下脈絡足以判定，順手補標
- **不確定就不標**（寧漏勿錯，同 L3 confidence 0.7 哲學）。**嚴禁從現況 code 反推「應該是合約吧」**——把偶然行為合約化會鎖死重構，比沒標更毒。只有對話中業務語意明確、或 decisions[] 已載明意圖的行為，才配 ★INVARIANT★（例：decisions 標「暫定，待業務確認」的行為 = ★DEBT★，不是 ★INVARIANT★）
- 慣例起源範例：某筆記的 `KEY:★INVARIANT★ 自動型流程只允許 X、不得走 Y`（合約性標記常自發長出，本規範把它 codify 成統一格式）

### ★INVARIANT★ → `[test:]` 綁定（合約即測試，2026-06-14 機制；doctor Check T 強制）

★INVARIANT★ 只是「宣稱」，沒有可執行證據就還停在「形式為真」（讀 code 看得出）而非「驗到真」（真跑會綠）。**每條 ★INVARIANT★ 在行尾加 `[test:方法名]`**，認領一個真實存在的測試方法：

```
KEY:★INVARIANT★ 點數不足 → INSUFFICIENT_POINTS,在扣點/寫 Registration 之前擋下 ... [test:ActivitySignupInsufficientPointsRejected]
```

- **doctor Check T 強制**：`lumos doctor` 把每條 ★INVARIANT★ 對到一個真實 `[Fact]/[Theory]/[SkippableFact]` 方法（`discover_test_methods` 認真方法，**非子字串比對**——綁到散文/工具方法/拼錯 = 偽證據,擋）。裸合約（沒綁）也擋。
- **① 先判平台（綁 [test:] 的第 0 步;單技術棧專案可略過）**：問「這條合約由**哪個平台/repo 的測試**驗?」——
  | 情境 | 綁法 |
  |------|------|
  | 同 repo 單技術棧(多數專案) | 裸 `[test:名]`(現況) |
  | **單一圖譜記錄的系統橫跨多技術棧 / 多 repo**(前端 App 一個 repo、後端 API 另一個 repo,共用同一圖譜) | `.lumos/config.json` 用 `platforms` map(各平台指 profile + root),綁 **`[test:平台:名]`**、`guard bind/scaffold --platform <平台>`。合約講**哪一端的行為就綁那一端的測試**(如後端合約 → `[test:<後端平台名>:…]`),別把它硬綁到另一端的測試(會變偽證據/套套邏輯) |
  | 合約由 **UI E2E** 驗(點擊流程/跨畫面/真機或瀏覽器,非單元) | 該平台 profile 用 **`maestro`**(mobile)/**`playwright`**(web),綁 flow `name:` / `test('id')`(見文末 test_profile 段) |
  - 判不準測試在哪個平台就**別亂綁**——先確認測試真的在哪、config 有沒有該平台(缺就先補 `platforms`)。詳見 [[Systems/test-profile-multiplatform]]。
- **② 三種 guard（在選定平台內,選最能「驗到真」的那種,別寫套套邏輯）**：
  | 類型 | 專案 | 何時用 | gate |
  |------|------|--------|------|
  | 純函式 | `MyApp.Tests` | 載重**公式**(累點/單次上限) | ubuntu 真跑,dev+prod+PR |
  | 行為整合 | `MyApp.IntegrationTests` | **拒絕路徑**零寫入(點數不足/超賣) | lab deploy 真跑(帶 DB secret) |
  | 狀態驗證 | 同上 | 真寫入 → **讀回 DB 斷言落地值**(累點真加對 AccountBalance、Complete↔Void 淨零) | 同上 |
- **誠實鐵則（B3/B4 教訓）**：守衛**不可靜默跳過**。唯一合法 skip = 本機/PR 無 `DB_CONNECTION_STRING`(整段 SkippableFact skip)。其餘「比率過期/種子取不到/schema 變更」一律 `Assert.True(...)` **大聲失敗**——否則守衛悄悄變儀式,綠燈但什麼都沒驗。純規則的套套邏輯測試(讀 code 就看得出對錯)不算數,要驗 service→repo→SQL→DB 真落地。
- **lab2 = 測試庫**：整合/狀態守衛用全新唯一測試會員,`finally` 依 CustNo 全刪,不留痕。不要把 lab2 當正式機綁手綁腳。
- **不重複**:guard 怎麼寫的細節 / lab CI 真機證據,寫進對應 `Verification/2026-06-14_lumos_*.md`,KEY 行只留 `[test:]` 指針。流程已知限制見 [[2026-06-14_lumos_guard審計_已知限制]]。

### ★INVARIANT★ → `[kill:recipes]` 殺傷力驗證（第三級，選配，2026-07-10）

`[test:]` 證保鑣存在、`[audit:]` 審保鑣合格——都沒真打一拳。高風險/金流合約建議補第三級：

```bash
lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y --note "業務上壞了什麼"
lumos guard kill <node>   # 沙盒(worktree)真弄壞 → 綁定測試必翻紅;survived=稻草人 rc1
```
- 壞法**從業務行為推導**（「驗章短路成恆真」），不從實作反轉；跑測試的指令由 `.lumos/config.json` 宣告（多平台 `platforms.<名>.run_cmd`、單平台 `test.run_cmd`，含 `{method}` 佔位）。
- 七態（2026-07-29 oracle 品質包升級）：**`killed`＝強證據**（綁定測試名與失敗標記鄰近共現，且標記不落在名字串內）／**`killed_unattributed`＝弱證據**（紅了但歸因不到綁定測試，可能是編譯錯/環境掛，印警告建議 run_cmd 加 filter）／**`timed_out_weak`＝弱證據且不計 killed**（刻意變更：掛掉可能是環境非變異）／`survived`（稻草人）／`drifted`（配方漂移重寫）／`abort`（baseline 就紅）／`error`。
- rc 優先序：survived→1；drifted/abort/error→2；**全部弱證據→1**（沒有任一條被證實咬住，不得以 rc0 報成功）；有強殺且無錯→0。摘要「咬得住」只配全強殺，混弱證據改印「強殺 X / 弱 Y」。留痕 `docs/.kill-log.jsonl`（逐筆 append；本精簡版無 `gov` 指令可查，需要時直接開檔看）。
- 天花板：證「接得住這條壞法」不證「接得住所有壞法」；沙盒只隔離程式碼不隔離 DB——只對自我清理的測試跑。

### ★INVARIANT★ → `[audit:]` 獨立合法性審計（合約即外審，2026-06-18 機制；doctor Check T 強制）

`[test:]` 證的是「程式**有沒有照規則做**」(verification);它證不了「這條**該不該**是不可改的鐵則」「綁的測試**夠不夠格**(會不會是同源套套邏輯)」。這兩個判斷**沒有標準答案**,而 2026 maker/checker 共識(治理日報 6/17)說得很白:**讓提出者自己評必手下留情**。所以:

> **每條 ★INVARIANT★ 一旦綁了 `[test:]`(視為宣告完成),其「合法性」必須由一個*無對話脈絡的獨立 agent* 判過並通過,在行尾留 `[audit:模型/日期]`。** doctor Check T 對「綁了測試卻沒 `[audit:]`」報**未審**(`--ci`/`--strict` 下擋)。

```
KEY:★INVARIANT★ 點數不足 → INSUFFICIENT_POINTS,扣點前擋下 ... [test:InsufficientPointsRejected] [audit:sonnet/2026-06-18]
```

**「乾淨」與「範圍」兩條件(缺一不算第三方驗證)**:

1. **乾淨脈絡**:審計 agent **只拿到圖譜 + 程式**,**不餵你的結論、不餵你的理由、prompt 必須中立(用「試圖反駁」而非「請確認這條合法」**——後者是帶風向,等於自己改自己的考卷)。它若繼承了 maker 的框架,只是換個分身蓋章,不算外人。
2. **範圍=五問 rubric,逐條打勾**(2026-07-27 升級,borrow Sage arXiv 2512.16041:判官難題約 1/4 偏好前後不一、無明確準則時同模型因情境飄移——rubric 錨定把「情境偏好」變準則判斷。原兩問保留為 ②③):
   - ① **意圖證據**:decisions[]/緣起讀得到「這是刻意設計」嗎?讀不到意圖=候選不合格(可能是 code 反推)。
   - ② **合約 vs 偶然**:只讀圖譜,這是『不可改的合約』還是『現在剛好這樣實作』被誤標?
   - ③ **測試夠格**:構造一個違反這條保證、但綁的測試**仍會過**的情形——構造得出=同源/套套邏輯,不合格。**必須實際去看測試碰了什麼**,不能只讀。
   - ④ **可證偽性**:宣稱有沒有可觀測的「違反長什麼樣」?「應該要好/要穩」型散文=不合格。
   - ⑤ **爆炸半徑**:改掉它,說得出具體 breaking 什麼下游(誰依賴這個行為)?說不出=可能不是合約。
   - **判決=五項全過才 legal**;任一不過=不合格並指出項次。逐項要「過/不過+一句證據」,不收整體印象分。
   - **穩定性探針(選配,難判場觸發)**:審計員判得猶疑/勉強過 → 同材料**換問法重問一次**(「試圖反駁」→「這條若降級為 ★DEBT★,會有什麼實害?」),兩問判決不一致=**unstable,不蓋章、記 note 交人裁**。理由(Sage):可靠度別拿小量人工標註當金標準(人標本身不一致),換序自一致是更便宜誠實的代理。
   - **防應試化兩道(2026-07-28,borrow arXiv 2605.12474:評分表公開固定→被評方學會剛好滿足字面,分數漲實質沒變好;強評分者只能減輕不能根除)**:① 派工時**五問語意不變、措辭改述**(每次審計換句式,勿逐字貼本節文字——固定考卷會被背熟);② **定期無表抽考**:約每 5 次 audit 抽 1 次不帶 rubric 的開放式獨立判定,兩邊結論落差記 note——落差拉大=五問正被寫合約方「照著填」,評分表儀式化訊號,回報人裁。
   - ⚠ 一個節點**通過第四道自足性審計(讀得懂、還原得出)** ≠ 這五問被覆核過——是不同的問題,別混為一談。

**天花板(再乾淨也跨不過)**:`[audit:]` 只買到 verification 那一半;它**證不了 validation**——「這條金流規則**現在還符不符合真實業務**」要對著業務現實的人來確認(見下節 `decisions`/最高層鐵則的『上次對業務確認』)。**別讓「乾淨 agent 過了」被誤讀成「業務上也對」**;不可逆動作與業務正確性,該擋的閘仍留給人。

**模型選擇**:預設 `sonnet`(`--model` 可改)。刻意用較弱模型是為了讓它**不腦補補洞**——圖譜真的自我解釋得通、測試真的擋得住,才過得了關;強模型太會「替你圓場」。

**留痕**:`lumos guard audit <node> "<KEY 行子字串>" [--model sonnet] [--date YYYY-MM-DD]`(寫後自驗,重審覆蓋舊日期)。**工具只記留痕,不證明審計真的乾淨**——那靠上面兩條件的誠實自律,同 §「防帶風向鐵則」。

### ★CHECKPOINT★ / ★IRREVERSIBLE★ → `[rollback:]` 可逆性綁定（2026-06-19;doctor Check R）

不可逆動作(上架、prod DB 遷移)動手前要寫好怎麼收回。KEY 行前綴,**僅限 Systems 節點**:
- `KEY:★IRREVERSIBLE★ <宣稱> [rollback:decisions]` — 收不回。**必綁**;`[rollback:decisions]` 需本節點 `decisions[]` 有非空 `rollback` 欄位(實際回退 SQL/補償步驟)。缺=doctor Check R **error**(--ci/pre-push 擋)。
- `KEY:★CHECKPOINT★ <宣稱>` — 改了難救;建議補 `[rollback:decisions]`,缺=warning 不擋。
- 未標 = 可逆(git/測試級,放手)。
- **天花板**:`[rollback:]` 證「你寫下了 undo」,**不證明它跑得動 / 與現行 schema 一致**(同 [test:]/[audit:])。別把「有寫」當「安全」。
- v1 手寫 `[rollback:decisions]`(無專用指令);`lumos lint` / `doctor` Check R 把關。
- 外部不可逆動作(信已送出、prod 遷移下游已消費)事後無逆操作 → 用 `[guard:decisions]`(decisions[] 記非空 `guard`:冪等鍵/核可閘)取代 `[rollback:]`;兩軌任一即過 Check R,`[guard:]` 僅 `★IRREVERSIBLE★` 適用。

### `lumos guard`：對談驅動的守衛 scaffold（2026-06-15)

把「★INVARIANT★ → 寫守衛 → 綁 [test:]」這條手抄苦工交給 lumos 的機械部分,**斷言本體仍由你經對談向人確認後填**。三步:

```bash
lumos guard list [--unbound]        # 列所有 ★INVARIANT★ 綁定狀態(real/dangling/fake/naked);--unbound 只列未綁
lumos guard scaffold --node <Systems/X> --invariant "<KEY行子字串>" \
    --method <測試名> --type pure|behavioral|state --claim "<向人確認過的可測斷言>" \
    [--out <測試專案目錄>] [--template <路徑>] [--class <類別名>]
lumos guard bind <node> "<KEY行子字串>" <測試名>   # 把 [test:測試名] 綁回 KEY 行(寫後自驗)
lumos guard audit <node> "<KEY行子字串>" [--model sonnet] [--date YYYY-MM-DD]   # 合法性經無脈絡獨立 agent 審計過 → 留痕 [audit:](見上節)
lumos guard trace [<node>]          # 合約→守衛測試→Verification 證據鏈(reverse:改某模組會動到哪些守衛/驗證)
lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--test 名] [--note "業務上壞了什麼"]   # 宣告壞法配方(kill_recipes+[kill:recipes])
lumos guard kill <node> ["<KEY子字串>"] [--json]   # 殺傷力驗證:worktree 隔離→baseline 綠→套壞法→綁定測試必須翻紅;survived=稻草人 rc1
```

**改某模組前查爆炸半徑**:`lumos guard trace Systems/X` 列出該節點每條 ★INVARIANT★ → 綁的測試方法 → 哪篇 Verification 背書(grep 輸出某測試名即反查「這守衛紅了會牽動誰」)。

**補 verified_by 漏寫**(doctor Check 3 的零判斷項自動修):
```bash
lumos sync-verified-by            # dry-run:列 Verification 連到 Systems 但 verified_by 漏列的
lumos sync-verified-by --apply    # 真寫(T1 atomic append,自帶 dedup,冪等)
```
> 只補 verified_by 這一項。orphan 補掛 / plan_refs 斷鏈需**語意判斷**,doctor 只報不自動修(亂補會掛錯節點)。

- **scaffold 產的是預設紅燈 stub**:套技術棧範本(`.lumos/guard-templates/<type>.tmpl`,專案自備、lumos 語言無關不內建),填好 class/method/invariant/claim/TestIds 前綴,**斷言留 `// TODO` + `Assert.Fail(...)`**——逼你填到綠,不准假綠。
- **bind 是 KEY 行外科手術**:把 `[test:]` 寫進 summary block 的 ★INVARIANT★ 行(已綁則 merge 進同一個 `[test:A,B]`),寫 tmp→自驗該 ref 真的 parse 得到→atomic。

**⛔ 防帶風向鐵則(leading the witness)**:這套指令存在的前提是「claim 的真來自**人確認的意圖**,不是 code 反推」。Claude 用它時必須:

1. **先問「這裡什麼必須永遠為真」,再去看 code 怎麼實作**——不可先讀 code 反推出斷言、再包裝成「請確認」讓人蓋章(那是假 validation,繞回 Check T 在打的套套邏輯)。
2. **誠實標記每條斷言的來源**:是「你(人)講的意圖」還是「我從 code 猜的、請你裁示」——後者必須明講、等人確認才寫進 `--claim`。
3. **重大 invariant 的 claim 等同重大決策**:確認時順手把 `decisions[]` 的 context/why 補上(見下節),別只留一句斷言。
4. **殘餘誠實**:人可能確認一條錯的 invariant——這是 validation 的天花板,工具只保證 claim 被攤開+明確確認,不保證人一定對。別吹過頭。

> scaffold/bind 只省「打字」,不省「確認」。doctor Check T + 誠實鐵則(上節)照舊兜底:stub 不填(留 Assert.Fail)= 紅;綁了不存在的方法 = 懸空被擋。
>
> **測試棧 profile(語言可插拔,P5)**:guard/Check T 的「認哪些測試方法」由 `.lumos/config.json` 決定。內建 4 個 profile:**`csharp-xunit`(預設)**、**`kotlin-junit`**(Android 單元)、**`maestro`**(Android E2E,綁 flow `name:` 欄位;`file_must_match=^appId:` 只認真 flow;多字 name NO MATCH)、**`playwright`**(web E2E,綁 `test('id')`/`test.describe('id')`;含空白 title 不可綁)。各 profile 定:掃哪些副檔名、方法 regex、scaffold 副檔名、測試目錄偵測。**無 config = csharp-xunit,完全向後相容**。逃生口:`config.json` 的 `test` 可欄位級覆蓋 `exts`/`scaffold_ext`/`method_regex`。範本仍技術棧專屬、放各專案 `.lumos/guard-templates/`。
> ```json
> // 單平台:Android 專案 .lumos/config.json
> { "test_profile": "kotlin-junit" }
> ```
> **多平台(單一圖譜跨平台綁測試,見 [[Systems/test-profile-multiplatform]])**:圖譜記錄橫跨前後端的系統時,用 `platforms` 多根多 profile map,讓 `[test:平台:方法]` 綁到不同 repo 的測試。`default_platform` 給無前綴裸 ref 的歸屬(多平台缺省即報錯)。`load_platforms`/`resolve_test_refs` 以「config 有無 `platforms` 鍵」為 legacy 信號,舊 `test_profile`/裸 ref 照舊。`guard bind/scaffold --platform` 指定平台(`--method` 維持識別字、平台另帶,bind 寫 `[test:平台:方法]`)。Check T/`classify_invariants`/`cmd_archive` 各 ref 對其平台的 root+profile 判定(跨 repo)。
> ```json
> // 多平台:<圖譜所在 repo>/.lumos/config.json(平台名/profile/root 依專案自訂)
> { "default_platform": "app",
>   "platforms": {
>     "app":     {"profile": "kotlin-junit", "root": "."},          // 前端 App(同 repo)
>     "e2e":     {"profile": "maestro",      "root": "."},          // 同 repo 的 E2E flow
>     "backend": {"profile": "csharp-xunit", "root": "../<後端 repo>"}  // 後端 API(另一 repo)
>   } }
> ```
> 天花板:Check T 只驗測試識別子存在、不驗跑綠(CI 的事);E2E(maestro/playwright)要裝置/瀏覽器(無裝置才 skip);跨 repo 只讀不寫。**撰寫期用 Maestro MCP / Playwright MCP** 把 scaffold 的紅燈 stub 填到綠(開發工具、非合約守門)。
> - **自我供裝(缺就自動裝、別叫使用者手動)**:要用該 MCP 但工具清單裡沒有(deferred 也 ToolSearch 不到)→ 先 `claude mcp list` 確認,沒有就自動配置再用:
>   - Playwright(web):`claude mcp add playwright npx @playwright/mcp@latest`(前置 Node18+;首用 `npx playwright install` 裝瀏覽器)
>   - Maestro(mobile):先裝 CLI `curl -Ls "https://get.maestro.mobile.dev" | bash`,再 `claude mcp add maestro -- maestro mcp`
>   - 裝完**重啟 session** 或重跑 ToolSearch 讓 MCP 工具載入,再繼續填 stub。E2E 仍需模擬器/真機(mobile)或瀏覽器(web)才跑得起來。
>   - 供裝是這條 workflow 的預設動作;唯一該先問人的情況 = 該機器有明確不得自動裝軟體的政策。
> **stub 的紅燈哨兵放在 skip 之前**——未填的整合守衛在無 DB 的 PR CI 也會紅(不被 skip 掩蓋成假綠);填完斷言後刪哨兵行,skip 才恢復「無 DB 才 skip」。

### decisions 欄位（ADR：決策時間有效性 + 為什麼選/為什麼不選）

**有重大架構/技術決策的筆記必須有 `decisions` 陣列。** 追蹤「為什麼當初選 A 後來改 B」，讓過期決策不污染 Claude Code 的上下文，並讓「為什麼不選 B」的學習資產保留下來。

> 設計理由：純粹只記「選了什麼、被誰取代」會掉資訊——下次有人想再考慮被推翻的方案時，看不到「當初為什麼放棄、放棄理由現在是否還成立」。`context` / `alternatives_considered` / `why_chosen` / `trade_offs` 是業界 ADR 標準四欄位，**「為什麼選 / 為什麼不選」才是真正的決策智慧，「選了什麼」只是結果。**

```yaml
decisions:
  # 重大決策範例（ADR 完整版）
  - content: "點數保留鎖採用 MSSQL 樂觀鎖（rowversion + 重試）"
    context: "POS 尖峰 300-1200 RPS，需避免重複扣點；既有架構只有 SQL Server，沒 Redis 基礎設施"
    alternatives_considered:
      - "Redis 分散式鎖：低延遲但要新增基礎設施、增加故障容錯複雜度"
      - "資料庫悲觀鎖（SELECT ... FOR UPDATE）：簡單但長交易卡連線池"
      - "MSSQL 樂觀鎖（rowversion + 退避重試）：用既有 DB，無新依賴"
    why_chosen: "POS API 共用連線池場景下，避免長交易最關鍵；樂觀鎖在 1200 RPS 實測通過，無新依賴成本"
    trade_offs: "高衝突場景重試成本高（但本系統實測衝突率 <0.1%）；錯誤處理複雜度↑（要實作退避重試）"
    decided: 2026-03-10
    valid: true

  # 被推翻的決策（保留 ADR 欄位作為學習資產）
  - content: "用 Redis 做保留鎖"
    context: "初期評估時假設需要跨服務分散式鎖；當時只看 throughput 沒看基礎設施成本"
    alternatives_considered:
      - "DB 鎖：當時誤判會卡連線池"
    why_chosen: "（當時）Redis 是業界主流選擇，throughput 數字漂亮"
    trade_offs: "新增基礎設施、運維負擔、故障容錯複雜度"
    decided: 2026-02-20
    valid: false
    superseded_by: "改用 MSSQL 樂觀鎖（見上方）"
    ended: 2026-03-10

  # 小決策範例（不需 ADR 完整版）
  - content: "採用三階段流程（reserve→complete→void）"
    decided: 2026-02-15
    valid: true
```

**規則**：

| 欄位 | 重大決策 | 小決策 |
|------|---------|--------|
| `content` | ✅ 必填 | ✅ 必填 |
| `decided` (日期) | ✅ 必填 | ✅ 必填 |
| `valid` (true/false) | ✅ 必填 | ✅ 必填 |
| `context` | ✅ **必填** | ⭕ 選填 |
| `alternatives_considered` (陣列) | ✅ **必填**（至少 2 項） | ⭕ 選填 |
| `why_chosen` | ✅ **必填** | ⭕ 選填 |
| `trade_offs` | ✅ **必填** | ⭕ 選填 |
| `superseded_by` | 推翻時必填 | 推翻時必填 |
| `ended` (日期) | 推翻時必填 | 推翻時必填 |

**「重大決策」判定**（任一即是）：
- 架構選型（DB / 快取 / 訊息佇列 / 框架）
- 技術方案（鎖機制 / 認證方式 / 序列化格式）
- 流程變更（三階段流程 / 工作流順序 / API 契約版本）
- 安全/合規方案（加密方式 / 授權策略 / 個資處理）

**Claude 的填寫義務**（在更新圖譜時主動完善這些欄位）：

1. **建立新筆記寫第一筆決策時**：判定是否「重大決策」→ 是 → **主動 ASK USER** 取得 `context` / `alternatives_considered` / `why_chosen` / `trade_offs`，**不可省略只填 content+valid**
2. **讀到舊筆記只有 content+valid 但內容是重大決策**：標記為「ADR 不完整」，**主動詢問使用者**是否補上四欄位（不可自行編造，缺資訊就問）
3. **決策被推翻時**：
   - 舊決策**保留** ADR 四欄位（不刪），加 `valid: false` + `superseded_by` + `ended`
   - 新決策**重新填寫**完整 ADR 四欄位（不是繼承舊的）
   - 新決策的 `why_chosen` 必須提到「為什麼舊方案的 trade_off 不再可接受」
4. **`alternatives_considered` 至少 2 項**（含被選中的方案在內共 3 項才合理；只有 1 個選項不算決策）
5. **不可自行編造**：context/alternatives/why_chosen/trade_offs 若無法從對話/code/commit 推得，**問使用者**，不可生成似是而非的內容污染學習資產
6. Claude Code 讀到 `valid: false` 時，理解為**歷史脈絡 + 學習資產**而非現行規格——但下次有人想用同方案時要先檢查「當時放棄的 trade_offs 現在是否還成立」

**self-check 清單**（每次新增重大決策時用）：
- [ ] context 講清楚當時的約束（不是泛泛而談「為了效能」）
- [ ] alternatives 至少 2 項，每項都有「為何不選」理由
- [ ] why_chosen 明確對比 alternatives（不是孤立陳述「因為 X 好」）
- [ ] trade_offs 寫具體犧牲（不是「沒什麼缺點」這種廢話）

### verified_by 欄位（Verification 反向索引）

**所有 Systems 筆記應有 `verified_by` 陣列**，列出**驗證過此模組的 Verification 筆記 wikilink**。改 Systems 時直接看 frontmatter 就知道哪些驗證會受影響，不用每次跑 `backlinks` 反查 + 過濾雜訊。

```yaml
verified_by:
  - "[[Verification/2026-04-07_API審計修復]]"
  - "[[Verification/2026-05-04_點數圈存顯示]]"
  - "[[Verification/2026-05-08_runbook_auto_rollback_e2e]]"
```

**設計理由**：
- Obsidian 內建 `backlinks` 已能反查引用關係，但會混入所有引用者（Issues、Sessions、Projects），需手動過濾 `Verification/` path
- `verified_by` 是**結構化、過濾後的純驗證索引**：Claude `property:read` 一次取出，不需要 eval 過濾
- 改 Systems 時可直接 iterate `verified_by`，逐一檢查並標 `stale`，比 backlinks 後處理更直接

**Claude 的同步義務**（雙向同步，缺一不可）：

1. **建立新 Verification 紀錄時** → **同時**把該 Verification 的 wikilink 加進**所有相關 Systems** 的 `verified_by`（Verification 的「## 相關模組」列了幾個 Systems，就要更新幾個）
2. **廢棄/刪除 Verification 時** → **同時**把對應 wikilink 從相關 Systems 的 `verified_by` 移除
3. **改 Systems 筆記時的優先順序**：
   - 先讀 `verified_by`（一個 property:read 命令）
   - 再對每個 wikilink 比對 `valid_under` 與當前環境
   - 不匹配的標 `status: stale`
   - **不再需要先跑 backlinks 再過濾 Verification path**（除非懷疑 `verified_by` 不同步）
4. **發現 verified_by 與 backlinks 不一致** → 跑同步檢查 eval（見下方），把缺漏補上

**設定指令**：

```bash
# 加入新的 verified_by 條目 → lumos append(鐵則1 安全 YAML list 格式、自動去重)
lumos append Systems/OrderService verified_by "[[Verification/2026-05-04_點數圈存顯示]]"

# 讀取 → lumos context(節點 frontmatter 一覽)或直接看檔
lumos context Systems/OrderService --brief
```

> ⚠️ **絕不要用 obsidian `property:set` 塞逗號串接的多個 wikilink**（`value="[[A]], [[B]]" type="list"`）——實測存成**單一字串**而非 YAML list，圖譜長出亂碼 ghost 節點(2026-06-10 踩雷 14 篇)。`lumos append` 天生用安全 list 格式,沒有這個雷;真要走 obsidian 則用 `processFrontMatter` 陣列操作,別用 property:set。

**自動同步檢查** → `lumos doctor`（巡檢用,Check 3「verified_by 雙向同步」直接掃出漏寫的 Systems,不必再寫 eval）：

```bash
lumos doctor    # 含「所有 Verification 都已掛進對應 Systems 的 verified_by」檢查
```

> 注意：歷史筆記的 `verified_by` 可能殘留字串型值（非 list）;lumos 讀取已內建正規化,obsidian eval fallback 才需自己 `Array.isArray(raw) ? raw.map(String) : ...`。

### plan_refs 欄位（Verification → 計劃的意圖鏈）

**落地或迭代某個計劃節點的 Verification 應有 `plan_refs` 陣列（選填）**，反指它對應的計劃筆記。意圖鏈 = 計劃（動工前的共識）→ 實作 → Verification 回指；有了這條邊，「後續翻盤有沒有回頭對照計劃」就從個人習慣變成 graph-doctor Check 4 可機械檢查的事。

```yaml
plan_refs:
  - "[[服務台豁免作廢_計劃]]"
```

設計理由（2026-06-12 Sonnet 對抗審計收斂，原「plan 物種四件套」提案砍半）：
- **單向指針，不雙寫**：計劃側不設 `fulfilled_by` 鏡像欄位——那會跟 Systems 的 `verified_by` 形成雙軌雙寫，必 drift。要看某計劃落地了哪些驗證，反查 `plan_refs` 即得。
- **不建 plan 物種**：計劃沿用 `type: project` + 檔名 `_計劃` 後綴識別；`proposed/agreed/done/superseded` 四態對單人+AI 流程過重。部分翻盤（計劃 5 條決策翻 1 條）用既有 `decisions[].valid: false` 決策級粒度表達，不整篇標 superseded。
- **不做模板化盤問**：enforcement 只管「鏈的存在與一致」，不管「思考的品質」——形式 section 保證不了思考發生（開發者 2026-06-12 否決）。

**何時寫計劃節點**（opt-in，非義務；2026-06-12 審計收斂的客觀判準）：

1. **需求討論跨超過一個 session → 預設寫**（session 數客觀可判，「大改造」主觀不可判）
2. 動工前需要跨人 / 跨團隊共識（如服務台豁免案的後台分工）
3. 變更跨多個 Systems 節點（計劃沒有單一宿主可住）
4. **任何工具產出「設計 / spec」→ 一律寫計劃節點**（brainstorming、writing-plans、OpenSpec、其他 SDD / spec-driven 框架皆同；既然有正式設計產出，它就該住圖譜，不是散在 repo 檔）

其餘變更**不寫計劃**：節點 `decisions[]` 一條 + Verification 即可——一條 decision 就是微型計劃（superseded 條目自帶意圖凍結語意）。常態工作流維持「對話敲定 → 依當下脈絡開發 → 事後沉澱」，計劃節點是大型變更的 opt-in，不是進場義務。

> **⚠ 橋接任何 spec/SDD 工具的預設輸出路徑（必讀）**：各家工具都有自己的 spec 落點——`superpowers:brainstorming` → `docs/superpowers/specs/YYYY-MM-DD-*.md`、`writing-plans` 有自己的落點、`OpenSpec` → `openspec/`、其他 SDD / spec-driven 框架亦各有目錄——**在本紀律下一律覆寫成 lumos 計劃節點**（`Projects/<主題>_計劃.md`，`type: project`），**不另存 `docs/superpowers/specs/`、`openspec/` 或任何 repo 路徑**。理由:「圖譜即唯一真相」涵蓋計劃/設計,不只 code;spec 散在 repo 檔 = 圖譜外的第二真相源,必 drift。多數此類工具也明示「user/專案偏好可覆寫預設 spec 路徑」,本紀律即該覆寫。落地的 Verification 用 `plan_refs` 回指該計劃節點。

**條款級追溯（唯讀說明）**：既有筆記可能看到計劃的規格 bullet 標 `[S1]`/`[S2]`…、落地的 Verification（有 plan_refs 回指）在 body 提及對應 `[SN]`——這是「哪篇 Verification 認領了計劃哪一條」的人工可讀慣例。★本精簡版不含 `spec-trace` 自動核對指令★，看到這類標記照原意讀即可，不必自己去對帳。一篇 Verification 盡量只回指一個計劃（條款 ID 無計劃域，多計劃回指會交叉記帳）。

**Claude 的維護義務**：

1. **寫 Verification 時，工作對應某個計劃節點** → 填 `plan_refs`。**含迭代/翻盤該計劃範圍的後續驗證，不只首輪落地**（意圖鏈斷裂的高發點正是第二輪之後）。
2. **動 Systems 筆記前** → 順手確認 Projects/ 是否有 `status: doing` 的計劃引用該 system（`grep -l "目標System" docs/{vault}/Projects/*_計劃*.md` 即可），有 → 本次 Verification 填 `plan_refs`。
3. **翻盤計劃中某條決策** → 改計劃本體（bump `updated` + 決策註記或 `decisions[].valid: false`），不是只改 Systems。graph-doctor Check 4 靠「計劃 `updated` 早於回指 Verification 的檔名日期」偵測漏做。
4. **計劃改名/歸檔** → `plan_refs` 是 frontmatter 字串，Obsidian 不會自動改寫（body wikilink 才會）→ 主動修各 Verification 的 `plan_refs`，graph-doctor Check 4 會抓斷鏈兜底。

### 讀取 decisions 的方式

decisions 是巢狀物件,**用 lumos 讀**（格式化輸出 valid/superseded,免自己寫 eval 拆 `[object Object]`）：

```bash
# 讀取單篇筆記的決策(格式化:✅/❌ + 日期 + content + superseded_by)
lumos decisions Systems/OrderService

# 全 vault 掃所有被推翻的決策
lumos decisions --superseded

# 看 summary / 整篇 frontmatter
lumos context Systems/OrderService --brief
```

> fallback(無 lumos 的舊專案):obsidian `eval` 讀 `getFileCache(f).frontmatter.decisions` 自己 map,或 `property:read name="summary"`。

### 更新圖譜時的 summary / decisions / verification 維護規則

1. **新增功能/模組** → 建立筆記時同時寫 summary
2. **修改功能** → 更新 summary 中受影響的行（FLOW/KEY/TEST 等）
3. **新增重大決策** → 主動填齊 ADR 四欄位（`context` / `alternatives_considered` / `why_chosen` / `trade_offs`），缺資訊就問使用者不要編造
4. **決策被推翻** → 舊決策保留 ADR 欄位（學習資產）+ 加 `valid: false` + `superseded_by` + `ended`；新決策重新填完整 ADR
5. **測試完成** → 更新 `TEST:` 和 `VERIFY:` 行，同時建立 Verification 紀錄並填 `valid_under` / `revalidate_when`
6. **新增 Verification** → **必須同步**把該 Verification 的 wikilink 加進相關 Systems 的 `verified_by`（雙向同步）
7. **環境/依賴變更** → 主動掃 Verification 看誰的 `valid_under` 命中變更條件 → 標記 `status: stale` 並提示使用者重跑
8. **Systems 筆記改 DEP/KEY 行** → 優先讀 `verified_by` 取出相關 Verification 清單 → 逐一比對 `valid_under` → 命中的標 `stale`（不再先跑 backlinks）
9. **廢棄 Verification** → 從相關 Systems 的 `verified_by` 移除對應 wikilink
10. **Verification 對應某計劃節點（含後續迭代/翻盤）** → 填 `plan_refs` 反指計劃（見 plan_refs 欄位章節）
11. **翻盤計劃決策** → 改計劃本體（bump `updated` + 決策註記），不是只改 Systems

設定 tags 範例：
```bash
obsidian vault="{vault}" property:set path="Projects/xxx.md" name="tags" value="status/doing, type/project" type="list"
```

## Obsidian（僅 GUI 檢視;指令參考已刪）

日常讀寫巡檢**全用 lumos**(見上方速查表)。Obsidian 只當**檢視器**,且只在這幾件 lumos 做不到時用(做法查 `obsidian --help`,不列指令):
- 在 App 開圖譜關係圖 / 開筆記或搜尋視圖給人看
- **權威解析驗證**(「這篇 Obsidian 到底讀不讀得到」最終判定) · **File Recovery** 版本比較 · 白名單外 frontmatter 的 `processFrontMatter` 寫入
> vault 有 `.obsidian/` = 會被 App 開 → frontmatter 四鐵則(頭版)因此是活的。若已純 headless 不開 Obsidian,連本節都可刪。

## 實戰範例（lumos 為主；body 編輯走 Edit）

> 分工提醒:**讀取 / 巡檢 / frontmatter 寫入 → lumos**;**body 內容(進度段落、checkbox、表格)→ Edit**(lumos T1 只管 frontmatter);**版本歷史 → git**(圖譜同 repo 版控)。

### 開工前：掌握現況
```bash
# 掃進行中 / 被阻擋的工作(搜 tag)
lumos search "status/doing"
lumos search "status/blocked"

# 看最近的交接 / 異動
lumos recent --days 7

# 快速了解某模組現況(節點+鄰居 closet 索引,頭部突顯 ⚠ 合約 — 比 read+outline 強)
lumos context Systems/Billing
```

### 改完程式碼後：更新圖譜
```bash
# 更新 updated 日期(frontmatter 純量 → lumos)
lumos set Systems/Billing updated 2026-03-27

# 追加一條 verified_by(frontmatter list → lumos,自動 dedup)
lumos append Systems/Billing verified_by "[[Verification/2026-03-27_xxx]]"
```
> body 的進度段落、打勾待辦、串接狀態表格 → 用 **Edit** 精準改(這類 body 編輯不是 lumos T1 範圍;真要叫 GUI 給人看才用 obsidian)。

### 查關聯：更新一份筆記後檢查連帶影響
```bash
# 誰引用了這份(反向連結) / 這份連出去的(正向連結)
lumos backlinks Issues/會員升等降級機制
lumos links Issues/會員升等降級機制

# 搜相關關鍵字,確認其他筆記是否也要更新
lumos search "贈獎"
```

### 追溯變更
```bash
# 圖譜同 repo 版控 → 直接用 git 看歷史 / diff
git log --oneline -- docs/myapp-knowledge/Systems/Billing.md
git diff -- docs/myapp-knowledge/Systems/Billing.md
```
> commit 前的本機版本(還沒進 git)→ obsidian File Recovery(obsidian-only,見上節)。

### 健康巡檢
```bash
# 一次到位:orphans / 破連結 / verified_by 同步 / plan_refs 意圖鏈 / 同名守衛 / 鐵則 lint / 合約測試綁定
lumos doctor

# 資料夾統計 / 最近異動
lumos stats
lumos recent --days 7
```
> lumos doctor 涵蓋了舊 obsidian `orphans`/`unresolved` 等;deadends 等 obsidian-only 巡檢才回頭用 obsidian(見上節)。

## 同步規則（何時更新知識圖譜）

### 程式碼變更後（必做）
更新對應 Systems 筆記：
- 串接狀態（mock → 已串接）
- 新增/修改的檔案、API 端點
- DB 表結構變更
- 待辦完成打勾（`obsidian task ... done`）

### 更新筆記後（必做）
`lumos backlinks <剛改的節點>` 看誰引用它 → `lumos search <相關關鍵字>` 逐一確認是否過時。

### 圖譜更新後：Sonnet agent 自足性審計（必做）

**原理**：圖譜的存在目的是讓「沒有主對話脈絡的下一個 session」能單靠圖譜還原現況。所以驗收方式就是模擬這件事——派一個**乾淨的 Sonnet agent**（沒有主對話上下文）只讀圖譜還原脈絡，主對話比對它的還原結果與自己腦中的現存脈絡：**有出入 = 圖譜當下不健全，需補足缺漏後重審**。

**時機**：每次對圖譜的**實質內容更新**完成後（新增/修改 Systems、Issues、Verification、decisions、summary）。純格式修正（typo、缺欄位補登、連結修復）可豁免，但修完建議至少跑一次健康巡檢。

**做法**：用 Agent tool 派出 subagent，`model: sonnet`，prompt 模板：

```
你是知識圖譜審計員。只允許讀 docs/{vault-name}/ 下的筆記（唯讀；優先用 obsidian CLI，
帶 leading vault="{vault-name}"，查詢指令見 search/backlinks/property:read/eval），
禁止讀程式碼、git log、其他文件——模擬「只有圖譜」的新 session。

請基於圖譜還原以下脈絡，據實回答，圖譜裡找不到的就明說「圖譜未記載」不要腦補：
1. {本次更新涉及的模組} 的現況：核心流程、關鍵欄位、現行有效的決策
2. 最近一次對 {模組} 的變更做了什麼、為什麼做、驗證狀態如何
3. 有哪些進行中(doing)/被阻擋(blocked)的工作與未決問題
4. 哪些決策已被推翻、被什麼取代

輸出：條列還原結果 + 末尾列出你覺得圖譜記載模糊或互相矛盾的地方。
```

**判定與處置**（主對話執行）：

| Agent 還原結果 vs 主對話脈絡 | 判定 | 處置 |
|---|---|---|
| 一致，無模糊點 | ✅ 圖譜自足 | 記錄審計 PASS（commit message 或 Verification 註記）|
| 缺漏（主對話知道但 agent 還原不出來）| ❌ 圖譜不健全 | 把缺的脈絡補進對應筆記（summary/decisions/內文）→ **重派 agent 直到一致** |
| 誤讀（agent 還原出與現實相反的結論）| ❌ 圖譜誤導 | 通常是過時決策沒標 superseded、summary 沒更新、或 frontmatter 解析失敗讓 property 隱性消失 → 修正後重審 |
| agent 自己回報「模糊/矛盾」| ⚠️ 視同缺漏 | 逐條釐清補寫 |

**注意**：
- 審計 agent 與主對話相同，優先用 obsidian CLI 查詢（圖譜感知能力：backlinks/property:read/eval）；CLI 不可用時才降級 Read/Grep（唯讀豁免）
- 主對話**不可把自己的脈絡餵給 agent**（污染測試），prompt 只給「審哪些模組」的範圍
- 比對時注意 agent 還原不出來的東西，到底是「圖譜缺漏」還是「本來就不該進圖譜」（如一次性對話細節）——後者不用補

**留痕**：審過且補到一致後，建議在節點 body 或 commit message 註記審過的日期/模型。★本精簡版無 `lumos self-audit` 指令可蓋 frontmatter 戳記★——`doctor` 仍可能軟提醒某節點「從未跑 L4」，那是無害的雜訊，`doctor --ci` 仍 exit 0，可忽略。
- `[H]` 漏標可逆性提醒（`doctor --ci` 才跑）:掃 diff 碰 prod/外部 API/寄送 → 軟提醒「是否漏標 ★IRREVERSIBLE★」。只提醒、不擋。

### 變體 B：圖譜×程式碼交叉審計（無主對話脈絡時用，以 code 為真值）

標準自足性審計需要「主對話脈絡」當比對基準。**沒有脈絡時**（定期巡檢、接手陌生專案、審很久沒動的大節點），改用程式碼當真值，兩階段、每節點各派一個乾淨 Sonnet agent：

**階段一（還原）**：agent **只讀單篇 Systems 筆記**（禁讀 code/其他筆記/git log），萃取 12~15 條「可被程式碼驗證的具體主張」：
- 挑載重最高的：流程順序、方法/類別名、欄位語意、invariant、邊界規則
- 必須可證偽（「設計良好」這種不算）；筆記有提檔案/方法名就照抄
- 只取 `valid: true`（或 partial 的「仍有效」部分）的決策，被推翻的不要
- 輸出：`C1. [主張] | 預期驗證點: [檔案/方法]`

**階段二（實證）**：另一個 agent **只讀程式碼（嚴格禁讀 docs/——那是被審計對象）**，逐條判定：
- ✅ 一致（附 file:line 證據）／❌ 不一致（說明 code 實際）／❓ 找不到（說明搜過哪裡）
- 多節點時兩階段都可並行（一節點一 agent）

**判定與處置**（主對話執行）：❌ = 圖譜腐爛 → 修筆記（過時決策標 superseded、錯誤描述更正並註明「YYYY-MM-DD 程式碼實證」）→ 建 Verification 紀錄審計結果 → 相關 Systems 的 `verified_by` 雙向同步。**修正一律以 code 為準**——除非 code 本身是 bug（那就開 Issue，不改筆記遷就）。

**實戰教訓（2026-06-10 四大節點首跑，60 主張 85% 一致）**：
1. 最高頻腐爛型態 = 「**決策在別篇筆記被推翻、本篇沒跟上**」——hooks 抓不到（改 code 時只同步了主筆記），交叉審計是目前唯一掃得出它的機制
2. **計數/清單型主張最會漂**（「共 5 處」「6 個檔案」「1 筆」）——寫筆記時這類數字要附截至日期或乾脆不寫死
3. 有筆記**引用了 codebase 不存在的方法名**（從未實證過就寫進去）——升格任何主張前先 grep 一次
4. 同篇筆記可能 KEY 行已更新、decisions 卻沒標 superseded——**自相矛盾**型,審計時兩處都要看

### 重生守衛(Check J):from-scratch 重建節點的 provenance 分級(2026-07-16)

**問題**:重建(目擊記錄佚失/接手 legacy/整篇重寫)=從 code 快照逆向工程 why——AI 沒有目擊記憶,會編出自信但腦補的「當初為什麼」;最毒是發明假合約(把偶然寫法標成 ★INVARIANT★ 鎖死重構)。統一原則:**讓重建優雅退化成「誠實的、分級的不確定」,把缺口變可見+有型別,不編自信 prose**。(設計全文與當初的三輪對抗審紀錄留在完整版工具鏈,★本精簡版沒有交付那些檔案★——這裡列的規則本身就是全部,不必去找。)

**完整工作流**:
1. 重建前:舊節點還在就 **diff 更新別整篇換**(保住殘存目擊內容);真要從零才走本流程。
2. 重建完蓋章:`lumos set <節點> regen from-scratch/<日期>`(`regen` 在 SCALAR_KEYS 白名單)。
3. summary 每條 claim 標身分(**只掃 summary 行**,body 內標記是人讀輔助、機器不執法):
   - `[src:路徑]` / `[src:路徑:行號]` — Tier A,現 code 可驗(行內 bracket 指針,同 [test:] 族)
   - `[git:sha]` — Tier B,變更事件作證(commit/revert/PR;7-40 位 hex)
   - `推測:` — Tier C 前綴,**緊接在 KEY:/DECISION: 後**(`KEY:推測: ...`);沒證據的推論顯式標
   - `佚失:` — 前綴同上;證據已不存在,老實留空不編
4. `lumos lint <節點>` 立驗;doctor 全圖同規(共用 check_regen_provenance,兩入口不漂移)。

**Check J 四檢**(只對 regen 節點):
- **J-a(擋)**:★INVARIANT★ 行無 [src:]/[git:] → 擋。[test:] 只證「行為現在成立」,不證「意圖是合約」——重建場景把偶然合約化是頭號毒;regen 節點的合約=[test:] **且** [src:]/[git:] 疊加。
- **J-b(擋)**:DECISION 行無證據指針且未標 推測:/佚失: → 擋(重建的 why 必須標來源或標推測)。
- **J-c(擋,substring gate)**:[src:] 真開檔驗存在+行號範圍;[git:] 真跑 cat-file 驗 commit;假路徑/空白/絕對路徑/`..` traversal/假 sha 全擋(防幻覺證據)。shallow clone 驗不到 git 物件→降警告不擋+顯性標示(僅 doctor --ci 落治理帳)。
- **J-d(提醒不擋)**:無標記 KEY 行計數提醒(prose 級誠實機械驗不了)。
- **不對稱接線**:`推測:`/`佚失:` 行不得承載 ★INVARIANT★/★IRREVERSIBLE★(合約不能建在推測上)→ 擋,恰一則專屬訊息。

**升級路徑**:推測→查證後補 [src:]/[git:];或業務面人工確認（本精簡版無 `signoff` 留痕指令，人工記錄即可）。**天花板**:J-c 只驗「指針可解析」不驗「內容真支持 claim」(語意層靠對抗審/人);佚失的 why 永久佚失,正確輸出是「佚失:」——嚴禁編一個合理的(把「不知道」渲染成「知道」正是 code 衍生 wiki 的原罪,見 `Systems/外部對照-code衍生wiki`)。

### 發現 Issue 時
`lumos new issue <名稱>` 建檔 → `lumos set` 填 status/type/priority → body 用 Edit 寫現象/相關系統/解法/狀態。

### 里程碑完成時
`lumos set <計劃> status done` + `lumos set <計劃> updated <日期>`;相關 Issue 一併 `lumos set ... status done`。

### 測試前：查既有驗證紀錄（必做）

要測試某個功能前，**優先順序**：

1. **先讀對應 Systems 筆記的 `verified_by`**（最快，O(1) frontmatter 讀取）：
   ```bash
   obsidian vault="{vault}" property:read path="Systems/相關系統.md" name="verified_by"
   ```
2. **若 Systems 無 `verified_by` 或不確定完整性，再 fallback search**：
   ```bash
   obsidian vault="{vault}" search query="功能關鍵字" path="Verification"
   ```
3. **同步檢查**：跑「verified_by 自動同步檢查 eval」確認 Systems 的 verified_by 是否完整（見上方）

判斷準則：
- **有，`status: pass` 且 `valid_under` 條件仍成立** → 照著紀錄的測試項目跑，更新 `date` / `commit`
- **有，`status: stale` 或 `valid_under` 條件已變** → **必須重跑全部測試**，跑完後改回 `pass` + 更新 `valid_under`
- **有，`valid_until` 已過期** → 同上，必須重跑
- **沒有** → 寫新測試，跑完後建立驗證紀錄並更新對應 Systems 的 `verified_by`

**Claude 必做的有效性檢查**（讀到 Verification 時自動跑）：
1. 比對 `valid_under` 每一條跟當前環境（commit hash / DB schema 版本 / 依賴版本 / 預估 RPS）
2. 任一條不匹配 → **主動提示使用者**「此驗證的 `valid_under` 條件已變（具體哪條），建議改 status: stale 並重跑」
3. 不可以「假裝沒看到」直接拿舊驗證當保證

### 功能完成後：寫驗證紀錄（必做）

每完成一個功能並測試通過後，在 `Verification/` 建立驗證紀錄。**`valid_under` 與 `revalidate_when` 是必填欄位**（讓未來的人/AI 知道這份驗證在什麼條件下還算數）：

```bash
obsidian vault="{vault}" create path="Verification/{日期}_{功能名稱}" content="---\ntype: verification\nstatus: pass\nfeature: {功能描述}\ncommit: {commit hash}\ndate: {日期}\nvalid_under:\n  - \"DB schema v1.0.20（Member 表結構未變）\"\n  - \"並發 ≤ 1000 RPS\"\n  - \"三竹 SMS API v2\"\n  - \"Android 14 + 三星 One UI 6.0（若涉及行動端）\"\nrevalidate_when:\n  - \"Member 表結構變更（加欄位/改型別）\"\n  - \"RPS 超過 1200（30 櫃位尖峰再 2x）\"\n  - \"三竹 API 改版\"\n  - \"Android 16 GA\"\ntags:\n  - type/verification\n  - status/pass\n---\n# 驗證：{功能名稱}\n\n## 變更範圍\n- ...\n\n## 測試項目\n\n### 1. {測試場景}\n| 步驟 | 預期 | 結果 |\n|------|------|------|\n| ... | ... | ✅/❌ |\n\n## 測試方式\n{如何測試：API 呼叫、瀏覽器、腳本等}\n\n## 相關模組\n- [[Systems/xxx]]"
```

**命名規則**：`{日期}_{功能簡稱}`，如 `2026-04-01_點數圈存顯示`

**Frontmatter 欄位**：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `type` | ✅ | 固定 `verification` |
| `status` | ✅ | `pass` / `fail` / `stale`（見下方規則） |
| `feature` | ✅ | 功能簡述 |
| `commit` | ✅ | 驗證當時的 commit hash |
| `date` | ✅ | 驗證日期 |
| `valid_under` | ✅ **必填** | 列出驗證**有效的環境條件**（list）—— 平台版本、規模、依賴版本、DB schema、外部 API 版本 |
| `revalidate_when` | ✅ **必填** | 列出**需要重驗的觸發條件**（list）—— 人類可讀，AI/人遇到該條件時應提示重跑 |
| `valid_until` | ⭕ 選填 | 只有絕對失效日才填（廠商合約到期、SDK EOL）；無就留空靠 `revalidate_when` 觸發 |

**status 規則**：
- `pass`：全部測試通過 + `valid_under` 條件仍成立
- `fail`：有失敗項目（需記錄失敗原因和後續處理）
- `stale`：曾經 pass，但 `valid_under` 條件已變或 `valid_until` 已過 → **下次有人依賴此功能前必須重跑驗證**，等同警告：「別把這份結論當現行依據」

**紀錄內容**：
- 變更範圍（改了哪些檔案/API）
- 測試項目表格（步驟 → 預期 → 實際結果）
- 測試方式（Python 腳本、curl、瀏覽器、DB 查詢等）
- 關聯模組（wikilink）

**Claude 主動填寫義務**：
- 對應計劃若有 `[SN]` 條款標記、本次 Verification 認領了某條 → body 內文字提及該 `[SN]`（純可讀慣例，本精簡版無自動核對工具）
- 重大業務規則（金流/對外合約）落地或翻盤後 → 提醒使用者留下 validation 簽核痕（技術驗證 ≠ 業務確認；本精簡版無 `signoff` 指令，人工記錄於 body 或 commit message 即可）
- 寫 `valid_under` 不可只填「現在好用」這種廢話；要具體版本/規模/schema 數字
- `revalidate_when` 從 `valid_under` 反推：每條 `valid_under` 對應一條「當條件 X 改變時」的 `revalidate_when`
- 若使用者沒提供具體環境條件（版本/RPS/schema 版本）→ **主動詢問**，不可自行假設
- **建立 Verification 後同步更新 Systems**：Verification 的「## 相關模組」列了幾個 Systems wikilink，就要更新幾個 Systems 的 `verified_by` 欄位（追加，不是覆蓋），雙向同步缺一不可

> 進場提示(2026-06-29 起):`lumos context` 讀節點時會在最上方自動顯示 `valid_under` 條件(>90 天未更新加紅標),並由 `lumos doctor` Check V 量全圖過期率——失效條件從「寫入時標記」變「進場主動提示」,不需 AI 自己去 `lumos stale` 查。

### Verification 健康檢查（巡檢時必做）

開工前、commit 圖譜更新前、重大環境變動後，用 lumos 掃 Verification：

```bash
# status: stale 的驗證(需重跑)
lumos stale

# 環境變動後:掃 valid_under / revalidate_when 命中某條件的驗證(改了 .NET 8 → 比對哪些要重驗)
lumos stale --match ".NET 8"

# Systems 改動後查 verified_by + 反向連結
lumos context Systems/{剛改的系統} --brief
lumos backlinks Systems/{剛改的系統}

# verified_by 雙向同步漏寫 → doctor Check 3 一次掃全 vault
lumos doctor
```

> `valid_until` 過期掃描 lumos 暫無對應(valid_until 用得少;多數用 valid_under 條件式),需要時走 obsidian eval fallback。

**掃出 stale / 過期 → Claude 必做**：
1. 列給使用者看：哪些 Verification 過期 / stale
2. 詢問：「這些要現在重跑、還是先標起來之後處理？」
3. 重跑通過後：更新 `date` / `commit` / `valid_under` / status 改 `pass`
4. 暫不處理：至少確保 status 已是 `stale`，不要保留 `pass` 假象

## MOC（Maps of Content）維護

MOC 是索引筆記，彙整某個主題下的所有相關筆記。
當某個領域的筆記超過 5 份時，建立或更新 MOC。

## 注意事項

1. **create 不帶 .md**：`name=` / `path=` 參數不帶副檔名，CLI 自動加 `.md`
2. **其他命令帶 .md**：`property:set`、`read`、`append`、`backlinks` 等用完整路徑含 `.md`
3. **file= vs path=**：`file=` 用 wikilink 解析（不需完整路徑），`path=` 要完整路徑
4. **內容換行**：用 `\n` 表示換行，`\t` 表示 tab。**Mermaid 區塊內換行用 `<br/>` 不是 `\n`**
5. **Wikilink**：筆記間互連用 `[[筆記名]]` 或 `[[資料夾/筆記名]]`
6. **不要覆寫**：優先用 `append` / Edit，除非明確要重建
7. **更新 updated**：每次修改筆記後，更新 `updated` property
8. **中文檔名**：可直接使用
9. **隨 git 版控**：所有變更被 git 追蹤，commit 時一起提交
10. **衝突處理**：知識圖譜 vs Memory vs Session 有出入時，向使用者確認
11. **vault 動態取得**：不要硬寫 vault 名稱，每次用 `obsidian vaults` 確認
12. **複製輸出**：任何命令加 `--copy` 可複製結果到剪貼簿
13. **Obsidian 必須執行中**：CLI 需要連接正在運行的 Obsidian App
14. **Verification 豁免**：Verification 筆記不需要 `summary` 和 `updated` 欄位（有 `feature` + `date` 已足夠），**但 `valid_under` + `revalidate_when` 是必填**
15. **避免假 Tag**：內文中的 `#` 會被 Obsidian 解析為 tag，顏色值用 backtick 包裹（如 `` `#FFF3E0` ``），編號用 `1~3` 不要用 `#1-3`
16. **ADR 不可編造**：`decisions` 的 `context` / `alternatives_considered` / `why_chosen` / `trade_offs` 若無法從對話/code/commit 推得，**問使用者**，不可生成似是而非的內容污染學習資產
17. **Verification 巡檢時機**：開工前、commit 圖譜更新前、重大環境/依賴/schema 變更後，跑健康檢查 eval 指令掃 `status: stale` 和過期 `valid_until`
18. **verified_by 雙向同步**：新增/廢棄 Verification 時，**必須同步**更新對應 Systems 的 `verified_by`；改 Systems 時優先讀 `verified_by` 而非跑 backlinks（backlinks 含 Issues/Sessions 雜訊）
