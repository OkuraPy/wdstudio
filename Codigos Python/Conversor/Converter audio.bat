@echo off
setlocal enabledelayedexpansion

REM Define o caminho do executável ffmpeg
set "ffmpeg_path=%~dp0ffmpeg-7.1\bin\ffmpeg.exe"

REM Verifica se o arquivo ffmpeg.exe existe
if not exist "%ffmpeg_path%" (
    echo O arquivo ffmpeg.exe nao foi encontrado na pasta ffmpeg-7.1\bin. Por favor, verifique o nome e tente novamente.
    timeout /t 3 >nul
    exit /b
)

REM Loop através de todos os arquivos de vídeo na pasta
for %%i in (*.mp4 *.avi *.mov *.mkv *.flv *.wmv) do (
    REM Remove caracteres especiais do nome do arquivo de saída
    set "filename=%%~ni"
    set "filename=!filename: =_!"
    
    REM Define o nome do arquivo de saída
    set "output_file=!filename!.wav"
    
    REM Extrai o áudio do arquivo de vídeo
    echo Extraindo audio de "%%i" para "!output_file!"...
    "%ffmpeg_path%" -i "%%i" -vn -acodec pcm_s16le -ar 44100 -ac 2 "!output_file!"
    
    REM Verifica se o arquivo de saída foi criado
    if exist "!output_file!" (
        echo Concluido: %%i foi convertido para !output_file!
    ) else (
        echo Erro ao converter o arquivo: %%i
    )
)

echo.
echo Processo finalizado!
timeout /t 2 >nul
exit