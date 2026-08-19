$ErrorActionPreference = "Stop"

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $workspace "livetr-captures\180342-latest.md"
$repo = Join-Path $workspace "ax"
$destDir = Join-Path $repo "AIS26"
$chunkDir = Join-Path $destDir "chunks-afternoon"
$fileName = "live-translation-afternoon.md"
$relativePath = "AIS26/$fileName"
$dest = Join-Path $destDir $fileName
$sessionStartKst = [DateTimeOffset]::Parse("2026-08-19T13:00:00+09:00")

if (!(Test-Path -LiteralPath $source)) {
  throw "Source transcript not found: $source"
}

if (!(Test-Path -LiteralPath $repo)) {
  throw "Repository not found: $repo"
}

Set-Location -LiteralPath $repo
git pull --rebase origin main

New-Item -ItemType Directory -Force -Path $destDir | Out-Null
New-Item -ItemType Directory -Force -Path $chunkDir | Out-Null

function Get-KstBucket {
  param([DateTimeOffset]$Timestamp)

  $kst = [TimeZoneInfo]::FindSystemTimeZoneById("Korea Standard Time")
  $local = [TimeZoneInfo]::ConvertTime($Timestamp, $kst)
  $minute = [Math]::Floor($local.Minute / 10) * 10
  $start = New-Object DateTimeOffset(
    $local.Year,
    $local.Month,
    $local.Day,
    $local.Hour,
    [int]$minute,
    0,
    $local.Offset
  )
  $end = $start.AddMinutes(10)

  [pscustomobject]@{
    Key = "{0:HHmm}-{1:HHmm}" -f $start, $end
    Start = $start
    End = $end
  }
}

function Write-LiveTrChunks {
  param(
    [string]$TranscriptPath,
    [string]$OutputDir
  )

  $lines = [System.IO.File]::ReadAllLines($TranscriptPath, [System.Text.Encoding]::UTF8)
  $groups = New-Object System.Collections.Generic.List[object]
  $current = $null

  foreach ($line in $lines) {
    if ($line -match '^- (?<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z) ') {
      if ($null -ne $current) {
        $groups.Add($current)
      }

      $timestamp = [DateTimeOffset]::Parse(
        $Matches.ts,
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AssumeUniversal
      )

      $current = [pscustomobject]@{
        Timestamp = $timestamp
        Lines = New-Object System.Collections.Generic.List[string]
      }
    }

    if ($null -ne $current) {
      $current.Lines.Add($line)
    }
  }

  if ($null -ne $current) {
    $groups.Add($current)
  }

  if ($groups.Count -eq 0) {
    $readme = New-Object System.Collections.Generic.List[string]
    $readme.Add("# LiveTR afternoon chunks")
    $readme.Add("")
    $readme.Add("- Full transcript: ../$fileName")
    $readme.Add("- Latest 10 minutes: not available yet")
    $readme.Add("")
    $readme.Add("No afternoon messages captured yet.")
    [System.IO.File]::WriteAllText((Join-Path $OutputDir "README.md"), ($readme -join "`n") + "`n", [System.Text.Encoding]::UTF8)
    return
  }

  $bucketMap = @{}
  foreach ($group in $groups) {
    $bucket = Get-KstBucket -Timestamp $group.Timestamp
    if (!$bucketMap.ContainsKey($bucket.Key)) {
      $bucketMap[$bucket.Key] = [pscustomobject]@{
        Bucket = $bucket
        Items = New-Object System.Collections.Generic.List[object]
      }
    }
    $bucketMap[$bucket.Key].Items.Add($group)
  }

  $ordered = $bucketMap.Values | Sort-Object { $_.Bucket.Start }

  foreach ($entry in $ordered) {
    $path = Join-Path $OutputDir "$($entry.Bucket.Key).md"
    $content = New-Object System.Collections.Generic.List[string]
    $content.Add("# LiveTR $($entry.Bucket.Key)")
    $content.Add("")
    $content.Add("- Source: $fileName")
    $content.Add("- Window: $($entry.Bucket.Start.ToString('yyyy-MM-dd HH:mm'))-$($entry.Bucket.End.ToString('HH:mm')) KST")
    $content.Add("- Messages: $($entry.Items.Count)")
    $content.Add("")

    foreach ($item in $entry.Items) {
      foreach ($itemLine in $item.Lines) {
        $content.Add($itemLine)
      }
      $content.Add("")
    }

    [System.IO.File]::WriteAllText($path, ($content -join "`n") + "`n", [System.Text.Encoding]::UTF8)
  }

  $latest = $ordered | Select-Object -Last 1
  Copy-Item -LiteralPath (Join-Path $OutputDir "$($latest.Bucket.Key).md") -Destination (Join-Path $OutputDir "latest-10min.md") -Force

  $readme = New-Object System.Collections.Generic.List[string]
  $readme.Add("# LiveTR afternoon chunks")
  $readme.Add("")
  $readme.Add("- Full transcript: ../$fileName")
  $readme.Add("- Latest 10 minutes: ./latest-10min.md")
  $readme.Add("")
  $readme.Add("## Windows")
  $readme.Add("")

  foreach ($entry in ($ordered | Sort-Object { $_.Bucket.Start } -Descending)) {
    $name = "$($entry.Bucket.Key).md"
    $readme.Add("- [$($entry.Bucket.Key)](./$name) - $($entry.Items.Count) messages")
  }

  [System.IO.File]::WriteAllText((Join-Path $OutputDir "README.md"), ($readme -join "`n") + "`n", [System.Text.Encoding]::UTF8)
}

function Write-FilteredTranscript {
  param(
    [string]$SourcePath,
    [string]$OutputPath,
    [DateTimeOffset]$StartKst
  )

  $lines = [System.IO.File]::ReadAllLines($SourcePath, [System.Text.Encoding]::UTF8)
  $header = New-Object System.Collections.Generic.List[string]
  $groups = New-Object System.Collections.Generic.List[object]
  $current = $null
  $seenFirstMessage = $false

  foreach ($line in $lines) {
    if ($line -match '^- (?<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z) ') {
      $seenFirstMessage = $true
      if ($null -ne $current) {
        $groups.Add($current)
      }

      $timestamp = [DateTimeOffset]::Parse(
        $Matches.ts,
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AssumeUniversal
      )

      $current = [pscustomobject]@{
        Timestamp = $timestamp
        Lines = New-Object System.Collections.Generic.List[string]
      }
    }

    if ($seenFirstMessage) {
      if ($null -ne $current) {
        $current.Lines.Add($line)
      }
    } else {
      $header.Add($line)
    }
  }

  if ($null -ne $current) {
    $groups.Add($current)
  }

  $startUtc = $StartKst.ToUniversalTime()
  $filtered = @($groups | Where-Object { $_.Timestamp -ge $startUtc })

  $content = New-Object System.Collections.Generic.List[string]
  $content.Add("# LiveTR 180342 - Afternoon Session")
  $content.Add("")
  $content.Add("- Source room: 180342")
  $content.Add("- Saved at: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))")
  $content.Add("- Language: ko")
  $content.Add("- Session start: $($StartKst.ToString('yyyy-MM-dd HH:mm')) KST")
  $content.Add("- Messages: $($filtered.Count)")
  $content.Add("")

  if ($filtered.Count -eq 0) {
    $content.Add("No afternoon messages captured yet.")
  } else {
    foreach ($group in $filtered) {
      foreach ($groupLine in $group.Lines) {
        $content.Add($groupLine)
      }
      $content.Add("")
    }
  }

  [System.IO.File]::WriteAllText($OutputPath, ($content -join "`n").TrimEnd() + "`n", [System.Text.Encoding]::UTF8)
}

Write-FilteredTranscript -SourcePath $source -OutputPath $dest -StartKst $sessionStartKst
Write-LiveTrChunks -TranscriptPath $dest -OutputDir $chunkDir

git add -- $relativePath
git add -- "AIS26/chunks-afternoon"

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
  Write-Output "No transcript changes to push."
  exit 0
}

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm K"
git commit -m "Update AIS26 live translation transcript ($stamp)"
git push origin main
