# uninstall.ps1 — 薄殼:所有卸載邏輯已搬進 uninstall.py(stdlib only,Unix/
# Windows 共用同一份原始碼)。本檔案只做兩件事:①定位套件目錄(自己所在目錄)
# ②挑一支可用的 python 直譯器,把參數原樣轉發給 uninstall.py。
#
# ★誠實聲明★(與 install.ps1 同款):沒有在真機 Windows 上跑過,只有 uninstall.py
# 本體透過 `LUMOS_SLIM_SIMULATE_WINDOWS=1` 驗過分支邏輯。
#
# ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★,與
# install.ps1 同款理由,細節見該檔案同一段註解)★:收尾不再呼叫裸的 `exit`
# (避免在 `& "路徑\uninstall.ps1"` 這種呼叫鏈裡把呼叫端整個 session 關掉),
# 改把子行程 rc 寫回 `$LASTEXITCODE` 供呼叫端讀取。
#
# ★2026-08 Task 15(接續 Task 14,補殘留缺陷,與 install.ps1 同款理由)★:
# 早期「找不到 python」錯誤分支的 `exit 2` 一併改掉——邏輯包進
# `Invoke-Uninstall` 函式,錯誤分支印完 `Write-Error` 後 `return 2`,本檔案
# 最下方把函式回傳值收進 `$rc` 再寫回 `$global:LASTEXITCODE`。這段語意同樣
# 沒有真機驗證過。
#
# ★2026-08 Task 16 修復①(BLOCKER,補 Task 15 遺漏,理由與 install.ps1 同款,
# 細節見該檔案同一段註解)★:`$ErrorActionPreference = "Stop"` 會把
# `Write-Error` 升級成終止型例外,讓它後面的 `return 2` 執行不到、例外炸穿
# `Invoke-Uninstall`、`$global:LASTEXITCODE` 永遠寫不進去、呼叫端把失敗誤判
# 成成功。改法:`Write-Error` 加 `-ErrorAction Continue` 明確覆寫。同樣沒有
# 真機驗證過。
#
# ★2026-08 Task 16 修復③(一致性處理,本檔案原本不受影響,理由與 install.ps1
# 同款,細節見該檔案同一段註解)★:`$ErrorActionPreference = "Stop"` 移進
# `Invoke-Uninstall` 函式內部第一行;頂層的 `$Pkg = Split-Path -Parent
# $MyInvocation.MyCommand.Path` 同款理由留在函式外(避免 `$MyInvocation` 語意
# 被函式 scope 改變)。
function Invoke-Uninstall {
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
  & $Py.Source "$Pkg\uninstall.py" @Args | Out-Host
  return $LASTEXITCODE
}

$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path
$rc = Invoke-Uninstall -Pkg $Pkg -Args $args
$global:LASTEXITCODE = $rc
