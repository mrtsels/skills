#!/bin/bash
set -e

echo "===== $(basename $0) — startup ====="
echo "Java: $(java -version 2>&1 | head -1)"
echo "JAR: /app/app.jar"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"

# Loop: keep container running even if JVM crashes
# Docker sees PID 1 (this script) alive → container stays "up"
# restart:unless-stopped in compose handles the outer lifecycle
while true; do
  echo "--- Starting JVM ---"
  java -Xms256m -Xmx512m -jar /app/app.jar \
    2>&1
  EXIT_CODE=$?
  echo "--- JVM exited with code $EXIT_CODE, restarting in 3s ---"
  sleep 3
done
