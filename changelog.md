# Changelog

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
