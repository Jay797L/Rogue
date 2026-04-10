function ShowCopy {
    param(
        [string]$dir = "."
    )
    
    $tempFile = [System.IO.Path]::GetTempFileName()
    $tempList = [System.IO.Path]::GetTempFileName()
    
    # Расширения текстовых файлов
    $textExts = @(
        "*.c", "*.h", "*.cpp", "*.hpp", "*.cc", "*.cxx", "*.hh", "*.hxx",
        "*.py", "*.pyx", "*.pyi",
        "*.ps1", "*.psm1", "*.psd1",
        "*.js", "*.ts", "*.jsx", "*.tsx", "*.mjs", "*.cjs",
        "*.html", "*.htm", "*.xhtml", "*.xml", "*.svg",
        "*.css", "*.scss", "*.sass", "*.less",
        "*.json", "*.json5", "*.yaml", "*.yml", "*.toml", "*.ini",
        "*.md", "*.markdown", "*.rst", "*.txt", "*.text", "*.log",
        "*.sql", "*.csv", "*.tsv",
        "*.gitignore", "*.gitattributes",
        "Dockerfile*", "Makefile", "CMakeLists.txt",
        "package.json", "requirements.txt", "README*", "LICENSE*"
    )
    
    # Собираем файлы
    $files = @()
    foreach ($ext in $textExts) {
        $found = Get-ChildItem -Path $dir -Filter $ext -Recurse -File -ErrorAction SilentlyContinue
        $files += $found
    }
    
    # Фильтруем исключения
    $excludeDirs = @(".git", "node_modules", "__pycache__", ".venv", "venv", "build", "dist", ".idea", ".vscode")
    $files = $files | Where-Object {
        $path = $_.FullName
        $exclude = $false
        foreach ($exDir in $excludeDirs) {
            if ($path -like "*\$exDir\*") {
                $exclude = $true
                break
            }
        }
        -not $exclude
    } | Sort-Object -Unique
    
    $fileCount = $files.Count
    
    if ($fileCount -eq 0) {
        Write-Host "Текстовые файлы не найдены" -ForegroundColor Yellow
        Remove-Item $tempFile, $tempList -ErrorAction SilentlyContinue
        return
    }
    
    # Собираем содержимое
    foreach ($file in $files) {
        "=== $($file.FullName) ===" | Out-File -FilePath $tempFile -Append -Encoding UTF8
        
        # Добавляем нумерацию строк
        $content = Get-Content $file.FullName -ErrorAction SilentlyContinue
        $lineNumber = 1
        foreach ($line in $content) {
            "{0,6}  {1}" -f $lineNumber, $line | Out-File -FilePath $tempFile -Append -Encoding UTF8
            $lineNumber++
        }
        "" | Out-File -FilePath $tempFile -Append -Encoding UTF8
        "" | Out-File -FilePath $tempFile -Append -Encoding UTF8
    }
    
    # Копируем в буфер обмена
    Get-Content $tempFile | Set-Clipboard
    Write-Host "Скопировано $fileCount файлов с нумерацией строк" -ForegroundColor Green
    
    # Очистка
    Remove-Item $tempFile, $tempList -ErrorAction SilentlyContinue
}

# Создаём алиас
Set-Alias -Name sc -Value ShowCopy