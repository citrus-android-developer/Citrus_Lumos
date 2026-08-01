#!/usr/bin/env bash
# uninstall.sh — 薄殼:所有卸載邏輯已搬進 uninstall.py(stdlib only,Unix/
# Windows 共用同一份原始碼)。本檔案只做兩件事:①解析 $0 的 symlink 鏈以定位
# 套件目錄(PKG,與 install.sh 同款理由)②挑一支可用的 python 直譯器,把參數
# 原樣轉發給 "${PKG}/uninstall.py"。
#
# 用法(裝好之後,兩種都可):
#   ~/.lumos-slim/uninstall.sh
#   curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/uninstall.sh | bash
set -eu

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

exec "$PY" "${PKG}/uninstall.py" "$@"
