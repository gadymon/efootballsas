# src/text_orchestrator.py
import subprocess
import sys

def run_text_pipeline_step(module_name):
    """Executes a text module as a separate process from the project root."""
    cmd = [sys.executable, "-m", module_name]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Error in {module_name}:\n{stderr}")
    return stdout

def execute_text_only_pipeline():
    """Runs text processing modules sequentially without touching the YouTube API."""
    steps = [
        {"name": "Parsing & Cleaning Comment Data", "module": "src.preprocessor"},
        {"name": "Compiling Buzzword Frequency Tables", "module": "src.word_frequency_engine"},
        {"name": "Sorting Vocabulary into Gameplay Categories", "module": "src.word_categorization_engine"}
    ]
    
    for step in steps:
        yield f"🔄 Processing: {step['name']}..."
        try:
            run_text_pipeline_step(step['module'])
            yield f"✅ Completed: {step['name']}"
        except Exception as e:
            yield f"❌ Pipeline Broken at {step['name']}!\n{str(e)}"
            return
            
    yield "🎉 Text Analytics Re-Calculated Successfully!"