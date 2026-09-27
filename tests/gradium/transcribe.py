"""Isolated WAV -> official Gradium SDK -> UTF-8 transcript smoke test."""
import argparse
import asyncio
from contextlib import aclosing
import json
import logging
import math
import os
from pathlib import Path
import sys
import wave


class TestInputError(Exception):
    """Safe local diagnostic, containing no credentials or server payload."""


def key_configured():
    return bool(os.environ.get("GRADIUM_API_KEY", "").strip())


def validate_wav(path):
    if not path.is_file():
        raise TestInputError("Input audio file does not exist.")
    if path.suffix.lower() != ".wav":
        raise TestInputError("This minimal test accepts WAV files only.")
    try:
        with wave.open(str(path), "rb") as audio:
            if audio.getcomptype() != "NONE" or audio.getnchannels() != 1 or audio.getsampwidth() != 2:
                raise TestInputError("Use an uncompressed, mono, 16-bit PCM WAV file.")
            if audio.getframerate() not in {8000, 16000, 22050, 24000, 44100, 48000}:
                raise TestInputError("Unsupported sample rate. A 24 kHz WAV is recommended.")
            frames = audio.getnframes()
            if frames == 0:
                raise TestInputError("The WAV file has no audio frames.")
            # Validate actual data, not only the size claimed in the WAV header.
            actual = 0
            while block := audio.readframes(32768):
                actual += len(block)
            if actual != frames * 2:
                raise TestInputError("The WAV file is truncated or has invalid frame data.")
    except (wave.Error, EOFError) as exc:
        raise TestInputError("Invalid PCM WAV file.") from exc


async def audio_chunks(path):
    # Send the WAV header as well as its samples with input_format='wav'.
    with path.open("rb") as source:
        while chunk := source.read(4096):
            yield chunk
            await asyncio.sleep(0)


async def transcribe(path, language, timeout, client_factory=None):
    if client_factory is None:
        from gradium.client import GradiumClient
        client_factory = GradiumClient
    # The SDK reads GRADIUM_API_KEY itself. Never pass keys as CLI arguments.
    client = client_factory()
    setup = {"model_name": "default", "input_format": "wav", "json_config": {"language": language}}
    segments = []
    async with asyncio.timeout(timeout):
        async with aclosing(audio_chunks(path)) as chunks:
            stream = await client.stt_stream(setup, chunks)
            async with aclosing(stream.iter_text()) as messages:
                async for segment in messages:
                    # SDK 0.6.4 can default stop_s to start_s; omit misleading end times.
                    segments.append({"text": segment.text, "start_s": segment.start_s})
    return {"text": " ".join(s["text"] for s in segments).strip(),
            "segments": segments, "language_requested": language,
            "model": "default", "input_format": "wav"}


def save_transcript(result, output):
    content = json.dumps(result, ensure_ascii=False, indent=2) if output.suffix.lower() == ".json" else result["text"]
    # Exclusive creation prevents overwriting an existing transcript or input.
    with output.open("x", encoding="utf-8", newline="\n") as target:
        target.write(content + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path, help="Mono 16-bit PCM WAV file")
    parser.add_argument("--output", type=Path, help="New .json or .txt file (default: tests/gradium/output/<audio>.json)")
    parser.add_argument("--language", default="any", choices=("any", "en", "fr", "de", "es", "pt"))
    parser.add_argument("--timeout", type=float, default=120, help="Maximum request duration in seconds")
    args = parser.parse_args(argv)
    # Avoid third-party diagnostics containing HTTP headers or server payloads.
    logging.disable(logging.CRITICAL)
    try:
        validate_wav(args.audio)
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise TestInputError("Timeout must be a positive finite number.")
        output = args.output or Path(__file__).parent / "output" / f"{args.audio.stem}.json"
        if output.suffix.lower() not in {".json", ".txt"}:
            raise TestInputError("Output must use .json or .txt.")
        if output.exists():
            raise TestInputError("Output already exists. Choose a new output filename.")
        if not key_configured():
            raise TestInputError("Set GRADIUM_API_KEY securely in the environment before running this test.")
        output.parent.mkdir(parents=True, exist_ok=True)
        result = asyncio.run(transcribe(args.audio, args.language, args.timeout))
        save_transcript(result, output)
        print("Transcript saved." if result["text"] else "Transcript saved; no speech was recognized.")
        return 0
    except TestInputError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except TimeoutError:
        print("Gradium request timed out. No transcript was saved.", file=sys.stderr)
        return 1
    except ImportError:
        print("Run this test with its dedicated virtual environment and install requirements.txt.", file=sys.stderr)
        return 2
    except OSError:
        print("Unable to read the audio, write the output, or connect to Gradium. Check paths and network access.", file=sys.stderr)
        return 1
    except Exception:
        # Do not print exception strings, response bodies, headers, or tracebacks.
        print("Gradium transcription failed. Check connectivity, API credentials, account credits, and audio format.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Transcription cancelled.", file=sys.stderr)
        raise SystemExit(130)
