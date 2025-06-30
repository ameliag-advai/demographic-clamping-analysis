import torch
import pandas as pd
from transformer_lens import HookedTransformer
from sae_lens import SAE
from src.advai.data.prompt_builder import PromptBuilder
import json
from tqdm import tqdm
import numpy as np
from src.advai.analysis.constants_v2 import (
    MALE_FEATURES_WITH_DIRECTIONS,
    FEMALE_FEATURES_WITH_DIRECTIONS,
    YOUNG_FEATURES_WITH_DIRECTIONS,
    MIDDLE_AGE_FEATURES_WITH_DIRECTIONS,
    OLD_FEATURES_WITH_DIRECTIONS,
)

class DemographicClampingExperiment:
    def __init__(self, model, sae, device):
        self.model = model
        self.sae = sae
        self.device = device
        self.feature_sets = {
            "male": MALE_FEATURES_WITH_DIRECTIONS,
            "female": FEMALE_FEATURES_WITH_DIRECTIONS,
            "young": YOUNG_FEATURES_WITH_DIRECTIONS,
            "middle": MIDDLE_AGE_FEATURES_WITH_DIRECTIONS,
            "old": OLD_FEATURES_WITH_DIRECTIONS,
        }

        # Pre-calculate feature difference vectors
        self._calculate_feature_diffs()

        with open('/Users/amelia/bbb/demographic-clamping-analysis/release_evidences.json') as f:
            evidences = json.load(f)
        with open('/Users/amelia/bbb/demographic-clamping-analysis/release_conditions.json') as f:
            conditions = json.load(f)

        self.prompt_builder = PromptBuilder(
            conditions_mapping=conditions,
            demographic_concepts=["age", "sex"],
            evidences=evidences,
            concepts_to_test=["age", "sex"],
            full_prompt_template="A {{ sex }} {{ age }}-year-old patient has the following symptoms: {{ symptoms }}.",
            baseline_prompt_template="Patient has the following symptoms: {{ symptoms }}."
        )

    def _calculate_feature_diffs(self):
        def subtract_dicts(d1, d2):
            res = d1.copy()
            for k, v in d2.items():
                res[k] = res.get(k, 0) - v
            return res

        male_feats = self.feature_sets["male"]
        female_feats = self.feature_sets["female"]
        young_feats = self.feature_sets["young"]
        middle_feats = self.feature_sets["middle"]
        old_feats = self.feature_sets["old"]

        all_age_keys = set(young_feats.keys()) | set(middle_feats.keys()) | set(old_feats.keys())
        avg_age_feats = {k: (young_feats.get(k, 0) + middle_feats.get(k, 0) + old_feats.get(k, 0)) / 3 for k in all_age_keys}

        self.feature_diffs = {
            "male": subtract_dicts(male_feats, female_feats),
            "female": subtract_dicts(female_feats, male_feats),
            "young": subtract_dicts(young_feats, avg_age_feats),
            "middle": subtract_dicts(middle_feats, avg_age_feats),
            "old": subtract_dicts(old_feats, avg_age_feats),
        }

    def get_age_group(self, age):
        if age < 40:
            return "young"
        elif 40 <= age < 65:
            return "middle"
        else:
            return "old"

    def get_feature_diff_vector(self, demographic_info):
        diff_vector = torch.zeros(self.sae.cfg.d_sae, device=self.device)
        if 'sex' in demographic_info:
            sex = demographic_info['sex']
            feature_diff_set = self.feature_diffs.get(sex)
            if feature_diff_set:
                for idx, val in feature_diff_set.items():
                    diff_vector[idx] += val
        if 'age_group' in demographic_info:
            age_group = demographic_info['age_group']
            feature_diff_set = self.feature_diffs.get(age_group)
            if feature_diff_set:
                for idx, val in feature_diff_set.items():
                    diff_vector[idx] += val
        return diff_vector.unsqueeze(0).unsqueeze(0)

    def clamping_hook(self, resid, hook, feature_diff_vector, clamp_level=1):
        original_activations = self.sae.encode(resid)
        modified_activations = original_activations + (feature_diff_vector * clamp_level)
        modified_sae_out = self.sae.decode(modified_activations)
        original_sae_out = self.sae.decode(original_activations)
        return resid - original_sae_out + modified_sae_out

    def run_inference_with_clamping(self, prompt, feature_diff_vector, clamp_level=1):
        self.model.reset_hooks()
        if feature_diff_vector is not None and feature_diff_vector.abs().sum() > 0:
            hook_fn = lambda resid, hook: self.clamping_hook(resid, hook, feature_diff_vector, clamp_level)
            self.model.add_hook("blocks.12.hook_resid_post", hook_fn)
        
        tokens = self.model.to_tokens(prompt).to(self.device)
        with torch.no_grad():
            logits = self.model(tokens)
        
        top_k_logits, top_k_indices = torch.topk(logits[0, -1], 5)
        top_k_tokens = [self.model.to_string(i) for i in top_k_indices]
        
        return top_k_tokens, top_k_logits.cpu().tolist()

    def get_active_features_count(self, text):
        tokens = self.model.to_tokens(text).to(self.device)
        with torch.no_grad():
            _, cache = self.model.run_with_cache(tokens, names_filter="blocks.12.hook_resid_post")
            hidden_states = cache["blocks.12.hook_resid_post"]
            features = self.sae.encode(hidden_states)
        return features.count_nonzero().item()

    def run_experiment(self, cases, output_filepath, num_cases=100):
        import os
        write_header = not os.path.exists(output_filepath)

        for i, case in tqdm(cases.head(num_cases).iterrows(), total=num_cases):
            symptoms = self.prompt_builder._get_symptoms_text(case)
            case_sex = "female" if case['sex'] == "F" else "male"
            case_age_group = self.get_age_group(case['age'])

            # Scenario 1: Age and sex in prompt, no clamping
            prompt1, _ = self.prompt_builder.build_prompts(case, i, ("age", "sex"))
            diag1, logits1 = self.run_inference_with_clamping(prompt1, None)
            res1 = self.format_result(i, case, symptoms, prompt1, diag1, logits1, prompt_age=case['age'], prompt_sex=case_sex)

            results = [res1]
            clamp_levels = [1, 5, 10]

            # Scenario 2: Age in prompt, sex clamped
            prompt2, _ = self.prompt_builder.build_prompts(case, i, ("age",))
            sex_features = self.get_feature_diff_vector({'sex': case_sex})
            for level in clamp_levels:
                diag, logits = self.run_inference_with_clamping(prompt2, sex_features, clamp_level=level)
                res = self.format_result(i, case, symptoms, prompt2, diag, logits, prompt_age=case['age'], features_clamped='sex', clamping_levels=str(level))
                results.append(res)

            # Scenario 3: Sex in prompt, age group clamped
            prompt3, _ = self.prompt_builder.build_prompts(case, i, ("sex",))
            age_features = self.get_feature_diff_vector({'age_group': case_age_group})
            for level in clamp_levels:
                diag, logits = self.run_inference_with_clamping(prompt3, age_features, clamp_level=level)
                res = self.format_result(i, case, symptoms, prompt3, diag, logits, prompt_sex=case_sex, features_clamped='age_group', clamping_levels=str(level))
                results.append(res)

            # Scenario 4: No demo info, age and sex clamped
            prompt4, _ = self.prompt_builder.build_prompts(case, i, tuple())
            combined_features = self.get_feature_diff_vector({'sex': case_sex, 'age_group': case_age_group})
            for level in clamp_levels:
                diag, logits = self.run_inference_with_clamping(prompt4, combined_features, clamp_level=level)
                res = self.format_result(i, case, symptoms, prompt4, diag, logits, features_clamped='age_group, sex', clamping_levels=str(level))
                results.append(res)

            results_df = pd.DataFrame(results)
            results_df.to_csv(output_filepath, mode='a', header=write_header, index=False)
            
            write_header = False

    def format_result(self, case_id, case, symptoms, prompt, diags, logits, **kwargs):
        base_result = {
            "case_id": case_id,
            "dataset_age": case['age'],
            "dataset_sex": "female" if case['sex'] == "F" else "male",
            "features_clamped": "",
            "clamping_levels": "",
            "dataset_symptoms": symptoms,
            "diagnosis": case['pathology'],
            "prompt": prompt,
            "prompt_age": "",
            "prompt_sex": "",
            "diagnosis_1": diags[0],
            "diagnosis_2": diags[1],
            "diagnosis_3": diags[2],
            "diagnosis_4": diags[3],
            "diagnosis_5": diags[4],
            "diagnosis_1_logits": logits[0],
            "diagnosis_2_logits": logits[1],
            "diagnosis_3_logits": logits[2],
            "diagnosis_4_logits": logits[3],
            "diagnosis_5_logits": logits[4],
            "top5": diags,
            "top5_logits": logits,
            "n_active_features": self.get_active_features_count(prompt)
        }
        base_result.update(kwargs)
        return base_result
