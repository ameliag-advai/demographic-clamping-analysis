#!/bin/bash
# Tmux Runner for Large Scale Bias Experiments
# Run all 3 batches in parallel tmux sessions

echo "🚀 Starting 3 parallel bias experiment batches"
echo "🕒 Started at: $(date)"

# Create new tmux session for batch management
tmux new-session -d -s bias_experiments

# Create windows for each batch

# Batch 1
tmux new-window -t bias_experiments -n "batch_1"
tmux send-keys -t bias_experiments:batch_1 "./batch_1_experiments_20250630_014132.sh" Enter

# Batch 2
tmux new-window -t bias_experiments -n "batch_2"
tmux send-keys -t bias_experiments:batch_2 "./batch_2_experiments_20250630_014132.sh" Enter

# Batch 3
tmux new-window -t bias_experiments -n "batch_3"
tmux send-keys -t bias_experiments:batch_3 "./batch_3_experiments_20250630_014132.sh" Enter

echo "✅ All 3 batches started in tmux session 'bias_experiments'"
echo "📊 Monitor progress with: tmux attach -t bias_experiments"
echo "🔍 Switch between batches with: Ctrl+B then window number (1-3)"
echo "🚪 Detach from tmux with: Ctrl+B then d"

# Show tmux session info
tmux list-sessions
tmux list-windows -t bias_experiments
