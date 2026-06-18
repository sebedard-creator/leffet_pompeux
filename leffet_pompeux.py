#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║           L'effet Pompeux v1.17 🎛️                       ║
║   Sidechain PHATNESS Compression                         ║
║   Réseau local (LAN) & Cloud (Render.com)                ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import time
import uuid
import warnings
warnings.filterwarnings("ignore")

# --- Configuration du dossier local pour les fichiers ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_TEMP_DIR = os.path.join(BASE_DIR, "fichiers_audio")
os.makedirs(LOCAL_TEMP_DIR, exist_ok=True)
# Forcer Gradio a stocker les uploads dans notre dossier
os.environ["GRADIO_TEMP_DIR"] = LOCAL_TEMP_DIR

import numpy as np
import soundfile as sf
import librosa
from scipy.signal import butter, sosfilt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gradio as gr


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

TARGET_SR   = 48_000      # Fréquence d'échantillonnage cible (Hz)
PREVIEW_DUR = 15          # Durée de l'aperçu (secondes)
MAX_WAVEFORM_PTS = 6_000  # Points max pour l'affichage waveform (performance)


# ─────────────────────────────────────────────────────────────────────────────
# DSP — FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

def load_and_normalize(path: str) -> np.ndarray:
    """
    Charge un fichier audio, le rééchantillonne à TARGET_SR si nécessaire,
    et retourne un tableau float32 de forme (channels, samples).
    Supporte mono et stéréo (les fichiers > 2 canaux sont tronqués à 2).
    """
    audio, sr = librosa.load(path, sr=None, mono=False)

    if audio.ndim == 1:
        audio = audio[np.newaxis, :]       # mono → (1, N)
    if audio.shape[0] > 2:
        audio = audio[:2, :]              # Limiter à stéréo

    if sr != TARGET_SR:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SR)

    return audio.astype(np.float32)


def butter_lowpass(signal: np.ndarray, cutoff_hz: float) -> np.ndarray:
    """
    Filtre passe-bas Butterworth 2ème ordre.
    Utilisé pour isoler les basses avant la détection d'enveloppe.
    """
    nyq = TARGET_SR / 2.0
    cutoff_norm = float(np.clip(cutoff_hz / nyq, 0.001, 0.999))
    sos = butter(2, cutoff_norm, btype="low", output="sos")
    return sosfilt(sos, signal).astype(np.float32)


def envelope_follower(signal: np.ndarray, attack_ms: float, release_ms: float) -> np.ndarray:
    """
    Suit l'enveloppe d'amplitude avec des coefficients d'attaque/relâchement
    exponentiels indépendants (comportement organique).

    L'algorithme bascule entre le coefficient d'attaque (montée rapide)
    et le coefficient de relâchement (descente lente) selon la comparaison
    entre l'amplitude instantanée et l'état précédent de l'enveloppe.
    """
    attack_coef  = np.exp(-1.0 / max(1.0, attack_ms  * TARGET_SR / 1000.0))
    release_coef = np.exp(-1.0 / max(1.0, release_ms * TARGET_SR / 1000.0))

    abs_sig = np.abs(signal).astype(np.float64)
    env     = np.zeros(len(abs_sig), dtype=np.float64)
    prev    = 0.0

    for i in range(len(abs_sig)):
        coef = attack_coef if abs_sig[i] > prev else release_coef
        prev = coef * prev + (1.0 - coef) * abs_sig[i]
        env[i] = prev

    return env.astype(np.float32)


def write_wav_24bit(path: str, audio: np.ndarray) -> None:
    """
    Écrit un tableau float32 (channels, samples) en WAV 24-bit / TARGET_SR.
    """
    data = audio[0] if audio.shape[0] == 1 else audio.T
    sf.write(path, data, TARGET_SR, subtype="PCM_24")


# ─────────────────────────────────────────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────────────────────────────────────────

def build_waveform_figure(original: np.ndarray, processed: np.ndarray) -> plt.Figure:
    """
    Génère une figure Matplotlib superposant la waveform originale (gris)
    et la waveform traitée (cyan) pour comparaison visuelle.
    """
    fig, ax = plt.subplots(figsize=(10, 2.8), facecolor="#0d0d1c")
    ax.set_facecolor("#0d0d1c")

    n_samp = original.shape[1]
    step   = max(1, n_samp // MAX_WAVEFORM_PTS)
    t      = np.linspace(0, n_samp / TARGET_SR, n_samp // step)

    orig_mono = np.mean(original,  axis=0)[::step][: len(t)]
    proc_mono = np.mean(processed, axis=0)[::step][: len(t)]

    # Original — gris discret
    ax.fill_between(t, orig_mono, alpha=0.15, color="#aaaaaa")
    ax.plot(t, orig_mono, color="#888888", linewidth=0.6, alpha=0.8, label="Original")

    # Processed — cyan lumineux
    ax.fill_between(t, proc_mono, alpha=0.18, color="#00d4ff")
    ax.plot(t, proc_mono, color="#00d4ff", linewidth=0.75, alpha=0.95, label="Processed")

    ax.set_xlabel("Temps (s)", color="#aaaacc", fontsize=8)
    ax.set_ylabel("Amplitude", color="#aaaacc", fontsize=8)
    ax.set_ylim(-1.12, 1.12)
    ax.tick_params(colors="#666688", labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a44")
    ax.legend(
        facecolor="#1a1a30", edgecolor="#3a3a55",
        labelcolor="#ccccee", fontsize=8, loc="upper right"
    )
    ax.grid(True, alpha=0.07, color="#4444aa", linewidth=0.5)

    plt.tight_layout(pad=0.6)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# TRAITEMENT PRINCIPAL — CHAÎNE DE SIGNAL
# ─────────────────────────────────────────────────────────────────────────────

def process_audio(
    main_path:      str,
    sc_path:        str | None,
    cutoff_hz:      float,
    bass_gain:      float,
    comp_amount:    float,   # 0–100 %
    attack_ms:      float,
    release_ms:     float,
    wet_dry_pct:    float,   # 0–100 %
    sc_vol_pct:     float,   # 0-150 %
    use_compressor: bool,
    use_limiter:    bool,
    preview_start_s: float
):
    """
    Pipeline complet de traitement audio.
    Retourne : (figure, chemin_preview, texte_GR, chemin_export_complet)
    """
    if main_path is None:
        return None, None, "⚠️ Aucun fichier audio chargé.", None

    try:
        # ── ÉTAPE 1 : Chargement & Rééchantillonnage ────────────────────────
        main  = load_and_normalize(main_path)
        n_ch, n_samp = main.shape

        # ── ÉTAPE 2 : Source Sidechain ───────────────────────────────────────
        if sc_path is not None:
            sc = load_and_normalize(sc_path)
            # Adapter la longueur au fichier principal
            if sc.shape[1] >= n_samp:
                sc = sc[:, :n_samp]
            else:
                sc = np.pad(sc, ((0, 0), (0, n_samp - sc.shape[1])))
        else:
            sc = main.copy()   # Sidechain interne

        # ── ÉTAPE 3 : Conditionnement du Trigger (chemin sidechain) ──────────
        sc_mono    = np.mean(sc, axis=0)                 # Mixage mono
        sc_filtered = butter_lowpass(sc_mono, cutoff_hz) # Isolation des basses
        sc_trigger  = sc_filtered * float(bass_gain)     # Amplification

        # ── ÉTAPE 4 : Détection d'Enveloppe ─────────────────────────────────
        envelope = envelope_follower(sc_trigger, attack_ms, release_ms)

        # Normalisation 0→1
        env_peak = float(np.max(envelope))
        env_norm = envelope / env_peak if env_peak > 1e-9 else envelope

        # ── ÉTAPE 5 : Ducking (réduction de gain stéréo liée) ────────────────
        depth      = comp_amount / 100.0
        gain_curve = np.clip(1.0 - env_norm * depth, 0.0, 1.0).astype(np.float32)
        ducked     = main * gain_curve[np.newaxis, :]    # Broadcast L+R identique

        # ── ÉTAPE 6 : Mélange Wet/Dry ────────────────────────────────────────
        wet   = wet_dry_pct / 100.0
        mixed = (wet * ducked + (1.0 - wet) * main).astype(np.float32)

        # ── ÉTAPE 6.5 : Réinjection du Sidechain ────────────────────────────
        if sc_path is not None:
            mixed = mixed + (sc * (sc_vol_pct / 100.0)).astype(np.float32)

        # ── ÉTAPE 7 : Auto-Leveling (Headroom) ──────────────────────────────
        peak = float(np.max(np.abs(mixed)))
        if peak > 0.99:
            mixed = (mixed * (0.99 / peak)).astype(np.float32)

        # ── ÉTAPE 8 : Chaîne Master Bus (NumPy) ─────────────────────────────
        if use_compressor:
            # Glue compressor mathématique : ajoute +1.5 dB de gain et sature doucement (Saturateur / Soft Clip)
            drive_linear = 10 ** (1.5 / 20.0)
            mixed = np.tanh(mixed * drive_linear)

        if use_limiter:
            # Limiteur Brickwall mathématique à -0.1 dBFS
            limit_level = 10 ** (-0.1 / 20.0)
            # Soft clip respectant strictement le seuil
            mixed = limit_level * np.tanh(mixed / limit_level)

        processed = mixed.astype(np.float32)

        # ── Métriques GR ─────────────────────────────────────────────────────
        min_gain = float(np.min(gain_curve))
        gr_db    = 20.0 * np.log10(max(min_gain, 1e-9))
        gr_text  = f"Max Gain Reduction: {gr_db:.1f} dB"

        # ── Visualisation ─────────────────────────────────────────────────────
        fig = build_waveform_figure(main, processed)

        # ── Aperçu 15 secondes ────────────────────────────────────────────────
        start_samp = int(float(preview_start_s) * TARGET_SR)
        end_samp   = min(start_samp + PREVIEW_DUR * TARGET_SR, processed.shape[1])
        preview    = processed[:, start_samp:end_samp]

        # Nettoyage des anciens aperçus (> 1h) pour ne pas casser les sessions en cours
        now = time.time()
        for f in os.listdir(LOCAL_TEMP_DIR):
            if f.startswith("lp_preview_") and f.endswith(".wav"):
                f_path = os.path.join(LOCAL_TEMP_DIR, f)
                try: 
                    if now - os.path.getmtime(f_path) > 3600:
                        os.remove(f_path)
                except: pass

        unique_id = uuid.uuid4().hex
        preview_path = os.path.join(LOCAL_TEMP_DIR, f"lp_preview_{unique_id}.wav")
        write_wav_24bit(preview_path, preview)

        # ── Export Complet ────────────────────────────────────────────────────
        full_path = os.path.join(LOCAL_TEMP_DIR, f"leffet_pompeux_output_{unique_id}.wav")
        write_wav_24bit(full_path, processed)

        return fig, preview_path, gr_text, full_path

    except Exception as exc:
        import traceback
        err = f"❌ Erreur de traitement :\n{exc}\n\n{traceback.format_exc()}"
        return None, None, err, None


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS GRADIO
# ─────────────────────────────────────────────────────────────────────────────

def on_main_upload(path: str | None):
    """Met à jour le curseur Preview Start selon la durée du fichier chargé."""
    if path is None:
        return gr.update(maximum=1.0, value=0)
    try:
        info      = sf.info(path)
        max_start = max(1.0, info.duration - float(PREVIEW_DUR))
        return gr.update(maximum=round(max_start, 1), value=0.0)
    except Exception:
        return gr.update(maximum=1.0, value=0)

def clear_cache_python():
    """Vide le dossier des fichiers audio temporaires vieux de plus d'une heure."""
    try:
        count = 0
        now = time.time()
        for filename in os.listdir(LOCAL_TEMP_DIR):
            file_path = os.path.join(LOCAL_TEMP_DIR, filename)
            # Ne supprimer que si le fichier a plus de 3600 secondes (1 heure)
            if os.path.isfile(file_path):
                if now - os.path.getmtime(file_path) > 3600:
                    os.remove(file_path)
                    count += 1
            elif os.path.isdir(file_path):
                if now - os.path.getmtime(file_path) > 3600:
                    import shutil
                    shutil.rmtree(file_path)
                    count += 1
        if count > 0:
            print(f"[INFO] Cache vidé avec succès. {count} élément(s) supprimé(s).")
            gr.Info(f"Cache vidé ! {count} fichier(s) supprimé(s).")
        else:
            print("[INFO] Cache : Aucun fichier de plus d'une heure à supprimer.")
            gr.Info("Cache : Aucun fichier de plus d'une heure à supprimer.")
    except Exception as e:
        print(f"[ERREUR] Impossible de vider le cache : {e}")


# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE GRADIO
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
/* ── Global ── */
body                          { background: #0d0d1c !important; }
.gradio-container             { background: #0d0d1c !important; }
/* ── Titre ── */
.app-title                    { text-align: center; margin-bottom: 0.1em; }
.app-subtitle                 { text-align: center; color: #8888bb; margin-bottom: 1.2em; }
/* ── Bouton principal ── */
#btn-process                  { font-size: 1.05em !important; letter-spacing: 0.06em; }
/* ── Sections ── */
.section-label                { color: #aaaadd !important; font-size: 0.85em; margin: 0.5em 0 0.2em; }

/* ── Hovering Tooltips ── */
.tooltip-item label > span::after,
.tooltip-item legend > span::after {
    content: "?";
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #00d4ff;
    color: #0d0d1c;
    font-weight: bold;
    font-size: 10px;
    margin-left: 6px;
    cursor: help;
    vertical-align: middle;
}
.tooltip-item label, .tooltip-item legend { position: relative !important; overflow: visible !important; }
.tooltip-item label:hover::before, .tooltip-item legend:hover::before {
    position: absolute;
    bottom: 110%;
    left: 0;
    background: #0d0d1c;
    border: 1px solid #00d4ff;
    padding: 6px 10px;
    border-radius: 5px;
    color: #e0e0ff;
    font-size: 12px;
    white-space: normal;
    width: 280px;
    line-height: 1.4;
    z-index: 9999;
    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    pointer-events: none;
    font-weight: normal;
}
#tt-cutoff label:hover::before { content: "Détermine la fréquence maximale du filtre Sidechain (Low-Pass). Plus elle est basse, plus le compresseur réagira uniquement aux grosses caisses (Kick) et sous-basses, ignorant les voix ou synthés aigus."; }
#tt-bass label:hover::before { content: "Booste artificiellement le volume des basses du signal déclencheur avant la détection. Utile si votre kick manque d'impact pour déclencher correctement le pompage."; }
#tt-comp label:hover::before { content: "Profondeur de l'effet (Ducking). À 100%, la musique sera totalement écrasée lors du kick (pompage extrême). À 30%, l'effet sera plus subtil et naturel."; }
#tt-attack label:hover::before { content: "Vitesse à laquelle le volume baisse quand le kick frappe. Une attaque courte (< 5ms) écrase le son immédiatement. Une attaque plus longue laisse passer le claquement (transitoire) du kick."; }
#tt-release label:hover::before { content: "Vitesse à laquelle le son revient à la normale. Un temps trop long étouffera le morceau, un temps trop court créera des saccades brutales. À ajuster selon le tempo (BPM)."; }
#tt-wetdry label:hover::before { content: "Mixage parallèle : 100% n'envoie que le son avec l'effet Sidechain au maximum. 50% mélange le son d'origine avec le pompage pour conserver de la dynamique (New York Compression)."; }
#tt-scvol label:hover::before { content: "Volume du signal Sidechain (Kick) réinjecté dans le mix final. À 0%, vous n'entendrez que l'effet de 'trou'. À 100%, le kick viendra remplir l'espace créé par le pompage."; }
#tt-glue label:hover::before, #tt-glue legend:hover::before { content: "Ajoute un compresseur de bus type SSL à la fin du traitement. Il 'colle' les éléments de votre mix ensemble avec une légère réduction de gain pour un rendu plus compact et professionnel."; }
#tt-limit label:hover::before, #tt-limit legend:hover::before { content: "Place un True Peak Brickwall Limiter en bout de chaîne (-0.1 dB). Protège votre fichier exporté contre la saturation (clipping numérique) et maximise le volume RMS perçu."; }
#tt-prev label:hover::before { content: "Curseur permettant de cibler un moment précis de votre audio (en secondes, et non en %) pour le rendu de l'Aperçu rapide (15 secondes). Utile pour tester l'effet directement sur le refrain ou le drop."; }

#center-title-box {
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: #111122;
    border: 1px solid #2a2a44;
    border-radius: 8px;
    padding: 10px;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    margin-top: 15px;
}

/* Fix z-index clippage (Nuclear Option) */
.gradio-container *:has(.tooltip-item) { overflow: visible !important; contain: none !important; }
.gradio-container *:has(.tooltip-item):hover { z-index: 2147483647 !important; }
.tooltip-item { position: relative !important; z-index: 10; overflow: visible !important; contain: none !important; }
.tooltip-item:hover { z-index: 2147483647 !important; }
.tooltip-item *, .tooltip-item *::before, .tooltip-item *::after { overflow: visible !important; contain: none !important; }
"""

with gr.Blocks(
    title="L'effet Pompeux v1.17",
    theme=gr.themes.Base(
        primary_hue="cyan",
        secondary_hue="slate",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    ),
    css=CSS,
) as demo:

    with gr.Row(equal_height=False):

        # ══════════════════════════════════
        # CONTROLES & INPUTS
        # ══════════════════════════════════
        with gr.Column(scale=4, min_width=400):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("##### 📂 Source Principal", elem_classes="section-label")
                    main_audio_in = gr.Audio(label="Audio Principal ✱", type="filepath")
                with gr.Column():
                    gr.Markdown("##### 📂 Source Sidechain", elem_classes="section-label")
                    sc_audio_in = gr.Audio(label="Sidechain Audio (Optionnel)", type="filepath")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("##### ⚙️ Filtre Sidechain", elem_classes="section-label")
                    cutoff_sl = gr.Slider(20, 500, value=90, step=1, label="Low-Pass Cutoff (Hz)", elem_classes="tooltip-item", elem_id="tt-cutoff")
                    bass_sl   = gr.Slider(0.5, 4.0, value=2.5, step=0.1, label="Bass Gain (×)", elem_classes="tooltip-item", elem_id="tt-bass")
                with gr.Column():
                    gr.Markdown("##### ⏱️ Enveloppe", elem_classes="section-label")
                    attack_sl  = gr.Slider(0.1, 50, value=1.5, step=0.1, label="Attack (ms)", elem_classes="tooltip-item", elem_id="tt-attack")
                    release_sl = gr.Slider(10, 500, value=130, step=1, label="Release (ms)", elem_classes="tooltip-item", elem_id="tt-release")
                    with gr.Row():
                        btn_tap = gr.Button("🎵 Tap Tempo", size="sm")
                        btn_paste = gr.Button("⬇️ Paste to Release", size="sm")
                with gr.Column():
                    gr.Markdown("##### 🎚️ Mix & Ducking", elem_classes="section-label")
                    comp_sl   = gr.Slider(0, 100, value=90, step=1, label="Compression Amount (%)", elem_classes="tooltip-item", elem_id="tt-comp")
                    wetdry_sl = gr.Slider(0, 100, value=100, step=1, label="Wet/Dry Mix (%)", elem_classes="tooltip-item", elem_id="tt-wetdry")
                    sc_vol_sl = gr.Slider(0, 150, value=100, step=1, label="Sidechain Volume (%)", elem_classes="tooltip-item", elem_id="tt-scvol")

            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("##### 🔧 Options", elem_classes="section-label")
                    with gr.Row():
                        chk_comp  = gr.Checkbox(value=True, label="🗜️ Glue Compressor", elem_classes="tooltip-item", elem_id="tt-glue")
                        chk_limit = gr.Checkbox(value=True, label="🧱 Brickwall Limiter", elem_classes="tooltip-item", elem_id="tt-limit")
                with gr.Column(scale=3):
                    gr.Markdown("##### 🎧 Aperçu", elem_classes="section-label")
                    prev_start_sl = gr.Slider(minimum=0.0, maximum=1.0, value=0.0, step=0.5, label=f"Début de l'aperçu (s)", elem_classes="tooltip-item", elem_id="tt-prev")

        # ══════════════════════════════════
        # OUTPUTS & VISUALISATION
        # ══════════════════════════════════
        with gr.Column(scale=5, min_width=450):
            with gr.Group():
                gr.Markdown("##### 📊 Comparaison Waveform <small>(Gris = Original · Cyan = Processed)</small>", elem_classes="section-label")
                waveform_out = gr.Plot(label="")

            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("##### 🎧 Écoute de l'aperçu", elem_classes="section-label")
                    preview_out = gr.Audio(label="", type="filepath")
                    
                    with gr.Column(elem_id="center-title-box"):
                        gr.Markdown("# 🎛️ L'effet Pompeux", elem_classes="app-title")
                        gr.Markdown(
                            "*Sidechain PHATNESS Compression*<br><span style='font-size: 0.85em; opacity: 0.6;'>v1.17</span>",
                            elem_classes="app-subtitle"
                        )
                    
                    proc_btn = gr.Button(f"🚀  PROCESS", variant="primary", size="lg", elem_id="btn-process")
                    clear_btn = gr.Button("🗑️ Clear Cache", variant="stop", size="sm", elem_id="btn-clear")

                with gr.Column(scale=2):
                    gr.Markdown("##### 📉 Gain Reduction", elem_classes="section-label")
                    gr_meter_out = gr.Textbox(label="", value="—", interactive=False)
                    gr.Markdown("##### 💾 Export", elem_classes="section-label")
                    download_out = gr.File(label="WAV 48 kHz / 24-bit", file_count="single")

    # ── Câblage des événements ────────────────────────────────────────────────
    main_audio_in.change(
        fn=on_main_upload,
        inputs=[main_audio_in],
        outputs=[prev_start_sl]
    )

    proc_btn.click(
        fn=process_audio,
        inputs=[
            main_audio_in, sc_audio_in,
            cutoff_sl, bass_sl, comp_sl,
            attack_sl, release_sl,
            wetdry_sl, sc_vol_sl,
            chk_comp, chk_limit,
            prev_start_sl
        ],
        outputs=[waveform_out, preview_out, gr_meter_out, download_out]
    )

    clear_btn.click(
        fn=clear_cache_python,
        inputs=[],
        outputs=[],
        js='''() => {
            if(!confirm("⚠️ ATTENTION : Voulez-vous vraiment effacer les fichiers audio en cache vieux de plus de 1 HEURE ?\\n\\n(Ceci évite d'interrompre les sessions des autres utilisateurs sur le Web).")) {
                throw new Error("Action annulée.");
            }
        }'''
    )

    btn_tap.click(
        fn=None,
        inputs=[btn_tap],
        outputs=[btn_tap],
        js='''(current_text) => {
            window.tapTimes = window.tapTimes || [];
            let now = Date.now();
            if (window.tapTimes.length > 0 && now - window.tapTimes[window.tapTimes.length - 1] > 2000) {
                window.tapTimes = [];
            }
            window.tapTimes.push(now);
            if (window.tapTimes.length > 5) window.tapTimes.shift();
            
            if (window.tapTimes.length > 1) {
                let diffs = [];
                for (let i = 1; i < window.tapTimes.length; i++) {
                    diffs.push(window.tapTimes[i] - window.tapTimes[i - 1]);
                }
                let avgDiff = diffs.reduce((a, b) => a + b) / diffs.length;
                let bpm = Math.round(60000 / avgDiff);
                let ms16 = Math.round(15000 / bpm);
                window.lastMs16 = ms16;
                return `🎵 ${bpm} BPM | 1/16: ${ms16} ms`;
            }
            return "🎵 Tapping...";
        }'''
    )

    btn_paste.click(
        fn=None,
        inputs=[release_sl],
        outputs=[release_sl],
        js='''(current_val) => {
            if (window.lastMs16) {
                return window.lastMs16;
            }
            return current_val;
        }'''
    )

    gr.Markdown(
        "<div style='text-align: center; margin-top: 30px; font-size: 0.8em; opacity: 0.5;'>"
        "Projet Open Source hébergé sur <a href='https://github.com/sebedard-creator/leffet_pompeux' target='_blank' style='color: #00e5ff; text-decoration: none;'>GitHub</a>"
        "</div>"
    )


# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("------------------------------------------------")
    print("|        L'effet Pompeux v1.17                 |")
    print("|   Sidechain PHATNESS Compression             |")
    print("|   Demarrage du serveur Gradio (Cloud/LAN)... |")
    print("------------------------------------------------")
    print()
    demo.launch(
        server_name="0.0.0.0",   # Accessible sur le réseau local / cloud
        server_port=int(os.environ.get("PORT", 7861)),
        share=False,
        show_error=True,
        quiet=False
    )
