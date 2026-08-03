# uninstall.ps1 -- Lumos slim edition, Windows thin shell. Forwards everything to uninstall.py.
#
# ASCII-ONLY, NO BOM. Do not add Chinese comments or a BOM to this file.
# Rationale and full design notes (in Chinese): see WINDOWS-NOTES.md next to this file.
#   - No BOM + non-ASCII bytes -> PowerShell 5.1 reads the file with the system ANSI
#     codepage; a DBCS lead byte swallows the next byte and breaks quoting, and the
#     parser then fails on an innocent ASCII line.
#   - BOM + `irm | iex`        -> the BOM is not stripped, U+FEFF ends up inside
#     line 1 and the first comment gets executed as a command.
#   ASCII-only removes both failure modes instead of trading one for the other.
#
# $Pkg is resolved OUTSIDE the function on purpose: inside a function $MyInvocation
# refers to the function's own call site, not to this script, so .MyCommand.Path
# would no longer locate the package directory.

function Invoke-Uninstall {
  # NOTE: the parameter must NOT be named $Args -- that is a PowerShell automatic
  # variable (the function's own unbound arguments). It shadows whatever the caller
  # passes, so `@Args` splats to nothing and every flag (--force / --here / -y) is
  # silently dropped. Real-machine symptom: passing --force still says "add --force".
  param($Pkg, $ScriptArgs)

  $ErrorActionPreference = "Stop"

  $Py = Get-Command python3 -ErrorAction SilentlyContinue
  if (-not $Py) { $Py = Get-Command python -ErrorAction SilentlyContinue }
  if (-not $Py) {
    Write-Error "ERROR: neither python3 nor python found. Install Python 3 first, then re-run." -ErrorAction Continue
    return 2
  }

  # `| Out-Host` is required: a function's `return` also emits every unconsumed
  # output of the function, so without it the caller receives Object[] not Int32.
  & $Py.Source "$Pkg\uninstall.py" @ScriptArgs | Out-Host
  return $LASTEXITCODE
}

$Pkg = Split-Path -Parent $MyInvocation.MyCommand.Path
$rc = Invoke-Uninstall -Pkg $Pkg -ScriptArgs $args
$global:LASTEXITCODE = $rc
