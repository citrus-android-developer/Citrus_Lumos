# Windows 腳本設計筆記（`.ps1` 的中文說明搬到這裡）

> ★這三支 `.ps1` 本體必須是 **ASCII-only 且不加 BOM**★——理由見下方〈為什麼 ASCII-only〉。
> 原本寫在檔案裡的中文註解全部搬到這裡，**知識不丟，但不進 `.ps1`**。

## 為什麼 ASCII-only

**BOM 是兩難，不是解法**：

| 執行路徑 | 無 BOM | 有 BOM |
|---|:--:|:--:|
| 磁碟執行 `& install.ps1` | ✗ PowerShell 5.1 用系統 ANSI codepage 讀，DBCS 前導位元組吃掉下一個位元組、撞壞引號配對 | ✅ |
| `irm … \| iex`（README 唯一教的） | ✅ | ✗ `irm` 回的是普通字串，BOM 不會被剝，`U+FEFF` 成為第 1 行內容 |

**ASCII-only 讓兩條路徑都不需要 BOM，問題被消滅而不是搬家。**

真 PowerShell（本機 pwsh 7.6.4）實測確認：

```
[無 BOM] → OK
[有 BOM] → ERROR: The term 'Windows/PowerShell' is not recognized as a name of a cmdlet…
```

**組織內早有同一條紀律**：`LandmarkMember` 的 `CLAUDE.md`〈Deploy 腳本踩雷規則〉第 1 條
「ASCII-only 規則」，理由一字不差，且是踩了三輪 prod deploy 失敗才立的。

## 另一個語言層陷阱：`param($Args)`

`$Args` 是 PowerShell **自動變數**（函式自己「未綁定的參數」），同名 `param` 會被它蓋掉：

```
param($Pkg, $Args)       + -Args @("--force","--here")  → 函式內 count=0   ← 旗標全部靜默失效
param($Pkg, $ScriptArgs) + -ScriptArgs @(...)           → count=2         ← 正常
```

（同樣是本機 pwsh 實測。）所以三支的參數一律叫 `$ScriptArgs`。

## `get.ps1`

- L1: get.ps1 — 公開精簡版 一行安裝入口(Windows/PowerShell)
- L3: 用法:
- L6: 邏輯與 get.sh 對稱(逐步翻譯,不是重新設計):
- L7: ① 把交付包 clone(首次)或更新(已存在時 git pull)到固定落點 ~\.lumos-slim
- L8: ② 執行套件內的 install.ps1(它只轉發給 install.py,細節見該檔案開頭註解)
- L10: ★為什麼要固定落點★:跟 get.sh 同款理由——`irm ... | iex` 執行時沒有穩定的
- L11: 檔案位置可定位自己,且使用者若把套件搬走/刪掉,全域指令就斷了。固定落點也讓
- L12: uninstall.py 有地方可以拿真值(sha256 比對)判斷 `~\.local\bin\lumos` 是不是
- L13: 我們裝的那份(見 install.py 的身分證 manifest 說明——manifest 是主要比對來源,
- L14: 這個固定落點只是找不到 manifest 時的備援)。
- L16: ★冪等★:~\.lumos-slim 已存在且是合法 git repo → git pull 更新,不重新 clone。
- L17: 已存在但不像我們的東西(沒有 .git)→ 拒絕動它、印清楚訊息,不猜測、不覆寫。
- L19: ★誠實聲明★:沒有在真機 Windows 上跑過(開發環境是 macOS,沒有 PowerShell/
- L20: git-for-Windows 可用)——邏輯照 get.sh 逐步翻譯,git clone/pull 的參數與
- L21: get.sh 相同,但這支腳本本身、`irm | iex` 這種執行方式在真實 Windows 上的行為
- L22: 都沒有真機驗證過。
- L24: ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★,與
- L25: install.ps1 同款理由,細節見該檔案同一段註解)★:收尾不再呼叫裸的 `exit`
- L26: ——`get.ps1` 正是 README 一行版 `irm ... | iex` 直接執行的那支腳本,`exit`
- L27: 在這種呼叫方式下最容易把使用者當下開著的 PowerShell 視窗整個關掉;改把
- L28: `install.ps1` 的 rc 寫回 `$LASTEXITCODE` 供呼叫端讀取。
- L30: ★2026-08 Task 15(接續 Task 14,補殘留缺陷,與 install.ps1 同款理由)★:
- L31: 這支檔案早期還有 4 處錯誤分支的 `exit 2`(找不到 git、pull 失敗、目的地已
- L32: 存在但不是我們的 clone、交付包內容不完整)沒有一併改掉,而 `get.ps1` 正是
- L33: `irm ... | iex` 一行版直接執行的腳本,踩到的機率最高。改法:整段邏輯包進
- L34: `Invoke-Get` 函式,每個錯誤分支印完 `Write-Error` 後 `return 2`(函式層級
- L35: 的 `return`,不是 `exit`——只結束這支函式,不終止呼叫端 session,也保證
- L36: 該分支之後真正的 clone/安裝動作不會被跑到);本檔案最下方把函式回傳值收進
- L37: `$rc` 再寫回 `$global:LASTEXITCODE`。這段語意同樣沒有真機驗證過。
- L39: ★2026-08 Task 16 修復①(BLOCKER,補 Task 15 遺漏,理由與 install.ps1 同款,
- L40: 細節見該檔案同一段註解)★:`$ErrorActionPreference = "Stop"` 會把
- L41: `Write-Error` 升級成終止型例外,讓它後面的 `return 2` 執行不到、例外炸穿
- L42: `Invoke-Get`、`$global:LASTEXITCODE` 永遠寫不進去、呼叫端把失敗誤判成成功
- L43: ——`get.ps1` 正是 `irm ... | iex` 一行版直接執行的腳本,踩到的機率最高。
- L44: 改法:4 處 `Write-Error` 都加 `-ErrorAction Continue` 明確覆寫。同樣沒有
- L45: 真機驗證過。
- L47: ★2026-08 Task 16 修復③★:`$ErrorActionPreference = "Stop"` 若寫在頂層(不在
- L48: 函式裡面),會污染呼叫端 session——README 教的一行安裝是 `irm ... | iex`,
- L49: `iex` 是在**呼叫端當下的 scope** 執行(不像 `& "path.ps1"` 會建新 script
- L50: scope),使用者跑完一行安裝後,同一個視窗裡任何原本靠非終止型錯誤運作的
- L51: 後續指令都會被意外中止,而且裝完不會自動還原,使用者也不會知道原因是
- L52: 「剛剛裝了個東西」。改法:把這行賦值移進 `Invoke-Get` 函式內部第一行——
- L53: PowerShell 函式預設有自己的子 scope,函式內對變數賦值(沒加 `$global:`/
- L54: `$script:` 前綴)只落在函式自己的 local scope,不會外溢回呼叫端;`Invoke-Get`
- L55: 這個函式本體已經涵蓋了本檔案所有會用到非終止型錯誤語意的邏輯(git 指令、
- L56: clone/pull),搬進去不影響行為,只是把賦值的可見範圍收窄。`install.ps1`／
- L57: `uninstall.ps1` 因為經 `&` 呼叫、本來就有自己的 script scope,不受這個污染
- L58: 問題影響,但一併搬進函式維持三支檔案寫法一致。這段 scope 語意同樣沒有真機
- L59: 驗證過(這台機器沒有 PowerShell)。
- L83: ★這道檢查以前漏了(2026-08-02 補)★:同一個函式裡 `git pull`
- L84: 那一支有檢 `$LASTEXITCODE`、`git clone` 這一支沒有,純粹是漏寫。
- L85: ★不能靠 `$ErrorActionPreference = "Stop"` 兜底★——它只管 PowerShell 自己
- L86: 的 cmdlet 錯誤,原生執行檔(git.exe)回非零 exit code ★不會★ 觸發終止
- L87: (PS 7.3 起才有 `$PSNativeCommandUseErrorActionPreference` 可改這行為,
- L88: 本腳本要支援更舊的 Windows PowerShell 5.1,不能依賴)。
- L89: 漏掉的後果:clone 失敗(沒網路/私有 repo 沒權限/磁碟滿)後照樣往下走,
- L90: 使用者看到的是下一段那句「交付包內容可能不完整」——把網路/權限問題
- L91: 誤導成「這個包壞掉了」,查錯方向完全被帶偏。
- L104: ★`| Out-Host` 不可省(2026-08-03 中文 Windows 真機驗證抓到)★:PowerShell 函式的
- L105: `return` 會帶出函式內★所有未被消費的輸出★。`&` 的 stdout 沒被指派給任何變數就
- L106: 進了輸出流,`return $LASTEXITCODE` 再追加一個數字 → 呼叫端收到的是 ★Object[]★
- L107: 而不是數字,實測 `SetShouldExit` 直接爆:
- L109: ★`$code = $LASTEXITCODE; return $code` 解決不了★——問題出在 `&` 的 stdout 進了
- L110: 輸出流,不是 return 的寫法。`| Out-Host` 讓子行程輸出直接進主機、不進 pipeline。

## `install.ps1`

- L1: install.ps1 — 薄殼:所有安裝邏輯已搬進 install.py(stdlib only,Unix/Windows
- L2: 共用同一份原始碼)。本檔案只做兩件事:①定位套件目錄(自己所在目錄)②挑一支
- L3: 可用的 python 直譯器,把參數原樣轉發給 install.py。
- L5: 形態沿用本 repo 完整版 `get.ps1` 的先例(幾乎什麼都不做,把工作丟給 python)。
- L7: ★誠實聲明★:這支腳本沒有在真機 Windows 上跑過(開發環境是 macOS,沒有
- L8: PowerShell)——邏輯與 install.sh/install.py 對照移植而來,只驗證過
- L9: install.py 本體透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 在非 Windows 機器上跑
- L10: 出的分支邏輯(見 install.py 模組 docstring),這支 .ps1 薄殼本身、Windows
- L11: PATH 的實際行為、`.cmd` shim 在真實 cmd.exe/PowerShell 下能不能被找到,都
- L12: 沒有真機驗證過。
- L14: ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★)★:
- L15: 舊版收尾是裸的 `exit $LASTEXITCODE`——PowerShell 的 `exit` 在 README 教的
- L16: 兩種呼叫方式(`irm ... | iex` 一行版、`& "路徑\install.ps1"` 兩行版)下都會
- L17: 終止整個呼叫端 session,不像 bash 子行程只結束自己:使用者貼上指令、安裝其實
- L18: 成功了,但畫面印完「裝好了」之後整個 PowerShell 視窗突然關閉,會被誤以為是
- L19: 崩潰。改成不呼叫 `exit`,只把子行程(`install.py`)的 rc 寫回
- L20: `$LASTEXITCODE`(PowerShell 的特殊自動變數,寫入即對呼叫端可見,呼叫端仍可
- L21: `& install.ps1; if ($LASTEXITCODE -ne 0) {...}` 讀到正確值)——★取捨★:若
- L22: 是用 `powershell.exe -File install.ps1` 這種「當成獨立行程啟動」的方式呼叫
- L23: (README 沒教這種呼叫法),因為腳本本身不再呼叫 `exit`,回給作業系統的行程
- L24: exit code 會固定是 0,不會反映失敗;README 教的兩種呼叫方式都是在同一個
- L25: session 內執行(不是啟動新行程),不受此取捨影響。
- L27: ★2026-08 Task 15(接續 Task 14,補殘留缺陷)★:Task 14 只修了「結尾」那個
- L28: `exit $LASTEXITCODE`,早期「找不到 python」錯誤分支的 `exit 2` 沒有一併改
- L29: ——這處反而更該修,因為它在錯誤路徑上,使用者最需要看到錯誤訊息的時候
- L30: 視窗反而被關掉,連錯在哪都來不及讀。改法:把整段邏輯包進 `Invoke-Install`
- L31: 函式,錯誤分支印完 `Write-Error` 後 `return 2`(函式層級的 `return`,不是
- L32: `exit`——只結束這支函式,不終止呼叫端 session);本檔案最下方把函式回傳值
- L33: 收進 `$rc` 再寫回 `$global:LASTEXITCODE`,沿用 Task 14 選定的慣例。這段
- L34: 語意同樣沒有真機驗證過,見上方「★誠實聲明★」與 `slim/README.md`〈支援
- L35: 平台〉。
- L37: ★2026-08 Task 16 修復①(BLOCKER,補 Task 15 遺漏)★:`$ErrorActionPreference
- L38: = "Stop"` 會把 `Write-Error` 這種非終止型錯誤升級成終止型例外(等同
- L39: `throw`)——Task 15 只驗了「Write-Error 後面緊接著 return 2」這個原始碼長相,
- L40: 完全沒注意到 `Stop` 之下 `Write-Error` 那行自己就會先拋例外,`return 2` 根本
- L41: 執行不到、例外炸穿呼叫端、`$rc = Invoke-Install ...` 那行也完成不了,最終
- L42: `$global:LASTEXITCODE = $rc` 永遠不執行——呼叫端讀到的是殘留舊值(很可能是
- L43: 0),把失敗誤判成成功。改法:每一處 `Write-Error` 都加 `-ErrorAction
- L44: Continue` 明確覆寫(而不是拆 try/catch 或改用 `[Console]::Error`)——理由:
- L45: ①這是 PowerShell 官方支援的逐次呼叫覆寫機制,語意上最直接對應「這個
- L46: 錯誤訊息我要它保持非終止型」這句意圖 ②維持「Write-Error 後緊接著 return」
- L47: 這個既有結構,不需要重新設計成 try/catch 包住整段函式 ③訊息仍然真的走
- L48: Write-Error(進 stderr、保留 PowerShell 錯誤記錄的語意),不是換一套機制
- L49: 把訊息換個管道印出。★這段修法同樣沒有真機驗證過★——見 `t_slim_ps1_
- L50: write_error_noterminating_under_stop_preference` 的誠實邊界說明:靜態測試
- L51: 只能驗「有沒有 -ErrorAction Continue」這個寫法,驗不到 PowerShell 真實執行
- L52: 時 Stop 語意是否真的被這個參數蓋掉。
- L54: ★2026-08 Task 16 修復③(一致性處理,本檔案原本不受影響)★:`$ErrorAction
- L55: Preference = "Stop"` 移進 `Invoke-Install` 函式內部第一行(原本在頂層)。
- L56: 本檔案是經 `& "路徑\install.ps1"` 呼叫,PowerShell 對指令碼檔案呼叫本來就會
- L57: 建立獨立的 script scope,原本寫在頂層就不會污染呼叫端 session(不像
- L58: `get.ps1` 被 `irm ... | iex` 直接在呼叫端 scope 執行、細節見該檔案同一段
- L59: 註解)——這裡搬進函式純粹是三支檔案寫法一致,不是修一個真的缺陷。
- L60: ★頂層的 `$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path` 刻意留在
- L61: 函式外★:`$MyInvocation` 在函式內部會變成指向函式自己的呼叫資訊,不是整支
- L62: 腳本的,搬進函式會改變 `.MyCommand.Path` 的語意(定位套件目錄的邏輯會壞掉)
- L63: ——只有 `$ErrorActionPreference` 這行單純賦值、不依賴 `$MyInvocation`,才
- L64: 搬得動。
- L77: ★`| Out-Host` 不可省(2026-08-03 中文 Windows 真機驗證抓到)★:PowerShell 函式的
- L78: `return` 會帶出函式內★所有未被消費的輸出★。`&` 的 stdout 沒被指派給任何變數就
- L79: 進了輸出流,`return $LASTEXITCODE` 再追加一個數字 → 呼叫端收到的是 ★Object[]★
- L80: 而不是數字,實測 `SetShouldExit` 直接爆:
- L82: ★`$code = $LASTEXITCODE; return $code` 解決不了★——問題出在 `&` 的 stdout 進了
- L83: 輸出流,不是 return 的寫法。`| Out-Host` 讓子行程輸出直接進主機、不進 pipeline。

## `uninstall.ps1`

- L1: uninstall.ps1 — 薄殼:所有卸載邏輯已搬進 uninstall.py(stdlib only,Unix/
- L2: Windows 共用同一份原始碼)。本檔案只做兩件事:①定位套件目錄(自己所在目錄)
- L3: ②挑一支可用的 python 直譯器,把參數原樣轉發給 uninstall.py。
- L5: ★誠實聲明★(與 install.ps1 同款):沒有在真機 Windows 上跑過,只有 uninstall.py
- L6: 本體透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 驗過分支邏輯。
- L8: ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★,與
- L9: install.ps1 同款理由,細節見該檔案同一段註解)★:收尾不再呼叫裸的 `exit`
- L10: (避免在 `& "路徑\uninstall.ps1"` 這種呼叫鏈裡把呼叫端整個 session 關掉),
- L11: 改把子行程 rc 寫回 `$LASTEXITCODE` 供呼叫端讀取。
- L13: ★2026-08 Task 15(接續 Task 14,補殘留缺陷,與 install.ps1 同款理由)★:
- L14: 早期「找不到 python」錯誤分支的 `exit 2` 一併改掉——邏輯包進
- L15: `Invoke-Uninstall` 函式,錯誤分支印完 `Write-Error` 後 `return 2`,本檔案
- L16: 最下方把函式回傳值收進 `$rc` 再寫回 `$global:LASTEXITCODE`。這段語意同樣
- L17: 沒有真機驗證過。
- L19: ★2026-08 Task 16 修復①(BLOCKER,補 Task 15 遺漏,理由與 install.ps1 同款,
- L20: 細節見該檔案同一段註解)★:`$ErrorActionPreference = "Stop"` 會把
- L21: `Write-Error` 升級成終止型例外,讓它後面的 `return 2` 執行不到、例外炸穿
- L22: `Invoke-Uninstall`、`$global:LASTEXITCODE` 永遠寫不進去、呼叫端把失敗誤判
- L23: 成成功。改法:`Write-Error` 加 `-ErrorAction Continue` 明確覆寫。同樣沒有
- L24: 真機驗證過。
- L26: ★2026-08 Task 16 修復③(一致性處理,本檔案原本不受影響,理由與 install.ps1
- L27: 同款,細節見該檔案同一段註解)★:`$ErrorActionPreference = "Stop"` 移進
- L28: `Invoke-Uninstall` 函式內部第一行;頂層的 `$Pkg = Split-Path -Parent
- L29: $MyInvocation.MyCommand.Path` 同款理由留在函式外(避免 `$MyInvocation` 語意
- L30: 被函式 scope 改變)。
- L43: ★`| Out-Host` 不可省(2026-08-03 中文 Windows 真機驗證抓到)★:PowerShell 函式的
- L44: `return` 會帶出函式內★所有未被消費的輸出★。`&` 的 stdout 沒被指派給任何變數就
- L45: 進了輸出流,`return $LASTEXITCODE` 再追加一個數字 → 呼叫端收到的是 ★Object[]★
- L46: 而不是數字,實測 `SetShouldExit` 直接爆:
- L48: ★`$code = $LASTEXITCODE; return $code` 解決不了★——問題出在 `&` 的 stdout 進了
- L49: 輸出流,不是 return 的寫法。`| Out-Host` 讓子行程輸出直接進主機、不進 pipeline。
