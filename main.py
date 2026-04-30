import os
import subprocess
import sys
from pathlib import Path

def run_step(name, command, cwd=None):
    print(f"\n>>> STARTING STEP: {name}")
    print(f"Running: {command}")
    env = os.environ.copy()
    # Consolidate all phase source directories into PYTHONPATH
    env["PYTHONPATH"] = ";".join([
        str(Path("phase2_preprocessing/src").absolute()),
        str(Path("phase3_classification/src").absolute()),
        str(Path("phase4_analytics/src").absolute()),
        str(Path("phase5_ui_report/src").absolute()),
        str(Path("phase6_chatbot/src").absolute()),
        env.get("PYTHONPATH", "")
    ])
    
    result = subprocess.run(command, shell=True, env=env, cwd=cwd)
    if result.returncode != 0:
        print(f"!!! STEP FAILED: {name}")
        sys.exit(1)
    print(f">>> COMPLETED STEP: {name}")

def main():
    print("====================================================")
    print("   CLAUDE REVIEW INTELLIGENCE: MASTER PIPELINE")
    print("====================================================")

    # Phase 1: Ingestion
    run_step("Phase 1: Reddit Ingestion", "python phase2_preprocessing/fetch_reddit.py")

    # Phase 2: Preprocessing
    run_step("Phase 2: Data Preprocessing", 
             "python phase2_preprocessing/run_phase2.py --input reddit_reviews.json --output reddit_preprocessed.json")

    # Phase 3: Classification & Issue Mining
    run_step("Phase 3: Theme Classification", 
             "python phase3_classification/run_phase3.py --input reddit_preprocessed.json --output reddit_classified.json --report phase3_top_issues.json")

    # Phase 4: Analytics & Trends
    run_step("Phase 4: Detailed Analytics", 
             "python phase4_analytics/run_phase4.py --reviews reddit_classified.json --issues phase3_top_issues.json --output phase4_analytics.json")

    # Summary Generation
    run_step("Generating Text Summary", "python phase4_analytics/generate_summary.py")

    print("\n" + "="*50)
    print("PIPELINE COMPLETE! You can now start the UI.")
    print("To launch the dashboard, run:")
    print("streamlit run phase5_ui_report/app.py")
    print("="*50)

if __name__ == "__main__":
    main()
