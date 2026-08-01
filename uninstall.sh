#!/usr/bin/env bash
# uninstall.sh — 公開精簡版 一行卸載
#
# 用法(裝好之後,兩種都可):
#   ~/.lumos-slim/uninstall.sh
#   curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/uninstall.sh | bash
#
# ★安全紀律是這支腳本的重點,比功能重要★——每一步都先判斷「這真的是我們裝的
# 東西嗎」,不確定就拒絕動、印清楚訊息,絕不用猜的去刪使用者的東西。
#
# ★絕不碰★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、
#          除了 lumos-project-notes 以外的任何 skill。
# ★唯一例外(★2026-07-31 使用者裁定第三次變更,與 install.sh 對稱★)★:執行
#          目錄下 CLAUDE.md 裡 `<!-- LUMOS-SLIM:START/END -->` sentinel 之間
#          的那一塊——找到就移除,並讀取區塊內建的 FULL-BACKUP 標記:若有
#          (代表 install.sh 當初取代掉了完整版 `LUMOS:GRAPH-DISCIPLINE` 區
#          塊),則位元組級還原該區塊原文回原位置;若無(當初本來就沒有完整版
#          區塊),單純移除精簡版區塊。sentinel(與還原的完整版區塊)以外的
#          內容一個位元組都不動;若移除後檔案變空,連同檔案本身一併刪除(還
#          原成「本來就沒這個檔案」的狀態)。
#
# ★2026-07-31 端到端實測抓到的真 bug,本次修的核心★:舊版把 bin 的 sha256
# 比對(拿 ~/.lumos-slim/scripts/lumos 當基準)當一票否決——`~/.lumos-slim`
# 只有走 get.sh(一行安裝)才會存在;README 也在教的另一條路(直接 clone 後
# 跑包內 install.sh)不會建立這個固定落點,bin 比對「找不到基準」就直接
# `exit 2`,CLAUDE.md 的還原(步驟④,見下方)完全沒機會執行——接手者從此卸
# 載不掉,而且舊訊息說「這可能是你自己的東西」在這個情境下是**誤導**(其實
# 就是本包裝的,只是找不到比對基準)。
#
# ★修法,兩件事★:
#  ①身分證 manifest —— install.sh 現在會在 ~/.local/share/lumos-slim/
#    manifest.json 記一份安裝當下的 bin sha256(見 install.sh ①b)。這是
#    ★比對的主要來源★,不依賴 ~/.lumos-slim 存不存在。找不到 manifest 時,
#    仍保留舊版「拿 ~/.lumos-slim/scripts/lumos 當基準」的比對法當備援(相容
#    早期(這次修之前)裝的、還沒有 manifest 的機器)。
#  ②四個清理步驟(bin／skill 目錄／~/.lumos-slim／CLAUDE.md 區塊)★各自獨立
#    判斷、各自執行、互不阻擋★——不再用 `exit` 讓某一步的安全考量中止其餘
#    步驟。全部跑完才彙總報告、決定 rc(語意見下方,比照 `lumos doctor --ci`
#    的三段式慣例)。
#
# rc 語意(彙總後決定,不是任一步驟直接 exit):
#   0 = 每一步都「完成」或「本來就沒裝/沒有這塊」(乾淨卸載,含冪等 no-op)
#   1 = 至少一步基於安全考量主動跳過(例如 bin 內容比對不符、或連比對基準都
#       找不到、或 ~/.lumos-slim 存在但內容不像本包)——這是「需要你注意」,
#       不是程式壞掉;確定要處理就重跑加 --force。
#   2 = 真正的錯誤(找不到 sha256sum/shasum、CLAUDE.md 有多個 sentinel 狀態
#       不明確、FULL-BACKUP 標記 base64/utf-8 解碼失敗……這些不是「安全性
#       跳過」,是腳本判斷不出下一步該怎麼做,需要手動處理)。
set -u

BIN="${HOME}/.local/bin/lumos"
SKILL="${HOME}/.claude/skills/lumos-project-notes"
PKG="${HOME}/.lumos-slim"
MANIFEST="${HOME}/.local/share/lumos-slim/manifest.json"

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

RC=0
_bump() { [ "$1" -gt "$RC" ] && RC="$1"; }

_sha256() {
  # macOS 常見 shasum、Linux 常見 sha256sum——挑存在的那支;兩者都沒有就回傳
  # 非 0(呼叫端自行決定怎麼處理,不在這裡直接中止整支腳本)。
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    return 1
  fi
}

_manifest_bin_sha256() {
  # 讀 install.sh 寫的 manifest.json 裡的 bin_sha256——沒有 manifest、或欄位
  # 是空字串,一律當「manifest 給不出參照」處理(呼叫端會退回 PKG 備援)。
  [ -f "$MANIFEST" ] || return 1
  python3 -c '
import json
import sys

try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    sys.exit(1)
v = data.get("bin_sha256", "")
if not v:
    sys.exit(1)
print(v)
' "$MANIFEST"
}

echo "== 公開精簡版卸載 =="

# ① ~/.local/bin/lumos —— ★只在它確實是我們裝的那份時才移除★
#    判斷方式:優先用 install.sh 寫的 manifest(不依賴 ~/.lumos-slim 存在);
#    manifest 給不出參照時,退回舊版做法(拿 ~/.lumos-slim/scripts/lumos 當
#    基準,相容這次修之前裝的機器)。★兩種「不移除」要分清楚★:完全找不到
#    任何比對基準(基準缺失)、跟找到基準但內容比對不符(內容真的不符)——
#    對使用者的意義不一樣,訊息分開講,不能都說成「這可能是你自己的東西」。
if [ -e "$BIN" ] || [ -L "$BIN" ]; then
  if [ "$FORCE" -eq 1 ]; then
    rm -f "$BIN"
    echo "✓ 已移除(--force,跳過內容比對): ${BIN}"
  elif ! CUR_SHA="$(_sha256 "$BIN")"; then
    echo "⚠ 找不到 sha256sum 或 shasum,無法安全比對內容——跳過移除 ${BIN}。" >&2
    echo "  確定要砍就加 --force 重跑:$0 --force" >&2
    _bump 2
  else
    REF_SHA=""
    REF_DESC=""
    if REF_SHA="$(_manifest_bin_sha256 2>/dev/null)"; then
      REF_DESC="安裝時記錄的 manifest(${MANIFEST})"
    elif [ -f "${PKG}/scripts/lumos" ] && REF_SHA="$(_sha256 "${PKG}/scripts/lumos" 2>/dev/null)"; then
      REF_DESC="${PKG}/scripts/lumos(無 manifest 時的備援比對,相容較舊安裝)"
    fi
    if [ -z "$REF_SHA" ]; then
      echo "⚠ 找不到任何比對基準——manifest(${MANIFEST})與 ${PKG}/scripts/lumos 都不存在。" >&2
      echo "  這是「基準缺失」,不是內容比對出不符;沒有基準就無法安全判斷 ${BIN}" >&2
      echo "  是不是本包裝的那份,拒絕移除。確定要砍就加 --force 重跑:$0 --force" >&2
      _bump 1
    elif [ "$CUR_SHA" = "$REF_SHA" ]; then
      rm -f "$BIN"
      echo "✓ 已移除: ${BIN}"
    else
      echo "⚠ ${BIN} 內容與比對基準(${REF_DESC})不一致——這是「內容真的不符」,不是基準缺失。" >&2
      echo "  這可能是你自己的東西,不是本包裝的那份 lumos——拒絕移除。" >&2
      echo "  確定要砍就加 --force 重跑:$0 --force" >&2
      _bump 1
    fi
  fi
else
  echo "  (未安裝: ${BIN})"
fi

# ② skill 目錄 —— ★移除前先備份,不直接 rm -rf★(使用者可能在裡面塞過自己的
#    檔)。★與①獨立★:①的比對結果(移除/跳過/錯誤)不影響這一步是否執行。
if [ -d "$SKILL" ]; then
  BAK="${SKILL}.bak.$(date +%Y%m%d%H%M%S)"
  if mv "$SKILL" "$BAK" 2>/dev/null; then
    echo "✓ 已備份並移除: ${SKILL} → ${BAK}"
  else
    echo "⚠ 備份/移除 ${SKILL} 失敗——保留,不動。" >&2
    _bump 2
  fi
else
  echo "  (未安裝: ${SKILL})"
fi

# ③ ~/.lumos-slim —— 可移除,但同樣先確認它長得像我們的包才刪。★與①②獨立★。
if [ -d "$PKG" ]; then
  if [ -f "$PKG/scripts/lumos" ] && [ -f "$PKG/install.sh" ]; then
    if rm -rf "$PKG" 2>/dev/null; then
      echo "✓ 已移除: ${PKG}"
    else
      echo "⚠ 移除 ${PKG} 失敗。" >&2
      _bump 2
    fi
  else
    echo "⚠ ${PKG} 存在,但內容不像本包(缺 scripts/lumos 或 install.sh)——保留,不動。" >&2
    _bump 1
  fi
else
  echo "  (未安裝: ${PKG})"
fi

# ④ 執行目錄下 CLAUDE.md 的 LUMOS-SLIM sentinel 區塊 —— 與 install.sh 對稱
#    的移除/還原:找不到 sentinel 就當「本來就沒裝」放行(冪等);找到就讀出
#    區塊內建的 FULL-BACKUP 標記——有備份(BASE64)就位元組級還原完整版區塊
#    回原位置,沒有(NONE)就單純移除這塊;其餘內容原封不動;移除/還原完若
#    整個檔案變空,連檔案一起刪掉,回到「原本沒有這個檔案」的狀態。
#    ★這是本次修的重點步驟★:不管①②③的結果如何,這一步永遠會跑——bin 的
#    安全檢查失敗絕不該擋住這裡。
CLAUDE_MD="$(pwd)/CLAUDE.md"
CLAUDE_OUT="$(python3 - "$CLAUDE_MD" <<'LUMOS_SLIM_UNINST_PY_EOF'
import base64
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])
SLIM_START = "<!-- LUMOS-SLIM:START -->"
SLIM_END = "<!-- LUMOS-SLIM:END -->"
BACKUP_RE = re.compile(r"<!-- LUMOS-SLIM:FULL-BACKUP:(NONE|BASE64:[A-Za-z0-9+/=]*) -->")

if not target.exists():
    print(f"  (未安裝: {target} 的 LUMOS-SLIM 圖譜標籤區塊 — 檔案不存在)")
    sys.exit(0)

current = target.read_text(encoding="utf-8")
pattern = re.compile(re.escape(SLIM_START) + r".*?" + re.escape(SLIM_END) + r"\n?", re.DOTALL)
matches = list(pattern.finditer(current))

if not matches:
    print(f"  (未安裝: {target} 的 LUMOS-SLIM 圖譜標籤區塊)")
    sys.exit(0)

if len(matches) > 1:
    print(f"⚠ {target} 內有多個 LUMOS-SLIM sentinel 區塊,拒絕自動移除"
          "——請手動清理。", file=sys.stderr)
    sys.exit(2)

m = matches[0]
block = m.group(0)
bm = BACKUP_RE.search(block)

restore_text = ""
if bm and bm.group(1) != "NONE":
    encoded = bm.group(1)[len("BASE64:"):]
    try:
        restore_text = base64.b64decode(encoded).decode("utf-8")
    except Exception as e:
        print(f"ERROR: 完整版區塊備份還原失敗(base64/utf-8 解碼錯誤): {e}"
              "——拒絕破壞性移除,請手動處理。", file=sys.stderr)
        sys.exit(2)

new = current[:m.start()] + restore_text + current[m.end():]

if new == "":
    target.unlink()
    print(f"✓ 已移除: {target} 的 LUMOS-SLIM 圖譜標籤區塊(內容變空,檔案本身一併移除)")
elif restore_text:
    target.write_text(new, encoding="utf-8")
    print(f"✓ 已還原: {target} 的完整版紀律區塊(位元組級還原自內建備份),LUMOS-SLIM 區塊已移除")
else:
    target.write_text(new, encoding="utf-8")
    print(f"✓ 已移除: {target} 的 LUMOS-SLIM 圖譜標籤區塊(其餘內容不變)")
LUMOS_SLIM_UNINST_PY_EOF
)"
CLAUDE_RC=$?
echo "$CLAUDE_OUT"
[ "$CLAUDE_RC" -ne 0 ] && _bump 2

echo
echo "== 卸載彙總 =="
case "$RC" in
  0) echo "✓ 全部完成(或本來就沒裝)。" ;;
  1) echo "⚠ 部分項目基於安全考量主動跳過,理由見上面——確定要處理就重跑加 --force。" ;;
  2) echo "✗ 有真正的錯誤(非安全性跳過),理由見上面——需要手動處理。" ;;
esac
echo "★未動★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、其他 skill;"
echo "        CLAUDE.md 除了上面那塊 LUMOS-SLIM sentinel 區塊(及它取代掉的完整版"
echo "        區塊,若有 — 已還原),其餘內容原封不動。"

exit "$RC"
