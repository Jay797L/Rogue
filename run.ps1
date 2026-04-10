# Получаем директорию скрипта
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Добавляем директорию скрипта в PATH, если её там нет
if ($env:PATH -notlike "*$ScriptDir*") {
    $env:PATH += ";$ScriptDir"
}

# Активируем виртуальное окружение, если оно существует
$venvActivate = Join-Path $ScriptDir ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
}

# Устанавливаем PYTHONPATH
$env:PYTHONPATH = "$env:PYTHONPATH;$PWD"

# Проверяем, есть ли аргументы командной строки
if ($args.Count -eq 0) {
    Write-Host "Ничего не пришло, скрипт завершается"
    exit 0
}
else {
    Write-Host "Получены аргументы, запускаем Python в цикле с задержкой 1 секунда"
    while ($true) {
        # Запускаем lint.sh (если он существует)
        if (Test-Path ".\lint.ps1") {
            # & .\lint.ps1
        }
        
        # Запускаем Python скрипт с переданными аргументами
        python $args
        
        Write-Host ""
        Write-Host "Python скрипт завершился."
        Write-Host "Нажмите Enter для повторного запуска или Ctrl+C для выхода..."
        Read-Host
    }
}