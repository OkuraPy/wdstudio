@echo off
setlocal enabledelayedexpansion

for %%f in (*.jpg *.bmb *.web *.jpeg) do (
    set "filename=%%~nf"
    ren "%%f" "!filename!.png"
)

echo Todos os arquivos .jpg foram renomeados para .png
timeout /t 3 >nul
exit