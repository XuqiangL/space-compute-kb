# Generate the complete file inventory appendix for the GMAT repo.
# Output: L:\gmat888\gmat-architecture-docs\APPENDIX-all-files.md
# NOTE: this script must stay pure ASCII (PowerShell 5.1 reads UTF-8 no-BOM as ANSI).
$ErrorActionPreference = 'Stop'
$root = 'L:\gmat888'
$out  = Join-Path $root 'gmat-architecture-docs\APPENDIX-all-files.md'
$skipPattern = '\\\.git\\|\\gmat-architecture-docs\\'
$files = Get-ChildItem $root -Recurse -Force -File | Where-Object { $_.FullName -notmatch $skipPattern }
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# Appendix: complete file inventory of the GMAT repository')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('> Generated: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + '; repo: ' + $root + ' (main, commit ce6eba2)')
[void]$sb.AppendLine('> Scope: all files except `.git\` and the `gmat-architecture-docs\` folder itself. Total: ' + $files.Count)
[void]$sb.AppendLine('')
$groups = $files | Group-Object { $_.FullName.Substring($root.Length + 1).Split('\')[0] } | Sort-Object Name
foreach ($g in $groups) {
  [void]$sb.AppendLine('## ' + $g.Name + '  (' + $g.Count + ' files)')
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('```')
  $sorted = $g.Group | Sort-Object { $_.FullName }
  foreach ($f in $sorted) {
    $rel = $f.FullName.Substring($root.Length + 1)
    $kb  = [math]::Round($f.Length / 1KB, 1)
    [void]$sb.AppendLine(('{0,10} KB  {1}' -f $kb, $rel))
  }
  [void]$sb.AppendLine('```')
  [void]$sb.AppendLine('')
}
Set-Content -Path $out -Value $sb.ToString() -Encoding UTF8
'Done: ' + $files.Count + ' files -> ' + $out
