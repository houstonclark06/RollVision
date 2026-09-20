#!/usr/bin/env python3
"""
Vision-assist proof of concept.

Pi 4 + Camera Module v2.1 + anything plugged into the 3.5 mm jack.
No buttons, no display, no battery. The keyboard is the button.

    ENTER  describe what the camera sees
    d      more detail about the last photo
    r      read any text in view
    q      quit
"""

import os
import subprocess
import time

from google import genai
from google.genai import types

VISION_MODEL = "gemini-flash-latest"
TTS_MODEL = "gemini-3.1-flash-tts-preview"
TTS_VOICE = "Kore"
TTS_RATE = 24000
CAPTURE_SIZE = (1024, 768)
WARMUP_MS = 1000
SHOT_PATH = "/tmp/poc_shot.jpg"

# Name the sound device explicitly. The ALSA "default" device on the desktop
# image points at HDMI and fails to open. Find yours with: aplay -l
AUDIO_DEVICE = "plughw:CARD=Headphones,DEV=0"

PROMPTS = {
    "describe": (
        "You are acting as the eyes of a person who is blind. Describe this "
        "photo in two sentences, under 40 words total. Lead with the single "
        "most important thing in the frame. Use concrete nouns and plain "
        "words. Never begin with 'the image shows' or 'this appears to be'. "
        "If the photo is too dark, blurry, or close to make out, say only "
        "that, and say what to change."
    ),
    "detail": (
        'You already told the user: "{previous}". Now add only what they '
        "would need in order to act. Cover spatial layout using left, right, "
        "ahead, and rough distances; colors; any text you can read; people "
        "and what they are doing. Under 90 words. Do not repeat anything you "
        "already said."
    ),
    "read": (
        "Read every piece of text in this image aloud, exactly as written, in "
        "natural reading order. Do not summarize, explain, or comment. If "
        "there is no text, say only 'No text visible.' If any text is cut off "
        "or unreadable, say which part."
    ),
}

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def capture():
    """Take a photo with rpicam-jpeg and read the bytes back.

    Shelling out to rpicam-jpeg instead of using the picamera2 library:
    fewer moving parts, and it is the exact command we already know works
    on this Pi. WARMUP_MS is the auto-exposure settle time -- lower it if
    the shot is fast enough, raise it if photos come out dark.
    """
    subprocess.run(
        [
            "rpicam-jpeg",
            "-o", SHOT_PATH,
            "-t", str(WARMUP_MS),
            "-n",                       # no preview window
            "--width", str(CAPTURE_SIZE[0]),
            "--height", str(CAPTURE_SIZE[1]),
        ],
        check=True,
        capture_output=True,
    )
    with open(SHOT_PATH, "rb") as handle:
        return handle.read()


def describe(jpeg, mode, previous=None, attempts=3):
    """Send the photo to the vision model and get text back.

    Retries with exponential backoff. A 503 from Google means the model is
    busy, which is temporary and worth waiting out -- unlike a 4xx, where
    retrying the same request would be pointless.
    """
    prompt = PROMPTS[mode]
    if mode == "detail":
        prompt = prompt.format(previous=previous)

    last_error = None
    for attempt in range(attempts):
        try:
            resp = client.models.generate_content(
                model=VISION_MODEL,
                contents=[
                    types.Part.from_bytes(data=jpeg, mime_type="image/jpeg"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=300,
                    temperature=0.4,
                ),
            )
            return resp.text.strip()
        except Exception as exc:
            last_error = exc
            if attempt < attempts - 1:
                wait = 2 ** attempt          # 1 second, then 2
                print(f"  [attempt {attempt + 1} failed, retrying in {wait}s]")
                time.sleep(wait)
    raise last_error


def play(pcm, rate):
    """Pipe raw PCM straight into aplay. No decoding, no extra libraries."""
    subprocess.run(
        [
            "aplay", "-q",
            "-D", AUDIO_DEVICE,
            "-r", str(rate),
            "-f", "S16_LE",
            "-c", "1",
        ],
        input=pcm,
        check=False,
    )


def say(text):
    """Speak with the cloud voice, fall back to espeak if anything fails."""
    try:
        resp = client.models.generate_content(
            model=TTS_MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=TTS_VOICE
                        )
                    )
                ),
            ),
        )
        play(resp.candidates[0].content.parts[0].inline_data.data, TTS_RATE)
    except Exception as exc:
        print(f"  [cloud voice unavailable: {exc}]")
        offline(text)


def offline(text):
    """espeak-ng writes a WAV to stdout, aplay puts it on the right device.

    espeak on its own would use the broken ALSA default, so route it the
    same way as the cloud voice. aplay reads the WAV header itself, so no
    rate or format flags are needed here.
    """
    speech = subprocess.run(
        ["espeak-ng", "-s", "150", "--stdout", text],
        capture_output=True,
        check=False,
    )
    subprocess.run(
        ["aplay", "-q", "-D", AUDIO_DEVICE],
        input=speech.stdout,
        check=False,
    )


def main():
    last_jpeg = None
    last_text = None

    print("\n  ENTER = describe   d = more detail   r = read text   q = quit\n")

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "q":
            break

        if cmd == "d":
            if last_text is None:
                say("Nothing to add detail to yet. Press enter to describe first.")
                continue
            mode = "detail"
            jpeg = last_jpeg
        elif cmd == "r":
            mode = "read"
            jpeg = capture()
        else:
            mode = "describe"
            jpeg = capture()

        started = time.time()
        try:
            text = describe(jpeg, mode, last_text)
        except Exception as exc:
            print(f"  [error: {exc}]")
            say("Something went wrong reaching the network. Try again.")
            continue

        print(f"  ({time.time() - started:.1f}s) {text}\n")
        say(text)

        last_jpeg = jpeg
        last_text = text


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
