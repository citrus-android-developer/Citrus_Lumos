#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""install.py — 公開精簡版 機器層安裝器(stdlib only,Windows 可跑)

★這是唯一的安裝邏輯來源★——`install.sh`／`install.ps1` 都只是薄殼,把參數原樣轉
發過來(`<python> install.py "$@"` / `& $py install.py @args`),真正的行為全在
這支檔案。這樣改一次邏輯,Unix/Windows 兩邊同步生效,不會漂移成兩份互相打架的
腳本(bash 版本已經證明維護不動——見 `slim/install.sh` 的舊版註解史)。

★做三件事★:①全域 `lumos` 指令(附帶身分證 manifest,見 `_install_cli()`)
②實體複製 skill 到 `~/.claude/skills/`(不是 symlink——複製後要跟交付包解耦,
就算 `~/.lumos-slim` 事後被砍掉,已裝好的東西仍要能動)③在執行時所在目錄(專案
根)的 `CLAUDE.md` 裡放一塊策展過的精簡版紀律區塊(sentinel
`<!-- LUMOS-SLIM:START/END -->`)。

★裁定演進(spec [S3],三次,原樣沿用自 bash 版本的裁決記錄)★:原裁定=絕不碰
專案 CLAUDE.md;第二次=只准 append-only 附加,sentinel 以外一個位元組都不動,
完整版 `LUMOS:GRAPH-DISCIPLINE` 區塊(若有)原封不動留著;第三次(現行)=若專案
已有完整版區塊,**整段移除**它,換成這塊精簡版區塊——但移除前先把完整版原文
位元組級備份(base64 編碼藏進精簡版區塊自己的 HTML 註解裡,見 `claude-block.md`
的 `FULL-BACKUP` 標記),`uninstall.py` 能用它精確還原。理由:完整版那段本身自稱
「優先級最高/第一個工具呼叫必須是 lumos」,兩套規則並存時接手者的 Claude 會先讀
到它、照著撲空(它引用的 design-loop/code-loop/pitfalls 等指令本包都沒交付)。

插入位置:①有完整版區塊 → 原位置整段換掉(不是搬到檔尾——那裡才顯眼)
         ②沒有 → 插在檔首「# 標題」之後,沒有標題就插最前面
         ③CLAUDE.md 不存在 → 建立,內容就是這個區塊
★冪等★:重跑只更新自己那塊(沿用既有備份標記,不重新編碼、不二次包裹)。
★仍明確不做★:不 scaffold 圖譜、不 vendor 工具進專案、不設 core.hooksPath、
             不裝任何 Claude hook。

★注入目標守衛(三層)★——★真實事故已咬過兩次★:子代理驗證時忘記先 cd 進交付包
clone,直接在 lumos-toolchain 這個來源 repo 底下跑,當場改掉了來源 repo 自己的
CLAUDE.md。三層各擋不同的東西:
  第一層 擋「在 $HOME 或隨便一個目錄下誤跑」—— 不像專案根就拒絕。
  第二層 擋「這個目錄其實是 lumos 工具鏈本身的來源 repo」—— ★這層才擋得住
         那兩次事故★:事故現場本身就有 .git/CLAUDE.md/docs/*-knowledge,長得
         完全像個合理的專案根,第一層擋不住。
  第三層 動手前把目標印大聲 —— 前兩層都擋不住「在另一個合法專案根誤跑」,只有
         把目標印出來才有機會被人眼看見,是最後一道防線。
逃生閥 `--here`:繞過第一、二層(但仍然印目標——第三層不因 --here 而略過)。

★移植到 Python 順帶消掉一整類 bug★:bash 版本得分別用 `pwd`(邏輯路徑,可能是
symlink 形式)跟 `pwd -P`(實體路徑)、稍有不慎就兩處算出的字串不一致(見舊版
`slim/install.sh` 的 symlink-cwd 回歸測試)。Python 的 `os.getcwd()`(`Path.cwd()`
底層呼叫的就是它)本來就一律回傳實體路徑,這裡從頭到尾只用一種路徑形式,那整類
bug 不會再發生。

★Windows 支援★(讀 `scripts/lumos` 的 `_IS_WIN` 分支照做,見 `cmd_install`/
`_link_or_copy`):
  - 全域指令:Unix 直接複製 + chmod +x;Windows 額外產生 `lumos.cmd` shim,
    shim 內容只用 `%~dp0`(自己所在目錄)相對定位、不參照 PKG 來源——維持與
    Unix 版相同的「複製後與交付包解耦」特性(`~/.lumos-slim` 事後被砍掉,已裝
    好的東西仍要能動)。shim 呼叫用的直譯器名稱(`python3`/`python`)由
    `_pick_windows_interpreter()` 在安裝當下偵測、寫進 shim,★不寫死字面
    `python`★(2026-08 Task 14 修復——舊寫法與 `install.sh`/`install.ps1`
    自己「python3 優先,找不到才退 python」的判斷邏輯互相矛盾,只有
    `python3.exe`、沒有 `python.exe` 的機器會裝完即壞,細節見該函式
    docstring)。碰撞偵測(是否需要 `--force`)在 Windows 路徑下同時看
    `lumos` 與 `lumos.cmd` 兩個檔案,任一存在都算碰撞(同次修復②——只看
    前者會讓單獨殘留的 `lumos.cmd` 被非 `--force` 重裝無聲覆寫)。
  - skill 目錄:精簡版一律實體複製(不像完整版那樣建 symlink/junction),
    Windows/Unix 共用同一段程式碼,較單純;但移除/備份時仍用「先 rename 再處理
    內容」的方式,不直接假設它是一般目錄(避免完整版 `_link_or_copy` 那個 W4
    Windows junction 坑的同款問題——即使精簡版目前不建 junction,防禦性寫法
    成本很低)。
  - PATH 缺失時的提示訊息分平台(Windows 講「系統環境變數」,Unix 講 shell
    設定檔)。

★這台機器沒有 Windows,無法做真機驗證★——Windows 分支靠 `LUMOS_SLIM_SIMULATE_
WINDOWS=1` 環境變數注入(見 `IS_WIN` 定義)在 macOS/Linux 上跑同一段程式碼、斷言
它做了「產生 .cmd shim / 不 chmod / Windows 版 PATH 提示」這些*程式邏輯*層級的
事,測不到 mklink/真實 PATH 行為/檔案總管觀感等*真機*層級的事——這個限制在
`slim/README.md` 與圖譜裡都有明講,不要誤讀成「Windows 已驗證」。
"""
import base64
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

# ★可注入,供測試在非 Windows 機器上驗證 Windows 分支邏輯★——真機一律看
# os.name;測試靠這個環境變數逼出同一份程式碼走 Windows 分支(見模組 docstring
# 結尾的誠實聲明)。
IS_WIN = (os.name == "nt") or (os.environ.get("LUMOS_SLIM_SIMULATE_WINDOWS") == "1")

SLIM_START = "<!-- LUMOS-SLIM:START -->"
SLIM_END = "<!-- LUMOS-SLIM:END -->"
# ★完整版 START 有版本號後綴(如 "...START v1.0 — 自動注入...-->"),不是固定
# 字面值★——只匹配前綴,與 scripts/lumos 的 _CLAUDE_START_PREFIX 同款做法。
FULL_START_PREFIX = "<!-- LUMOS:GRAPH-DISCIPLINE:START"
FULL_END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
BACKUP_NONE = "<!-- LUMOS-SLIM:FULL-BACKUP:NONE -->"
BACKUP_RE = re.compile(r"<!-- LUMOS-SLIM:FULL-BACKUP:(NONE|BASE64:[A-Za-z0-9+/=]*) -->")


def _sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _unique_backup_path(dst: Path) -> Path:
    """回傳一個保證還不存在的 `<dst>.bak.<timestamp>[.N]` 路徑。★為什麼不能只
    用秒級時間戳★:bash 版本原本 `mv "$DST_SKILL" "$BAK"`——`$BAK` 若剛好已存在
    且是目錄,bash 的 `mv` 語意是把來源「搬進」那個目錄裡(不會報錯,只是巢狀
    放錯位置);Python 的 `Path.rename()` 對「目的地是已存在的非空目錄」的語意
    不同——直接拋 `OSError: Directory not empty`。同一顆 timestamp(僅秒級解析
    度)在測試(甚至真實使用者連續操作)裡並非不可能撞——例如「先 --force 重裝
    一次、緊接著又跑一次卸載」兩次備份可能落在同一秒。用遞增後綴保證每次呼叫
    都拿到全新路徑,不改變既有測試依賴的 glob 樣式(`*.bak.*` 仍然匹配)。"""
    base = f"{dst.name}.bak.{time.strftime('%Y%m%d%H%M%S')}"
    candidate = dst.parent / base
    n = 1
    while candidate.exists() or candidate.is_symlink():
        candidate = dst.parent / f"{base}.{n}"
        n += 1
    return candidate


def _merge_claude_md_text(target: Path, template: str):
    """回傳 (rc, new_text_or_None)。純函式(不寫檔),與 uninstall.py 的
    `_restore_claude_md` 對稱——邏輯逐字對應舊版 `install.sh` 內嵌的 heredoc
    python 區塊,搬過來只是換了個檔案放。"""
    slim_pat = re.compile(re.escape(SLIM_START) + r".*?" + re.escape(SLIM_END) + r"\n?", re.DOTALL)
    full_pat = re.compile(re.escape(FULL_START_PREFIX) + r".*?" + re.escape(FULL_END) + r"\n?", re.DOTALL)

    original = target.read_text(encoding="utf-8") if target.exists() else ""
    slim_matches = list(slim_pat.finditer(original))
    full_matches = list(full_pat.finditer(original))

    if len(slim_matches) > 1:
        print(f"ERROR: {target} 內有多個 LUMOS-SLIM sentinel 區塊,拒絕自動處理"
              "——請手動清理後重跑。", file=sys.stderr)
        return 2, None
    if len(full_matches) > 1:
        print(f"ERROR: {target} 內有多個 LUMOS:GRAPH-DISCIPLINE sentinel 區塊,"
              "拒絕自動處理——請手動清理後重跑。", file=sys.stderr)
        return 2, None
    if slim_matches and full_matches:
        print(f"ERROR: {target} 同時有 LUMOS-SLIM 與 LUMOS:GRAPH-DISCIPLINE 兩種"
              "sentinel 區塊並存,狀態不明確,拒絕自動處理——請手動清理後重跑。",
              file=sys.stderr)
        return 2, None

    if full_matches:
        # 情境①:有完整版區塊 —— 先把原文位元組級編碼進備份標記,再原位置整段
        # 換成精簡版區塊(不是搬到檔尾)。
        m = full_matches[0]
        full_text = m.group(0)
        encoded = base64.b64encode(full_text.encode("utf-8")).decode("ascii")
        backup_marker = f"<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:{encoded} -->"
        start, end = m.start(), m.end()
    elif slim_matches:
        # 情境②:冪等重跑 —— 精簡版區塊已存在,沿用它既有的備份標記(★不重新
        # 編碼、不因這次沒看到完整版區塊就誤判成「原本沒有」而把備份洗掉★)。
        m = slim_matches[0]
        bm = BACKUP_RE.search(m.group(0))
        backup_marker = bm.group(0) if bm else BACKUP_NONE
        start, end = m.start(), m.end()
    else:
        # 情境③:兩種都沒有 —— 全新安裝,無備份;插入點是「檔首 # 標題之後」,
        # 沒有標題就插最前面,原檔不存在/空檔就直接整份是這個區塊。
        backup_marker = BACKUP_NONE
        if original.startswith("# "):
            nl = original.find("\n")
            pos = nl + 1 if nl != -1 else len(original)
        else:
            pos = 0
        start = end = pos

    block_text = template.replace(BACKUP_NONE, backup_marker)
    new_text = original[:start] + block_text + original[end:]
    return 0, new_text


def _pick_windows_interpreter():
    """回傳要寫進 `.cmd` shim 的直譯器命令名稱(★2026-08 Task 14 修復①★,
    不是絕對路徑)——安裝當下依序試 `python3`/`python`(與 `install.sh` 的
    候選清單、`install.ps1` 的 `Get-Command` 鏈同一套「python3 優先」判斷
    邏輯,三處判斷一致、不漂移),寫進 shim 供之後每次執行 `lumos` 時使用。

    ★為什麼寫在安裝當下偵測到的名稱、不是寫死字面 `python`★:舊寫法
    `python "%~dp0lumos" %*` 與同專案兩支薄殼(`install.sh`/`install.ps1`)
    自己都承認「`python` 可能不存在,得先試 `python3`」互相矛盾——只有
    `python3.exe`、沒有 `python.exe` 的 Windows 機器(常見於某些官方安裝器/
    Microsoft Store 版 Python)上,`install.ps1` 用 `python3` 把安裝跑完、
    印出「裝好了」,但產生的 shim 卻寫死呼叫 `python`,之後每次打 `lumos`
    都得到 `'python' is not recognized`——裝完即壞,且要等使用者真的執行才
    會發現,不會在安裝當下就報錯。

    ★為什麼寫命令名稱、不寫 `sys.executable` 的絕對路徑★:安裝當下其實可以
    拿到更「精確」的答案——`install.ps1` 已經用 `Get-Command` 解出一支具體
    存在的 exe 絕對路徑並用它跑起 `install.py`,理論上 `sys.executable` 就是
    那支路徑,直接烤進 shim 看似「當下已驗證存在」最穩。但實務上 Windows 常見
    的 python 版本管理方式(pyenv-win、winget/choco 升級)經常是「换一支新
    exe、搬動安裝目錄」而不是「原地替換同一個路徑」,絕對路徑撐不過這類升級;
    相對地,`python3`/`python` 這兩個命令名稱通常穩定掛在 PATH 上,版本管理
    工具本身的職責就是讓這兩個名字持續可用。寫名稱與另外兩支薄殼的判斷邏輯
    語意一致,是三處一致中最不會漂移的選擇。兩個候選都試不到就退回 "python"
    (維持與舊版相同的『至少嘗試一次』語意,不讓 shim 產生這一步本身失敗——
    真正「兩者都沒有」的情況本來就該在使用者執行 `lumos` 時才浮現,不該卡在
    安裝步驟;安裝當下若真的兩者都無法偵測,通常代表 `install.ps1`/`install.sh`
    自己也早就已經因為同樣理由 rc2 退出了,不會走到這裡)。

    ★這台機器沒有 Windows,無法用真實 `where`/PATH 語意驗證★——這裡呼叫的
    `shutil.which()` 是 Python 標準庫的跨平台實作,在 `LUMOS_SLIM_SIMULATE_
    WINDOWS=1` 模擬下實際查的仍是這台機器真正的 PATH(見 `scripts/test_lumos.py`
    的 `t_slim_install_windows_shim_does_not_hardcode_python_*`)——驗證的是
    ★程式邏輯本身★(偵測到什麼就寫什麼),不是 Windows 真機下 `where.exe`/
    `cmd.exe` 對 `.cmd` 的實際解析行為。
    """
    for cand in ("python3", "python"):
        if shutil.which(cand):
            return cand
    return "python"


def _install_cli(pkg: Path, bin_dir: Path, force: bool):
    """回傳 rc。① 全域指令 —— 碰撞語意沿用完整版 cmd_install 的階梯。

    Unix:直接把 `scripts/lumos` 複製成 `~/.local/bin/lumos`、chmod +x。
    Windows:同一份內容複製成 `~/.local/bin/lumos`(沒有可執行位元的意義,純粹
    是 shim 呼叫的目標),另外產生 `~/.local/bin/lumos.cmd` 這個 shim——shim
    內容用 `%~dp0`(批次檔自己所在目錄)相對定位到同目錄下的 `lumos`,★不寫死
    PKG 路徑★,理由與 Unix 版一致:複製完要跟交付包來源解耦;shim 呼叫用的
    直譯器名稱由 `_pick_windows_interpreter()` 在安裝當下偵測,不寫死
    `python`(★2026-08 Task 14 修復①,見該函式 docstring★)。

    ★2026-08 Task 14 修復②★:碰撞偵測(Windows 路徑下)同時看 `lumos` 與
    `lumos.cmd` 兩個檔案——只看前者的舊寫法,若使用者手動刪了 `lumos` 忘了刪
    `lumos.cmd`(單獨殘留),非 `--force` 重裝時 `dst_script.exists()` 為
    False、collided 判成假,會直接跳過碰撞保護、無聲覆寫殘留的 `lumos.cmd`
    (繞過「碰撞需要 --force」這條保護的存在意義)。
    """
    src_cli = pkg / "scripts" / "lumos"
    dst_script = bin_dir / "lumos"
    dst_shim = bin_dir / "lumos.cmd"

    collided = dst_script.exists() or dst_script.is_symlink()
    if IS_WIN:
        collided = collided or dst_shim.exists() or dst_shim.is_symlink()
    if collided:
        if not force:
            if IS_WIN:
                print(f"⚠ {dst_script} 或 {dst_shim} 已存在,加 --force 覆寫", file=sys.stderr)
            else:
                print(f"⚠ {dst_script} 已存在,加 --force 覆寫", file=sys.stderr)
            return 2
        if dst_script.exists() or dst_script.is_symlink():
            dst_script.unlink()
        if IS_WIN and (dst_shim.exists() or dst_shim.is_symlink()):
            dst_shim.unlink()

    shutil.copyfile(src_cli, dst_script)
    if IS_WIN:
        py_cmd = _pick_windows_interpreter()
        shim_text = f'@echo off\r\n{py_cmd} "%~dp0lumos" %*\r\n'
        dst_shim.write_bytes(shim_text.encode("utf-8"))
        print(f"✓ 全域指令: {dst_shim} (→ {dst_script}, 直譯器={py_cmd})")
    else:
        dst_script.chmod(0o755)
        print(f"✓ 全域指令: {dst_script}")

    # ①b 身分證 manifest —— 讓 uninstall.py 有穩定比對基準,★不依賴
    # ~/.lumos-slim 事後還存不存在★;bin_sha256 記的是「被複製進 bin 目錄的
    # 那份原始腳本內容」的雜湊(Windows 上是 dst_script,不是 dst_shim ——
    # shim 內容固定、跟安裝位置無關,拿它比對沒有鑑別力;dst_script 才是真正
    # 從交付包複製過來、可以拿去跟 PKG/scripts/lumos 互相比對雜湊的那份,
    # Unix/Windows 兩邊語意因此一致)。放在 ~/.local/share/(不是使用者的專案
    # 目錄),不會污染任何專案的 git status。冪等:每次成功安裝都覆寫。
    manifest_dir = Path.home() / ".local" / "share" / "lumos-slim"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest.json"
    bin_sha = _sha256_file(dst_script)
    manifest_path.write_text(
        json.dumps({
            "format_version": 1,
            "bin_sha256": bin_sha,
            "installed_at_epoch": int(time.time()),
            "pkg_dir": str(pkg),
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"✓ 身分證 manifest: {manifest_path}")
    return 0


def _install_skill(pkg: Path, skills_dir: Path, force: bool):
    """② skill —— ★實體複製,不是 symlink★(來源=交付包,但複製後與包解耦)。
    碰撞時先備份成 `.bak.<timestamp>`,不直接覆寫(使用者可能在裡面塞過自己的
    筆記)。用 `rename()` 而非 `shutil.move()` 做備份搬移——`rename()` 只動
    目錄項本身,不會「跟進」目標內容,即使未來某天這裡意外變成 symlink/
    Windows junction 也不會被牽連(即使精簡版目前從不建立這兩種東西,防禦性
    寫法成本很低,見模組 docstring 的 Windows 支援段落)。"""
    src_skill = pkg / "skills" / "lumos-project-notes"
    dst_skill = skills_dir / "lumos-project-notes"

    if dst_skill.exists() or dst_skill.is_symlink():
        if not force:
            print(f"⚠ {dst_skill} 已存在,加 --force 覆寫(★會先備份★)", file=sys.stderr)
            return 2
        bak = _unique_backup_path(dst_skill)
        dst_skill.rename(bak)
        print(f"  已備份既有 skill → {bak}")

    shutil.copytree(src_skill, dst_skill)
    print(f"✓ skill: {dst_skill}")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)

    # 包的位置 = 本檔案所在目錄(隨包走,不需要參數)。`Path(__file__).resolve()`
    # 本身就會解掉 symlink 鏈——這正是薄殼 install.sh/install.ps1 仍保留(對
    # 自身路徑的)symlink 解析迴圈的理由:要先把正確的 install.py 絕對路徑
    # 傳給 python 直譯器,之後這裡才能用 __file__ 精準定位 PKG。
    pkg = Path(__file__).resolve().parent
    bin_dir = Path.home() / ".local" / "bin"
    skills_dir = Path.home() / ".claude" / "skills"
    src_cli = pkg / "scripts" / "lumos"
    src_skill = pkg / "skills" / "lumos-project-notes"

    if not src_cli.is_file():
        print(f"ERROR: 找不到 {src_cli}", file=sys.stderr)
        return 2
    if not src_skill.is_dir():
        print(f"ERROR: 找不到 {src_skill}", file=sys.stderr)
        return 2

    force = "--force" in argv
    here = "--here" in argv

    # ⓪ 注入目標守衛(見模組 docstring)。
    target_dir = Path.cwd().resolve()
    target_claude_md = target_dir / "CLAUDE.md"
    print(f"目標專案: {target_dir}")
    print(f"將修改: {target_claude_md}")

    if not here:
        home = Path.home()
        home_phys = home.resolve() if home.is_dir() else home
        if target_dir == home_phys:
            print(f"ERROR: {target_dir} 是你的家目錄($HOME),不是專案根目錄——拒絕注入。",
                  file=sys.stderr)
            print("  若確定要在這裡安裝,加 --here 明示。", file=sys.stderr)
            return 2

        looks_like_project_root = (target_dir / ".git").exists()
        if not looks_like_project_root:
            docs_dir = target_dir / "docs"
            if docs_dir.is_dir():
                looks_like_project_root = any(
                    p.is_dir() for p in docs_dir.glob("*-knowledge"))
        if not looks_like_project_root and target_claude_md.is_file():
            looks_like_project_root = True

        if not looks_like_project_root:
            print(f"ERROR: {target_dir} 這裡看起來不是專案根目錄——拒絕注入。",
                  file=sys.stderr)
            print("  已檢查(至少一項成立才放行):.git / docs/*-knowledge/ / 既有 CLAUDE.md",
                  file=sys.stderr)
            print("  結果一項都沒有。若確定要在這裡安裝,加 --here 明示。", file=sys.stderr)
            return 2

        if ((target_dir / "skills" / "lumos-project-notes").is_dir()
                and (target_dir / "scripts" / "lumos").is_file()
                and (target_dir / "scripts" / "templates" / "graph-discipline.md").is_file()):
            print(f"ERROR: {target_dir} 是 lumos 工具鏈的來源 repo,不是要交接的專案——拒絕注入。",
                  file=sys.stderr)
            print("  若確定要在這裡安裝,加 --here 明示。", file=sys.stderr)
            return 2

    bin_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    rc = _install_cli(pkg, bin_dir, force)
    if rc != 0:
        return rc

    rc = _install_skill(pkg, skills_dir, force)
    if rc != 0:
        return rc

    # ③ 專案層 CLAUDE.md —— 用策展後的精簡版紀律區塊取代完整版(若有)/附加。
    # 範本 = 本包隨附的 claude-block.md(靜態檔,不在腳本裡手刻字串)。
    block_template = pkg / "claude-block.md"
    if not block_template.is_file():
        print(f"ERROR: 找不到 {block_template}", file=sys.stderr)
        return 2
    template_text = block_template.read_text(encoding="utf-8")
    merge_rc, new_text = _merge_claude_md_text(target_claude_md, template_text)
    if merge_rc != 0:
        return merge_rc
    target_claude_md.write_text(new_text, encoding="utf-8")
    print(f"✓ CLAUDE.md 精簡版紀律區塊已安裝/更新: {target_claude_md}")

    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if str(bin_dir) not in path_entries:
        if IS_WIN:
            print(f"⚠ {bin_dir} 不在當前 PATH — Windows:把 {bin_dir} 加進使用者 PATH(系統環境變數)",
                  file=sys.stderr)
        else:
            print(f'⚠ {bin_dir} 不在 PATH,請自行加入 shell 設定檔(例如 export PATH="{bin_dir}:$PATH")',
                  file=sys.stderr)
    else:
        print(f"  {bin_dir} 已在 PATH")

    print()
    print("裝好了。驗證: lumos --help")
    print("★這是凍結快照,不是發布通道——不會有更新。出問題請直接改 Python 原始碼。★")
    return 0


def _main_guarded(argv=None):
    """把 `main()` 的檔案系統例外轉成一句可行動的訊息 + rc2,不噴 traceback。

    ★這裡刻意不學 uninstall.py 的做法★:uninstall 宣告的合約是「各步互不阻擋」
    (一步失敗其餘照跑),所以它是逐步吞 `OSError` 再彙總;install 的 `main()`
    正好相反——它是★遇錯早退★的(`rc != 0` 就 return),因為每一步依賴前一步,
    裝到一半就該停下來,而不是硬著頭皮把 skill 裝進一個沒有 CLI 的環境。
    在 install 這邊逐處包 try/except 讓它繼續跑會★把它的順序語意改掉★,
    那不是修 bug 是製造 bug。

    所以這裡只做一件事:例外別以 traceback 的形式丟給使用者。使用者看到
    `PermissionError` 的堆疊完全不知道要幹嘛,看到「權限不足,請確認 X 可寫」
    才知道。控制流一行都沒動。

    ★半成品狀態是已知且刻意保留的★:中途失敗會留下已完成的前幾步(例如 CLI
    裝好了、skill 沒裝成)。精簡版不做交易式回滾——回滾本身也會失敗,而且刪
    使用者的東西風險比留著高;重跑 `install.py --force` 即可收斂到完整狀態。
    """
    try:
        return main(argv)
    except UnicodeDecodeError as e:
        # ★同一個 reviewer、同一種漏法(2026-08-02)★:`_merge_claude_md_text()` 會
        # 讀★使用者既有的★ CLAUDE.md,那份檔案不是我們寫的、編碼不歸我們管。
        # 不是合法 utf-8 時拋的是 UnicodeDecodeError——★它繼承 ValueError 不是
        # OSError★,只接 OSError 攔不到,照樣 traceback + rc1。
        print(f"ERROR: 讀取既有 CLAUDE.md 時發現它不是合法 utf-8,已中止: {e}", file=sys.stderr)
        print("  本安裝器只處理 utf-8;不會在看不懂內容的情況下改寫你的 CLAUDE.md。", file=sys.stderr)
        print("  請先確認該檔編碼(或另存成 utf-8)後重跑。", file=sys.stderr)
        # ★與下面 OSError 分支對稱地講一句半成品狀態(2026-08-02 交付包端到端真跑
        # 時發現只有 OSError 那條有講)★——①CLI 與②skill 這時已經裝好了,只有
        # ③CLAUDE.md 沒動;不講的話使用者會以為整件事失敗、跑去手動清理已裝好的東西。
        print("  ★①全域指令與②skill 這時已經裝好、不會被回滾★,只有③CLAUDE.md 沒動;"
              "修好編碼後重跑即可補上(重跑是冪等的)。", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"ERROR: 安裝過程發生檔案系統錯誤,已中止: {e}", file=sys.stderr)
        print("  常見原因:目標路徑沒有寫入權限、磁碟空間不足、檔案被其他程式鎖住(Windows)。",
              file=sys.stderr)
        print("  ★已完成的步驟不會被回滾★——排除原因後重跑本腳本(加 --force 覆寫已裝好的部分)。",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(_main_guarded())
