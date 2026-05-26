@echo off
REM ============================================================================
REM  İlaçTarif Watcher - Arka plan (minimize konsol) başlatıcı
REM  Botanik EOS + Medula açıldığında etiketleri otomatik üretir.
REM ============================================================================

REM Proje dizini (bu .bat'ın bulunduğu yerden bir üst)
cd /d "%~dp0\.."

REM Log dizini
if not exist "data\logs" mkdir "data\logs"

REM Zaman damgalı log dosyası (her başlatmada yeni log)
set TS=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TS=%TS: =0%
set LOG=data\logs\watcher_%TS%.log

REM Python varlığını kontrol et
where python >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi! PATH ayarini kontrol edin. >> "%LOG%"
    exit /b 1
)

REM Eski logları temizle (30 günden eski)
forfiles /p "data\logs" /s /m watcher_*.log /d -30 /c "cmd /c del @path" 2>nul

REM Python'u minimize edilmiş konsolda çalıştır
REM /MIN: pencere küçültülmüş başlar
REM /B yok: konsol görünür ama minimize
title İlaçTarif Watcher (Arka plan)
echo [%date% %time%] Watcher başlatılıyor... >> "%LOG%"
python -u scripts\watch_medula.py >> "%LOG%" 2>&1
