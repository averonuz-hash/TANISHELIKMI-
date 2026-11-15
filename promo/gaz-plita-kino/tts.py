"""Synthesize the Uzbek voice-over lines with Microsoft Edge neural TTS (uz-UZ-MadinaNeural).

Usage: python3 tts.py            -> vo/<id>.mp3 for every line in LINES
The voice is pitched up and slightly slowed to sound like a young girl narrator.
Behind a TLS-intercepting proxy set SSL_CERT_FILE to its CA bundle.
"""
import asyncio
import json
import os
import ssl
import sys

import certifi
import edge_tts
import edge_tts.communicate as comm

CA = os.environ.get("SSL_CERT_FILE") or certifi.where()
comm._SSL_CTX = ssl.create_default_context(cafile=CA)
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = "uz-UZ-MadinaNeural"
PITCH = "+12Hz"   # slightly younger timbre; kept small so the voice stays natural
RATE = "-6%"

LINES = json.load(open(os.path.join(HERE, "voiceover.json"), encoding="utf-8"))


async def synth(line):
    out = os.path.join(HERE, "vo", f"{line['id']}.mp3")
    c = edge_tts.Communicate(line["say"], VOICE, rate=line.get("rate", RATE), pitch=line.get("pitch", PITCH), proxy=PROXY)
    await c.save(out)
    return out


async def main(ids):
    os.makedirs(os.path.join(HERE, "vo"), exist_ok=True)
    for line in LINES:
        if ids and line["id"] not in ids:
            continue
        print("ok", await synth(line))


asyncio.run(main(sys.argv[1:]))
