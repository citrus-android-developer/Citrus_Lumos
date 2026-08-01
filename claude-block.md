<!-- LUMOS-SLIM:START -->
## Lumos 圖譜標籤速查(精簡版接手教學;2026-07-31 由 lumos-slim 安裝器維護——取代完整版紀律區塊,策展吸收其中仍有效的內容)

> 本區塊由 `lumos-slim` 的 `install.sh` 自動維護(冪等重跑只更新這一塊,不疊出第二塊;`uninstall.sh` 可乾淨移除,若這個專案原本有完整版紀律區塊,卸載後會位元組級還原回原本內容——備份就編碼藏在本區塊自己的 HTML 註解裡,不額外新增檔案)。若原本有完整版紀律區塊,它那套進階治理機制本包沒有交付,以下只留讀既有圖譜用得到的部分。

### 核心原則:知識圖譜是唯一真相來源

`docs/{project}-knowledge/` 知識圖譜是本專案系統脈絡的唯一真相來源。程式碼只是「現在長這樣」;圖譜才是「為什麼這樣設計 / 邊界在哪 / 哪些是不可改的合約(★INVARIANT★)/ 驗證過沒」——這些 code 讀不出來。圖譜與行為事實(測試結果 / 實際執行 / 生產觀測)衝突時,不自動判圖譜為真——那是有東西壞了,查清哪邊錯。

**動任何既有系統之前,第一個工具呼叫必須是 `lumos`,不是 grep / Read / DB 查詢。** 入口三步:

```
lumos search <關鍵字>      # 定位
lumos context <節點>       # 掃脈絡(頭部攤合約)
lumos contracts <節點>     # 查硬合約
```

三步做完,再去 grep 程式碼或查資料庫印證。這是精簡版,只保留讀取/導航、寫入、健康巡檢(`doctor`/`lint`)、合約守衛(`guard`)這 24 支指令;`doctor` 若建議跑本版沒交付的指令修復,代表那項檢查在本版沒有對應的機械修復路徑,看到請忽略(判準是「跑了會得到未知指令錯誤」,不是背一份清單)。

### A. summary 欄位符號(Systems/Issues 筆記的結構化摘要)

| 符號 | 用途 |
|------|------|
| `FLOW:` | 核心流程 |
| `KEY:` | 關鍵概念/欄位 |
| `DEP:` | 依賴模組(wikilink) |
| `TEST:` | 測試狀態 |
| `VERIFY:` | 驗證紀錄連結 |
| `DECISION:` | 重大決策,帶 `(valid)`/`(superseded)` |
| `FLAG:` | 語意標記(TECHNICAL/DECISION/ORIGIN) |
| `AUTH:` | 認證方式 |

分隔符:`→` 流程方向、`｜` 分隔同類、`,` 分隔同欄細項。看哪幾行:Systems 看 `FLOW`+`KEY`+`DEP`+`TEST`;Issues 看 `FLAG`+`DECISION`+`KEY`;Verification 看 `TEST`+`VERIFY`。

### B. 合約鏈(`KEY:` 行前綴,最要命,別搞混)

- `★INVARIANT★` — 業務合約,**改動＝breaking**,動前先看它綁的 `[test:]`
- `★DEBT★` — 已知偶然行為,**可以改、不算 breaking**
- `★IRREVERSIBLE★`/`★CHECKPOINT★`(僅 Systems 節點會出現)— 不可逆,動前找 `[rollback:]`

把兩者搞混的兩種後果:把 `★DEBT★` 當合約 → 不敢動該動的;把 `★INVARIANT★` 當普通說明 → 動了就壞。行尾括號指針:`[test:]` 綁定測試、`[audit:]` 獨立審計、`[rollback:]` 回滾路徑。

### C. 重生標記(regen,重建/legacy 接手節點才有)

節點若標了 `regen: from-scratch/<日期>`,代表這篇是從 code 快照逆向重建的,`KEY:`/`DECISION:` 行可能帶這些前綴:

- `[src:]`/`[git:]` — 證據指針(檔案位置/commit),`★INVARIANT★` 行沒有這個不算合約,只是描述
- `推測:` — 沒證據的推論,顯式標出來,不當定論
- `佚失:` — 證據已不存在,**老實留空不編**——佚失的 why 就寫「佚失:」,嚴禁腦補一個聽起來合理的原因

### D. frontmatter 欄位

- `type:`/`status:` — 節點種類(system/issue/verification/project)與活躍度(如 doing/pass/stale)
- `valid_under:`/`revalidate_when:` — 這條結論在什麼前提下成立、什麼條件變了要重驗
- `plan_refs:`/`verified_by:` — 追回「為什麼這樣設計」與「哪次驗證證實」
- `related:`/`tags:` — 關聯節點與分類標籤
- `decisions:` — ADR,含被取代的舊決策

多個 wikilink 必須寫成 YAML list、一項一行(寫成單一字串會長出讀不到的 ghost 節點)。純量/list/decisions 一律走 `lumos set`/`append`/`decision-add`,別手改 frontmatter。
<!-- LUMOS-SLIM:FULL-BACKUP:NONE -->
<!-- LUMOS-SLIM:END -->
