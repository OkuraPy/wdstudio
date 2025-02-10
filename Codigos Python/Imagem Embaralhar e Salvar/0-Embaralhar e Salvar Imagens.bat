@echo off
setlocal enabledelayedexpansion

:: Define as extensões de imagem comuns
set "extensions=*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.ico"

:: Criar pasta principal
echo Iniciando processo...
rd /s /q "Imagens selecionadas" 2>nul
mkdir "Imagens selecionadas"

:: Criar lista de imagens
echo Listando arquivos de imagem...
del /f /q temp_list.txt 2>nul
for %%x in (%extensions%) do (
    dir /b %%x 2>nul >> temp_list.txt
)

:: Contar arquivos
set /a total=0
for /f %%A in ('type temp_list.txt ^| find /c /v ""') do set total=%%A

if %total% EQU 0 (
    echo Nenhuma imagem encontrada!
    pause
    goto :EOF
)

:: Criar lista embaralhada
echo Embaralhando !total! imagens...
set "tempFile=temp_shuffled.txt"
del /f /q !tempFile! 2>nul
type nul > !tempFile!

for /f "delims=" %%a in ('type temp_list.txt') do (
    set /a "rand=!random! %% 1000"
    echo !rand!:%%a >> !tempFile!
)

sort /R !tempFile! > temp_sorted.txt

:: Copiar arquivos
set /a pasta=1
set /a contador=1

for /f "tokens=1* delims=:" %%a in (temp_sorted.txt) do (
    set /a "numeroLocal=!contador!%%24"
    if !numeroLocal! EQU 0 set numeroLocal=24
    
    mkdir "Imagens selecionadas\Pasta_!pasta!" 2>nul
    echo Copiando imagem !contador! de %total% - Pasta !pasta! [!numeroLocal!/24]
    
    for %%i in ("%%b") do (
        set "ext=%%~xi"
        copy "%%b" "Imagens selecionadas\Pasta_!pasta!\!numeroLocal!!ext!" >nul
    )
    
    if !numeroLocal! EQU 24 (
        set /a pasta+=1
    )
    set /a contador+=1
)

:: Limpar arquivos temporários
echo Limpando arquivos temporários...
del /f /q temp_list.txt
del /f /q temp_shuffled.txt
del /f /q temp_sorted.txt

echo Processo concluído! Foram processadas %total% imagens em !pasta! pastas.
echo Pressione qualquer tecla para sair...
pause >nul