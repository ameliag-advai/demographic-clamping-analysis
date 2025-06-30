#!/bin/bash
# run_all_gpu_batches.sh - Optimized for 3 GPU server

echo "🚀 Starting 25,000 experiments across 3 GPUs"
echo "📊 GPU Status:"
nvidia-smi --query-gpu=index,name,memory.free --format=csv

echo ""
echo "🎯 Starting experiments..."

# Batch 1 - GPU 0 (Cases 1-8334)
echo "📍 Batch 1: GPU 0 - Cases 1 to 8,334"
tmux new-session -d -s batch1
tmux send-keys -t batch1 "export CUDA_VISIBLE_DEVICES=0" Enter
tmux send-keys -t batch1 "python run_production_bias_analysis.py --num-cases 8334 --skip-cases 0 --device cuda --batch-id 1 --output-suffix batch1_gpu0" Enter

sleep 2

# Batch 2 - GPU 1 (Cases 8335-16667)
echo "📍 Batch 2: GPU 1 - Cases 8,335 to 16,667"
tmux new-session -d -s batch2
tmux send-keys -t batch2 "export CUDA_VISIBLE_DEVICES=1" Enter
tmux send-keys -t batch2 "python run_production_bias_analysis.py --num-cases 8333 --skip-cases 8334 --device cuda --batch-id 2 --output-suffix batch2_gpu1" Enter

sleep 2

# Batch 3 - GPU 2 (Cases 16668-25000)
echo "📍 Batch 3: GPU 2 - Cases 16,668 to 25,000"
tmux new-session -d -s batch3
tmux send-keys -t batch3 "export CUDA_VISIBLE_DEVICES=2" Enter
tmux send-keys -t batch3 "python run_production_bias_analysis.py --num-cases 8333 --skip-cases 16667 --device cuda --batch-id 3 --output-suffix batch3_gpu2" Enter

echo ""
echo "✅ All 3 batches started successfully!"
echo ""
echo "📊 Management Commands:"
echo "  Monitor sessions: tmux list-sessions"
echo "  Attach to batch:  tmux attach -t batch1 (or batch2, batch3)"
echo "  Detach safely:    Ctrl+B then d"
echo "  Kill session:     tmux kill-session -t batch1"
echo ""
echo "🔍 Monitoring Commands:"
echo "  GPU usage:        watch -n 5 nvidia-smi"
echo "  Progress:         ls -la src/advai/outputs/*batch*_results_*.csv"
echo "  File sizes:       du -sh src/advai/outputs/"
echo ""
echo "⏱️  Expected completion: 3-4 hours"
echo "💾 Results will be saved with batch-specific suffixes"
