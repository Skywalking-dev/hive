#!/bin/bash
# Monitor E2E test execution in real-time
# Highlights important events and filters noise

LOG_FILE="${1:-test-debug.log}"
TEST_PID_FILE="${2:-test.pid}"

echo "🔍 E2E Test Monitor"
echo "==================="
echo ""

# Check if test is running
if [ -f "$TEST_PID_FILE" ]; then
    TEST_PID=$(cat "$TEST_PID_FILE")
    if ps -p "$TEST_PID" > /dev/null 2>&1; then
        echo "✅ Test ejecutándose (PID: $TEST_PID)"
    else
        echo "⚠️  Test no está ejecutándose"
    fi
else
    echo "ℹ️  No se encontró archivo de PID (opcional)"
fi

echo ""
echo "📊 Monitoreando: $LOG_FILE"
echo "Presiona Ctrl+C para salir"
echo ""

# Monitor log file
if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  Archivo de log no encontrado: $LOG_FILE"
    echo "Esperando que se cree..."
    sleep 2
fi

# Tail log file with highlighting
tail -f "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
    # Success indicators
    if echo "$line" | grep -qE "✓|Success|Passed|completed"; then
        echo "✅ $line"
    # Error indicators
    elif echo "$line" | grep -qE "❌|Error:|Failed|Timeout"; then
        echo "❌ $line"
    # Progress indicators
    elif echo "$line" | grep -qE "📍|📄|⏳"; then
        echo "$line"
    # Payment/MP related
    elif echo "$line" | grep -qiE "MercadoPago|MP|payment|checkout"; then
        echo "💳 $line"
    # Selected/Found events
    elif echo "$line" | grep -qE "Selected|Found|Click"; then
        echo "🔘 $line"
    fi
done

