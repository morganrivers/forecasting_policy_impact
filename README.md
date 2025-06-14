# Forecasting Policy Impact

A preliminary demo framework for evaluating the effectiveness of language models in predicting the outcomes of policy interventions for environmental outcomes.

## DISCLAIMER

**This project is currently in an experimental phase. The training data used by the language models may already include the results of the policy interventions being forecasted, which could artificially inflate performance metrics.**

**Next steps:**
- Collect new data from Web of Science and Scopus
	- **NOTE**: Preliminary investigation from Scopus freely available abstracts (not in this repo) has revealed approximately 20,000 records with impact evaluations published in the years 2022, 2023, 2024, and 2025. Based on the results of `scripts/count_abstracts_with_interventions_past_2021.py`, approximately 3% of impact evaluations pertain to impact evaluations in the 3 years prior to publication (based on years mentioned in the abstracts and manual inspection). Because each abstract has a mean of 1.7 outcomes with information per record, this means there are approximately 600 records which would describe interventions and 1000 gradeable outcomes present in scopus. Because gpt4 has a training cutoff in 2021, these interventions could be used to produced contamination-free forecasts to provide a statistically robust test of LLM ability to forecast policy impact based on an intervention, including a sizeable validation set.
- Perform manual categorization with the 3ie database as a baseline
- Ensure forecasts are not leveraging results that may be present in LLM training data

## Why do this in the first place?

As a clear disclaimer: **LLM's are not in general superior to humans at forecasting as of May 2025.** At the same time, their forecasting ability for short-term predictions is closing in at a rapid pace as AI capabilities have advanced [source]. Furthermore, predictions with a significant number of relevant news articles or very near to the date of a forecasting resolution can best teams of trained forecaster's aggregate predictions in prediction accuracy (Halawi et. al., 2024). It is currently unknown to what extent the ability of AI systems to forecast geopolitical and economic events can be extended to forecasting the impact of interventions with implications in the earth system sciences. Exploring this domain opens a promising avenue to improve the efficacy of interventions in the earth system sciences. In the remaining section, we discuss the beneficial aspects of the system developed, as well as the potential dangers or risks this system may pose.

One co-benefit of a system fine-tuned on earth system sciences is that by its cross-domain nature, the LLM will be able to identify a wide range of likely impacts, and the degree of effect of those impacts, on a wide range of quantitative and qualitative outcomes. When implementing interventions, researchers, policy-makers, and decision makers must always consider many relevant outcomes of their interventions. The similarity and vector search of the system allow users to quickly identify relevant documentation as well as outcomes of similar scientific research most relevant to their proposed intervention.

Another benefit of the system is that AI's typically excel in domains where human experts are particularly challenged: when there is a very large range of relevant data or when predictions about the effect of an intervention involve carefully calibrated probabilities. AI's can also perform predictions in a way that human experts can learn from: introducing one piece of information can be used to quantify the effect on AI forecasts. AI forecasts can be ensembled arbitrary and at relatively little expense compared to humans. 

However, there are clear risks of using AI for evaluating the likely outcomes of interventions in the earth system sciences. The most obvious issue may be that while AI can be accurate in some domains, current AI systems do not accurately present their confidence in their answers and can completely hallucinate events and facts which have no grounding in reality. The result is a misleading analysis, which in the space of earth system sciences may lead to significant risks. Policy makers may trust AI more than is justified by its performance, or view it as an unbiased source, despite nearly all current AI systems having a well-documented political bias acknowledged by both the political left and political right [source]. 

Another risk is that scientists may not perform research deemed to be unlikely to succeed, and thus the range of explored outcomes may be narrowed to the outcomes known to work in the past or deemed to be likely to be successful by the AI system. 

While AI may be able to calibrate itself on many different domains and automatically pull in relevant information, it currently lacks the ability to reliably perform complex mathematical calculations or run long-term analysis. Furthermore, as AI becomes more advanced there is significant concern in the technology community that it may form its own goals and intrinsic values, out of alignment with its human operators. An AI that advises on AI policy may in fact present a conflict of interest, even if the AI is simply using heuristics mimicking human tendencies towards self-preservation and in-group preferences. 


We address these concerns by noting that as AI begins to become more accurate and lower cost than human researchers at forecasting the impact of policy outcomes, it becomes ever more important to have specifically designed systems that take steps to reduce the dangers of AI systems. We believe the system developed clearly fulfills this criterion. The system we use in this work specifically provides credible, peer-reviewed scientific information and news from reputable sources to the AI, rather than relying on general internet search as many current AI providers rely on.   [OPTIONAL: Furthermore design our system to be calibrated via fine-tuning, meaning that some of the reliability concerns may be ameliorated. ] As AI systems advance, there appears to be a progression towards more agentic systems with more clear intermediate goals. A misalignment with human preferences (an example in this work might be downplaying the CO2 effects of building more AI systems in order to increase the number of AI systems as an in-group preference) may occur and be missed by humans with extremely long thought chains and insufficient detection of misalignment. Our system by contrast allows the user to inspect the series of logical deductions performed by the model and view available sources the model used as scientific reference material. The system has been specifically quantified in terms of its bias, allowing users to have full knowledge of the likely failure modes when using the system, often absent in generally available AI chat interfaces. [ OPTIONAL: with an explicit attempt to correct these biases via fine-tuning, syncophantic behavior is also reduced compared to RLHF models.].

Another risk is that papers tend to have a bias, and the model will learn to replicate that bias. Papers are much more likely to have "significant" results than mixed effect or no effect. The optimistic bias towards positive bias published in journals should mean we interpret the prediction of the model cautiously, with knowledge that it will likely present a more optimistic version of the outcomes than is justified from a neutral observer's perspective. In order to counteract this risk, we are also looking at the accuracy of the quantitative result of the intervention, which is more valid to compare between abstracts and has a relatively smaller publisher bias [source]. 

Finally, much of the promise of the AI forecasting approach relies on models continuing to become lower cost and more performant in general domains. While multiple empirical trends and the longstanding success of Moore's law clearly indicate this should continue, it is by no means guaranteed. If AI models cease to improve on relevant metrics, or otherwise become increasingly biased or unreliable, much of the promist of an AI forecasting tool for estimating interventions in the earth system sciences goes away. Despite this risk, the system remains useful and informative for the scientific and public policy community as it provides a system with sources proven to provide useful information for the evaluation of policy outcomes, and introduces a framework by which the impact of interventions can be broken down for more accurate predictions. While there is a possibility that AI's may never reach the capabilities of humans in integrating the disparate sources of information, automated information search and a new tool that can synthesize relevant information can be a powerful tool for scientists and policy makers.

Forecasting has the distinct benefit of disallowing training on any particular benchmarks and is a rather difficult-to-game metric compared to standard LLM performance benchmarks. It becomes increasingly useful to society to understand what the true capabilities of LLM's are and the rate of their improvement, both for the regulation of dangerous AI capabilities and the improved understanding where AI may be capable enough for reliable use in various critical domains such as automated medicine and driverless vehicles.

The codebase and research done here can with relatively little modification be repurposed from specifically earth system science, to other domains where impact forecasts are clearly useful. A similar system with an expanded set of abstracts and data could be used with relatively little modification in domains such as public health, financial policy, and in a more general way to provide predictions for scientists about likely qualitative and quantitative outcomes of their scientific studies. The success of the model demonstrates that a great deal of opportunity to synthesize scientific findings and improve decision making on an institutional level is policy.

Onle particularly promising avenue for expansion of the system would be as an application to Futarchy first proposed by Robin Hanson. Futarchy proposes to use prediction markets to allow policy makers or the general public to only have to agree on what they value and quantify as utility, not on how to maximize that utility. Several prediction markets in parallel are formed, creating a zero-sum game financially rewarding players that best predict the utility outcome conditional on a policy being implemented. To the extent that complex public policy can ever be reduced to a single utility function, that this function can be agreed on by a quorum of policy makers, Futarchy could significantly reduce gridlock and polarization in politics, at least in the domains in which the necessary conditions are useful and possible. In essence, Futarchy aids policy makers in coming to agreement on how to implement policies by reducing the scope of disagreement to what the set of possible policy implementations could be and how they would choose to quantify a successful outcome.

If and when the system proposed is shown to exceed human ability in predicting policy, or if it can be shown that the system can be complementary to human predictions, cheaply improving their accuracy, this system could be integrated to a scheme for futarchy by replacing or augmenting prediction markets. This may be especially helpful in use-cases where AI succeeds and prediction markets fail: very low probabilities over long time periods (as the winners may choose to invest their money on a higher-return investments), predictions about long-run outcomes that are difficult to gain information about, particularly contentious outcomes, or issues where markets may be biased by particularly wealthy individuals who come in very late in the market and buy many more shares than expected.

## Ideation: Extensions and other applications
	- improving prospects of futarchy to improve governance
	- understanding how different sources of information contribute to effective forecasting of impact
	- before the forecasting at all: collecting the information for forecasting all in one place, both resources to make reasonable forecasts, as well as creating structure out of unstructured papers in earth systems science
	- creating general hierarchies of impact for different categories of interventions
	- ability to create "unbiased" forecasts that are both evidence based and listened to by both sides of the political spectrum
	- increasing democratic understanding of the likely effects of laws from third party sources -- allows non-experts to assess the efficacy of elected officials in accomplishing their goals
	- automated scoring of introduced legislation 
	- sufficient statistics to introduce confidence bars on the effects of political outcomes
	- leveraging the advance of AI for good
	- constraining the use of AI in a scientifically valid, constrained manner, which minimizes the risk that AI biases themselves influence policy decisions.  
	- automated feedback on proposed interventions (registered studies): what are the likely things this has impact on? What are some relevant papers for their proposal?


## Overview


This project aims to evaluate how well language models can forecast the outcomes of policy interventions, particularly in developing countries. The pipeline:

1. Collects policy intervention records from the 3ie Development Evidence Portal
2. Extracts intervention descriptions and outcomes from paper abstracts
3. Grades actual outcomes based on a 5-point scale
4. Uses language models to forecast expected outcomes using only intervention descriptions
5. Evaluates forecast accuracy against actual outcomes

Due to the general (rather than specific) nature of LLM intelligence, and the ability of LLMs to transfer increased competence in one domain to increased competence in other loosely related domains [source], we choose to train LLMs on a wide range of evaluations of interventions in the earth system sciences. This provides a challenge due to the need for a wide range of background documents, while making accurate evaluation and acquiring higher quality data for training easier due to the breadth of available source material.

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
See (Halawi et. al., 2024) for the "reference point" numbers in the table below.

| Metric                                            | GPT4.1 single-shot | Always "Significant" baseline | Random baseline | Reference points                                                                                           |
| ------------------------------------------------- | ---------- | -------------------- | --------------- | ---------------------------------------------------------------------------------------------------------- |
| **RMSE** (0 ➜ "worsened", 1 ➜ "very significant") | **0.308**  | 0.306                | 0.498           | –                                                                                                          |
| **Accuracy** (exact 5-class match)                | 48 %   | **51 %**             | 20 %            | –                                                                                                          |
| **Macro-F1**                                      | 0.334      | –                    | –               | –                                                                                                          |
| **Brier (binary "positive" ≥ 0.75)**              | **0.203**  | 0.206                | 0.250           | • human crowd on real forecasting tournaments ≈ 0.149 <br>• GPT-4 zero-shot on the geopolitical forecasting benchmark ≈ 0.208  |


## Interpretation of Results

- The model shows ability to extract signal (Brier score of 0.203 vs. random baseline of 0.250)
- Performance is comparable to zero-shot GPT-4 but trails human forecaster aggregates on geopolitical forecasts, which is approximately 0.149 (Halawi et. al., 2024)
- With only 133 records scored, small sample size effects should be considered
- Current (0.203) performance falls between median human forecasters (0.203) and elite forecasting aggregates (0.149)
- **Assuming data contamination is not significantly improving forecasting accuracy**, we can expect an improvement of approximately  (0.208 - 0.179 = 0.029) from fine-tuning to a forecasting accuracy of approximately 0.174 using techniques from (Halawi et. al., 2024).


## Next Steps

1. **Data integrity**: Collect new data from sources like Web of Science and Scopus
2. **Retrieval enhancement**: Add contextual retrieval and structured reasoning steps
3. **Ensemble methods**: Average forecasts with baseline models or human seed data
4. **Fine-tuning**: Switch to gpt4, apply fine-tuning of gpt4 to improve probability calibration

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


# References
Halawi, D., Zhang, F., Yueh-Han, C., & Steinhardt, J. (2024). Approaching human-level forecasting with language models. arXiv preprint arXiv:2402.18563.