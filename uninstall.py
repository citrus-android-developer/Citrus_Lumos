#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""uninstall.py — 公開精簡版 卸載器(stdlib only,Windows 可跑)

★這是唯一的卸載邏輯來源★——`uninstall.sh`／`uninstall.ps1` 都只是薄殼轉發參數,
真正的行為全在這支檔案(與 `install.py` 對稱,理由同它的 docstring)。

★安全紀律是這支腳本的重點,比功能重要★——每一步都先判斷「這真的是我們裝的
東西嗎」,不確定就拒絕動、印清楚訊息,絕不用猜的去刪使用者的東西。

★絕不碰★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、除了
         lumos-project-notes 以外的任何 skill。
★唯一例外★:執行目錄下 CLAUDE.md 裡 `<!-- LUMOS-SLIM:START/END -->` sentinel
         之間的那一塊——找到就移除,並讀取區塊內建的 FULL-BACKUP 標記:若有
         (代表 install.py 當初取代掉了完整版 `LUMOS:GRAPH-DISCIPLINE` 區塊),
         則位元組級還原該區塊原文回原位置;若無,單純移除精簡版區塊。
         sentinel(與還原的完整版區塊)以外的內容一個位元組都不動;若移除後
         檔案變空,連同檔案本身一併刪除(還原成「本來就沒這個檔案」的狀態)。

★歷史真 bug,搬過來時原樣保留修法(不是這次順手改的)★:舊版 bash 曾把 bin 的
sha256 比對(拿 ~/.lumos-slim/scripts/lumos 當基準)當一票否決——`~/.lumos-slim`
只有走 get.sh/get.ps1(一行安裝)才會存在;README 也在教的另一條路(直接 clone
後跑包內 install.sh/install.py)不會建立這個固定落點,比對「找不到基準」就直接
中止,CLAUDE.md 的還原(步驟④)完全沒機會執行。修法兩件事:①身分證 manifest
(`~/.local/share/lumos-slim/manifest.json`,install.py 裝機時寫)是★比對的
主要來源★,不依賴 `~/.lumos-slim` 存不存在;找不到時才退回舊版做法(拿
`~/.lumos-slim/scripts/lumos` 當基準,相容早期裝的機器)②清理步驟
(bin／skill 目錄／`~/.lumos-slim`／CLAUDE.md 區塊／manifest 本身)★各自獨立判斷、
各自執行、互不阻擋★——不用 return/exit 讓某一步的安全考量中止其餘步驟。

★2026-08-01 真跑冒煙補的第⑤步:manifest 自己也要清掉★——在此之前,卸載跑完
會在 `~/.local/share/lumos-slim/` 底下留著 manifest.json,彙總卻印「✓ 全部完成」。
整套測試全綠也看不到,因為根本沒有任何一條測試斷言過卸載後它該消失(不是斷言
寫錯,是「沒去驗」)。★唯一的資料相依(不是控制相依,不違反上面那條獨立性)★:
①/①b 有任何一份 bin 檔案基於安全考量沒被移除時,manifest 必須留著——它是使用者
之後加 `--force` 或手動確認時唯一的比對基準,先刪掉等於銷毀判斷依據,下次重跑
只會落到「基準缺失」。留著時印一句為什麼留。

rc 語意(彙總後決定,不是任一步驟直接中止):
  0 = 每一步都「完成」或「本來就沒裝/沒有這塊」(乾淨卸載,含冪等 no-op)
  1 = 至少一步基於安全考量主動跳過(例如 bin 內容比對不符、或連比對基準都
      找不到、或 ~/.lumos-slim 存在但內容不像本包)——這是「需要你注意」,
      不是程式壞掉;確定要處理就重跑加 --force。
  2 = 真正的錯誤(CLAUDE.md 有多個 sentinel 狀態不明確、FULL-BACKUP 標記
      base64/utf-8 解碼失敗、備份/刪除操作本身失敗……)這些不是「安全性跳過」,
      是腳本判斷不出下一步該怎麼做或操作本身失敗,需要手動處理。
      ★移植到 Python 順帶消掉一種錯誤★:舊版 bash 有「找不到 sha256sum/
      shasum 這兩支外部工具」的失敗分支——Python 的 `hashlib` 是標準庫,永遠
      存在,這個失敗模式在本版不會發生,故未保留對應分支(無測試依賴它)。

★Windows 支援★:全域指令在 Windows 上是一對檔案(`lumos.cmd` shim +
`lumos` 內容副本,見 `install.py` 的 `_install_cli` 說明),兩者總是成對安裝/
移除——manifest 的 bin_sha256 記的是 `lumos`(內容副本)的雜湊,跟 Unix 版
語意一致,拿它比對即可判斷這對檔案是不是本包裝的,兩個檔案一起處理。
★這台機器沒有 Windows,無法做真機驗證★——與 install.py 同款誠實聲明,見它的
docstring 結尾與 `slim/README.md`。
"""
import base64
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import time
from pathlib import Path

IS_WIN = (os.name == "nt") or (os.environ.get("LUMOS_SLIM_SIMULATE_WINDOWS") == "1")

SLIM_START = "<!-- LUMOS-SLIM:START -->"
SLIM_END = "<!-- LUMOS-SLIM:END -->"
BACKUP_RE = re.compile(r"<!-- LUMOS-SLIM:FULL-BACKUP:(NONE|BASE64:[A-Za-z0-9+/=]*) -->")

# ★2026-08 Task 16 修復②★:`lumos.cmd` shim 的固定樣板,與 install.py
# `_install_cli()` 產生的 `shim_text = f'@echo off\r\n{py_cmd} "%~dp0lumos" %*\r\n'`
# 一一對應——`py_cmd` 只會是 `python3` 或 `python`(見 `_pick_windows_interpreter()`
# 候選清單)。沒有 manifest 雜湊可比對 shim 本身時,拿這個樣板當安全判斷基準。
SHIM_TEXT_RE = re.compile(r'\A@echo off\r\n(?:python3|python) "%~dp0lumos" %\*\r\n\Z')


def _sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _unique_backup_path(dst: Path) -> Path:
    """與 `install.py` 的同名函式對稱,同款理由(秒級時間戳可能撞,
    `Path.rename()` 撞到已存在的非空目錄會拋例外,不像 bash `mv` 會靜默巢狀
    搬入)——見那邊的完整說明。"""
    base = f"{dst.name}.bak.{time.strftime('%Y%m%d%H%M%S')}"
    candidate = dst.parent / base
    n = 1
    while candidate.exists() or candidate.is_symlink():
        candidate = dst.parent / f"{base}.{n}"
        n += 1
    return candidate


def _manifest_bin_sha256(manifest_path: Path):
    """讀 install.py 寫的 manifest.json 裡的 bin_sha256——沒有 manifest、或
    欄位是空字串/檔案損毀,一律回傳 None(呼叫端退回 PKG 備援)。"""
    if not manifest_path.is_file():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    v = data.get("bin_sha256", "")
    return v or None


def _restore_claude_md(target: Path):
    """④ 執行目錄下 CLAUDE.md 的 LUMOS-SLIM sentinel 區塊 —— 與 install.py
    對稱的移除/還原。回傳 (rc, message)——★不做 sys.exit★,呼叫端(main)彙總
    多步驟結果後才決定最終 rc,這是「步驟互不阻擋」的核心。"""
    if not target.exists():
        return 0, f"  (未安裝: {target} 的 LUMOS-SLIM 圖譜標籤區塊 — 檔案不存在)"

    # ★讀也會失敗,而且漏掉讀比漏掉寫更容易(2026-08-02 複審抓到:第一版
    # 只把下面的 unlink()/write_text() 包起來,這一行 read_text() 留在 try 外面
    # ——「檔案系統寫入」這個字眼讓我只掃了寫。CLAUDE.md 被 chmod 000、或內容
    # 不是合法 utf-8(中文專案裡別的編輯器存成 Big5、貼進壞位元組都很真實)時,
    # 這一行照樣炸穿 main(),步驟⑤一樣不會執行——跟修之前的症狀一模一樣)★。
    # ★UnicodeDecodeError 不是 OSError 子類★(它繼承 ValueError),必須分開接;
    # 本檔第 ①b 段讀 shim 內容時就是同時接兩種,那裡對了、這裡漏了。
    try:
        current = target.read_text(encoding="utf-8")
    except OSError as e:
        return 2, (f"⚠ 讀不到 {target},無法處理 LUMOS-SLIM 區塊(檔案系統錯誤): {e}"
                   "——CLAUDE.md 未被修改,其餘步驟照跑;請手動處理。")
    except UnicodeDecodeError as e:
        return 2, (f"⚠ {target} 內容不是合法 utf-8,無法安全處理 LUMOS-SLIM 區塊: {e}"
                   "——CLAUDE.md 未被修改(★拒絕在看不懂內容的情況下改寫它★),"
                   "其餘步驟照跑;請自行確認該檔編碼後手動移除區塊。")
    pattern = re.compile(re.escape(SLIM_START) + r".*?" + re.escape(SLIM_END) + r"\n?", re.DOTALL)
    matches = list(pattern.finditer(current))

    if not matches:
        return 0, f"  (未安裝: {target} 的 LUMOS-SLIM 圖譜標籤區塊)"

    if len(matches) > 1:
        return 2, (f"⚠ {target} 內有多個 LUMOS-SLIM sentinel 區塊,拒絕自動移除"
                    "——請手動清理。")

    m = matches[0]
    block = m.group(0)
    bm = BACKUP_RE.search(block)

    restore_text = ""
    if bm and bm.group(1) != "NONE":
        encoded = bm.group(1)[len("BASE64:"):]
        try:
            restore_text = base64.b64decode(encoded).decode("utf-8")
        except Exception as e:
            return 2, (f"ERROR: 完整版區塊備份還原失敗(base64/utf-8 解碼錯誤): {e}"
                        "——拒絕破壞性移除,請手動處理。")

    new = current[:m.start()] + restore_text + current[m.end():]

    # ★這三處以前是裸呼叫(2026-08-02 補)★:寫/刪本身可能拋 OSError
    # (唯讀目錄、磁碟滿、Windows 檔案被別的程式鎖住),而 main() 呼叫本函式時
    # 也沒有 try——一拋就炸穿整支 main(),★後面的步驟⑤完全不會執行★,使用者
    # 只看到 traceback。那正好違反本檔 docstring 與圖譜 ★INVARIANT★ 宣稱的
    # 「各步驟各自獨立、互不阻擋」。改成回 rc=2 讓 main() 彙總,與本函式其他
    # 錯誤路徑(多 sentinel、base64 解碼失敗)一致。
    try:
        if new == "":
            target.unlink()
            return 0, f"✓ 已移除: {target} 的 LUMOS-SLIM 圖譜標籤區塊(內容變空,檔案本身一併移除)"
        elif restore_text:
            target.write_text(new, encoding="utf-8")
            return 0, f"✓ 已還原: {target} 的完整版紀律區塊(位元組級還原自內建備份),LUMOS-SLIM 區塊已移除"
        else:
            target.write_text(new, encoding="utf-8")
            return 0, f"✓ 已移除: {target} 的 LUMOS-SLIM 圖譜標籤區塊(其餘內容不變)"
    except OSError as e:
        return 2, (f"⚠ {target} 的 LUMOS-SLIM 區塊移除/還原失敗(檔案系統錯誤): {e}"
                   "——CLAUDE.md 未被修改,其餘步驟照跑;請手動處理或加 --force 重跑。")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    force = "--force" in argv

    bin_dir = Path.home() / ".local" / "bin"
    dst_script = bin_dir / "lumos"
    dst_shim = bin_dir / "lumos.cmd"
    skill = Path.home() / ".claude" / "skills" / "lumos-project-notes"
    pkg = Path.home() / ".lumos-slim"
    manifest_path = Path.home() / ".local" / "share" / "lumos-slim" / "manifest.json"

    rc = 0

    def bump(n):
        nonlocal rc
        if n > rc:
            rc = n

    print("== 公開精簡版卸載 ==")

    # ① ~/.local/bin/lumos —— ★只在它確實是我們裝的那份時才移除★。判斷方式:
    #    優先用 install.py 寫的 manifest(不依賴 ~/.lumos-slim 存在);manifest
    #    給不出參照時,退回舊版做法(拿 ~/.lumos-slim/scripts/lumos 當基準,
    #    相容較舊安裝)。★兩種「不移除」要分清楚★:完全找不到任何比對基準
    #    (基準缺失)、跟找到基準但內容比對不符(內容真的不符)——對使用者的
    #    意義不一樣,訊息分開講。
    #    ★2026-08 Task 16 修復②:Windows 的 lumos.cmd 搭檔已移出這個 if,改成
    #    ①b 獨立區塊(見下)★——舊寫法把 dst_shim 的移除巢狀在這個 if 裡面,
    #    `lumos` 不存在但 `lumos.cmd` 還在(孤兒殘留,例如使用者手滑只刪了
    #    `lumos`)時,外層 `if dst_script.exists()...` 直接判假,整段(含
    #    --force 分支)都跳過,孤兒 `lumos.cmd` 永遠清不掉、`--force` 也救不了
    #    ——這牴觸本檔案 docstring 自己講的「兩者總是成對安裝/移除」,也是
    #    install.py 那邊已經修過的「碰撞偵測要同時看兩個檔案」的鏡像缺口。
    if dst_script.exists() or dst_script.is_symlink():
        if force:
            try:
                dst_script.unlink()
                print(f"✓ 已移除(--force,跳過內容比對): {dst_script}")
            except OSError as e:   # 見 _restore_claude_md 的說明:不得炸穿 main()
                print(f"⚠ 移除 {dst_script} 失敗,跳過(其餘步驟照跑): {e}", file=sys.stderr)
                bump(2)
        else:
            try:
                cur_sha = _sha256_file(dst_script)
            except OSError as e:
                print(f"⚠ 無法讀取 {dst_script} 內容,無法安全比對——跳過移除: {e}", file=sys.stderr)
                print("  確定要砍就加 --force 重跑。", file=sys.stderr)
                bump(2)
                cur_sha = None

            if cur_sha is not None:
                ref_sha, ref_desc = None, None
                manifest_sha = _manifest_bin_sha256(manifest_path)
                if manifest_sha:
                    ref_sha, ref_desc = manifest_sha, f"安裝時記錄的 manifest({manifest_path})"
                else:
                    pkg_cli = pkg / "scripts" / "lumos"
                    if pkg_cli.is_file():
                        try:
                            ref_sha = _sha256_file(pkg_cli)
                            ref_desc = f"{pkg_cli}(無 manifest 時的備援比對,相容較舊安裝)"
                        except OSError:
                            ref_sha = None

                if not ref_sha:
                    print(f"⚠ 找不到任何比對基準——manifest({manifest_path})與 {pkg}/scripts/lumos 都不存在。",
                          file=sys.stderr)
                    print(f"  這是「基準缺失」,不是內容比對出不符;沒有基準就無法安全判斷 {dst_script}",
                          file=sys.stderr)
                    print("  是不是本包裝的那份,拒絕移除。確定要砍就加 --force 重跑。", file=sys.stderr)
                    bump(1)
                elif cur_sha == ref_sha:
                    try:
                        dst_script.unlink()
                        print(f"✓ 已移除: {dst_script}")
                    except OSError as e:
                        print(f"⚠ 移除 {dst_script} 失敗,跳過(其餘步驟照跑): {e}", file=sys.stderr)
                        bump(2)
                else:
                    print(f"⚠ {dst_script} 內容與比對基準({ref_desc})不一致——這是「內容真的不符」,不是基準缺失。",
                          file=sys.stderr)
                    print("  這可能是你自己的東西,不是本包裝的那份 lumos——拒絕移除。", file=sys.stderr)
                    print("  確定要砍就加 --force 重跑。", file=sys.stderr)
                    bump(1)
    else:
        print(f"  (未安裝: {dst_script})")

    # ①b ~/.local/bin/lumos.cmd(Windows 搭檔,僅 IS_WIN)—— ★與①各自獨立
    #    判斷、各自執行,互不阻擋★(2026-08 Task 16 修復②)。shim 本身沒有
    #    manifest 雜湊可比對(install.py `_install_cli()` 只記 dst_script 的
    #    雜湊,shim 內容是固定樣板、跟安裝位置無關,拿它比對沒有鑑別力,見該處
    #    註解)——改用「內容是否符合 install.py 產生的固定樣板」當安全判斷
    #    基準:`@echo off\r\n<偵測到的直譯器> "%~dp0lumos" %*\r\n`,直譯器只會
    #    是 `python3` 或 `python`(見 `_pick_windows_interpreter()`)。符合樣板
    #    視為本包裝的 shim,可以安全移除(不需要 --force);不符合就當成使用者
    #    自己的東西,拒絕移除。
    if IS_WIN:
        if dst_shim.exists() or dst_shim.is_symlink():
            if force:
                try:
                    dst_shim.unlink()
                    print(f"✓ 已移除(--force,跳過內容比對): {dst_shim}")
                except OSError as e:   # 見 _restore_claude_md 的說明:不得炸穿 main()
                    print(f"⚠ 移除 {dst_shim} 失敗,跳過(其餘步驟照跑): {e}", file=sys.stderr)
                    bump(2)
            else:
                try:
                    # ★用 read_bytes().decode() 比對,不用 read_text()★——後者
                    # 預設 universal-newline 轉譯,會把 shim 內容裡的 `\r\n`
                    # 正規化成 `\n`,即使檔案位元組完全沒被動過,也會讓下面比對
                    # `\r\n` 的 SHIM_TEXT_RE 永遠比對不到(同一個坑,`t_slim_
                    # install_windows_collision_detects_orphan_cmd_shim` 的
                    # docstring 已經點過一次,這裡是它在讀取端的鏡像版本)。
                    shim_text = dst_shim.read_bytes().decode("utf-8")
                except OSError as e:
                    print(f"⚠ 無法讀取 {dst_shim} 內容,無法安全比對——跳過移除: {e}", file=sys.stderr)
                    print("  確定要砍就加 --force 重跑。", file=sys.stderr)
                    bump(2)
                    shim_text = None
                except UnicodeDecodeError as e:
                    print(f"⚠ {dst_shim} 內容不是合法 utf-8,無法安全比對——跳過移除: {e}", file=sys.stderr)
                    print("  確定要砍就加 --force 重跑。", file=sys.stderr)
                    bump(2)
                    shim_text = None

                if shim_text is not None:
                    if SHIM_TEXT_RE.match(shim_text):
                        try:
                            dst_shim.unlink()
                            print(f"✓ 已移除: {dst_shim}")
                        except OSError as e:
                            print(f"⚠ 移除 {dst_shim} 失敗,跳過(其餘步驟照跑): {e}", file=sys.stderr)
                            bump(2)
                    else:
                        print(f"⚠ {dst_shim} 內容不符合本包產生的 shim 樣板——可能是你自己的東西,拒絕移除。",
                              file=sys.stderr)
                        print("  確定要砍就加 --force 重跑。", file=sys.stderr)
                        bump(1)
        else:
            print(f"  (未安裝: {dst_shim})")

    # ② skill 目錄 —— ★移除前先備份,不直接刪★(使用者可能在裡面塞過自己的
    #    檔)。★與①獨立★:①的比對結果(移除/跳過/錯誤)不影響這一步是否執行。
    if skill.is_dir() or skill.is_symlink():
        # ★備份落點必須★離開★ ~/.claude/skills/(2026-08-03 中文 Windows 真機驗證抓到)★
        # 舊寫法 `_unique_backup_path(skill)` 是「同目錄改名」,而 ~/.claude/skills/ 正是
        # Claude Code ★掃描 skill 的目錄★——往裡面放任何含 SKILL.md 的子目錄都會被載入。
        # 實測卸載後下一個 session 的 skill 清單真的多出:
        #   - lumos-project-notes.bak.20260803102236: 維護專案知識圖譜…
        # ★也就是卸載沒有讓這個 skill 停止作用,只是換了個怪名字繼續生效★,
        # 而訊息還印「已備份並移除」——它根本沒離開那個目錄。
        # 落點選 ~/.local/share/lumos-slim/backups/:那裡已經是本安裝器放 manifest 的地方,
        # 語意一致,且★不在任何掃描範圍內★。
        _bak_root = Path.home() / ".local" / "share" / "lumos-slim" / "backups"
        try:
            _bak_root.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"⚠ 無法建立備份目錄 {_bak_root}——保留 skill 不動: {e}", file=sys.stderr)
            bump(2)
            _bak_root = None
        if _bak_root is None:
            bak = None
        else:
            _base = f"{skill.name}.bak.{time.strftime('%Y%m%d%H%M%S')}"
            bak = _bak_root / _base
            _n = 1
            while bak.exists() or bak.is_symlink():
                bak = _bak_root / f"{_base}.{_n}"
                _n += 1
        try:
            if bak is None:
                raise OSError("備份目錄不可用")
            skill.rename(bak)
            print(f"✓ 已備份並移除: {skill} → {bak}")
            print(f"  (備份放在 {_bak_root},★刻意不留在 ~/.claude/skills/★"
                  f"——留在那裡會被 Claude Code 當成一個新 skill 繼續載入)")
        except OSError as e:
            print(f"⚠ 備份/移除 {skill} 失敗——保留,不動: {e}", file=sys.stderr)
            bump(2)
    else:
        print(f"  (未安裝: {skill})")

    # ③ ~/.lumos-slim —— 可移除,但同樣先確認它長得像我們的包才刪。★與①②獨立★。
    if pkg.is_dir():
        if (pkg / "scripts" / "lumos").is_file() and (pkg / "install.sh").is_file():
            # ★Windows 上 git 把 pack 檔(.idx/.pack)設成唯讀,rmtree 預設會 PermissionError★
            # (2026-08-03 中文 Windows 真機驗證抓到)。★而且它是「刪到一半」才撞上★——
            # 舊訊息只說「移除失敗」,聽起來像什麼都沒動;實測 .git 目錄還在但 HEAD/config/
            # index 已被刪掉,留下一個「看起來像 repo、實際已損壞」的目錄。
            # ★後果是把使用者鎖死★:get.ps1 用 `Test-Path "$Dest\.git"` 判斷「是不是我們的
            # clone」→ True → 跑 `git pull` → rc=128「not a git repository」→ 使用者看到的
            # 錯誤訊息是「可能有本地改動,或不是 fast-forward」,★完全指錯方向★。
            # 修法兩件:①唯讀檔改成可寫再刪(Windows 經典陷阱的標準解)
            #          ②真的失敗時★明講「已部分刪除、不再是可用的 clone」★,不要讓使用者
            #            以為什麼都沒發生(訊息誤導比失敗本身更貴)。
            def _on_rm_error(func, path, _exc):
                # ★不能寫成 `os.chmod(path, stat.S_IWRITE)`★——那是「設定」不是「加上」:
                # 對★目錄★會把執行位元一起拿掉,反而更刪不掉(自測踩到)。
                # 正解=在既有 mode 上★補★寫入位元;目錄再補執行位元(要能進去才刪得掉)。
                try:
                    _m = os.stat(path).st_mode
                    _add = stat.S_IWUSR | (stat.S_IXUSR if os.path.isdir(path) else 0)
                    os.chmod(path, _m | _add)
                    # 父目錄沒有寫入權時,刪不掉裡面的項目——一起補
                    _par = os.path.dirname(path)
                    if _par and os.path.isdir(_par):
                        os.chmod(_par, os.stat(_par).st_mode | stat.S_IWUSR | stat.S_IXUSR)
                    func(path)
                except OSError:
                    raise
            try:
                # Python 3.12 起 onerror 改名 onexc(簽名不同);本包宣告 ≥3.8,兩邊都要能跑
                if sys.version_info >= (3, 12):
                    shutil.rmtree(pkg, onexc=lambda f, pth, e: _on_rm_error(f, pth, e))
                else:
                    shutil.rmtree(pkg, onerror=_on_rm_error)
                print(f"✓ 已移除: {pkg}")
            except OSError as e:
                print(f"⚠ 移除 {pkg} 失敗: {e}", file=sys.stderr)
                if pkg.exists():
                    print(f"  ★注意:{pkg} 已被★部分刪除★,它不再是一個可用的 clone。",
                          file=sys.stderr)
                    print(f"  重跑一行安裝會看到「更新失敗/不是 fast-forward」之類的訊息"
                          f"——那是誤導,真正的狀況是這個目錄壞了。", file=sys.stderr)
                    print(f"  請手動移除整個 {pkg} 後再重裝"
                          f"(Windows: Remove-Item -Recurse -Force '{pkg}')。", file=sys.stderr)
                bump(2)
        else:
            print(f"⚠ {pkg} 存在,但內容不像本包(缺 scripts/lumos 或 install.sh)——保留,不動。",
                  file=sys.stderr)
            bump(1)
    else:
        print(f"  (未安裝: {pkg})")

    # ④ 執行目錄下 CLAUDE.md 的 LUMOS-SLIM sentinel 區塊 —— ★這是本次修的
    #    重點步驟★:不管①②③的結果如何,這一步永遠會跑——bin 的安全檢查失敗
    #    絕不該擋住這裡。
    claude_md = Path.cwd() / "CLAUDE.md"
    claude_rc, claude_msg = _restore_claude_md(claude_md)
    print(claude_msg)
    if claude_rc != 0:
        bump(claude_rc)

    # ⑤ 身分證 manifest(~/.local/share/lumos-slim/manifest.json)—— ★2026-08-01
    #    真跑冒煙抓到的殘留:一整套測試全綠、卸載彙總印「✓ 全部完成」,實際跑完
    #    卻在使用者 $HOME 底下留著這支檔案★(整套測試沒有任何一條斷言過它——同
    #    一個「測試存在但沒在驗它宣稱要驗的」老坑,這次是「根本沒去驗」)。
    #    ★與①②③④獨立★:它自己判斷、自己執行,不擋任何其他步驟、也不被擋。
    #    ★但有一個資料相依(不是控制相依)★:只有 bin 確實清乾淨(或本來就沒裝)
    #    才刪 manifest——①/①b 任一份基於安全考量沒移除時,manifest 是使用者之後
    #    重試(加 --force / 手動確認)唯一的比對基準,先刪掉等於把判斷依據銷毀,
    #    下次重跑只會落到「基準缺失」。留著並印一句為什麼留,比默默刪掉誠實。
    #    ★判斷方式見下方 bin_cleared:直接查檔案系統實況,不做分支簿記★
    #    只刪這支檔案與(空的)父目錄 lumos-slim/,★絕不碰 ~/.local/share 底下
    #    其他任何東西★——那裡是很多工具共用的地方。
    # ★「bin 有沒有清乾淨」直接查檔案系統實況,不用旗標簿記★(2026-08-01 代碼審
    #    r4 抓到):原本在①/①b 的每一條「沒移除」分支手動設 `bin_cleared = False`,
    #    ①b 的 OSError 分支漏設了一條——Windows 上 `lumos.cmd` 讀不到(權限/被別的
    #    程序鎖住)時 shim 明明還在,manifest 卻照樣被刪,把使用者重試時唯一的比對
    #    基準銷毀。分支簿記天生會漏(這次就漏了),改成事後問一句「東西還在不在」:
    #    對每一條現有與未來新增的分支都自動成立,漏不掉。
    #    ★兩個邊界(2026-08-01 代碼審 r5 抓到,都是 r4 這個修法自己引入的)★:
    #    (a) shim 的存在性檢查必須跟①b 一樣受 `IS_WIN` 限定——①b 整段包在
    #        `if IS_WIN:` 底下,非 Windows 機器根本不會去看/去動 `lumos.cmd`;
    #        這裡若無條件檢查,macOS/Linux 上只要那個路徑上剛好有別的東西
    #        (`~/.local/bin` 是很多工具共用的地方),manifest 就會被永久卡住,
    #        而且⑤沒有 `--force` 分支(①/①b 才有),使用者照訊息重跑也解不開。
    #    (b) shim 那一半要跟 `dst_script` 對稱補上 `is_symlink()`——`exists()`
    #        對「目標已被刪掉的斷鏈 symlink」回傳 False,但那個 symlink 本身
    #        仍佔著路徑、①b 也確實沒把它移除掉。
    bin_cleared = not (
        dst_script.exists() or dst_script.is_symlink()
        or (IS_WIN and (dst_shim.exists() or dst_shim.is_symlink()))
    )

    if manifest_path.is_file():
        if bin_cleared:
            try:
                manifest_path.unlink()
                print(f"✓ 已移除: {manifest_path}(身分證 manifest)")
            except OSError as e:
                print(f"⚠ 移除 {manifest_path} 失敗: {e}", file=sys.stderr)
                bump(2)
            else:
                # ★父目錄清理必須自己一個 try,不能跟上面共用★(2026-08-01 代碼審
                # r3 抓到):共用時 iterdir()/rmdir() 拋 OSError 會印成「移除
                # manifest 失敗」並 bump(2)——但 manifest 其實已經刪成功了(上面
                # 的 ✓ 都印出來了),使用者會同時看到 ✓ 和 ⚠、以為要手動處理。
                # 這一步是選配的收尾清理(目錄非空/被別的流程動過都算正常),
                # 失敗不該升級成「真正的錯誤」,只印一句就好。
                parent = manifest_path.parent
                try:
                    if parent.name == "lumos-slim" and not any(parent.iterdir()):
                        parent.rmdir()
                        print(f"✓ 已移除空目錄: {parent}")
                except OSError as e:
                    print(f"  (順帶清理空目錄 {parent} 沒成功,不影響卸載結果: {e})")
        else:
            print(f"  (保留: {manifest_path} — 上面 bin 有項目未移除,manifest 是重試時的比對基準)")
    else:
        print(f"  (未安裝: {manifest_path})")

    print()
    print("== 卸載彙總 ==")
    if rc == 0:
        print("✓ 全部完成(或本來就沒裝)。")
    elif rc == 1:
        print("⚠ 部分項目基於安全考量主動跳過,理由見上面——確定要處理就重跑加 --force。")
    else:
        print("✗ 有真正的錯誤(非安全性跳過),理由見上面——需要手動處理。")
    # ★備份是刻意留下的殘留,必須在彙總裡明講(2026-08-03)★——否則就是原本 manifest
    # 殘留那條缺陷的同一形狀:彙總說「全部完成」,實際上 $HOME 底下留了東西。
    # 差別在這次是★刻意★留的(那是使用者可能塞過自己筆記的 skill 備份),但
    # ★刻意留 ≠ 可以不講★。
    _bk = Path.home() / ".local" / "share" / "lumos-slim" / "backups"
    try:
        _left = sorted(x.name for x in _bk.iterdir()) if _bk.is_dir() else []
    except OSError:
        _left = []
    if _left:
        print(f"★刻意保留★:skill 備份 {len(_left)} 份留在 {_bk}")
        for _x in _left[:5]:
            print(f"        • {_x}")
        if len(_left) > 5:
            print(f"        … 還有 {len(_left) - 5} 份")
        print("        (確認裡面沒有你要留的東西之後可以自行刪除;"
              "★刻意不放回 ~/.claude/skills/★——放那裡會被當成新 skill 載入)")
    print("★未動★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、其他 skill;")
    print("        CLAUDE.md 除了上面那塊 LUMOS-SLIM sentinel 區塊(及它取代掉的完整版")
    print("        區塊,若有 — 已還原),其餘內容原封不動。")

    return rc


if __name__ == "__main__":
    sys.exit(main())
