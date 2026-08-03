# get.ps1 -- Lumos slim edition, one-line installer entry (Windows / PowerShell)
#
# Usage:
#   irm <raw-url>/get.ps1 | iex
#
# ASCII-ONLY, NO BOM. Do not add Chinese comments or a BOM to this file.
# Rationale and full design notes (in Chinese): see WINDOWS-NOTES.md next to this file.
#   - No BOM + non-ASCII bytes  -> PowerShell 5.1 reads the file with the system ANSI
#     codepage (cp950/936/932/949). A DBCS lead byte swallows the following byte; when
#     that byte is a double quote, quoting breaks and the parser fails on an innocent
#     ASCII line. Real-machine result: install never runs.
#   - BOM + `irm | iex`         -> the BOM is NOT stripped (iex gets a plain string),
#     U+FEFF becomes part of line 1 and the first comment is executed as a command.
#   ASCII-only removes both failure modes instead of trading one for the other.

function Invoke-Get {
  # NOTE: the parameter must NOT be named $Args. $Args is a PowerShell automatic
  # variable (the function's own unbound arguments) and shadows anything passed in,
  # so `@Args` splats to nothing and every command-line flag is silently dropped.
  param($RepoUrl, $Dest, $ScriptArgs)

  $ErrorActionPreference = "Stop"

  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: git not found. Install git first, then re-run: https://git-scm.com/download/win" -ErrorAction Continue
    return 2
  }

  if (Test-Path (Join-Path $Dest ".git")) {
    Write-Host "Existing $Dest found, updating..."
    git -C $Dest pull --ff-only -q
    # $ErrorActionPreference = "Stop" does NOT cover native executables: git.exe
    # returning non-zero will not terminate. Check $LASTEXITCODE explicitly.
    if ($LASTEXITCODE -ne 0) {
      Write-Error "ERROR: update of $Dest failed (local changes, or not a fast-forward). If you edited files in there, back them up, delete $Dest and re-run. NOTE: if a previous uninstall reported a removal failure, this directory may be a partially deleted clone -- in that case just remove it entirely." -ErrorAction Continue
      return 2
    }
  } elseif (Test-Path $Dest) {
    Write-Error "ERROR: $Dest exists but is not a clone of this package (no $Dest\.git). Refusing to overwrite; inspect and remove it yourself." -ErrorAction Continue
    return 2
  } else {
    Write-Host "First install, cloning into $Dest ..."
    git clone -q $RepoUrl $Dest
    if ($LASTEXITCODE -ne 0) {
      Write-Error "ERROR: clone of $RepoUrl failed (check your network connection and whether you have access to that repo)." -ErrorAction Continue
      return 2
    }
  }

  $InstallScript = Join-Path $Dest "install.ps1"
  if (-not (Test-Path $InstallScript)) {
    Write-Error "ERROR: $InstallScript not found -- the package looks incomplete." -ErrorAction Continue
    return 2
  }

  # `| Out-Host` is required: a PowerShell function's `return` also emits every
  # unconsumed output of the function. Without it the caller receives Object[]
  # instead of an Int32 and SetShouldExit throws.
  & $InstallScript @ScriptArgs | Out-Host
  return $LASTEXITCODE
}

$RepoUrl = if ($env:LUMOS_SLIM_REPO_URL) { $env:LUMOS_SLIM_REPO_URL } else { "https://github.com/citrus-android-developer/Citrus_Lumos.git" }
$Dest = Join-Path $HOME ".lumos-slim"

$rc = Invoke-Get -RepoUrl $RepoUrl -Dest $Dest -ScriptArgs $args
$global:LASTEXITCODE = $rc
