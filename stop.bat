@echo off
echo Arret de L'effet Pompeux...

:: Tenter d'arreter via le titre de la fenetre (si lancee via start.bat)
taskkill /F /FI "WINDOWTITLE eq Leffet Pompeux Server*" /T >nul 2>&1

:: Tenter d'arreter via le processus Python directement
wmic process where "name='python.exe' and commandline like '%%leffet_pompeux.py%%'" call terminate >nul 2>&1
wmic process where "name='pythonw.exe' and commandline like '%%leffet_pompeux.py%%'" call terminate >nul 2>&1

echo.
echo Le serveur a ete arrete.
timeout /t 3 >nul
