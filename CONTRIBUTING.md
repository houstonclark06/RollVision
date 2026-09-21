# Contributing to RollVision

## Before starting work

1. Pull the newest `main` branch.
2. Create a focused branch such as `feature/physical-button` or
   `fix/camera-error-message`.
3. Confirm that no API key, captured image, or private user data is present in
   the files you plan to commit.

## Making a change

- Keep commits small and describe the result in the commit message.
- Avoid changing prompts, model names, audio configuration, and hardware
  configuration in the same commit unless the changes depend on each other.
- Document hardware assumptions and test on the Raspberry Pi when a change
  affects the camera, audio, networking, or physical controls.
- Do not treat a successful Gemini response as proof that its description is
  accurate or safe.

## Basic checks

Run the syntax check from the repository root:

```bash
python3 -m py_compile src/rollvision.py
```

On the Raspberry Pi, also test:

```bash
rpicam-jpeg -n -t 1000 -o /tmp/rollvision-test.jpg
aplay -l
```

Never make a live Gemini request during an automated test without explicitly
marking it as an integration test. API calls can consume quota and transmit
images outside the device.

## Pull requests

Describe:

- What changed and why
- Hardware and Raspberry Pi OS version used for testing
- Commands or manual checks performed
- Any effect on privacy, accessibility, latency, or user safety

At least one teammate should review changes to prompts, update behavior,
physical controls, or safety-related output before merging.
