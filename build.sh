#!/usr/bin/env bash
# Installation des dépendances système pour librosa / soundfile sous Linux (Render)
apt-get update && apt-get install -y libsndfile1 ffmpeg

# Installation des dépendances Python
pip install -r requirements.txt
