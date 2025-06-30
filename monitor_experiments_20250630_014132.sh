#!/bin/bash
# Monitor Large Scale Bias Experiments

echo "📊 Bias Experiment Monitoring Dashboard"
echo "======================================="

# Check tmux sessions
echo "🖥️  Active tmux sessions:"
tmux list-sessions 2>/dev/null || echo "No tmux sessions found"

echo ""
echo "📁 Output files:"
ls -la src/advai/outputs/*batch*20250630_014132* 2>/dev/null || echo "No output files found yet"

echo ""
echo "💾 Disk usage in outputs directory:"
du -sh src/advai/outputs/ 2>/dev/null || echo "Outputs directory not found"

echo ""
echo "🔍 Recent log entries (last 10 lines from each batch):"
for i in {1..3}; do
    echo "--- Batch $i ---"
    tail -n 5 nohup_batch_$i.out 2>/dev/null || echo "No log file for batch $i yet"
done

echo ""
echo "⚡ System resources:"
echo "CPU usage: $(top -l 1 | grep "CPU usage" | head -1)"
echo "Memory: $(top -l 1 | grep "PhysMem" | head -1)"
echo "GPU usage: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "No GPU info available")"
