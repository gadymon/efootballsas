# src/orchestrator.py
import subprocess
import sys
import os

def run_pipeline_step(module_name):
    """Executes a python module as a separate process."""
    cmd = [sys.executable, "-m", module_name]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Error in {module_name}:\n{stderr}")
    return stdout

def execute_full_pipeline():
    """Runs the entire eFootball ML pipeline sequentially."""
    steps = [
        {"name": "Scraping YouTube Data", "module": "src.scraper"},
        {"name": "Building Dynamic Player Directory", "module": "src.build_dynamic_dictionary"},
        {"name": "Syncing Database Baselines", "module": "src.database_sync"},
        {"name": "Preprocessing Comment Data", "module": "src.preprocessor"},
        {"name": "Running Transformer Sentiment Engine", "module": "src.sentiment_engine"}
    ]
    
    for step in steps:
        yield f"🔄 Starting: {step['name']}..."
        try:
            run_pipeline_step(step['module'])
            yield f"✅ Completed: {step['name']}"
        except Exception as e:
            yield f"❌ Failed at {step['name']}!\n{str(e)}"
            return
            
    yield "🎉 Pipeline Execution Successful! All stats calculated."