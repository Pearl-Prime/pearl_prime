# Manga render assets

## lbpcascade_animeface.xml
Anime/manga face-detection cascade by nagadomi.
Source: https://github.com/nagadomi/lbpcascade_animeface (MIT License).

Used by `phoenix_v4/manga/chapter/tail_geometry.py` (`detect_anime_face_boxes`)
to anchor speech-bubble tails at a speaker's actual face. Detection is OPTIONAL:
when OpenCV (`cv2`) or this file is absent, the renderer falls back to the
zone/head-box heuristic, so CI and Pearl Star stay green without the dependency.
