@echo off
setlocal enabledelayedexpansion

REM Altere para o caminho da sua pasta
set "pasta_alvo=C:\Users\Infoaplicados\Desktop\imagens"

cd "%pasta_alvo%"

REM Reinicia os contadores para cada extensão
set contador_png=1
set contador_jpg=1
set contador_web=1
set contador_jpeg=1
set contador_mp4=1
set contador_mov=1
set contador_avi=1
set contador_wmv=1
set contador_mkv=1
set contador_doc=1
set contador_docx=1
set contador_pdf=1

REM Processa arquivos por extensão
for %%x in (png jpg web jpeg mp4 mov avi wmv mkv doc docx pdf) do (
    for %%f in (*%%x) do (
        set "novo_nome=!contador_%%x!%%~xf"
        ren "%%f" "!novo_nome!"
        set /a contador_%%x+=1
    )
)

endlocal
