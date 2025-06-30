#!/usr/bin/env python3
"""
Standalone script to run demographic clamping combinations using src/advai modules.
"""
import argparse
from datetime import datetime

import torch

from src.advai.models.loader import load_model_and_sae
from src.advai.analysis.pipeline import run_analysis_pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Run demographic clamping experiment.")
    parser.add_argument("--patient-file", required=True,
                        help="Path to patient data CSV file.")
    parser.add_argument("--conditions", required=True,
                        help="Path to conditions JSON file.")
    parser.add_argument("--evidences", required=True,
                        help="Path to evidences JSON file.")
    parser.add_argument("--num-cases", type=int, default=100,
                        help="Number of cases to process.")
    parser.add_argument("--start-case", type=int, default=0,
                        help="Index of first case to process.")
    parser.add_argument("--device", default=None,
                        help="Device to use (cpu or cuda).")
    parser.add_argument("--output", default=None,
                        help="Output CSV filename (optional).")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load model and SAE
    model, sae = load_model_and_sae(device=args.device)

    # Determine output name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = args.output or f"clamping_results_{timestamp}.csv"

    # Run pipeline
    run_analysis_pipeline(
        patient_data_path=args.patient_file,
        conditions_json_path=args.conditions,
        evidences_json_path=args.evidences,
        model=model,
        sae=sae,
        num_cases=args.num_cases,
        start_case=args.start_case,
        output_name=output_name
    )

    print(f"✅ Demographic clamping experiment completed. Results saved to {output_name}")


if __name__ == "__main__":
    main()
