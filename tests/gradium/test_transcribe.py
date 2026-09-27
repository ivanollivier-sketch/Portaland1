"""Offline tests: no real credentials, uploaded audio or API calls."""
import asyncio
import contextlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, mock_open, patch

import transcribe


class GradiumSmokeTests(unittest.TestCase):
    def test_stream_collects_text_and_wav_header(self):
        async def messages():
            yield SimpleNamespace(text="Bonjour", start_s=0.1)
            yield SimpleNamespace(text="Portaland", start_s=0.8)

        class Client:
            async def stt_stream(self, setup, chunks):
                self.setup = setup
                self.audio = b"".join([block async for block in chunks])
                return SimpleNamespace(iter_text=messages)

        client = Client()
        audio = Mock()
        audio.open.return_value = io.BytesIO(b"RIFF-test-WAV")
        result = asyncio.run(transcribe.transcribe(audio, "fr", 10, lambda: client))
        self.assertEqual(result["text"], "Bonjour Portaland")
        self.assertEqual(client.audio, b"RIFF-test-WAV")
        self.assertEqual(client.setup["input_format"], "wav")
        self.assertEqual(client.setup["json_config"]["language"], "fr")

    def test_json_and_text_outputs(self):
        for suffix in (".json", ".txt"):
            output = Mock(suffix=suffix)
            output.open = mock_open()
            result = {"text": "Équipe Portaland", "segments": []}
            transcribe.save_transcript(result, output)
            written = output.open().write.call_args.args[0]
            if suffix == ".json":
                self.assertEqual(json.loads(written), result)
            else:
                self.assertEqual(written, "Équipe Portaland\n")
            output.open.assert_any_call("x", encoding="utf-8", newline="\n")

    def test_missing_key_makes_no_request(self):
        with patch.object(transcribe, "validate_wav"), patch.dict("os.environ", {}, clear=True), patch.object(Path, "exists", return_value=False), patch.object(transcribe, "transcribe", new_callable=AsyncMock) as request, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(transcribe.main(["sample.wav"]), 2)
            request.assert_not_called()

    def test_invalid_audio_is_rejected(self):
        path = Mock(suffix=".mp3")
        path.is_file.return_value = True
        with self.assertRaises(transcribe.TestInputError):
            transcribe.validate_wav(path)

    def test_stereo_audio_is_rejected(self):
        path = Mock(suffix=".wav")
        path.is_file.return_value = True
        wav = Mock()
        wav.getcomptype.return_value = "NONE"
        wav.getnchannels.return_value = 2
        with patch.object(transcribe.wave, "open") as opened:
            opened.return_value.__enter__.return_value = wav
            with self.assertRaises(transcribe.TestInputError):
                transcribe.validate_wav(path)

    def test_server_error_details_are_not_displayed(self):
        # No key is populated: only replace the presence check for this offline test.
        stderr = io.StringIO()
        with patch.object(transcribe, "validate_wav"), patch.object(transcribe, "key_configured", return_value=True), patch.object(Path, "exists", return_value=False), patch.object(Path, "mkdir"), patch.object(transcribe, "transcribe", new_callable=AsyncMock, side_effect=RuntimeError("private-server-diagnostic")), contextlib.redirect_stderr(stderr):
            self.assertEqual(transcribe.main(["sample.wav"]), 1)
        self.assertNotIn("private-server-diagnostic", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
