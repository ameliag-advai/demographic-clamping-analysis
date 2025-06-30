import pandas as pd
import torch
from datetime import datetime
from src.advai.models.loader import load_model_and_sae
from custom_experiment import DemographicClampingExperiment

def main():
    data_path = '/Users/amelia/bbb/demographic-clamping-analysis/release-test-patients-age-grouped.csv'
    cases = pd.read_csv(data_path)
    cases.columns = cases.columns.str.lower()
    cases.rename(columns={'evidences': 'features'}, inplace=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, sae = load_model_and_sae(device=device)

    experiment = DemographicClampingExperiment(model, sae, device)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f'demographic_clamping_experiment_results_{timestamp}.csv'
    
    print(f"Running experiment for 5 cases. Results will be saved to {output_filename}")
    experiment.run_experiment(cases, output_filepath=output_filename, num_cases=5)
    print(f"Experiment finished. Results saved to {output_filename}")

if __name__ == "__main__":
    main()
