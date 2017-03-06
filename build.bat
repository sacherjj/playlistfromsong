REM  Batch File to build executable with PyInstaller on Windows

REM  CANNOT make windowed only, due to subprocess.
REM    --noconsole ^
REM    --windowed ^

pyinstaller --noconfirm ^
    --clean ^
    --onefile ^
	--noupx ^
	--win-private-assemblies ^
	--name playlistfromsong ^
	--workpath .\compile\build ^
	--distpath .\compile\dist ^
	--specpath .\compile ^
	--key QPWOEIRUTYALSKDJFHG ^
	playlistfromsong\main.py
