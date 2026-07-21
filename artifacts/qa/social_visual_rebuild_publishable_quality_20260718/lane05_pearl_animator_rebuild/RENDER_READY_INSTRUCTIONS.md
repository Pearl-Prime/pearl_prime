# Render-Ready Instructions

MP4 rendering was not available in this environment. Use the storyboard JSON and frame
folders as Pearl Animator source material. Render each frame sequence as a 27 second
vertical asset using the beat timing, motion notes, caption lines, and sound cues in
shortform_publishable_storyboards.json.

## Host ffmpeg status (2026-07-18)

FFMPEG=broken:missing libass.9.dylib — `ffmpeg -version` fails under dyld. Treat all shortform outputs as render-ready/storyboard-only. Do not claim MP4 proof on this host until libass is restored.
