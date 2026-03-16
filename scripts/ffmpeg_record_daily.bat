@echo off
setlocal enabledelayedexpansion

REM === Configuration ===
set STREAM_URL=http://192.168.1.105:8080/video
set OUTPUT_DIR=static\recordings

REM Create output folder if it doesn't exist
if not exist "%OUTPUT_DIR%" (
  mkdir "%OUTPUT_DIR%"
)

REM === Recording notes ===
REM This records the camera into one MP4 file per calendar day, named YYYY-MM-DD.mp4
REM Using H.264 video. MJPEG from IP Webcam is re-encoded to H.264 to fit MP4 nicely.
REM If you prefer original codec without re-encode (copy), use RTSP/HLS sources with H.264.

REM Variant A (simple, video-only):
REM   Pros: Simpler. Cons: No audio track.
REM ffmpeg -hide_banner -loglevel info -i "%STREAM_URL%" -c:v libx264 -preset veryfast -crf 23 -movflags +faststart -f segment -segment_atclocktime 1 -segment_clocktime 86400 -strftime 1 "%OUTPUT_DIR%\%%Y-%%m-%%d.mp4"

REM Variant B (add silent audio track so players are happier):
REM   Pros: Wider player compatibility. Cons: Slightly more CPU.
REM   Adds a silent audio source at 44.1kHz.
ffmpeg -hide_banner -loglevel info ^
  -stream_loop -1 -re ^
  -i "%STREAM_URL%" ^
  -f lavfi -t 0.1 -i anullsrc=channel_layout=stereo:sample_rate=44100 ^
  -shortest ^
  -c:v libx264 -preset veryfast -crf 23 ^
  -c:a aac -ar 44100 -b:a 128k ^
  -movflags +faststart ^
  -f segment -segment_atclocktime 1 -segment_clocktime 86400 -strftime 1 "%OUTPUT_DIR%\%%Y-%%m-%%d.mp4"

endlocal
