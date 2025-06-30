#!/usr/bin/env python3
"""
Quick test to verify argument parsing works
"""

import argparse

parser = argparse.ArgumentParser(description="Test Batch Arguments")
parser.add_argument("--num-cases", type=int, default=100, help="Number of cases to process")
parser.add_argument("--skip-cases", type=int, default=0, help="Number of cases to skip (for batch processing)")
parser.add_argument("--device", type=str, default="cpu", help="Device to use (cuda/cpu/mps)")
parser.add_argument("--batch-id", type=int, default=1, help="Batch ID for parallel processing")
parser.add_argument("--output-suffix", type=str, default="", help="Suffix for output files")

args = parser.parse_args()

print("✅ Arguments parsed successfully!")
print(f"📊 Num cases: {args.num_cases}")
print(f"⏭️ Skip cases: {args.skip_cases}")
print(f"🖥️ Device: {args.device}")
print(f"🔢 Batch ID: {args.batch_id}")
print(f"📝 Output suffix: '{args.output_suffix}'")
