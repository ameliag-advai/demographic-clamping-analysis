#!/bin/bash
# Batch 3: Cases 16668 to 25000
# Total cases in this batch: 8333

echo "🚀 Starting Batch 3 - Processing 8333 cases"
echo "📊 Cases 16668 to 25000"
echo "🕒 Started at: $(date)"

# Set environment variables
export CUDA_VISIBLE_DEVICES=2  # Distribute across GPUs if available
export PYTHONUNBUFFERED=1

# Run the experiment
python run_production_bias_analysis.py \
    --num-cases 8333 \
    --skip-cases 16667 \
    --device cuda \
    --batch-id 3 \
    --output-suffix "batch_3_20250630_014132"

echo "✅ Batch 3 completed at: $(date)"
echo "📁 Results saved with suffix: batch_3_20250630_014132"
