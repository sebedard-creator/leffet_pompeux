@echo off
title Leffet Pompeux Server
echo Demarrage de L'effet Pompeux...
cd /d "%~dp0"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERREUR] L'environnement virtuel n'est pas trouve ! 
    echo Veuillez l'installer avec : python -m venv venv ^& venv\Scripts\pip install -r requirements.txt
    pause
    exit /b
)
start /min "Leffet Pompeux Server" python leffet_pompeux.py
echo Serveur demarre !
echo.
echo L'interface sera bientot disponible a l'adresse :
echo http://localhost:7861
echo.
echo (Vous pouvez fermer cette fenetre, le serveur tourne en arriere-plan.)
echo Pour arreter le serveur, utilisez le fichier stop.bat.
timeout /t 5 >nul
