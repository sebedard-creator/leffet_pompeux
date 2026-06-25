# Architecture du Projet - L'effet Pompeux

Ce fichier documente l'architecture, la stack technique et les conventions de développement du projet "L'effet Pompeux". Il doit être maintenu à jour à chaque modification structurelle.

## 1. Stack Technique
- **Langage** : Python 3.10+
- **Interface Utilisateur (UI)** : Gradio (Interface Web)
- **Traitement du Signal (DSP)** : NumPy et SciPy (Traitement mathématique vectorisé). Aucune dépendance à des binaires pré-compilés externes (ex: Pedalboard) pour garantir la compatibilité absolue avec l'architecture cloud de Render.com (évite les erreurs `SIGILL` / `Erreur 132` liées aux instructions matérielles AVX/FMA).
- **Audio I/O** : Soundfile (`pysoundfile`), Resampy.

## 2. Structure des Fichiers
- `leffet_pompeux.py` : Le fichier monolithique principal contenant toute l'application (Interface Gradio + Moteur Audio DSP).
- `requirements.txt` : Les dépendances du projet pour l'environnement Python.
- `start.bat` / `stop.bat` : Scripts utilitaires pour la gestion du serveur en environnement de développement local (Windows).
- `build.sh` : Script de compilation/démarrage utilisé par Render.com.
- `changelog.md` : Historique complet des versions et des correctifs mathématiques.
- `README.md` : Documentation utilisateur.
- `architecture.md` : Le présent document décrivant la structure technique et les conventions.

## 3. Architecture du Moteur Audio (v2.0)
La philosophie du projet repose sur un traitement purement mathématique hors-ligne (Offline Processing). Le signal entier est chargé en RAM sous forme de tableaux NumPy (Arrays), puis traité bloc par bloc mathématique.

Le flux audio suit une architecture de routing extrêmement précise, modélisant un pipeline de studio de mixage professionnel :

1. **Génération de la Source (Trigger Sidechain)**
   - Si un fichier audio externe est fourni, il sert de signal fantôme. Sinon, on utilise une copie du fichier audio principal.
   - Ce signal passe dans un **Filtre Low-Pass** (Butterworth) pour isoler les sub-basses et le Kick.
   - Un paramètre de **Bass Gain** (Drive) est appliqué pour saturer le signal. La saturation est calculée via un *Soft Clipper* (`np.tanh`) afin de générer une distorsion analogique chaleureuse si le gain dépasse 1.0. Le signal résultant est appelé **`sc_trigger`**.

2. **Détection d'Enveloppe**
   - L'enveloppe du `sc_trigger` est calculée à l'aide d'un détecteur Attack/Release.

3. **Compression / Ducking (Étape VCA)**
   - Le volume de la piste principale est écrasé de façon logarithmique (en dB) en suivant l'enveloppe.
   - La profondeur est fixée par défaut au maximum (-48 dB de réduction). Le résultat est appelé **`ducked_A`**.

4. **Mixage Étape 1 (Compression Amount)**
   - Crossfade parfait (Dry/Wet) entre la piste principale intacte et la piste `ducked_A`.

5. **Mixage Étape 2 (Sidechain Volume)**
   - Crossfade permettant de réinjecter le `sc_trigger` (le signal des basses saturées) par-dessus le mix final. À 100%, l'utilisateur n'écoute que le moniteur du sidechain.

6. **Mastering Bus**
   - **Glue Compressor** : Un algorithme numérique classique de ratio 2:1, avec seuil de -12 dB, temps d'attaque de 5ms et release de 100ms. Utilise une fonction de calcul d'overshoot en dB et un Makeup gain automatique.
   - **Limiteur (Brickwall)** : Un limiteur True Peak mathématique réglé à -0.1 dBFS.

## 4. Conventions de Code
- **Stabilité Cloud** : Aucun module C++ lourd (Pedalboard, librosa) n'est autorisé pour l'audio afin d'éviter les crashs matériels sur des CPU virtualisés (Render.com). Tout l'audio doit être traité en mathématiques vectorielles pures avec NumPy.
- **Secrets** : Aucun secret ou configuration sensible n'est hardcodé.
- **Variables Globales** : L'utilisation de Gradio impose l'absence de variables d'état globales (State) persistantes, chaque appel de fonction doit être idempotent.
- **Zéro Polling** : L'interface repose sur les événements Gradio sans boucle de polling active.
