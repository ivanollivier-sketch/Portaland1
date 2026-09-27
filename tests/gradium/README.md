# Isolated Gradium Speech-to-Text test

`audio.wav → official Gradium Python SDK → transcript.json or transcript.txt`

This folder is independent of Portaland's main/Pipelex pipeline. It does not import or modify the pipeline.

## Environment

Installed and import-checked on Windows with Python **3.14.3** and official SDK **gradium 0.6.4**. The SDK and its dependencies are in `tests/gradium/.venv/`; the project's main environment is unchanged.

To recreate it from the project root:

```powershell
python -m venv tests/gradium/.venv
& .\tests\gradium\.venv\Scripts\python.exe -m pip install -r tests/gradium/requirements.txt
```

## Configure the key without displaying or saving it

Run this in your own PowerShell terminal. The prompt hides your input; the command history contains no key value:

```powershell
$gradiumSecret = Read-Host 'Gradium API key' -AsSecureString
$env:GRADIUM_API_KEY = [System.Net.NetworkCredential]::new('', $gradiumSecret).Password
Remove-Variable gradiumSecret
```

The SDK reads `GRADIUM_API_KEY` from the process environment. The `.env.example` file is an empty reference only; no `.env` loader is used. Do not place the key in source code, CLI arguments, screenshots, or chat. Raw SDK errors and HTTP headers are not printed by this test.

## Run a real transcription

Supply a **mono, uncompressed, 16-bit PCM WAV** file. Recommended sample rate: 24 kHz; the script also accepts 8, 16, 22.05, 44.1 and 48 kHz. Compressed formats such as MP3/M4A and stereo WAV are intentionally outside this minimal test.

From the project root, using your audio file's real path:

```powershell
& .\tests\gradium\.venv\Scripts\python.exe tests/gradium/transcribe.py "C:\path\sample.wav" --language fr --output tests/gradium/output/transcript.json
```

For plain text, choose `--output tests/gradium/output/transcript.txt`. Without `--output`, the script creates `tests/gradium/output/<audio-name>.json`. Existing output files are never overwritten. Language defaults to `any` for automatic detection. `--timeout 120` controls the request timeout.

Running this command uploads the audio to Gradium and uses the account's STT service. JSON stores the full text, text segments and start timestamps. End timestamps are omitted because SDK 0.6.4 can substitute the start timestamp when an end time is missing. The transcript is saved in UTF-8 and is not printed to the terminal.

After testing, remove the key from this terminal session:

```powershell
Remove-Item Env:GRADIUM_API_KEY
```

## Offline checks

```powershell
& .\tests\gradium\.venv\Scripts\python.exe -m unittest discover -s tests/gradium -p test_transcribe.py -v
& .\tests\gradium\.venv\Scripts\python.exe -m pip check
```

These tests mock Gradium; they do not prove that live authentication or speech recognition works. At setup time no API key was configured and no input audio was supplied, so a live transcript has **not** been generated. Complete the command above with your own key and audio to validate the actual service.

## Official references

- [SDK installation and environment authentication](https://docs.gradium.ai/guides/installation)
- [Speech-to-Text SDK: stt_stream and WAV input](https://docs.gradium.ai/guides/speech-to-text)

This example uses the SDK's WebSocket file-streaming API so the installed official SDK is exercised directly.
