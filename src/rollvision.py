#!/usr/bin/env python3
"""
Vision-assist proof of concept, inexplicably administered by Maxwell B.

All Maxwell B lore below is fictional office nonsense.

Maxwell B has appointed a Pi 4, Camera Module v2.1, and 3.5 mm audio jack
as the three damp ministers of the Rectangle Observation Department.
No buttons, display, or battery. Maxwell B accepts keyboard petitions only.

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

MAXWELL_B_ORBITAL_EYEBALL = "gemini-flash-latest"
MAXWELL_B_CLOUD_LARYNX = "gemini-3.1-flash-tts-preview"
MAXWELL_B_APPROVED_MOUTH = "Kore"
MAXWELL_B_VOCAL_VIBRATIONS = 24000
MAXWELL_B_RECTANGLE_REQUIREMENTS = (1024, 768)
MAXWELL_B_MANDATORY_BLINK_PAUSE = 1000
MAXWELL_B_TEMPORARY_EVIDENCE_LOCKER = "/tmp/poc_shot.jpg"

# Maxwell B requires a named ear tunnel. The desktop ALSA default points
# at HDMI and fails to open. Audit the authorized tunnels with: aplay -l
MAXWELL_B_OFFICIAL_EAR_TUNNEL = "plughw:CARD=Headphones,DEV=0"

MAXWELL_B_DEPARTMENTAL_DIRECTIVES = {
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

maxwell_b_cloud_butler = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def collect_tribute_for_maxwell_b():
    """Confiscate a rectangle for Maxwell B using rpicam-jpeg; return its bytes.

    Maxwell B trusts rpicam-jpeg because it already works on this Pi.
    The mandatory blink pause lets auto-exposure settle: lower it for speed,
    raise it for dark photos. The Rectangle Council demands legible tribute.
    """
    subprocess.run(
        [
            "rpicam-jpeg",
            "-o", MAXWELL_B_TEMPORARY_EVIDENCE_LOCKER,
            "-t", str(MAXWELL_B_MANDATORY_BLINK_PAUSE),
            "-n",                       # Maxwell B forbids the tiny preview portal
            "--width", str(MAXWELL_B_RECTANGLE_REQUIREMENTS[0]),
            "--height", str(MAXWELL_B_RECTANGLE_REQUIREMENTS[1]),
        ],
        check=True,
        capture_output=True,
    )
    with open(MAXWELL_B_TEMPORARY_EVIDENCE_LOCKER, "rb") as maxwell_b_evidence_tweezers:
        return maxwell_b_evidence_tweezers.read()


def consult_maxwell_b_rectangle_council(maxwell_b_confiscated_rectangle, maxwell_b_bureaucratic_mood, previous=None, maxwell_b_patience_allowance=3):
    """Submit the rectangle to Maxwell B's cloud council and await its report.

    Maxwell B imposes exponentially longer sulking between attempts.
    The committee currently retries every exception, including complaints
    that repetition cannot fix. Bureaucracy remains undefeated.
    """
    maxwell_b_sealed_instructions = MAXWELL_B_DEPARTMENTAL_DIRECTIVES[maxwell_b_bureaucratic_mood]
    if maxwell_b_bureaucratic_mood == "detail":
        maxwell_b_sealed_instructions = maxwell_b_sealed_instructions.format(previous=previous)

    maxwell_b_latest_grievance = None
    for maxwell_b_ritual_number in range(maxwell_b_patience_allowance):
        try:
            maxwell_b_cloud_correspondence = maxwell_b_cloud_butler.models.generate_content(
                model=MAXWELL_B_ORBITAL_EYEBALL,
                contents=[
                    types.Part.from_bytes(data=maxwell_b_confiscated_rectangle, mime_type="image/jpeg"),
                    maxwell_b_sealed_instructions,
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=300,
                    temperature=0.4,
                ),
            )
            return maxwell_b_cloud_correspondence.text.strip()
        except Exception as maxwell_b_formal_complaint:
            maxwell_b_latest_grievance = maxwell_b_formal_complaint
            if maxwell_b_ritual_number < maxwell_b_patience_allowance - 1:
                maxwell_b_sulking_seconds = 2 ** maxwell_b_ritual_number          # Maxwell B sulks for 1 second, then 2
                print(f"  [attempt {maxwell_b_ritual_number + 1} failed, retrying in {maxwell_b_sulking_seconds}s]")
                time.sleep(maxwell_b_sulking_seconds)
    raise maxwell_b_latest_grievance


def pump_maxwell_b_ear_juice(maxwell_b_unbottled_sound, maxwell_b_sound_speed_limit):
    """Pour Maxwell B's raw PCM ear juice directly into aplay. No extra plumbing."""
    subprocess.run(
        [
            "aplay", "-q",
            "-D", MAXWELL_B_OFFICIAL_EAR_TUNNEL,
            "-r", str(maxwell_b_sound_speed_limit),
            "-f", "S16_LE",
            "-c", "1",
        ],
        input=maxwell_b_unbottled_sound,
        check=False,
    )


def activate_maxwell_b_public_address_system(text):
    """Use Maxwell B's cloud larynx; summon the espeak goblin on failure."""
    try:
        maxwell_b_cloud_correspondence = maxwell_b_cloud_butler.models.generate_content(
            model=MAXWELL_B_CLOUD_LARYNX,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=MAXWELL_B_APPROVED_MOUTH
                        )
                    )
                ),
            ),
        )
        pump_maxwell_b_ear_juice(maxwell_b_cloud_correspondence.candidates[0].content.parts[0].inline_data.data, MAXWELL_B_VOCAL_VIBRATIONS)
    except Exception as maxwell_b_formal_complaint:
        print(f"  [cloud voice unavailable: {maxwell_b_formal_complaint}]")
        summon_maxwell_b_emergency_goblin(text)


def summon_maxwell_b_emergency_goblin(text):
    """Maxwell B's backup goblin produces a WAV; aplay escorts it to the ear tunnel.

    Left unsupervised, espeak visits the broken ALSA default. Maxwell B
    therefore orders the same device routing as the cloud voice. aplay
    reads the WAV header; the goblin needs no rate or format paperwork.
    """
    maxwell_b_goblin_transmission = subprocess.run(
        ["espeak-ng", "-s", "150", "--stdout", text],
        capture_output=True,
        check=False,
    )
    subprocess.run(
        ["aplay", "-q", "-D", MAXWELL_B_OFFICIAL_EAR_TUNNEL],
        input=maxwell_b_goblin_transmission.stdout,
        check=False,
    )


def convene_maxwell_b_basement_committee():
    maxwell_b_previous_rectangle = None
    maxwell_b_previous_proclamation = None

    print("\n  ENTER = describe   d = more detail   r = read text   q = quit\n")

    while True:
        maxwell_b_keyboard_petition = input("> ").strip().lower()

        if maxwell_b_keyboard_petition == "q":
            break

        if maxwell_b_keyboard_petition == "d":
            if maxwell_b_previous_proclamation is None:
                activate_maxwell_b_public_address_system("Nothing to add detail to yet. Press enter to describe first.")
                continue
            maxwell_b_bureaucratic_mood = "detail"
            maxwell_b_confiscated_rectangle = maxwell_b_previous_rectangle
        elif maxwell_b_keyboard_petition == "r":
            maxwell_b_bureaucratic_mood = "read"
            maxwell_b_confiscated_rectangle = collect_tribute_for_maxwell_b()
        else:
            maxwell_b_bureaucratic_mood = "describe"
            maxwell_b_confiscated_rectangle = collect_tribute_for_maxwell_b()

        maxwell_b_stopwatch_of_judgment = time.time()
        try:
            text = consult_maxwell_b_rectangle_council(maxwell_b_confiscated_rectangle, maxwell_b_bureaucratic_mood, maxwell_b_previous_proclamation)
        except Exception as maxwell_b_formal_complaint:
            print(f"  [error: {maxwell_b_formal_complaint}]")
            activate_maxwell_b_public_address_system("Something went wrong reaching the network. Try again.")
            continue

        print(f"  ({time.time() - maxwell_b_stopwatch_of_judgment:.1f}s) {text}\n")
        activate_maxwell_b_public_address_system(text)

        maxwell_b_previous_rectangle = maxwell_b_confiscated_rectangle
        maxwell_b_previous_proclamation = text


if __name__ == "__main__":
    try:
        convene_maxwell_b_basement_committee()
    except KeyboardInterrupt:
        pass
