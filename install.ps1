# install.ps1 — 薄殼:所有安裝邏輯已搬進 install.py(stdlib only,Unix/Windows
# 共用同一份原始碼)。本檔案只做兩件事:①定位套件目錄(自己所在目錄)②挑一支
# 可用的 python 直譯器,把參數原樣轉發給 install.py。
#
# 形態沿用本 repo 完整版 `get.ps1` 的先例(幾乎什麼都不做,把工作丟給 python)。
#
# ★誠實聲明★:這支腳本沒有在真機 Windows 上跑過(開發環境是 macOS,沒有
# PowerShell)——邏輯與 install.sh/install.py 對照移植而來,只驗證過
# install.py 本體透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 在非 Windows 機器上跑
# 出的分支邏輯(見 install.py 模組 docstring),這支 .ps1 薄殼本身、Windows
# PATH 的實際行為、`.cmd` shim 在真實 cmd.exe/PowerShell 下能不能被找到,都
# 沒有真機驗證過。
#
# ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★)★:
# 舊版收尾是裸的 `exit $LASTEXITCODE`——PowerShell 的 `exit` 在 README 教的
# 兩種呼叫方式(`irm ... | iex` 一行版、`& "路徑\install.ps1"` 兩行版)下都會
# 終止整個呼叫端 session,不像 bash 子行程只結束自己:使用者貼上指令、安裝其實
# 成功了,但畫面印完「裝好了」之後整個 PowerShell 視窗突然關閉,會被誤以為是
# 崩潰。改成不呼叫 `exit`,只把子行程(`install.py`)的 rc 寫回
# `$LASTEXITCODE`(PowerShell 的特殊自動變數,寫入即對呼叫端可見,呼叫端仍可
# `& install.ps1; if ($LASTEXITCODE -ne 0) {...}` 讀到正確值)——★取捨★:若
# 是用 `powershell.exe -File install.ps1` 這種「當成獨立行程啟動」的方式呼叫
# (README 沒教這種呼叫法),因為腳本本身不再呼叫 `exit`,回給作業系統的行程
# exit code 會固定是 0,不會反映失敗;README 教的兩種呼叫方式都是在同一個
# session 內執行(不是啟動新行程),不受此取捨影響。
#
# ★2026-08 Task 15(接續 Task 14,補殘留缺陷)★:Task 14 只修了「結尾」那個
# `exit $LASTEXITCODE`,早期「找不到 python」錯誤分支的 `exit 2` 沒有一併改
# ——這處反而更該修,因為它在錯誤路徑上,使用者最需要看到錯誤訊息的時候
# 視窗反而被關掉,連錯在哪都來不及讀。改法:把整段邏輯包進 `Invoke-Install`
# 函式,錯誤分支印完 `Write-Error` 後 `return 2`(函式層級的 `return`,不是
# `exit`——只結束這支函式,不終止呼叫端 session);本檔案最下方把函式回傳值
# 收進 `$rc` 再寫回 `$global:LASTEXITCODE`,沿用 Task 14 選定的慣例。這段
# 語意同樣沒有真機驗證過,見上方「★誠實聲明★」與 `slim/README.md`〈支援
# 平台〉。
#
# ★2026-08 Task 16 修復①(BLOCKER,補 Task 15 遺漏)★:`$ErrorActionPreference
# = "Stop"` 會把 `Write-Error` 這種非終止型錯誤升級成終止型例外(等同
# `throw`)——Task 15 只驗了「Write-Error 後面緊接著 return 2」這個原始碼長相,
# 完全沒注意到 `Stop` 之下 `Write-Error` 那行自己就會先拋例外,`return 2` 根本
# 執行不到、例外炸穿呼叫端、`$rc = Invoke-Install ...` 那行也完成不了,最終
# `$global:LASTEXITCODE = $rc` 永遠不執行——呼叫端讀到的是殘留舊值(很可能是
# 0),把失敗誤判成成功。改法:每一處 `Write-Error` 都加 `-ErrorAction
# Continue` 明確覆寫(而不是拆 try/catch 或改用 `[Console]::Error`)——理由:
# ①這是 PowerShell 官方支援的逐次呼叫覆寫機制,語意上最直接對應「這個
# 錯誤訊息我要它保持非終止型」這句意圖 ②維持「Write-Error 後緊接著 return」
# 這個既有結構,不需要重新設計成 try/catch 包住整段函式 ③訊息仍然真的走
# Write-Error(進 stderr、保留 PowerShell 錯誤記錄的語意),不是換一套機制
# 把訊息換個管道印出。★這段修法同樣沒有真機驗證過★——見 `t_slim_ps1_
# write_error_noterminating_under_stop_preference` 的誠實邊界說明:靜態測試
# 只能驗「有沒有 -ErrorAction Continue」這個寫法,驗不到 PowerShell 真實執行
# 時 Stop 語意是否真的被這個參數蓋掉。
#
# ★2026-08 Task 16 修復③(一致性處理,本檔案原本不受影響)★:`$ErrorAction
# Preference = "Stop"` 移進 `Invoke-Install` 函式內部第一行(原本在頂層)。
# 本檔案是經 `& "路徑\install.ps1"` 呼叫,PowerShell 對指令碼檔案呼叫本來就會
# 建立獨立的 script scope,原本寫在頂層就不會污染呼叫端 session(不像
# `get.ps1` 被 `irm ... | iex` 直接在呼叫端 scope 執行、細節見該檔案同一段
# 註解)——這裡搬進函式純粹是三支檔案寫法一致,不是修一個真的缺陷。
# ★頂層的 `$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path` 刻意留在
# 函式外★:`$MyInvocation` 在函式內部會變成指向函式自己的呼叫資訊,不是整支
# 腳本的,搬進函式會改變 `.MyCommand.Path` 的語意(定位套件目錄的邏輯會壞掉)
# ——只有 `$ErrorActionPreference` 這行單純賦值、不依賴 `$MyInvocation`,才
# 搬得動。
function Invoke-Install {
  param($Pkg, $Args)

  $ErrorActionPreference = "Stop"

  $Py = Get-Command python3 -ErrorAction SilentlyContinue
  if (-not $Py) { $Py = Get-Command python -ErrorAction SilentlyContinue }
  if (-not $Py) {
    Write-Error "ERROR: 找不到 python3 或 python 指令——請先安裝 Python 3 再重跑本腳本。" -ErrorAction Continue
    return 2
  }

  # ★`| Out-Host` 不可省(2026-08-03 中文 Windows 真機驗證抓到)★:PowerShell 函式的
  # `return` 會帶出函式內★所有未被消費的輸出★。`&` 的 stdout 沒被指派給任何變數就
  # 進了輸出流,`return $LASTEXITCODE` 再追加一個數字 → 呼叫端收到的是 ★Object[]★
  # 而不是數字,實測 `SetShouldExit` 直接爆:
  #   Cannot convert argument "exitCode", with value: "System.Object[]" ... to "System.Int32"
  # ★`$code = $LASTEXITCODE; return $code` 解決不了★——問題出在 `&` 的 stdout 進了
  # 輸出流,不是 return 的寫法。`| Out-Host` 讓子行程輸出直接進主機、不進 pipeline。
  & $Py.Source "$Pkg\install.py" @Args | Out-Host
  return $LASTEXITCODE
}

$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path
$rc = Invoke-Install -Pkg $Pkg -Args $args
$global:LASTEXITCODE = $rc
