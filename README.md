# RollVision

RollVision is an ECEN 1400 assistive-technology project at the University of
Colorado Boulder. A Raspberry Pi captures an image of the area near a
wheelchair, sends it to Google Gemini for interpretation, and plays a spoken
description for the user.

> **Prototype status:** This is an early proof of concept, not a certified
> mobility or collision-avoidance device. It must not be used as the user's
> only source of navigation or safety information.

## Current system

```text
Camera Module -> Raspberry Pi -> Gemini vision -> Gemini TTS -> headphones
                                      |
                                      +-> espeak-ng fallback for speech only
```

The Raspberry Pi runs the application. Gemini remains a cloud service, so
scene interpretation requires internet access. The offline `espeak-ng`
fallback can speak an existing text response, but it cannot analyze images.

The current prototype supports:

- `Enter`: capture a new image and describe the scene
- `d`: add detail about the most recent image
- `r`: capture an image and read visible text
- `q`: quit

## Hardware

- Raspberry Pi 4
- Raspberry Pi Camera Module v2.1
- Headphones or a speaker connected to the Pi's 3.5 mm audio jack
- Keyboard for prototype input
- Internet connection for Gemini requests

Physical buttons, battery operation, distance-sensor integration, and the
optional companion web interface are not implemented yet.

## Software requirements

- Raspberry Pi OS Bookworm or newer
- Python 3.9 or newer
- `rpicam-jpeg` from Raspberry Pi's camera applications
- ALSA `aplay`
- `espeak-ng`
- A Gemini API key

Raspberry Pi OS Bookworm uses the `rpicam-*` camera commands. Older
`libcamera-*` names are not supported by this prototype.

## Raspberry Pi setup

Clone the repository and enter it:

```bash
git clone https://github.com/houstonclark06/RollVision.git
cd RollVision
```

Install the operating-system packages:

```bash
sudo apt update
sudo apt install -y python3-venv espeak-ng alsa-utils
```

Create an isolated Python environment and install the Python dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy the environment-variable template:

```bash
cp .env.example .env
```

Open `.env`, replace the placeholder with a real Gemini API key, and load it
into the current terminal:

```bash
set -a
source .env
set +a
```

Never commit `.env` or a real API key.

## Verify the hardware

Confirm that the camera works:

```bash
rpicam-jpeg -n -t 1000 -o /tmp/rollvision-test.jpg
```

List audio devices:

```bash
aplay -l
```

The prototype currently expects this device:

```text
plughw:CARD=Headphones,DEV=0
```

If your Pi reports a different card or device, update `AUDIO_DEVICE` in
`src/rollvision.py` before running the program.

## Run RollVision

With the virtual environment active and `GEMINI_API_KEY` loaded:

```bash
python src/rollvision.py
```

Images are temporarily written to `/tmp/poc_shot.jpg`. They are sent to the
Gemini API for analysis and are not committed to the repository.

## Repository structure

```text
RollVision/
├── src/
│   └── rollvision.py   Raspberry Pi proof of concept
├── .env.example        Safe environment-variable template
├── .gitignore          Local and generated files excluded from Git
├── CONTRIBUTING.md     Team Git and review workflow
├── LICENSE             Project license
├── README.md           Setup and project overview
└── requirements.txt    Python dependency range
```

## Configuration

The current constants are near the top of `src/rollvision.py`:

- `VISION_MODEL`: Gemini image-analysis model
- `TTS_MODEL`: Gemini text-to-speech model
- `TTS_VOICE`: selected cloud voice
- `CAPTURE_SIZE`: captured image resolution
- `WARMUP_MS`: camera exposure warm-up time
- `AUDIO_DEVICE`: ALSA playback device

The two Gemini model aliases can change or be retired. Verify them against
Google's current model documentation before a demonstration.

## Known limitations and safety concerns

- Gemini can produce incomplete or incorrect descriptions.
- A single camera image cannot provide safety-grade distance measurements.
- Network latency and outages can delay or prevent a description.
- Camera failures currently stop the program instead of producing a spoken
  recovery message.
- The retry loop currently retries every exception, including some errors that
  will not improve with another attempt.
- The audio device is hard-coded for one Raspberry Pi configuration.
- Images leave the Raspberry Pi and are processed by a cloud service.
- The program has no physical button, startup service, automatic update
  mechanism, battery monitoring, or companion interface yet.
- The distance sensor described in the project proposal is not integrated.

Before user testing, the team should define a privacy policy, add explicit
camera and audio error handling, test response latency, and create a procedure
for reporting unsafe or misleading descriptions.

## Planned companion interface

A future phone-accessible page may run locally on the Raspberry Pi for status,
configuration, diagnostics, and signed software updates. The core capture and
audio workflow should continue working without that interface. No companion
web application is included in the repository yet.

## Documentation

- [Google GenAI SDK](https://ai.google.dev/gemini-api/docs/libraries)
- [Gemini API quickstart](https://ai.google.dev/gemini-api/docs/get-started)
- [Raspberry Pi camera software](https://www.raspberrypi.com/documentation/computers/camera_software.html)

## Team

RollVision is developed for ECEN 1400 at the University of Colorado Boulder.
Team members should add agreed roles and contact information only after the
group approves publishing them.
