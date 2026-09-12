param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

# Builds the fable-r2d2 video soundtrack: Windows System.Speech narration for each storyboard
# chapter, mixed with the original robot WAV clips in firmware/pi/sounds. Local only: no
# network, no account and no scheduled task. Fails loudly if a narration line does not fit its
# chapter window or if two clips would overlap.

$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
    throw 'OutputPath must be an absolute WAV path.'
}
$outputFile = [System.IO.Path]::GetFullPath($OutputPath)
if ([System.IO.Path]::GetExtension($outputFile) -ne '.wav') {
    throw 'OutputPath must have a .wav extension.'
}
if (Test-Path -LiteralPath $outputFile) {
    throw 'OutputPath already exists. Choose a new output path.'
}
if (-not (Test-Path -LiteralPath (Split-Path $outputFile -Parent) -PathType Container)) {
    throw 'OutputPath parent directory must already exist.'
}
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$ffprobe = (Get-Command ffprobe -ErrorAction Stop).Source
$story = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'video_storyboard.json') -Raw | ConvertFrom-Json
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$total = [double]$story.total_seconds
$soundDirectory = Join-Path $projectRoot $story.sound_directory

function Get-AudioDuration([string]$Path) {
    $probe = & $ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $Path
    if ($LASTEXITCODE -ne 0) { throw "Cannot probe audio: $Path" }
    return [double]::Parse(($probe -join '').Trim(), $culture)
}

Add-Type -AssemblyName System.Speech
$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$scratchName = 'r2d2-video-audio-' + [guid]::NewGuid().ToString('N')
$scratch = Join-Path $tempRoot $scratchName
New-Item -ItemType Directory -Path $scratch | Out-Null
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$clips = [System.Collections.Generic.List[object]]::new()

try {
    $installed = @($synth.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo.Name })
    $voice = $null
    foreach ($candidate in $story.narration_voice_candidates) {
        if ($installed -contains $candidate) { $voice = $candidate; break }
    }
    if (-not $voice) {
        throw ("No storyboard narration voice is installed. Installed voices: " + ($installed -join ', '))
    }
    $synth.SelectVoice($voice)
    $synth.Rate = 0
    $synth.Volume = 100
    $format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
    $number = 0
    foreach ($chapter in $story.chapters) {
        if (-not $chapter.narration) { continue }
        $number += 1
        $wav = Join-Path $scratch ('narration-{0:D2}.wav' -f $number)
        $synth.SetOutputToWaveFile($wav, $format)
        $synth.Speak($chapter.narration)
        $synth.SetOutputToNull()
        $duration = Get-AudioDuration $wav
        $start = if ($null -ne $chapter.narration_start) { [double]$chapter.narration_start } else { [double]$chapter.start + 0.35 }
        if ($start -lt [double]$chapter.start) {
            throw "Narration starts before its chapter: $($chapter.name)"
        }
        if ($start + $duration -gt [double]$chapter.end - 0.2) {
            throw "Narration exceeds its chapter window: $($chapter.name), $duration seconds from $start. Shorten the narration."
        }
        $clips.Add([pscustomobject]@{
            kind = 'narration'; start = $start; duration = $duration
            path = $wav; text = $chapter.narration
        })
    }
    foreach ($cue in $story.audio_cues) {
        $wav = Join-Path $soundDirectory $cue.file
        if (-not (Test-Path -LiteralPath $wav -PathType Leaf)) { throw "Missing original robot clip: $($cue.file)" }
        $clips.Add([pscustomobject]@{
            kind = 'robot'; start = [double]$cue.start; duration = (Get-AudioDuration $wav)
            path = $wav; text = $cue.text
        })
    }
    $ordered = @($clips | Sort-Object start)
    $previousEnd = 0.0
    foreach ($clip in $ordered) {
        if ($clip.start -lt $previousEnd -or $clip.start + $clip.duration -gt $total) {
            throw "Audio cue overlaps another cue or exceeds the video: '$($clip.text)' at $($clip.start) s"
        }
        $previousEnd = $clip.start + $clip.duration
    }

    $ffmpegArguments = [System.Collections.Generic.List[string]]::new()
    foreach ($item in @('-hide_banner', '-loglevel', 'error', '-n', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono')) {
        $ffmpegArguments.Add($item)
    }
    $filter = [System.Collections.Generic.List[string]]::new()
    $mixInputs = '[0:a]'
    for ($index = 0; $index -lt $ordered.Count; $index++) {
        $clip = $ordered[$index]
        $ffmpegArguments.Add('-i')
        $ffmpegArguments.Add($clip.path)
        $inputIndex = $index + 1
        $delay = [int][math]::Round($clip.start * 1000)
        $gain = if ($clip.kind -eq 'robot') { 'I=-20' } else { 'I=-17' }
        $filter.Add("[$($inputIndex):a]loudnorm=$($gain):TP=-2:LRA=7,aformat=sample_rates=48000:channel_layouts=mono,adelay=$($delay):all=1[a$inputIndex]")
        $mixInputs += "[a$inputIndex]"
    }
    $durationText = $total.ToString('0.###', $culture)
    $filter.Add("${mixInputs}amix=inputs=$($ordered.Count + 1):duration=first:normalize=0,alimiter=limit=0.95:level=0,atrim=duration=$durationText,asetpts=N/SR/TB[out]")
    foreach ($item in @('-filter_complex', ($filter -join ';'), '-map', '[out]', '-t', $durationText, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', $outputFile)) {
        $ffmpegArguments.Add($item)
    }
    & $ffmpeg @ffmpegArguments
    if ($LASTEXITCODE -ne 0) { throw 'Video soundtrack rendering failed.' }
    $outputDuration = Get-AudioDuration $outputFile
    if ([math]::Abs($outputDuration - $total) -gt 0.0001) { throw "Wrong soundtrack length: $outputDuration" }
    & $ffmpeg -hide_banner -loglevel error -i $outputFile -f null -
    if ($LASTEXITCODE -ne 0) { throw 'Soundtrack full-decode check failed.' }
    [pscustomobject]@{
        output = $outputFile; voice = $voice
        duration_seconds = $outputDuration; sample_rate = 48000; channels = 1
        full_decode = 'PASS'; overlapping_cues = 0; clip_count = $ordered.Count
        clips = @($ordered | Select-Object kind, start, duration, text)
    } | ConvertTo-Json -Depth 5
} finally {
    $synth.Dispose()
    # Validate the exact unique child of Temp before removing this script's scratch WAVs.
    $resolvedScratch = [System.IO.Path]::GetFullPath($scratch)
    $expectedScratch = [System.IO.Path]::GetFullPath((Join-Path $tempRoot $scratchName))
    if ($resolvedScratch.Equals($expectedScratch, [StringComparison]::OrdinalIgnoreCase) -and
        ([System.IO.Path]::GetDirectoryName($resolvedScratch)).Equals($tempRoot, [StringComparison]::OrdinalIgnoreCase) -and
        (Split-Path $resolvedScratch -Leaf) -match '^r2d2-video-audio-[0-9a-f]{32}$') {
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
    } else {
        throw 'Refused scratch cleanup because the resolved path failed validation.'
    }
}
