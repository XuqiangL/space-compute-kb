# Validate gmat-architecture-docs chapters (run after chapters land).
# Usage: & L:\gmat888\gmat-architecture-docs\scripts\validate-docs.ps1
# NOTE: this script must stay pure ASCII (PowerShell 5.1 reads UTF-8 no-BOM as ANSI).
$ErrorActionPreference = 'Continue'
$docs = 'L:\gmat888\gmat-architecture-docs'
$chapters = @{
  'CH00-README.md'            = 8;    'CH01-build-system.md'      = 20;
  'CH02-foundation.md'        = 40;   'CH03-math.md'              = 30;
  'CH04-executive-factory.md' = 40;   'CH05-command.md'           = 40;
  'CH06-dynamics.md'          = 40;   'CH07-propagator.md'        = 40;
  'CH08-base-subsystems.md'   = 40;   'CH09-gui-core.md'          = 35;
  'CH10-gui-dynamics.md'      = 35;   'CH11-gui-commands.md'      = 35;
  'CH12-applications.md'      = 30;   'CH13-plugins-a.md'         = 30;
  'CH14-plugins-b.md'         = 30;   'CH15-csalt-interop-tests.md' = 30;
  'CH16-docs-data-prototype.md' = 25
}
$fail = 0
foreach ($name in $chapters.Keys | Sort-Object) {
  $minKB = $chapters[$name]
  $p = Join-Path $docs $name
  if (-not (Test-Path $p)) { 'MISSING      ' + $name; $fail++; continue }
  $item = Get-Item $p
  $kb = [math]::Round($item.Length/1KB, 1)
  $lines = (Get-Content $p | Measure-Object -Line).Lines
  $txt = Get-Content $p -Raw
  # ASCII-only invariants: a markdown table row (appendix tables etc.)
  $hasTable = $txt -match '(?m)^\|.+\|.+\|'
  $sizeOK = $item.Length -ge ($minKB * 1KB)
  $isIndex = $name -eq 'CH00-README.md'
  $status = if ($sizeOK -and ($hasTable -or $isIndex)) { 'OK' } else { 'CHECK' }
  ('{0,-30} {1,8} KB {2,7} lines  table={3} sizeOK={4}  [{5}]' -f $name, $kb, $lines, $hasTable, $sizeOK, $status)
  if ($status -eq 'CHECK') { $fail++ }
}
''
'RESULT: ' + ($chapters.Count - $fail) + '/' + $chapters.Count + ' passed'
if ($fail -gt 0) { exit 1 } else { exit 0 }
