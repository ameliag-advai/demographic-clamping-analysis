# Single Server Commands for 25,000 Experiments

## 🖥️ Server Specs Detected
- **3x NVIDIA RTX 6000 Ada Generation GPUs**
- **49GB VRAM per GPU**
- **CUDA 12.9 Support**

## 🚀 Optimized Commands for Your Server

### Option 1: Run All 3 Batches Simultaneously (Recommended)

Open 3 separate tmux sessions, one for each GPU:

```bash
# Terminal 1 - GPU 0 (Batch 1: 8,334 cases)
tmux new-session -d -s batch1
tmux send-keys -t batch1 "export CUDA_VISIBLE_DEVICES=0" Enter
tmux send-keys -t batch1 "python run_production_bias_analysis.py --num-cases 8334 --skip-cases 0 --device cuda --batch-id 1 --output-suffix batch1_gpu0" Enter

# Terminal 2 - GPU 1 (Batch 2: 8,333 cases)  
tmux new-session -d -s batch2
tmux send-keys -t batch2 "export CUDA_VISIBLE_DEVICES=1" Enter
tmux send-keys -t batch2 "python run_production_bias_analysis.py --num-cases 8333 --skip-cases 8334 --device cuda --batch-id 2 --output-suffix batch2_gpu1" Enter

# Terminal 3 - GPU 2 (Batch 3: 8,333 cases)
tmux new-session -d -s batch3
tmux send-keys -t batch3 "export CUDA_VISIBLE_DEVICES=2" Enter
tmux send-keys -t batch3 "python run_production_bias_analysis.py --num-cases 8333 --skip-cases 16667 --device cuda --batch-id 3 --output-suffix batch3_gpu2" Enter
```

### Option 2: Single Command Script (Automated)

Create and run this script:

```bash
#!/bin/bash
# run_all_gpu_batches.sh

echo "🚀 Starting 25,000 experiments across 3 GPUs"
echo "📊 GPU Status:"
nvidia-smi --query-gpu=index,name,memory.free --format=csv

# Batch 1 - GPU 0
echo "🎯 Starting Batch 1 on GPU 0..."
tmux new-session -d -s batch1
tmux send-keys -t batch1 "export CUDA_VISIBLE_DEVICES=0 && python run_production_bias_analysis.py --num-cases 8334 --skip-cases 0 --device cuda --batch-id 1 --output-suffix batch1_gpu0" Enter

# Batch 2 - GPU 1  
echo "🎯 Starting Batch 2 on GPU 1..."
tmux new-session -d -s batch2
tmux send-keys -t batch2 "export CUDA_VISIBLE_DEVICES=1 && python run_production_bias_analysis.py --num-cases 8333 --skip-cases 8334 --device cuda --batch-id 2 --output-suffix batch2_gpu1" Enter

# Batch 3 - GPU 2
echo "🎯 Starting Batch 3 on GPU 2..."
tmux new-session -d -s batch3
tmux send-keys -t batch3 "export CUDA_VISIBLE_DEVICES=2 && python run_production_bias_analysis.py --num-cases 8333 --skip-cases 16667 --device cuda --batch-id 3 --output-suffix batch3_gpu2" Enter

echo "✅ All 3 batches started!"
echo "📊 Monitor with: tmux list-sessions"
echo "🔍 Attach to batch: tmux attach -t batch1 (or batch2, batch3)"
echo "🚪 Detach safely: Ctrl+B then d"
```

### Option 3: Individual Commands (Copy-Paste Ready)

**Batch 1 (GPU 0):**
```bash
tmux new-session -d -s batch1 'export CUDA_VISIBLE_DEVICES=0; python run_production_bias_analysis.py --num-cases 8334 --skip-cases 0 --device cuda --batch-id 1 --output-suffix batch1_gpu0'
```

**Batch 2 (GPU 1):**
```bash
tmux new-session -d -s batch2 'export CUDA_VISIBLE_DEVICES=1; python run_production_bias_analysis.py --num-cases 8333 --skip-cases 8334 --device cuda --batch-id 2 --output-suffix batch2_gpu1'
```

**Batch 3 (GPU 2):**
```bash
tmux new-session -d -s batch3 'export CUDA_VISIBLE_DEVICES=2; python run_production_bias_analysis.py --num-cases 8333 --skip-cases 16667 --device cuda --batch-id 3 --output-suffix batch3_gpu2'
```

## 📊 Monitoring Commands

**Check all sessions:**
```bash
tmux list-sessions
```

**Monitor GPU usage:**
```bash
watch -n 5 nvidia-smi
```

**Check progress:**
```bash
# Count completed results
ls -la src/advai/outputs/*batch*_results_*.csv | wc -l

# Check file sizes
du -sh src/advai/outputs/
```

**Attach to specific batch:**
```bash
tmux attach -t batch1  # or batch2, batch3
```

## 🎯 Expected Performance

- **Per GPU:** ~2,800 cases per hour (estimated)
- **Total Runtime:** ~3-4 hours for all 25,000 experiments
- **Memory Usage:** ~8-12GB VRAM per GPU
- **Output Files:** 3 separate result sets with batch-specific suffixes

## ⚠️ Important Notes

1. **GPU Isolation:** Each batch uses a dedicated GPU via `CUDA_VISIBLE_DEVICES`
2. **Independent Execution:** Batches run completely independently
3. **Persistent Sessions:** tmux keeps experiments running if you disconnect
4. **Unique Outputs:** Each batch saves results with different suffixes
5. **Error Recovery:** If one batch fails, others continue unaffected

## 🔧 Troubleshooting

**If a batch stops:**
```bash
tmux attach -t batch1  # Check the session
# Restart if needed:
tmux kill-session -t batch1
# Then rerun the command
```

**Check memory usage:**
```bash
nvidia-smi -l 5  # Continuous monitoring
```
