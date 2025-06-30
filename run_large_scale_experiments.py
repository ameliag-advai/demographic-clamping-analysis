#!/usr/bin/env python3
"""
Large Scale Bias Experiment Runner
Divides experiments into batches for parallel execution on remote servers.
"""

import argparse
import os
import sys
from datetime import datetime

def create_batch_scripts(total_cases=25000, num_batches=3, device='cuda'):
    """Create batch scripts for parallel execution."""
    
    # Calculate batch sizes
    batch_size = total_cases // num_batches
    remainder = total_cases % num_batches
    
    batch_sizes = [batch_size] * num_batches
    # Distribute remainder across first batches
    for i in range(remainder):
        batch_sizes[i] += 1
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"🚀 Creating {num_batches} batch scripts for {total_cases} total experiments")
    print(f"📊 Batch sizes: {batch_sizes}")
    
    # Create batch scripts
    batch_scripts = []
    start_case = 0
    
    for batch_num in range(num_batches):
        end_case = start_case + batch_sizes[batch_num] - 1
        script_name = f"batch_{batch_num + 1}_experiments_{timestamp}.sh"
        
        script_content = f"""#!/bin/bash
# Batch {batch_num + 1}: Cases {start_case + 1} to {end_case + 1}
# Total cases in this batch: {batch_sizes[batch_num]}

echo "🚀 Starting Batch {batch_num + 1} - Processing {batch_sizes[batch_num]} cases"
echo "📊 Cases {start_case + 1} to {end_case + 1}"
echo "🕒 Started at: $(date)"

# Set environment variables
export CUDA_VISIBLE_DEVICES={batch_num % 4}  # Distribute across GPUs if available
export PYTHONUNBUFFERED=1

# Run the experiment
python run_production_bias_analysis.py \\
    --num-cases {batch_sizes[batch_num]} \\
    --skip-cases {start_case} \\
    --device {device} \\
    --batch-id {batch_num + 1} \\
    --output-suffix "batch_{batch_num + 1}_{timestamp}"

echo "✅ Batch {batch_num + 1} completed at: $(date)"
echo "📁 Results saved with suffix: batch_{batch_num + 1}_{timestamp}"
"""
        
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_name, 0o755)
        
        batch_scripts.append(script_name)
        start_case += batch_sizes[batch_num]
        
        print(f"✅ Created {script_name} - Cases {start_case - batch_sizes[batch_num] + 1} to {start_case}")
    
    # Create tmux runner script
    tmux_script = f"run_all_batches_tmux_{timestamp}.sh"
    tmux_content = f"""#!/bin/bash
# Tmux Runner for Large Scale Bias Experiments
# Run all {num_batches} batches in parallel tmux sessions

echo "🚀 Starting {num_batches} parallel bias experiment batches"
echo "🕒 Started at: $(date)"

# Create new tmux session for batch management
tmux new-session -d -s bias_experiments

# Create windows for each batch
"""
    
    for i, script in enumerate(batch_scripts):
        tmux_content += f"""
# Batch {i + 1}
tmux new-window -t bias_experiments -n "batch_{i + 1}"
tmux send-keys -t bias_experiments:batch_{i + 1} "./{script}" Enter
"""
    
    tmux_content += f"""
echo "✅ All {num_batches} batches started in tmux session 'bias_experiments'"
echo "📊 Monitor progress with: tmux attach -t bias_experiments"
echo "🔍 Switch between batches with: Ctrl+B then window number (1-{num_batches})"
echo "🚪 Detach from tmux with: Ctrl+B then d"

# Show tmux session info
tmux list-sessions
tmux list-windows -t bias_experiments
"""
    
    with open(tmux_script, 'w') as f:
        f.write(tmux_content)
    
    os.chmod(tmux_script, 0o755)
    
    # Create monitoring script
    monitor_script = f"monitor_experiments_{timestamp}.sh"
    monitor_content = f"""#!/bin/bash
# Monitor Large Scale Bias Experiments

echo "📊 Bias Experiment Monitoring Dashboard"
echo "======================================="

# Check tmux sessions
echo "🖥️  Active tmux sessions:"
tmux list-sessions 2>/dev/null || echo "No tmux sessions found"

echo ""
echo "📁 Output files:"
ls -la src/advai/outputs/*batch*{timestamp}* 2>/dev/null || echo "No output files found yet"

echo ""
echo "💾 Disk usage in outputs directory:"
du -sh src/advai/outputs/ 2>/dev/null || echo "Outputs directory not found"

echo ""
echo "🔍 Recent log entries (last 10 lines from each batch):"
for i in {{1..{num_batches}}}; do
    echo "--- Batch $i ---"
    tail -n 5 nohup_batch_$i.out 2>/dev/null || echo "No log file for batch $i yet"
done

echo ""
echo "⚡ System resources:"
echo "CPU usage: $(top -l 1 | grep "CPU usage" | head -1)"
echo "Memory: $(top -l 1 | grep "PhysMem" | head -1)"
echo "GPU usage: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo "No GPU info available")"
"""
    
    with open(monitor_script, 'w') as f:
        f.write(monitor_content)
    
    os.chmod(monitor_script, 0o755)
    
    print(f"\n🎯 Created execution scripts:")
    print(f"📜 Batch scripts: {', '.join(batch_scripts)}")
    print(f"🖥️  Tmux runner: {tmux_script}")
    print(f"📊 Monitor script: {monitor_script}")
    
    return batch_scripts, tmux_script, monitor_script

def main():
    parser = argparse.ArgumentParser(description='Create large scale bias experiment batches')
    parser.add_argument('--total-cases', type=int, default=25000, help='Total number of cases to process')
    parser.add_argument('--num-batches', type=int, default=3, help='Number of parallel batches')
    parser.add_argument('--device', type=str, default='cuda', help='Device to use (cuda/cpu)')
    
    args = parser.parse_args()
    
    batch_scripts, tmux_script, monitor_script = create_batch_scripts(
        total_cases=args.total_cases,
        num_batches=args.num_batches,
        device=args.device
    )
    
    print(f"\n🚀 Ready to run {args.total_cases} experiments in {args.num_batches} parallel batches!")
    print(f"\n📋 Instructions for remote server:")
    print(f"1. Upload all files to your remote server")
    print(f"2. Run: ./{tmux_script}")
    print(f"3. Monitor with: ./{monitor_script}")
    print(f"4. Attach to tmux: tmux attach -t bias_experiments")
    print(f"5. Detach safely: Ctrl+B then d")
    
    print(f"\n⚠️  Important notes:")
    print(f"- Each batch will run independently")
    print(f"- Results will be saved with batch-specific suffixes")
    print(f"- GPU distribution: batches will use different CUDA devices if available")
    print(f"- Sessions will persist even if you disconnect from the server")

if __name__ == "__main__":
    main()
