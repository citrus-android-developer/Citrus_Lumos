#!/usr/bin/env bash
# get.sh — 公開精簡版 一行安裝入口
#
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.sh | bash
#   # 帶參數轉給 install.sh(如 --force):
#   curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.sh | bash -s -- --force
#
# 只做兩件事:
#   ① 把交付包 clone(首次)或更新(已存在時 git pull)到固定落點 ~/.lumos-slim
#   ② 執行包內的 install.sh(它只動 $HOME,細節見該腳本開頭註解)——把任何額外
#     參數(如 --force)原樣轉給它
#
# ★為什麼要固定落點★:install.sh 用 `$(dirname "$0")` 定位包自身——透過
# `curl | bash` 執行時 `$0` 是 bash/`/dev/stdin`,沒有穩定的檔案位置可定位;
# 而且使用者若把包搬走/刪掉,全域指令就斷了。固定落點給它一個穩定的家,也讓
# uninstall.sh 有地方可以拿真值(sha256 比對)判斷 ~/.local/bin/lumos 是不是
# 我們裝的那份。
#
# ★冪等★:~/.lumos-slim 已存在且是合法 git repo → git pull 更新,不重新 clone
# (git clone 對非空目錄會報錯,不是「冪等」是「爆炸」)。已存在但不像我們的東西
# (沒有 .git)→ 拒絕動它、印清楚訊息,不猜測、不覆寫。
set -eu

REPO_URL="${LUMOS_SLIM_REPO_URL:-https://github.com/citrus-android-developer/Citrus_Lumos.git}"
DEST="${HOME}/.lumos-slim"

command -v git >/dev/null 2>&1 || {
  echo "ERROR: 找不到 git 指令——請先安裝 git 再重跑這支腳本。" >&2
  echo "  macOS: xcode-select --install" >&2
  echo "  Debian/Ubuntu: sudo apt install git" >&2
  exit 2
}

if [ -d "${DEST}/.git" ]; then
  echo "已存在 ${DEST},更新到最新版..."
  if ! git -C "$DEST" pull --ff-only -q; then
    echo "ERROR: ${DEST} 更新失敗(可能有本地改動,或不是 fast-forward)。" >&2
    echo "  若你動過裡面的檔案,確認沒有要留的東西後備份/刪掉 ${DEST} 再重跑本腳本。" >&2
    exit 2
  fi
elif [ -e "${DEST}" ]; then
  echo "ERROR: ${DEST} 已存在,但不是本包的 git clone(找不到 ${DEST}/.git)。" >&2
  echo "  為避免誤刪你自己的東西,不會自動覆寫——請自行確認該目錄內容後處理。" >&2
  exit 2
else
  echo "首次安裝,clone 到 ${DEST}..."
  git clone -q "$REPO_URL" "$DEST"
fi

[ -f "${DEST}/install.sh" ] || {
  echo "ERROR: ${DEST}/install.sh 不存在——交付包內容可能不完整。" >&2
  exit 2
}

bash "${DEST}/install.sh" "$@"
