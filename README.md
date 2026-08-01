# Lumos 公開精簡版

這是知識圖譜工具 lumos 的**離職交接精簡版**——目的只有一個：讓接手的人能讀懂既有專案留下的知識圖譜（`docs/{project}-knowledge/`）。可讀是目標，可維護是加分，本包不設任何機械強制（不擋 commit、不擋 push、不裝任何 hook）。

## 支援平台

支援 **macOS／Linux／Windows** 三個平台。安裝／卸載的全部邏輯只有一份，寫在 `install.py`／`uninstall.py`（Python 3 標準庫，零依賴）——`.sh`（macOS/Linux）與 `.ps1`（Windows）都只是**薄殼**，負責定位套件位置、挑一支可用的 `python3`/`python` 直譯器，然後把參數原樣轉發過去。這樣設計是為了避免同一套邏輯維護兩份、隨時間漂移出兩套不一致的行為。

各平台的一行安裝指令：

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.sh | bash
```

```powershell
# Windows(PowerShell)
irm https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.ps1 | iex
```

裝完後 `lumos` 指令會落在 `~/.local/bin`（Windows 是 `%USERPROFILE%\.local\bin`）——這個路徑通常**不在預設 PATH 裡**，需要自己加：macOS/Linux 在 shell 設定檔（`~/.zshrc`／`~/.bashrc`）加一行 `export PATH="$HOME/.local/bin:$PATH"`；Windows 把 `%USERPROFILE%\.local\bin` 加進「系統環境變數」的使用者 PATH（安裝器結尾若偵測到不在 PATH 裡,會依平台印出對應提示）。

★**誠實標記,別誤讀成「Windows 已驗證」**★：這台開發機是 macOS,沒有 Windows/PowerShell 環境可用,**Windows 路徑沒有在真機上跑過**。`install.py`/`uninstall.py` 的邏輯與 Unix 共用同一份 Python 原始碼,Windows 分支（`.cmd` shim 產生、PATH 提示文字）靠 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 環境變數在非 Windows 機器上注入、只驗證過**分支邏輯本身跑對路**（見 `scripts/test_lumos.py` 的 `t_slim_install_windows_*`/`t_slim_uninstall_windows_*` 系列）——`.cmd` shim 在真實 `cmd.exe`/PowerShell 下能不能被正確找到並執行、`install.ps1`/`uninstall.ps1`/`get.ps1` 這三支 `.ps1` 薄殼本身、PATH 環境變數在 Windows 上的實際生效方式,都**沒有機會做真機驗證**。若你在 Windows 上使用本包遇到問題,請直接檢查 `install.py`/`uninstall.py`（跨平台邏輯都在這兩支,可讀可改)。

★**2026-08 Task 14 新增兩項未驗清單(同款誠實聲明,不要誤讀成已解決)**★:
- **`.cmd` shim 直譯器 fallback**——shim 呼叫用的直譯器名稱(`python3`/`python`)改成安裝當下用 `shutil.which()` 偵測、寫進 shim(見 `install.py` 的 `_pick_windows_interpreter()`),不再寫死字面 `python`。用意是修「Windows 機器只有 `python3.exe`、沒有 `python.exe` 時裝完即壞」這個問題,邏輯層級已用 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 驗過(`t_slim_install_windows_shim_does_not_hardcode_python_when_only_python3_available`),但 `shutil.which()` 在真實 Windows `cmd.exe`/PowerShell 環境下解析 PATH 的實際行為(含副檔名 `.exe` 解析、`PATHEXT` 等)沒有真機驗證過。
- **`.ps1` 全程不再呼叫 `exit`**——`install.ps1`/`uninstall.ps1`/`get.ps1` 三支原本收尾是裸的 `exit $LASTEXITCODE`,理由是 `exit` 在 `irm ... | iex`/`& "路徑\install.ps1"` 這種呼叫鏈裡會終止整個呼叫端 PowerShell session,不像 bash 子行程只結束自己(Task 14 先修的收尾那一處)。**2026-08 Task 15 補上殘留缺陷**:三支檔案早期錯誤分支(找不到 python3/python、找不到 git、`git pull`/`git clone` 失敗、交付包不完整,共 6 處)當時仍留著裸的 `exit 2`——這幾處反而更該修,因為全在錯誤路徑上,使用者最需要看到錯誤訊息的時候,視窗反而被關掉,連錯在哪都來不及讀。現在三支檔案的邏輯都包進一個函式,錯誤分支印完訊息後用函式層級的 `return <int>`(不是 `exit`)中止,呼叫端在腳本最下方把函式回傳值收進 `$global:LASTEXITCODE`。**這整段修法(結尾與早期分支)本身都沒有真機驗證過**——只能推理不會再主動關掉呼叫端視窗、`return` 不會意外落空(有靜態結構測試 `t_slim_ps1_error_branches_still_halt_via_return` 驗過「錯誤訊息後一定接 `return`」,但驗不到 PowerShell 的真實執行語意),改法是否真的完全解決原問題、`$LASTEXITCODE` 在各種呼叫路徑下是否確實對呼叫端可見,都得等真機驗證才能下定論。

★**2026-08 Task 16 分支終審抓到三條缺陷,同款誠實聲明,不要誤讀成已解決**★:
- **①BLOCKER,`$ErrorActionPreference = "Stop"` 讓 Task 14/15 那批 `Write-Error`+`return` 修法在錯誤路徑上等於沒做**——PowerShell 語意:`Stop` 模式下 `Write-Error` 這種非終止型錯誤會被升級成終止型例外(等同 `throw`)。後果:`Write-Error` 那行直接拋例外,它後面的 `return <int>` 是死碼、永遠執行不到;例外炸穿呼叫端函式,連 `$rc = Invoke-* ...` 的賦值都完成不了;檔尾 `$global:LASTEXITCODE = $rc` 永遠不執行,呼叫端讀到的是殘留舊值(很可能是 0)——把失敗誤判成成功。修法:三支檔案共 6 處 `Write-Error` 都加 `-ErrorAction Continue` 明確覆寫(PowerShell 官方支援的逐次呼叫覆寫機制,對單一 cmdlet 呼叫的 `-ErrorAction` 會蓋過 `$ErrorActionPreference`)。**這段修法本身沒有真機驗證過**——`-ErrorAction Continue` 在真實 PowerShell 執行時是否確實蓋過 `$ErrorActionPreference`,只能相信官方文件,沒有機會實際跑一行 `$ErrorActionPreference = "Stop"; Write-Error "x" -ErrorAction Continue; Write-Host "still alive"` 驗證「still alive」真的印得出來。
- **③MINOR,`get.ps1` 的 `$ErrorActionPreference` 原本寫在頂層(函式外),會污染呼叫端互動 session**——README 教的一行安裝 `irm ... | iex` 中,`iex` 在**呼叫端當下的 scope** 執行(不像 `& "path.ps1"` 會建新 script scope),這行會直接改到使用者互動 shell 的設定且裝完不還原,同一視窗裡任何原本靠非終止型錯誤運作的後續指令都會被意外中止。修法:把賦值搬進 `Invoke-Get` 函式內部第一行(函式預設有自己的子 scope,函式內賦值不外溢回呼叫端);`install.ps1`/`uninstall.ps1` 因為經 `&` 呼叫本來就有自己的 script scope,不受影響,但一併搬進函式維持三支檔案寫法一致。**這段 scope 隔離語意本身也沒有真機驗證過**——這台機器沒有 PowerShell,無法實際驗證 `iex` 執行下函式內賦值真的不會外溢回呼叫端 session。
- **②MAJOR(Python 邏輯,不是 `.ps1` 未驗清單的一員)Windows 卸載孤兒 `lumos.cmd` 永遠清不掉**——`uninstall.py` 舊版把 `lumos.cmd` 的移除邏輯巢狀在 `lumos` 的 `if` 區塊裡,`lumos` 被手動刪除但 `lumos.cmd` 還在時,整段(含 `--force` 分支)都跳過。已改成獨立區塊,用 shim 固定樣板內容比對當安全基準,並用 `LUMOS_SLIM_SIMULATE_WINDOWS=1` + git-stash 因果驗證(紅→綠,非稻草人)。這條**不在**「未在真機驗證」清單裡——它是 Python 邏輯,驗證方式與既有 Windows 分支邏輯測試一致;但 `.cmd` shim 在真實 `cmd.exe`/PowerShell 下能不能被正確找到並執行,仍與既有未驗清單相同,未擴大也未縮小。

## 怎麼裝

包裡有一支機器層安裝器，做三件事：①把 `lumos` 裝到 `~/.local/bin`（Windows 額外產生 `lumos.cmd` shim，見上方〈支援平台〉）②把技能說明實體複製到 `~/.claude/skills/lumos-project-notes/`（不是 symlink，交付包搬走／刪掉後 skill 仍在）③（★2026-07-31 裁定第三次變更，見下方〈會不會動我專案的 CLAUDE.md〉★）在**執行安裝器時所在的目錄**（你的專案根）的 `CLAUDE.md` 裡放一塊策展過的「怎麼解析圖譜標籤」精簡版紀律區塊——若專案原本就有完整版紀律區塊會被整段取代掉（原位置，不是搬到檔尾），沒有就插在檔首標題之後。

**一行安裝**（把交付包拉到固定落點 `~/.lumos-slim` 再自動執行安裝器）：

```bash
curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.sh | bash
```

不想 `curl | bash` 也可以，**兩行分開跑**（效果完全一樣，只是自己掌控每一步）：

```bash
git clone https://github.com/citrus-android-developer/Citrus_Lumos.git ~/.lumos-slim
~/.lumos-slim/install.sh
```

Windows 對應版本（PowerShell）：

```powershell
git clone https://github.com/citrus-android-developer/Citrus_Lumos.git $HOME\.lumos-slim
& "$HOME\.lumos-slim\install.ps1"
```

兩種方式都會把套件放在 `~/.lumos-slim`（見下方〈`~/.lumos-slim` 是什麼〉），再執行套件裡的安裝器；若目標（全域指令或 skill 目錄）已存在，加 `--force` 覆寫（skill 目錄會先備份成 `.bak.<時間戳>` 才覆寫）——一行版：在 `curl`/`irm` 那行末尾加 `-s -- --force`（Windows 是 `iex "& { $(irm ...) } --force"` 或直接兩行版加 `--force`）；兩行版：`~/.lumos-slim/install.sh --force` 或 `install.ps1 --force`。

**確認裝好**：

```bash
lumos --help
```

看到指令清單（`context`／`search`／`doctor`…）就是裝好了。安裝器**不會改 `.git/config`**、不會碰專案裡除了 `CLAUDE.md` 以外的任何檔案；`CLAUDE.md` 這一份會被動，細節見下方〈會不會動我專案的 CLAUDE.md〉。

## 會不會動我專案的 CLAUDE.md

**會**（★2026-07-31 裁定第三次變更★）。這條裁定改了三次，如實記錄演進，別誤會成一次到位：

1. **原裁定（絕不碰）**：安裝器完全不注入／不更新任何 `CLAUDE.md`。
2. **第二次（只准附加）**：開放在 `CLAUDE.md` 檔尾用專屬 sentinel 附加一段教學句，sentinel 以外一個位元組都不動；專案原本若有完整版 `LUMOS:GRAPH-DISCIPLINE` 紀律區塊，原封不動留著、兩套規則並存。
3. **現在（可移除既有區塊並策展吸收）**：發現「兩套規則並存」本身就是問題——完整版那段開頭就自稱「優先級最高」「第一個工具呼叫必須是 `lumos`」，接手者的 Claude 會先讀到它、照著它引用的十幾處進階指令去撲空（那些指令本包都沒交付）。現在若專案已有完整版區塊，安裝器會**整段移除它**，換成精簡版區塊——但移除前**先把完整版原文位元組級備份**，`uninstall.sh` 能精確還原。

**移除前會先策展**：完整版區塊裡仍然有效的內容（圖譜即唯一真相來源的核心原則、進場三步、summary 符號表、合約鏈 `★INVARIANT★`/`★DEBT★`/`[test:]`/`[audit:]`、可逆性標記 `★IRREVERSIBLE★`/`★CHECKPOINT★`/`[rollback:]`、regen 重生標記 `[src:]`/`[git:]`/`推測:`/`佚失:`、frontmatter 欄位）已經吸收進精簡版區塊（範本見本包隨附的 `claude-block.md`）；拿掉的只有依賴本包沒交付的指令才有意義的段落。

**插入位置**：①專案原本有完整版區塊 → 精簡版區塊插在**它原本的位置**（不是搬到檔尾——那裡才顯眼）②沒有 → 插在檔首「# 標題」之後，沒有標題就插最前面 ③`CLAUDE.md` 不存在 → 建立，內容就是這個區塊。sentinel（`<!-- LUMOS-SLIM:START -->` … `<!-- LUMOS-SLIM:END -->`）以外的既有內容，一律 byte-equal 保留。

**備份機制**：完整版區塊原文（含它自己的 sentinel）base64 編碼後，藏在精簡版區塊自己的 HTML 註解裡（`<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->`）——不新增任何檔案到你的專案（不污染 `git status`），也不依賴 `~/.lumos-slim` 存在（就算那個目錄事後被刪掉，備份仍隨 `CLAUDE.md` 本身留著）。`uninstall.sh` 讀出這個標記、解碼、還原回原位置，位元組級一致。

**寫入紀律（三條，都有回歸測試釘住）**：
1. **原地取代，不搬位置**——sentinel 以外的既有內容 byte-equal 保留；有完整版區塊就原位置換掉，沒有就插在檔首標題後。
2. **冪等**——裝好之後重跑安裝器（例如帶 `--force` 重裝），只會更新自己那塊 sentinel 之間的內容，不疊出第二塊、備份也不會被重新編碼或洗掉。
3. **可移除**——跑 `uninstall.sh` 能位元組級還原（若原本有完整版區塊）或乾淨拿掉這一塊（若原本沒有），其餘內容原封不動；若 `CLAUDE.md` 是安裝時才新建的（原本沒有這份檔案），卸載後連檔案本身也會一併消失。

**已知風險（已知並接受的取捨）**：完整版區塊自稱「自動注入/更新」——如果這個專案還有其他人在用完整版 lumos-toolchain、他跑了更新流程，會把完整版裝回來，兩邊就變成來回覆蓋。本包沒有機制阻止這件事，只能在這裡講清楚。

**目標是哪一份 `CLAUDE.md`**：**執行安裝器（或 `get.sh`）時所在的目錄**（也就是你的專案根）底下的 `CLAUDE.md`。跟其他機器層動作（裝全域指令、複製 skill）不同，這一步是唯一會碰專案檔案的動作——但範圍嚴格限制在這一塊 sentinel（及它取代掉的完整版區塊，若有）。

## 注入目標守衛（裝到哪裡才安全）

安裝器會對「執行時所在的目錄」動手，這件事本身就有誤用風險——★真實事故發生過兩次★：有人忘記先 `cd` 進交付包的 clone，直接在別的專案（甚至 lumos 工具鏈自己的來源 repo）底下跑了 `install.sh`，當場改掉了那個目錄的 `CLAUDE.md`。兩次都當場發現、手動還原，但足以說明這支腳本本質上容易誤用。為此裝了三層守衛，**各擋不同的東西，別把它們當成同一件事**：

1. **第一層：不像專案根就拒絕**——目標目錄要有 `.git`、或有 `docs/*-knowledge/`（lumos 圖譜專案）、或已有 `CLAUDE.md`，三項至少一項成立才放行；一項都沒有就拒絕（rc=2，`CLAUDE.md` 不會被建立）。特例：目標目錄等於你的 `$HOME` 一律硬擋，就算 `$HOME` 底下剛好有 `.git` 也一樣。這層擋的是「在 `~` 或隨便一個目錄下誤跑」。
2. **第二層：拒絕裝進 lumos 工具鏈的來源 repo**——★這層才是真正擋住上述兩次事故的那層★：事故發生的目錄本身就有 `.git`／`docs/*-knowledge/`／既有 `CLAUDE.md`，長得完全像個合理的專案根，第一層擋不住。這層改用更精確的判斷：目標目錄若同時具備 `skills/lumos-project-notes/`、`scripts/lumos`、`scripts/templates/graph-discipline.md` 三件套，就判定它是 lumos 工具鏈本身的原始碼 repo（不是要交接的消費端專案），拒絕（rc=2）。
3. **第三層：把目標印大聲**——不管前兩層過不過，動手前一定先印出「目標專案」與「將修改」的絕對路徑。這是最後一道人眼防線：前兩層擋不住「在另一個合法專案根誤跑」（例如手滑跑錯專案），只有把目標印出來才有機會被看見。

**逃生閥 `--here`**：明確知道自己要在這個目錄安裝、且目錄不像專案根或恰好被判成來源 repo，加 `--here` 繞過第一、二層（第三層的目標印出不受影響，一定會印）。

## 怎麼移除

**一行卸載**：

```bash
curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/uninstall.sh | bash
```

已經裝過的話，也可以直接跑套件裡帶的那支：

```bash
~/.lumos-slim/uninstall.sh
```

**卸載會做什麼**（安全紀律比功能更重要，逐條講清楚）：

★2026-07-31 改版★：下面五步**各自獨立判斷、各自執行、互不阻擋**——任何一步基於安全考量選擇跳過，都不會連帶讓其他步驟不執行（尤其是第 4 點的 `CLAUDE.md` 還原）。全部跑完才彙總報告，結束碼依整體結果決定：**0**＝每一步都完成或本來就沒裝；**1**＝至少一步基於安全考量主動跳過（不是程式壞掉，是它不確定能不能安全動手，需要你看一下，確定要處理就加 `--force` 重跑）；**2**＝真正的錯誤（例如 `CLAUDE.md` 狀態不明確、備份解碼失敗、刪除/備份操作本身失敗）。★注意★：舊版 bash 有一條「找不到 `sha256sum`／`shasum` 這兩支外部工具」的 rc=2，Python 版**不可能發生**（`hashlib` 是標準庫），所以那個診斷方向已經作廢，別往那邊查。

1. 移除全域指令 `~/.local/bin/lumos`——**只有在它的內容經比對確實是本包裝的那份時才會動**。比對基準優先讀 `install.sh` 裝機時寫下的身分證 manifest（`~/.local/share/lumos-slim/manifest.json`）——這份**不依賴 `~/.lumos-slim` 還存不存在**；只有在 manifest 也讀不到時，才退回舊版做法（比對 `~/.lumos-slim/scripts/lumos`，相容較舊的安裝）。兩種情況會拒絕移除，訊息分開講、別搞混：「**基準缺失**」（manifest 跟 `~/.lumos-slim` 都沒有可比對的東西，判斷不出來，不是內容有問題）跟「**內容真的不符**」（找得到基準，但內容比對不一樣，可能是你自己另外裝的東西）——不管哪一種，不會用猜的去刪，真的確定要砍才加 `--force`。
2. 移除技能目錄 `~/.claude/skills/lumos-project-notes/`——**移除前一定先備份成 `.bak.<時間戳>`，不會直接砍掉**；你如果在裡面塞過自己的筆記或修改，備份目錄裡找得到。這一步不受第 1 點的結果影響。
3. 移除 `~/.lumos-slim` 本身——前提是它裡面的東西看起來還是本包的內容（有 `scripts/lumos` 跟 `install.sh`），不是就留著不動。這一步也不受前面步驟的結果影響。
4. 處理**執行卸載腳本時所在目錄**（專案根）`CLAUDE.md` 裡的 `<!-- LUMOS-SLIM:START -->` … `<!-- LUMOS-SLIM:END -->` 區塊——找不到這塊 sentinel 就當「本來沒裝」放行，不會報錯；找到就讀出區塊內建的備份標記：**有**完整版原文備份（代表 `install.sh` 當初取代掉了完整版 `LUMOS:GRAPH-DISCIPLINE` 區塊）→ 位元組級還原該區塊回原位置；**沒有**（當初本來就沒有完整版區塊）→ 單純移除精簡版區塊。sentinel（與還原出來的完整版區塊）以外的既有內容原封不動；若整份 `CLAUDE.md` 是安裝時才新建的（挖完變空），連檔案本身也會一併移除，回到「原本沒有這份檔案」的狀態。★這一步永遠會跑,不會因為第 1 點的 bin 比對失敗就沒機會執行★——這是 2026-07-31 端到端實測抓到的真 bug 修好之後的行為：舊版把第 1 點的比對失敗當一票否決，直接中止整支腳本，導致這一步（也是使用者最在意的「把完整版紀律區塊還給我」）完全沒機會跑到；現在五步互不相干，各自對各自的結果負責。

5. 移除身分證 manifest `~/.local/share/lumos-slim/manifest.json` 本身（以及它那個空掉的 `lumos-slim/` 父目錄）——★2026-08-01 真跑冒煙補的★：在此之前卸載跑完會把這支檔案留在你家目錄底下，彙總卻印「全部完成」（整套自動測試也看不到，因為根本沒有任何一條去驗它該消失）。**只刪這支檔案跟它的空父目錄，`~/.local/share` 底下其他任何東西一律不碰**（那是很多工具共用的地方）。★這一步有一個例外條件★：如果第 1 點的 bin 因為安全考量沒被移除（內容不符／基準缺失），manifest 會**刻意留著**——★Windows 上還有第二種情況★：`lumos.cmd` shim 被拒絕移除時同樣會留著 manifest，所以你可能會看到第 1 點印「✓ 已移除: lumos」、卻同時收到保留 manifest 的訊息，那是正常的（`lumos` 跟 `lumos.cmd` 是一對，只要有一個沒清掉就都算沒清乾淨）並印一句為什麼——它正是你之後加 `--force` 或手動確認時唯一的比對基準，先刪掉等於把判斷依據銷毀，下次重跑只會落到「基準缺失」，反而更難判斷。等你確定要處理、加 `--force` 重跑把 bin 清掉之後，manifest 一樣會跟著收乾淨。

**卸載不會碰什麼**：

- 不碰任何專案目錄／repo（**唯一例外**：上面第 4 點那塊 `CLAUDE.md` 裡的 `LUMOS-SLIM` sentinel 區塊，及它取代掉的完整版區塊（若有，已還原）——除此之外不動專案任何其他檔案）。
- 不碰 `~/.claude/settings.json`。
- 不碰 `~/.claude/hooks/`。
- 不碰除了 `lumos-project-notes` 以外的任何其他 skill。

## `~/.lumos-slim` 是什麼

`get.sh` 會把交付包 clone 到這個固定路徑，再執行裡面的安裝器，把 `lumos` 複製到 `~/.local/bin`、把 skill 複製到 `~/.claude/skills/`——複製之後兩邊就解耦了：就算事後把 `~/.lumos-slim` 整個刪掉，已經裝好的全域指令跟 skill 仍然能正常用，不會斷。

固定放在這裡（而不是像早期版本用「安裝器所在目錄」定位自己）是為了讓一行安裝可以透過 `curl | bash` 執行——那種跑法下腳本沒有穩定的檔案位置可定位自己，需要一個固定的家。

**兩行版安裝（見〈怎麼裝〉）不會建立這個路徑**——你自己挑地方 clone、直接跑那個路徑下的 `install.sh`，`~/.lumos-slim` 從頭到尾不會存在，這是正常、支援的用法，不是錯誤操作。★2026-07-31 起★：卸載腳本比對 `~/.local/bin/lumos` 的**主要**依據已經改成 `install.sh` 裝機時另外寫的一份身分證 manifest（`~/.local/share/lumos-slim/manifest.json`），不依賴 `~/.lumos-slim` 存不存在；只有在讀不到這份 manifest 時，才會退回舊版做法（拿 `~/.lumos-slim/scripts/lumos` 當比對基準）。

**可以自己刪掉嗎？可以**，留著或刪掉都不影響卸載——比對基準已經不靠這個目錄。留著的唯一理由是可以用〈怎麼裝〉的一行/兩行指令再跑一次做冪等更新（雖然本包是凍結快照，不會有真正的新版本可拉，見下方〈凍結聲明〉）。

## 進場三步

讀一個既有專案的圖譜，永遠先做這三步，再去翻程式碼：

```bash
lumos search <關鍵字>      # 定位
lumos context <節點>       # 掃脈絡(頭部會攤開 ⚠ 合約)
lumos contracts <節點>     # 查硬合約
```

`lumos search` 找到相關筆記 → `lumos context` 看該筆記加上鄰居的濃縮索引（合約會被突顯在最上面）→ `lumos contracts` 專門列出這個模組的硬合約（改了算 breaking 的那些）。三步做完，再去 grep 程式碼或查資料庫印證。

## Frontmatter 四條鐵則

寫圖譜筆記時 frontmatter 有四條血換來的鐵則，違反會讓圖譜長出讀不到的 ghost 節點、甚至整篇 frontmatter 報廢（以下逐字轉錄自 `skills/lumos-project-notes/reference.md`）：

1. **多個 wikilink 必須是 YAML list，一項一連結**。❌ `verified_by: "[[A]], [[B]]"`（單一字串）→ Obsidian 把整串從第一個 `[[` 貪婪吃到最後一個 `]]` 當成**一個**超長連結 → 圖譜長出亂碼灰色 ghost 節點；在 Obsidian 點到該節點還會**自動建立含 `]], [[` 的垃圾檔案**（檔名中的 `/` 切成巢狀資料夾）。✅ 寫法見 `related` / `verified_by` 範例。
2. **block scalar（`summary: |` 等）內的 wikilink 不會被索引**。寫在 summary 裡的 `[[X]]` 只是文字，不產生圖譜連結、不算 backlink——要建立關聯必須同時在內文（如「## 相關模組」）或 list 型 property 放一份，否則目標筆記可能變孤兒。
3. **含 `: `（冒號+空格）的長文必須用 block scalar 或引號**。❌ `- content: 處置 SQL: UPDATE ...`（未引號）→ YAML `mapping values are not allowed` → **整篇 frontmatter 解析失敗**，所有 property 查詢對此筆記隱性失效。✅ `- content: |-` 換行縮排放長文。
4. **同一層級禁止重複鍵**。`decided:` / `valid:` 在同一個 decision item 出現兩次 → Obsidian 的 js-yaml 直接整篇 fail（CLI 的 ruby/libyaml 寬鬆放行，**用 CLI 驗過不代表 Obsidian 讀得到**）。

**純量／list／decisions 一律走 `lumos set`/`append`/`decision-add`**，別手改 frontmatter——這條鐵則的規避方法比記住鐵則本身更重要。

## 合約鏈是什麼、doctor 為什麼會擋、怎麼解

Systems 筆記記的是「現在長什麼樣」，天生分不出哪些是**合約**（改了算 breaking）、哪些是**偶然**（實作副產物，可以隨便改）。圖譜用 KEY 行的前綴聲明這件事：

```
KEY:★INVARIANT★ <業務合約,改=breaking> [test:測試名] [audit:模型/日期]
KEY:★DEBT★ <已知偶然行為,可改不算 breaking>
```

`[test:方法名]` 是**合約鏈**的第一環：每條 ★INVARIANT★ 都要綁一個真實存在的測試方法。`lumos doctor` 巡檢時會檢查這個綁定——**綁定走指令** `lumos guard bind <node> "<KEY子字串>" <測試名>`。

**doctor 為什麼會擋**：`lumos doctor --ci` 底下，有 ★INVARIANT★ 卻沒綁 `[test:]`（裸合約）、或綁的測試方法根本不存在，都會讓 doctor 回報問題（`--ci` 模式視情況變成非零結束碼）。這不是任性刁難——沒有可執行證據的「合約」只是自稱，doctor 在替你把「宣稱」和「驗過」分開。

**怎麼解**：

- 先判斷這條 KEY 行到底該不該是合約——不確定就先拿掉 ★INVARIANT★（寧漏勿錯，把偶然行為合約化會鎖死未來重構）。
- 確定是合約 → 找到（或先寫一個）真實測試方法 → `lumos guard bind` 把 `[test:方法名]` 綁回 KEY 行。
- 寫完一個節點先跑 `lumos lint <節點>` 自驗（比全圖 `doctor` 快），收尾再跑一次 `lumos doctor`。

### ⚠ doctor 有些建議指向本包沒給的指令，看到請忽略

`doctor`／`lint` 有幾個檢查項是從完整版原封繼承的，訊息裡會叫你跑本精簡版沒交付的指令修復——已知至少有 `lumos init`、`lumos update`、`lumos self-audit <node>`、`lumos signoff <node>`（最後一支出現在 `lint` 對 regen 節點的證據檢查訊息裡）——**這份列舉不保證窮盡**，跑了只會得到「未知指令」錯誤才是判準。看到本精簡版沒有的指令名就知道不必照做，該檢查項在本版沒有機械修復路徑。

### ⚠ 程式碼註解裡也會提到本包沒交付的檔案

`scripts/lumos` 的註解是**刻意原樣保留**的（那是「當初為什麼這樣寫」的脈絡，砍掉就再也問不到人了）。但其中有些註解會指向完整版工具鏈才有的東西——圖譜節點路徑（`Projects/xxx_計劃`）、對抗審語料目錄（`governance/golden/...`）、或 `[code-loop rN]`／`[design-loop]` 這類流程標記。**這些檔案本包都沒交付，查不到是正常的，不是你漏拿了什麼**；註解本身要表達的意思（為什麼這行要這樣寫）是完整的，照著讀就好。

本包附的 `slim-scan` 掃描器只掃**指令名**的懸空引用，掃不到這種**路徑型**的——所以這裡也一樣不宣稱窮盡。

相關的是 **Check D（`CLAUDE.md` 紀律區塊比對）**：這項檢查在**找不到任何 sentinel 區塊時會自動略過**（印「尚未注入」，不算 issue）。本包安裝器若在你的專案裡發現完整版 `<!-- LUMOS:GRAPH-DISCIPLINE:START -->` 那個 sentinel 區塊，會整段取代成本包自己的 `<!-- LUMOS-SLIM:START/END -->` 區塊（見〈會不會動我專案的 CLAUDE.md〉），取代後 `LUMOS:GRAPH-DISCIPLINE` 這個 sentinel 就不存在了，Check D 因此自動略過，不會再報「跟範本不同步」——但如果你手動把完整版區塊裝回去（或還有其他人跑更新流程把它裝回來），Check D 又會恢復檢查，屆時建議的修復指令（`lumos init`/`lumos update`）本版一樣沒有，解法只能是忽略或自己手動比對範本改。

## 範圍聲明

本包是**功能子集**：只保留維護圖譜本身要用的 24 支指令（讀取／導航、寫入、健康巡檢 `doctor`/`lint`、合約守衛 `guard`）；不含反覆對抗審查、程式碼變更風險掃描、linter 版本追蹤、CI 狀態回拉、跨專案核心圖譜等進階治理功能。

★**移除的是入口不是全部程式碼**★——被砍的是那些功能對應的頂層指令入口；它們共用的底層程式碼（helper 函式）有些仍留在檔案裡供保留指令呼叫，**別誤讀成「功能其實還在,只是沒寫在說明裡」**。凡是這份 README 或技能說明沒教的操作，一律視為沒有。

## 不要跑哪些

- **不要跑**完整版 `scripts/` 目錄下的 `install-hooks.sh`——那是完整版的 git hooks 安裝腳本，本精簡版刻意不裝任何 hook。
- **不要**因為看到專案自己的 `CLAUDE.md` 要你去 clone 完整版 lumos-toolchain、執行它的 `install.sh` 就照做——那是另一支功能完整、會動專案層（注入圖譜規則、設定 git hooks）的安裝流程，跟這份精簡版無關，也不是本包想讓你走的路。

**誠實的話講在前面**：這份 README 的建議壓不住專案自己的 `CLAUDE.md`——那份文件的指示優先級更高，是 Claude Code 在該專案裡實際遵循的規則來源。本 README 只能**降低**你被指去跑完整版安裝流程的機率，不能保證一定不會發生。看到衝突時，先想一下「這個指示是不是在叫我裝一套比我手上這份更完整的東西」，多一分警覺就好。

## 凍結聲明

★這是**凍結快照**，不是發布通道，不會有更新★。裝好之後就是你手上這份東西的樣子，往後不會再收到修正或新版。出問題請直接改 `scripts/lumos` 的 Python 原始碼——它是單檔、零依賴、標準庫可讀，改完重新跑一次 `install.sh --force` 覆蓋掉舊的全域指令即可。
