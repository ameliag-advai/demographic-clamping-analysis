#!/bin/bash
# monitor_gpu_experiments.sh - Monitor 3-GPU experiment progress

clear
echo "🔍 GPU Experiment Monitor"
echo "========================="
date
echo ""

echo "📊 GPU Status:"
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | while read line; do
    echo "  GPU $line"
done
echo ""

echo "🖥️  Tmux Sessions:"
tmux list-sessions 2>/dev/null | grep -E "batch[1-3]" || echo "  No batch sessions found"
echo ""

echo "📁 Output Files:"
if ls outputs/*batch*_results_*.csv 1> /dev/null 2>&1; then
    echo "  Results files:"
    ls -lh outputs/*batch*_results_*.csv | awk '{print "    " $9 " (" $5 ")"}'
else
    echo "  No result files found yet"
fi

if ls outputs/*batch*_activations_*.csv 1> /dev/null 2>&1; then
    echo "  Activation files:"
    ls -lh outputs/*batch*_activations_*.csv | awk '{print "    " $9 " (" $5 ")"}'
fi
echo ""

echo "💾 Storage Usage:"
if [ -d "outputs" ]; then
    du -sh outputs/ | awk '{print "  Total: " $1}'
else
    echo "  Output directory not found"
fi
echo ""

echo "🔄 Recent Activity (last 5 lines from each batch):"
for i in {1..3}; do
    session="batch$i"
    if tmux has-session -t $session 2>/dev/null; then
        echo "  --- Batch $i ---"
        # Try to capture recent output from tmux session
        tmux capture-pane -t $session -p | tail -n 3 | sed 's/^/    /'
    else
        echo "  --- Batch $i: Not running ---"
    fi
done
echo ""

echo "⚡ Quick Commands:"
echo "  Attach to batch: tmux attach -t batch1 (or batch2, batch3)"
echo "  Continuous GPU:  watch -n 5 nvidia-smi"
echo "  Kill session:    tmux kill-session -t batch1"
echo "  Restart monitor: ./monitor_gpu_experiments.sh"
