# get.ps1 — 公開精簡版 一行安裝入口(Windows/PowerShell)
#
# 用法:
#   irm https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.ps1 | iex
#
# 邏輯與 get.sh 對稱(逐步翻譯,不是重新設計):
#   ① 把交付包 clone(首次)或更新(已存在時 git pull)到固定落點 ~\.lumos-slim
#   ② 執行套件內的 install.ps1(它只轉發給 install.py,細節見該檔案開頭註解)
#
# ★為什麼要固定落點★:跟 get.sh 同款理由——`irm ... | iex` 執行時沒有穩定的
# 檔案位置可定位自己,且使用者若把套件搬走/刪掉,全域指令就斷了。固定落點也讓
# uninstall.py 有地方可以拿真值(sha256 比對)判斷 `~\.local\bin\lumos` 是不是
# 我們裝的那份(見 install.py 的身分證 manifest 說明——manifest 是主要比對來源,
# 這個固定落點只是找不到 manifest 時的備援)。
#
# ★冪等★:~\.lumos-slim 已存在且是合法 git repo → git pull 更新,不重新 clone。
# 已存在但不像我們的東西(沒有 .git)→ 拒絕動它、印清楚訊息,不猜測、不覆寫。
#
# ★誠實聲明★:沒有在真機 Windows 上跑過(開發環境是 macOS,沒有 PowerShell/
# git-for-Windows 可用)——邏輯照 get.sh 逐步翻譯,git clone/pull 的參數與
# get.sh 相同,但這支腳本本身、`irm | iex` 這種執行方式在真實 Windows 上的行為
# 都沒有真機驗證過。
#
# ★2026-08 Task 14 修復③(保險性修法,★這段語意本身也沒有真機驗證過★,與
# install.ps1 同款理由,細節見該檔案同一段註解)★:收尾不再呼叫裸的 `exit`
# ——`get.ps1` 正是 README 一行版 `irm ... | iex` 直接執行的那支腳本,`exit`
# 在這種呼叫方式下最容易把使用者當下開著的 PowerShell 視窗整個關掉;改把
# `install.ps1` 的 rc 寫回 `$LASTEXITCODE` 供呼叫端讀取。
#
# ★2026-08 Task 15(接續 Task 14,補殘留缺陷,與 install.ps1 同款理由)★:
# 這支檔案早期還有 4 處錯誤分支的 `exit 2`(找不到 git、pull 失敗、目的地已
# 存在但不是我們的 clone、交付包內容不完整)沒有一併改掉,而 `get.ps1` 正是
# `irm ... | iex` 一行版直接執行的腳本,踩到的機率最高。改法:整段邏輯包進
# `Invoke-Get` 函式,每個錯誤分支印完 `Write-Error` 後 `return 2`(函式層級
# 的 `return`,不是 `exit`——只結束這支函式,不終止呼叫端 session,也保證
# 該分支之後真正的 clone/安裝動作不會被跑到);本檔案最下方把函式回傳值收進
# `$rc` 再寫回 `$global:LASTEXITCODE`。這段語意同樣沒有真機驗證過。
#
# ★2026-08 Task 16 修復①(BLOCKER,補 Task 15 遺漏,理由與 install.ps1 同款,
# 細節見該檔案同一段註解)★:`$ErrorActionPreference = "Stop"` 會把
# `Write-Error` 升級成終止型例外,讓它後面的 `return 2` 執行不到、例外炸穿
# `Invoke-Get`、`$global:LASTEXITCODE` 永遠寫不進去、呼叫端把失敗誤判成成功
# ——`get.ps1` 正是 `irm ... | iex` 一行版直接執行的腳本,踩到的機率最高。
# 改法:4 處 `Write-Error` 都加 `-ErrorAction Continue` 明確覆寫。同樣沒有
# 真機驗證過。
#
# ★2026-08 Task 16 修復③★:`$ErrorActionPreference = "Stop"` 若寫在頂層(不在
# 函式裡面),會污染呼叫端 session——README 教的一行安裝是 `irm ... | iex`,
# `iex` 是在**呼叫端當下的 scope** 執行(不像 `& "path.ps1"` 會建新 script
# scope),使用者跑完一行安裝後,同一個視窗裡任何原本靠非終止型錯誤運作的
# 後續指令都會被意外中止,而且裝完不會自動還原,使用者也不會知道原因是
# 「剛剛裝了個東西」。改法:把這行賦值移進 `Invoke-Get` 函式內部第一行——
# PowerShell 函式預設有自己的子 scope,函式內對變數賦值(沒加 `$global:`/
# `$script:` 前綴)只落在函式自己的 local scope,不會外溢回呼叫端;`Invoke-Get`
# 這個函式本體已經涵蓋了本檔案所有會用到非終止型錯誤語意的邏輯(git 指令、
# clone/pull),搬進去不影響行為,只是把賦值的可見範圍收窄。`install.ps1`／
# `uninstall.ps1` 因為經 `&` 呼叫、本來就有自己的 script scope,不受這個污染
# 問題影響,但一併搬進函式維持三支檔案寫法一致。這段 scope 語意同樣沒有真機
# 驗證過(這台機器沒有 PowerShell)。
function Invoke-Get {
  param($RepoUrl, $Dest, $Args)

  $ErrorActionPreference = "Stop"

  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: 找不到 git 指令——請先安裝 git 再重跑這支腳本(https://git-scm.com/download/win)。" -ErrorAction Continue
    return 2
  }

  if (Test-Path (Join-Path $Dest ".git")) {
    Write-Host "已存在 $Dest,更新到最新版..."
    git -C $Dest pull --ff-only -q
    if ($LASTEXITCODE -ne 0) {
      Write-Error "ERROR: $Dest 更新失敗(可能有本地改動,或不是 fast-forward)。若你動過裡面的檔案,確認沒有要留的東西後備份/刪掉 $Dest 再重跑本腳本。" -ErrorAction Continue
      return 2
    }
  } elseif (Test-Path $Dest) {
    Write-Error "ERROR: $Dest 已存在,但不是本包的 git clone(找不到 $Dest\.git)。為避免誤刪你自己的東西,不會自動覆寫——請自行確認該目錄內容後處理。" -ErrorAction Continue
    return 2
  } else {
    Write-Host "首次安裝,clone 到 $Dest..."
    git clone -q $RepoUrl $Dest
    # ★這道檢查以前漏了(2026-08-02 補)★:同一個函式裡 `git pull`
    # 那一支有檢 `$LASTEXITCODE`、`git clone` 這一支沒有,純粹是漏寫。
    # ★不能靠 `$ErrorActionPreference = "Stop"` 兜底★——它只管 PowerShell 自己
    # 的 cmdlet 錯誤,原生執行檔(git.exe)回非零 exit code ★不會★ 觸發終止
    # (PS 7.3 起才有 `$PSNativeCommandUseErrorActionPreference` 可改這行為,
    # 本腳本要支援更舊的 Windows PowerShell 5.1,不能依賴)。
    # 漏掉的後果:clone 失敗(沒網路/私有 repo 沒權限/磁碟滿)後照樣往下走,
    # 使用者看到的是下一段那句「交付包內容可能不完整」——把網路/權限問題
    # 誤導成「這個包壞掉了」,查錯方向完全被帶偏。
    if ($LASTEXITCODE -ne 0) {
      Write-Error "ERROR: clone $RepoUrl 失敗(檢查網路連線,以及你有沒有這個 repo 的存取權限)。" -ErrorAction Continue
      return 2
    }
  }

  $InstallScript = Join-Path $Dest "install.ps1"
  if (-not (Test-Path $InstallScript)) {
    Write-Error "ERROR: $InstallScript 不存在——交付包內容可能不完整。" -ErrorAction Continue
    return 2
  }

  # ★`| Out-Host` 不可省(2026-08-03 中文 Windows 真機驗證抓到)★:PowerShell 函式的
  # `return` 會帶出函式內★所有未被消費的輸出★。`&` 的 stdout 沒被指派給任何變數就
  # 進了輸出流,`return $LASTEXITCODE` 再追加一個數字 → 呼叫端收到的是 ★Object[]★
  # 而不是數字,實測 `SetShouldExit` 直接爆:
  #   Cannot convert argument "exitCode", with value: "System.Object[]" ... to "System.Int32"
  # ★`$code = $LASTEXITCODE; return $code` 解決不了★——問題出在 `&` 的 stdout 進了
  # 輸出流,不是 return 的寫法。`| Out-Host` 讓子行程輸出直接進主機、不進 pipeline。
  & $InstallScript @Args | Out-Host
  return $LASTEXITCODE
}

$RepoUrl = if ($env:LUMOS_SLIM_REPO_URL) { $env:LUMOS_SLIM_REPO_URL } else { "https://github.com/citrus-android-developer/Citrus_Lumos.git" }
$Dest = Join-Path $HOME ".lumos-slim"

$rc = Invoke-Get -RepoUrl $RepoUrl -Dest $Dest -Args $args
$global:LASTEXITCODE = $rc
