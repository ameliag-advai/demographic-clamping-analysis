#!/bin/bash
# Batch 1: Cases 1 to 8334
# Total cases in this batch: 8334

echo "🚀 Starting Batch 1 - Processing 8334 cases"
echo "📊 Cases 1 to 8334"
echo "🕒 Started at: $(date)"

# Set environment variables
export CUDA_VISIBLE_DEVICES=0  # Distribute across GPUs if available
export PYTHONUNBUFFERED=1

# Run the experiment
python run_production_bias_analysis.py \
    --num-cases 8334 \
    --skip-cases 0 \
    --device cuda \
    --batch-id 1 \
    --output-suffix "batch_1_20250630_014132"

echo "✅ Batch 1 completed at: $(date)"
echo "📁 Results saved with suffix: batch_1_20250630_014132"
