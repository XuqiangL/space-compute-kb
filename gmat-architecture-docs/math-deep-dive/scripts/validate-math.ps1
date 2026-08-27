# Validate math-deep-dive chapters (run after MD-01..MD-14 land).
# NOTE: pure ASCII only (PowerShell 5.1 reads UTF-8 no-BOM as ANSI); Chinese matched via [char] codes.
$ErrorActionPreference = 'Continue'
$dir = 'L:\gmat888\gmat-architecture-docs\math-deep-dive'
$chapters = @{
  'MD-01-time.md'                  = 15; 'MD-02-coordsystems.md'         = 20;
  'MD-03-orbitelements.md'         = 20; 'MD-04-integrators.md'          = 25;
  'MD-05-interpolation.md'         = 15; 'MD-06-linearalgebra.md'        = 15;
  'MD-07-attitude.md'              = 15; 'MD-08-gravity.md'              = 25;
  'MD-09-atmosphere-srp.md'        = 20; 'MD-10-burns-thrust.md'         = 15;
  'MD-11-solvers.md'               = 20; 'MD-12-estimation-measurements.md' = 25;
  'MD-13-csalt.md'                 = 20; 'MD-14-mathexpressions.md'      = 20
}
$G = [char]0x516C + [char]0x5F0F      # formula word
$IDX = $G + [char]0x7D22 + [char]0x5F15 + [char]0x8868  # formula index table
$patFormula = '(\*\*' + $G + '\*\*|### ' + $G + ')'
$fail = 0
foreach ($name in $chapters.Keys | Sort-Object) {
  $minKB = $chapters[$name]
  $p = Join-Path $dir $name
  if (-not (Test-Path $p)) { 'MISSING      ' + $name; $fail++; continue }
  $item = Get-Item $p
  $kb = [math]::Round($item.Length/1KB, 1)
  $txt = Get-Content $p -Raw -Encoding UTF8
  $formulaCount = ([regex]::Matches($txt, $patFormula)).Count
  $hasIndexTable = $txt.Contains($IDX)
  $sizeOK = $item.Length -ge ($minKB * 1KB)
  $status = if ($sizeOK -and $formulaCount -ge 5 -and $hasIndexTable) { 'OK' } else { 'CHECK' }
  ('{0,-34} {1,7} KB  formulas={2,3} index={3} sizeOK={4}  [{5}]' -f $name, $kb, $formulaCount, $hasIndexTable, $sizeOK, $status)
  if ($status -eq 'CHECK') { $fail++ }
}
''
'RESULT: ' + ($chapters.Count - $fail) + '/' + $chapters.Count + ' passed'
if ($fail -gt 0) { exit 1 } else { exit 0 }
