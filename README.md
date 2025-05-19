# Forecasting Policy Impact

A preliminary demo framework for evaluating the effectiveness of language models in predicting the outcomes of policy interventions for environmental outcomes.

## 🚨 IMPORTANT DISCLAIMER 🚨

**This project is currently in an experimental phase. The training data used by the language models may already include the results of the policy interventions being forecasted, which could artificially inflate performance metrics.**

**Next steps:**
- Collect new data from Web of Science and Scopus
	- **NOTE**: Preliminary investigation from Scopus freely available abstracts (not in this repo) has revealed approximately 20,000 records with impact evaluations published in the years 2022, 2023, 2024, and 2025. Based on the results of `scripts/count_abstracts_with_interventions_past_2021.py`, approximately 3% of impact evaluations pertain to impact evaluations in the 3 years prior to publication (based on years mentioned in the abstracts and manual inspection). Because each abstract has a mean of 1.7 outcomes with information per record, this means there are approximately 600 records which would describe interventions and 1000 gradeable outcomes present in scopus. Because gpt4 has a training cutoff in 2021, these interventions could be used to produced contamination-free forecasts to provide a statistically robust test of LLM ability to forecast policy impact based on an intervention, including a sizeable validation set.
- Perform manual categorization with the 3ie database as a baseline
- Ensure forecasts are not leveraging results that may be present in LLM training data

## Overview

This project aims to evaluate how well language models can forecast the outcomes of policy interventions, particularly in developing countries. The pipeline:

1. Collects policy intervention records from the 3ie Development Evidence Portal
2. Extracts intervention descriptions and outcomes from paper abstracts
3. Grades actual outcomes based on a 5-point scale
4. Uses language models to forecast expected outcomes using only intervention descriptions
5. Evaluates forecast accuracy against actual outcomes

## Pipeline Stages

### 1. Building the Database (`1_make_database.py`)

Queries the 3ie Development Evidence Portal API to collect data on each impact evaluation record, including:
- Paper titles, abstracts, and publication year
- Outcome categories for the abstract

The data is saved to `impact_records.yaml`.

### 2. Outcome and Intervention Classification (`2_classify_abstract_outcomes_and_interventions.py`)

Uses GPT-4.1-mini to extract and classify:
- Descriptions of interventions from abstracts (excluding results)
- Information about specific outcomes mentioned in the abstracts

Results are stored in `abstract_extractions.yaml`.

### 3. Outcome Grading (`3_grade_outcomes.py`)

Evaluates each outcome from the abstracts on a 5-point scale:
1. **Very significant**: Substantial improvement with robust evidence
2. **Significant**: Noticeable improvement with moderate evidence
3. **Neutral/mixed results**: Some improvement but limited or unclear
4. **No effect**: No discernible impact
5. **Outcome was worsened**: Negative impact

Results are stored in `abstract_outcome_grades.yaml`.

### 4. Outcome Forecasting (`4_predict_the_grade_based_on_intervention.py`)

Asks a language model (GPT-4.1) to predict the expected outcomes using only:
- The intervention description
- The name of the outcome metric

The model provides:
- Step-by-step reasoning in a scratchpad
- A concise qualitative prediction
- A grade on the same 5-point scale

Results are stored in `abstract_outcome_forecasts.yaml`.

### 5. Forecast Evaluation (`5_report_stats_on_forecasts.py`)

Compares forecasted grades against actual outcome grades using metrics:
- RMSE (Root Mean Square Error)
- Accuracy (exact 5-class match)
- Macro-F1 score
- Brier score (binary classification where "positive" ≥ 0.75)

The script also compares against two baselines:
- Most-common grade baseline
- Random grade baseline

## Results (133 impact forecasts, for impact evaluations published in 2024)

| Metric                                            | GPT4.1 single-shot | Always "Significant" baseline | Random baseline | Reference points                                                                                           |
| ------------------------------------------------- | ---------- | -------------------- | --------------- | ---------------------------------------------------------------------------------------------------------- |
| **RMSE** (0 ➜ "worsened", 1 ➜ "very significant") | **0.308**  | 0.306                | 0.498           | –                                                                                                          |
| **Accuracy** (exact 5-class match)                | **48 %**   | **51 %**             | 20 %            | –                                                                                                          |
| **Macro-F1**                                      | 0.334      | –                    | –               | –                                                                                                          |
| **Brier (binary "positive" ≥ 0.75)**              | **0.203**  | 0.206                | 0.250           | • human crowd on real forecasting tournaments ≈ 0.149 <br>• GPT-4 zero-shot on the same benchmark ≈ 0.208  |

### 🚨 DISCLAIMER ON RESULTS 🚨

The current model's performance may be influenced by the fact that the LLM training data potentially includes information about these intervention outcomes. **Future work will focus on forecasting truly novel policies where results are not present in the training data.**

## Interpretation of Results

- The model shows ability to extract signal (Brier score of 0.203 vs. random baseline of 0.250)
- Performance is comparable to zero-shot GPT-4 but trails human forecaster aggregates
- With only 133 overlapping records scored, small sample size effects should be considered
- Current performance falls between median human forecasters and elite forecasting aggregates

## Next Steps

1. **Data integrity**: Collect new data from sources like Web of Science and Scopus
2. **Retrieval enhancement**: Add contextual retrieval and structured reasoning steps
3. **Ensemble methods**: Average forecasts with baseline models or human seed data
4. **Fine-tuning**: Apply fine-tuning of gpt4.1 to improve probability calibration

## Setup and Usage

### Prerequisites

```bash
pip install requests pyyaml textwrap3 openai matplotlib
```

### Environment Variables

Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

### Data Collection

The public api from `3ieimpact.org` was queried. To do so, ~2,400 records were collected and put into the `data/all_record_urls.txt` file. 
```
# all_record_urls.txt
https://developmentevidence.3ieimpact.org/record/123
https://developmentevidence.3ieimpact.org/record/456
...
```

### Running the Pipeline

Execute the scripts in sequence:

```bash
python src/1_make_database.py
python src/2_classify_abstract_outcomes_and_interventions.py
python src/3_grade_outcomes.py
python src/4_predict_the_grade_based_on_intervention.py
python src/5_report_stats_on_forecasts.py
```

## Additional Scripts

The `scripts/` directory contains utility scripts for analyzing the dataset:
- `count_abstracts_with_interventions_past_2021.py`: Identifies recent interventions
- `print_counts_of_all_outcomes.py`: Summarizes outcome metrics frequency
- `print_intervention_in_abstracts.py`: Extracts intervention descriptions
- `print_outcome_results_in_abstracts.py`: Extracts outcome information

## Data Files

- `data/impact_records.yaml`: Raw 3ie records
- `data/abstract_extractions.yaml`: Processed intervention and outcome descriptions
- `data/abstract_outcome_grades.yaml`: Graded outcomes
- `data/abstract_outcome_forecasts.yaml`: Model forecasts
- `data/all_record_urls.txt`: Source record URLs
