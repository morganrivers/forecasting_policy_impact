#!/usr/bin/env python3
import pprint
# scrape_to_yaml.py
#
# Prerequisites
#   pip install requests pyyaml textwrap3

import requests
import yaml
import textwrap
from pathlib import Path
from time import sleep
FILE_WITH_URLS = "all_record_urls.txt"
OUTPUT_YAML    = "impact_records.yaml"
GRAPHQL_URL    = "https://api.developmentevidence.3ieimpact.org/graphql"

QUERY = textwrap.dedent("""
    query recordDetail($id: Int!) {
      recordDetail(id: $id) {
      product_type
      title
      synopsis
      id
      short_title
      language
      sector_name
      sub_sector
      journal
      journal_volume
      journal_issue
      year_of_publication
      publication_type
      publication_url
      egm_url
      report_url
      grantholding_institution
      evidence_programme
      context
      research_questions
      main_finding
      review_type
      quantitative_method
      qualitative_method
      overall_of_studies
      overall_of_high_quality_studies
      overall_of_medium_quality_studies
      headline_findings
      additional_method
      additional_method_2
      pages
      evaluation_design
      impact_evaluations
      systematic_reviews
      authors {
        author
        institutions {
          author_affiliation
          department
          author_country
        }
      }
      continent {
        continent
        countries {
          country
          income_level
          fcv_status
        }
      }
      project_name {
        project_name
        implementation_agencies {
          implementation_agency
          implement_agency
        }
        funding_agencies {
          program_funding_agency
          agency_name
        }
        research_funding_agencies {
          research_funding_agency
          agency_name
        }
      }
      publisher_location
      status
      threeie_funded
      is_bookmark
      based_on_the_above_assessments_of_the_methods_how_would_you_rate_the_reliability_of_the_review
      provide_an_overall_of_the_assessment_use_consistent_style_and_wording
      abstract
      open_access
      doi
      equity_focus
      equity_dimension
      equity_description
      keywords
      evaluation_method
      mixed_methods
      unit_of_observation
      methodology
      methodology_summary
      main_findings
      evidence_findings
      policy_findings
      research_findings
      background
      objectives
      region
      stateprovince_name
      district_name
      citytown_name
      location_name
      other_resources
      research_funding_agency {          # ⬅︎ NOW HAS CHILDREN
        research_funding_agency
        agency_name
      }
      relatedArticles {
        product_id
        title
        product_type
      }
      dataset_url
      dataset_available
      instances_of_evidence_use
      study_status
      primary_dac_code
      secondary_dac_code
      crs_voluntary_dac_code
      un_sustainable_development_goal
      primary_dataset_url
      pre_registration_url
      primary_dataset_availability
      primary_dataset_format
      secondary_dataset_name
      secondary_dataset_disclosure
      additional_dataset_info
      analysis_code_availability
      analysis_code_format
      study_materials_availability
      study_materials_list
      pre_registration
      protocol_pre_analysis_plan
      ethics_approval
      interventions
      outcome
      }
    }
""").strip()

def extract_id(path: str) -> int:
    """Return the integer after the last slash of the path line."""
    return int(path.rstrip().split("/")[-1])
    
def fetch_record(rid: int) -> dict | None:
    payload = {
        "operationName": "recordDetail",
        "variables": {"id": rid},
        "query": QUERY,
    }
    r = requests.post(GRAPHQL_URL, json=payload, timeout=30)
    r.raise_for_status()

    data = r.json()
    if "errors" in data:                # GraphQL rejected the query
        print(f"✗ {rid}  GraphQL error → {data['errors'][0]['message']}")
        return None
    return data["data"]["recordDetail"]

def main() -> None:
    records = []

    # 1  read each line from the text file
    for line in Path(FILE_WITH_URLS).read_text(encoding="utf-8").splitlines():
        sleep(.5)
        if not line.strip():
            continue                      # skip blank lines
        rid = extract_id(line)
        try:
            record = fetch_record(rid)
            records.append(record)
            print(f"✓ {rid}  {record['title'][:80]}")
            with open(OUTPUT_YAML, "a", encoding="utf-8") as f:
                yaml.dump([record], f, allow_unicode=True, sort_keys=False)

            print(f"✓ {rid}  {record['title'][:80]}")
        except Exception as exc:
            print(f"✗ {rid}  ({exc})")

        # 2  write everything to YAML
        Path(OUTPUT_YAML).write_text(
            yaml.dump(records, allow_unicode=True, sort_keys=False),
            encoding="utf-8"
        )
        print(f"\nSaved {len(records)} records → {OUTPUT_YAML}")

if __name__ == "__main__":
    main()
