@echo off
setlocal enabledelayedexpansion

echo Renomeando imagens na pasta atual: %cd%

REM Inicializa o contador e o timestamp
set "contador=1"
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,14%"

REM Renomeia os arquivos
for %%f in (*.png *.jpg *.jpeg *.webp *.docx *.mp4 *.mov *.avi *.wmv *.mkv *.flv *.mpeg *.mpg *.webm *.3gp *.m4v *.ts *.vob *.mxf *.rmvb *.divx) do (
    REM Gera um nome único para cada arquivo
    set /a "random_num=!random! %% 10000 + 1"
    set "novo_nome=%timestamp%_!random_num!_!contador!%%~xf"
    
    echo Tentando renomear: "%%f" para "!novo_nome!"
    ren "%%f" "!novo_nome!" 2>nul
    if errorlevel 1 (
        echo Não foi possível renomear "%%f". O arquivo original permanece intacto.
    ) else (
        echo Arquivo renomeado com sucesso.
    )
    set /a "contador+=1"
)

echo Processo concluído. As imagens foram renomeadas de forma única.
echo Nenhum arquivo foi apagado durante o processo.
endlocal