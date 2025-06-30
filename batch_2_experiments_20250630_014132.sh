#!/bin/bash
# Batch 2: Cases 8335 to 16667
# Total cases in this batch: 8333

echo "🚀 Starting Batch 2 - Processing 8333 cases"
echo "📊 Cases 8335 to 16667"
echo "🕒 Started at: $(date)"

# Set environment variables
export CUDA_VISIBLE_DEVICES=1  # Distribute across GPUs if available
export PYTHONUNBUFFERED=1

# Run the experiment
python run_production_bias_analysis.py \
    --num-cases 8333 \
    --skip-cases 8334 \
    --device cuda \
    --batch-id 2 \
    --output-suffix "batch_2_20250630_014132"

echo "✅ Batch 2 completed at: $(date)"
echo "📁 Results saved with suffix: batch_2_20250630_014132"
