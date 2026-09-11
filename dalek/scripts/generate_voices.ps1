param(
    [string]$Voice = 'Microsoft David Desktop',
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$wavDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ('dalek-voice-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $wavDirectory | Out-Null
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $synth.SelectVoice($Voice)
    $synth.Rate = -1
    $synth.Volume = 100
    $format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(22050, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
    foreach ($phrase in Import-Csv -LiteralPath (Join-Path $projectRoot 'audio/phrases.csv')) {
        $wavPath = Join-Path $wavDirectory ([System.IO.Path]::GetFileNameWithoutExtension($phrase.file) + '.wav')
        $synth.SetOutputToWaveFile($wavPath, $format)
        $synth.Speak($phrase.text)
        $synth.SetOutputToNull()
    }
    & $Python (Join-Path $PSScriptRoot 'process_voices.py') --input $wavDirectory --voice $Voice
    if ($LASTEXITCODE -ne 0) { throw 'Voice processing failed.' }
} finally {
    $synth.Dispose()
    # Only delete the unique scratch directory created in the system temp directory above.
    $resolvedWav = [System.IO.Path]::GetFullPath($wavDirectory)
    $resolvedTemp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    if ($resolvedWav.StartsWith($resolvedTemp, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path $resolvedWav -Leaf).StartsWith('dalek-voice-')) {
        Remove-Item -LiteralPath $resolvedWav -Recurse -Force
    }
}
