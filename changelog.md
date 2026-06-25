# Changelog

## [v2.0] - 2026-06-25
### Ajouts et Modifications
- **Refonte Majeure de l'Architecture du Signal Audio** :
  - **Simplification du Mixage :** Le curseur obsolète `Wet/Dry Mix (%)` a été définitivement supprimé pour laisser place à une logique pure et sans ambiguïté basée sur le workflow des producteurs.
  - **Nouveau rôle pour `Compression Amount (%)` :** Agit dorénavant comme un crossfader parfait entre le fichier original non compressé (0%) et le fichier totalement écrasé par le sidechain (100%).
  - **Nouveau rôle pour `Sidechain Volume (%)` :** Agit comme un second crossfader permettant de réinjecter le signal du filtre Sidechain (Cutoff + Bass Gain pur) par-dessus le mix. À 100%, l'utilisateur n'entend plus que le filtre Sidechain, ce qui permet de le monitorer précisément ou de l'utiliser comme un générateur de sous-basses parallèle. Par défaut, ce réglage est désormais à 0% pour ne pas brouiller le mix.
  - **Soft Clipper sur le Bass Gain :** Remplacement de la fonction `np.clip` (Hard Clipping) par `np.tanh` (Soft Clipping). Cela permet d'obtenir une saturation analogique (Overdrive) beaucoup plus chaleureuse lorsque le paramètre Bass Gain est poussé fort (ex: > 1.0), évitant la distorsion numérique agressive (onde carrée).


## [v1.23] - 2026-06-25
### Ajouts et Modifications
- **Correction du "Ducking" permanent (Audio inaudible)** :
  - **Problème :** La version 1.21 avait introduit un gain interne artificiel de x10 pour compenser la perte de volume du filtre passe-bas. Cependant, multiplier *tout* le signal des basses par 10 (et parfois 40 avec le Bass Gain) poussait non seulement les kicks, mais aussi toutes les lignes de basse et les bruits de fond au-delà du seuil de 1.0. Résultat : le détecteur d'enveloppe voyait un bloc solide continu à 1.0. Le compresseur ne relâchait jamais la compression (-48dB en permanence), rendant le fichier inaudible.
  - **Solution :** Suppression du multiplicateur arbitraire x10. À la place, le signal sidechain est désormais *normalisé* globalement à 1.0 juste après le filtrage. Ainsi, le son le plus fort de la piste basse (le kick) vaut exactement 1.0, et les lignes de basses restent naturellement en dessous. Le curseur `Bass Gain` retrouve son utilité parfaite de "Drive" contrôlé, garantissant un pompage rythmique propre sans détruire la dynamique de la piste.



## [v1.22] - 2026-06-25
### Ajouts et Modifications
- **Véritable Compresseur de Master Bus (Glue Compressor)** :
  - **Refonte DSP :** La version 1.17 avait introduit un compresseur de "Glue" simulé par un saturateur mathématique (Soft Clipper). Sur demande expresse, cette approche a été remplacée par un véritable algorithme de compression numérique.
  - **Spécifications (Type 2:1) :** Le compresseur de bus (activable via la case `Glue Compressor`) utilise désormais de véritables paramètres de compression : Ratio fixe de 2:1, Seuil à -12 dB, Attaque 5ms et Release 100ms. L'enveloppe est calculée de manière logarithmique (overshoot en dB) pour reproduire fidèlement l'action d'un compresseur de Mastering standard.



## [v1.21] - 2026-06-25
### Ajouts et Modifications
- **Correction d'Amplitude du Trigger (Gain Interne x10)** :
  - **Problème :** Après la suppression de la normalisation globale, l'effet de compression ne s'activait plus du tout. La raison : le filtre passe-bas (Low-Pass) à 90Hz enlève énormément d'énergie au signal audio. Le volume du kick devenait si faible qu'il n'arrivait jamais à atteindre le seuil de 1.0 pour déclencher le Ducking.
  - **Solution :** Ajout d'un gain de compensation interne de **+20dB (x10)** sur le signal sidechain juste après le filtre passe-bas. Le curseur `Bass Gain` peut de nouveau "driver" le signal à fond dans le clipper, réveillant toute la puissance du VCA de la v1.19.



## [v1.19] - 2026-06-25
### Ajouts et Modifications
- **Émulation VCA Analogique (Release Courbe Logarithmique)** :
  - **Correction du "Release trop rapide" :** L'enveloppe de Sidechain était auparavant appliquée de manière *linéaire* à l'amplitude audio. Résultat : une baisse de 50% de l'enveloppe faisait remonter le volume instantanément à -6dB, ce que l'oreille perçoit comme "déjà terminé", donnant l'impression d'un release expéditif.
  - **Nouveau comportement :** La réduction de gain est désormais calculée en décibels (comme un vrai compresseur analogique). L'enveloppe pilote les décibels. Ainsi, lorsque le compresseur relâche sa compression, le volume "gonfle" de manière beaucoup plus ronde et organique, créant cette fameuse "aspiration" (suction) propre à la House Music.



## [v1.18] - 2026-06-25
### Ajouts et Modifications
- **Refonte DSP du Moteur de Pompage (Ducking)** : 
  - **Correction majeure :** Suppression de la *normalisation globale* de l'enveloppe de sidechain. Auparavant, le moteur comparait le signal au kick le plus fort de toute la chanson, ce qui annulait mathématiquement le paramètre `Bass Gain` et affaiblissait drastiquement le "pompage" sur les kicks plus faibles.
  - **Nouveau comportement :** L'enveloppe est désormais un simple *Hard Clipper*. Le `Bass Gain` agit désormais comme un véritable "Drive/Threshold" inversé. Pousser le curseur sature le signal de détection contre le plafond mathématique de `1.0`. Résultat : le "Ducking" s'engage à 100% à chaque coup de kick, offrant un effet de pompage constant, lourd et dévastateur typique de la French Touch.



## [v1.17] - 2026-06-18
### Ajouts et Modifications
- **Fix Render.com (Erreur 132 SIGILL)** : 
  - La librairie `pedalboard` (Spotify) a été **complètement supprimée** de l'application et retirée des dépendances. Elle requérait des instructions processeurs AVX/AVX2 modernes, ce qui provoquait un plantage instantané du serveur sur l'offre gratuite de Render.com (processeurs virtuels anciens).
- **Nouveau Master Bus (NumPy)** :
  - Le compresseur de "Glue" et le Limiteur Brickwall de Pedalboard ont été remplacés par notre propre algorithme en pur **NumPy**.
  - **Glue Compressor** : Remplacé par un algorithme de *Soft Clipping Mathématique* (`np.tanh`) avec un drive interne de +1.5dB pour donner une chaleur et une saturation caractéristiques de la French Touch, unifiant le mix.
  - **Limiteur Brickwall** : Remplacé par un hard/soft clip limitant strictement le signal à `-0.1 dBFS`.
- L'application est désormais 100% stable sur n'importe quel hébergeur Cloud sans nécessiter d'instructions CPU particulières.



## [v1.16] - 2026-06-18
### Ajouts et Modifications
- **Compatibilité Cloud (Render.com)** :
  - **Port Dynamique** : Le port n'est plus forcé à `7861`, il s'adapte automatiquement à la variable d'environnement `PORT` imposée par Render.com. (S'il n'y en a pas, il utilise `7861` par défaut en local).
  - **Isolation multi-utilisateurs** : Les fichiers temporaires (aperçus et exports) ne sont plus nommés avec un simple horodatage (timestamp) susceptible de créer des collisions si deux personnes cliquent en même temps. Ils utilisent désormais un `UUID` (identifiant cryptographique unique) pour isoler les sessions.
  - **Sécurité du Cache** : La fonction de nettoyage automatique et le bouton "Clear Cache" ont été modifiés pour ne supprimer *que les fichiers vieux de plus de 1 heure*. Ainsi, le cache n'explosera pas le stockage serveur, et vous ne risquez pas d'effacer le travail en cours d'un autre utilisateur !
- **Dépôt Git** : Ajout d'un `.gitignore` pour protéger les fichiers locaux lourds (`venv`, `fichiers_audio`, `.zip`) et d'un script `build.sh` pour forcer l'installation de `libsndfile1` sur Linux.
- **Mise à jour version** : Passage à la version `v1.16`.



## [v1.15] - 2026-05-29
### Ajouts et Modifications
- **Tap Tempo et Calculateur de Release** : Ajout de deux boutons dans la section Enveloppe.
  - *🎵 Tap Tempo* : Un bouton cliquable en rythme pour calculer instantanément le BPM et la valeur en millisecondes d'une double-croche (1/16th note).
  - *⬇️ Paste to Release* : Un clic sur ce bouton copie immédiatement la valeur en ms (la double-croche calculée) et l'applique au curseur "Release (ms)", permettant un "groove de pompage" parfaitement calé sur le rythme de la chanson !
- **Mise à jour version** : Passage à la version `v1.15`.



## [v1.14] - 2026-05-04
### Ajouts et Modifications
- **Réinjection du Sidechain** : Il est désormais possible d'entendre le fichier audio utilisé comme Sidechain (Kick) dans le mix final. 
- **Curseur Sidechain Volume** : Ajout d'un nouveau curseur "Sidechain Volume (%)" allant de 0% à 150%. Par défaut à 100%, il permet de remplir le "trou" créé par l'effet de Ducking. Si défini à 0%, le logiciel fonctionnera uniquement comme un "Ducker" classique. (Option disponible uniquement lorsqu'un fichier audio secondaire est fourni dans "Source Sidechain").
- **Mise à jour version** : Passage à la version `v1.14`.



## [v1.13] - 2026-05-03
### Ajouts et Modifications
- **Aperçu - Fix de Cache** : Ajout d'un Timestamp unique (`lp_preview_[timestamp].wav`) au nom de fichier de l'aperçu audio pour contourner le cache abusif du navigateur. Dorénavant, lors de multiples clics sur PROCESS, le navigateur jouera *toujours* la version mise à jour de l'aperçu au lieu de recharger la précédente. L'outil efface automatiquement les anciens aperçus.
- **Aperçu - Correction sémantique** : L'infobulle pour le slider du début de l'aperçu a été modifiée pour préciser qu'il s'agit bien de *secondes* et non d'un pourcentage. Le maximum ne s'arrête donc pas à 100 mais correspond à `durée_totale - 15s`.
- **Mise à jour version** : Passage à la version `v1.13`.



## [v1.12] - 2026-05-03
### Ajouts et Modifications
- **Correction Bouton Clear Cache** : Le bouton *Clear Cache* ne déclenchait pas l'action Python dans Gradio 4+. Le code a été corrigé en fusionnant l'exécution JavaScript et Python dans le même appel `.click()`. Le bouton est désormais pleinement fonctionnel !
- **Mise à jour version** : Passage à la version `v1.12`.



## [v1.11] - 2026-05-03
### Ajouts et Modifications
- **Bouton Clear Cache** : Ajout d'un bouton rouge "🗑️ Clear Cache" sous le bouton PROCESS. 
- **Sécurité et Avertissement** : Le bouton déclenche une fenêtre pop-up de confirmation (warning) pour éviter les clics accidentels. Il ne cible *que* le contenu du dossier `fichiers_audio` garantissant l'intégrité du code source.
- **Mise à jour version** : Passage à la version `v1.11`.



## [v1.10] - 2026-05-03
### Ajouts et Modifications
- **Gestion des Fichiers (Local)** : Le logiciel ne cache plus de fichiers dans les dossiers temporaires obscurs de Windows (`AppData/Temp`). Un nouveau dossier `fichiers_audio` est créé directement à côté du programme pour stocker :
  - Les fichiers audio importés via l'interface Gradio (`GRADIO_TEMP_DIR`).
  - L'Aperçu généré (`lp_preview.wav`).
  - L'Export final plein format (`leffet_pompeux_output.wav`).
- **Mise à jour version** : Passage à la version `v1.10`.



## [v1.09] - 2026-05-03
### Ajouts et Modifications
- **Paramètres optimisés (French Touch)** : Suite à des recherches ciblées sur l'effet "pompage" classique popularisé par Daft Punk et Justice, les réglages par défaut de l'application ont été affinés pour produire un résultat immédiat, lourd et authentique :
  - *Cutoff* : abaissé à 90 Hz (pour se concentrer strictement sur le corps du kick).
  - *Bass Gain* : monté à 2.5x (pour un déclenchement hyper réactif).
  - *Attack* : abaissé à 1.5 ms (pour écraser instantanément le son sans laisser passer le transitoire).
  - *Release* : ajusté à 130 ms (pour un "groove" de remontée rythmique parfait, proche de la double-croche à 125 BPM).
  - *Compression Amount* : monté à 90% (pour une réduction de gain drastique, la marque de fabrique du genre).
- **Mise à jour version** : Passage à la version `v1.09`.



## [v1.08] - 2026-05-03
### Ajouts et Modifications
- **Aide détaillée (Tooltips)** : Les descriptions de toutes les infobulles d'aide ont été réécrites pour être beaucoup plus détaillées, explicites et pédagogiques.
- **Support Multiligne CSS** : Modification du CSS des infobulles pour supporter le retour à la ligne (`white-space: normal` et `width: 280px`), permettant l'affichage de textes plus longs.
- **Mise à jour version** : Passage à la version `v1.08`.



## [v1.07] - 2026-05-03
### Ajouts et Modifications
- **CSS Tooltips (Fix Ultime)** : Utilisation du sélecteur CSS `:has()` pour remonter l'arborescence DOM de Gradio et désactiver dynamiquement l'`overflow: hidden` et le `contain` de **tous** les parents contenant un tooltip. Les bulles s'afficheront *toujours* au-dessus de n'importe quelle boîte !
- **Mise à jour version** : Passage à la version `v1.07`.



## [v1.06] - 2026-05-03
### Ajouts et Modifications
- **CSS Tooltips** : Forcage du `position: relative !important` sur les classes pour activer le vrai support du `z-index` et corriger enfin la superposition défectueuse. Les tooltips apparaissent au premier plan.
- **Bouton Process** : Le bouton `PROCESS` a été déplacé sous la boîte de titre / description.
- **Mise à jour version** : Passage à la version `v1.06`.



## [v1.05] - 2026-05-03
### Ajouts et Modifications
- **Déplacement du Titre** : Le bloc du titre et de la description a été déplacé sous "Écoute de l'aperçu" dans la colonne de droite, pour s'intercaler parfaitement entre "Enveloppe" et "Export".
- **Fix des Tooltips** : Les boîtes qui tronquaient ou masquaient les tooltips d'aide ont été corrigées avec une élévation de priorité (z-index + overflow-visible global des composants parents).
- **Tooltips supprimés** : Retrait du point d'interrogation pour l'Audio Principal et l'Audio Sidechain.
- **Mise à jour version** : Passage à la version `v1.05`.



## [v1.04] - 2026-05-03
### Ajouts et Modifications
- **Nouveau Titre / Description** : La description a été changée en "Sidechain PHATNESS Compression".
- **Design du Header** : L'en-tête (Titre, description et version) a été déplacé dans une belle boîte stylisée au centre du programme, entre les deux composants d'entrée audio, comblant ainsi l'espace vide.
- **Mise à jour version** : Passage à la version `v1.04`.



## [v1.03] - 2026-05-03
### Ajouts et Modifications
- **Esthétique des Tooltips** : Le point d'interrogation "❔" est remplacé par un icône "❓" centré dans un cercle cyan avec un z-index élevé pour éviter qu'il ne passe sous d'autres éléments.
- **Réorganisation 16:9** : L'interface a été compactée en colonnes afin que tous les paramètres et visuels s'affichent sur une seule page sans avoir besoin de faire défiler, parfait pour du 1080p.
- **Mise à jour version** : Passage à la version `v1.03`.


## [v1.02] - 2026-05-03
### Ajouts et Modifications
- **Aide au survol (Tooltips)** : Ajout d'une icône `❔` interactive à côté de chaque paramètre. Le survol de l'icône affiche une bulle d'aide textuelle décrivant le fonctionnement du paramètre.
- **Mise à jour version** : Passage à la version `v1.02`.


## [v1.01] - 2026-05-03
### Ajouts et Modifications
- **Port réseau modifié** : Le port par défaut est passé de `7860` à `7861` pour éviter les conflits de ports avec d'autres applications.
- **Gestion de version** : Ajout de la version `v1.01` affichée discrètement sous le titre de l'interface Gradio et dans la console.
- **Scripts de lancement** : Création des scripts `start.bat` et `stop.bat` pour démarrer et arrêter l'application facilement en un clic.

## [v1.0] - Version Initiale
### Fonctionnalités
- Moteur de traitement audio avec Pedalboard et Numpy.
- Interface Gradio locale.
- Effet Sidechain / Pumping optimisé (Duckings, Wet/Dry).
- Export en WAV 48kHz 24-bit.
