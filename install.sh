#!/usr/bin/env bash
# install.sh — 薄殼:所有安裝邏輯已搬進 install.py(stdlib only,Unix/Windows
# 共用同一份原始碼,不再有兩份互相漂移的實作)。本檔案只做兩件事:①解析 $0
# 的 symlink 鏈以定位套件目錄(PKG)②挑一支可用的 python 直譯器,把參數原樣
# 轉發給 "${PKG}/install.py"。
set -eu

# 解析 $0 的 symlink 鏈(macOS 無 `readlink -f`,手捲迴圈逐層解;POSIX `readlink`
# 每次只吐一層目標,相對路徑目標要接回所在目錄再繼續判是否還是 symlink)。
# ★為什麼薄殼仍需要這段★:install.py 用 `Path(__file__).resolve()` 定位自己
# 沒問題,但那是 python 直譯器收到的路徑之後的事——這裡要先把「正確的
# install.py 絕對路徑」算出來、傳給 python,前提是先解開 install.sh 自己可能
# 身處的 symlink 鏈。
# 取路徑的目錄部分。★不呼叫外部 `dirname`★——這支薄殼是要在別人機器上跑的,
# PATH 被縮到很小時(容器最小映像、CI 的乾淨 shell、或使用者自己設過 PATH)
# 外部工具不保證在;純 bash 參數展開零依賴。2026-08-01 本 repo 的測試閘就是
# 因為 `dirname` 不在測試組出來的最小 PATH 上而紅,見
# Issues/prepush測試閘假紅-git環境洩漏。
_dirof() {
  case "$1" in
    */*) d="${1%/*}"; [ -n "$d" ] || d="/"; printf '%s\n' "$d" ;;
    *)   printf '%s\n' "." ;;
  esac
}

SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$(cd "$(_dirof "$SOURCE")" && pwd)"
  LINK="$(readlink "$SOURCE")"
  case "$LINK" in
    /*) SOURCE="$LINK" ;;
    *)  SOURCE="${DIR}/${LINK}" ;;
  esac
done
PKG="$(cd "$(_dirof "$SOURCE")" && pwd)"

# Windows 常只裝了 `python`(無 `python3` 別名),Unix 系統慣例反過來——兩者
# 都試,都沒有就給清楚錯誤訊息(不是讓後面的呼叫用 command-not-found 的方式炸)。
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    PY="$cand"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: 找不到 python3 或 python 指令——請先安裝 Python 3 再重跑本腳本。" >&2
  exit 2
fi

exec "$PY" "${PKG}/install.py" "$@"
