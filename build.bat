REM    --noconsole ^
REM    --windowed ^
REM    --clean ^

pyinstaller --noconfirm ^
    --onefile ^
	--noupx ^
	--win-private-assemblies ^
	--name playlistfromsong ^
	--workpath .\compile\build ^
	--distpath .\compile\dist ^
	--specpath .\compile ^
	--key QPWOEIRUTYALSKDJFHG ^
	playlistfromsong\main.py
