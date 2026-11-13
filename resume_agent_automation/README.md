# Resume Agent Automation Framework

## Objective
This project implements a modular automation framework for the Resume Updating Agent workflow described in the assignment. It follows the required architecture: Excel manual test cases -> validation and preparation -> Ollama-based data generation -> Playwright UI automation -> transcript capture -> DeepEval evaluation -> HTML/CSV reporting.

The framework is intentionally organized so that the user can substitute the correct Resume Studio selectors and agent flow once the actual live application is available, while keeping the evaluation and reporting pipeline intact.

## Included manual test scenario mapping
The supplied workbook in `test_data/manual_test_cases.xlsx` contains the manual test set. The automation mapping uses the following five high-priority scenarios, all directly traced to the workbook IDs:

- `TC_RES_001` - successful Resume Agent launch
- `TC_RES_002` - Start New Conversation
- `TC_RES_004` - Update Resume action card
- `TC_RES_006` - response to proceed confirmation
- `TC_RES_014` - multi-turn conversation continuity

These are the primary automated scenarios referenced by the suite under `tests/test_resume_agent.py`.

## Project structure
```text
resume_agent_automation/
├── approved_test_inputs/
├── config/
│   ├── __init__.py
│   └── settings.py
├── evaluations/
│   ├── evaluation_runner.py
│   └── metrics.py
├── integrations/
│   ├── __init__.py
│   ├── deepeval_judge.py
│   └── ollama_client.py
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   └── resume_agent_page.py
├── prompts/
│   └── prompt_templates.py
├── reports/
├── screenshots/
├── test_data/
│   └── manual_test_cases.xlsx
├── tests/
│   ├── conftest.py
│   ├── test_deepeval.py
│   └── test_resume_agent.py
├── transcripts/
├── utils/
│   ├── excel_reader.py
│   ├── logger.py
│   ├── test_data_manager.py
│   └── transcript_manager.py
├── .env.example
├── .gitignore
├── main.py
├── pytest.ini
├── README.md
├── requirements.txt
└── .env
```

## Prerequisites
- Python 3.10+
- Playwright-supported browser runtime
- Ollama installed locally and reachable at `http://localhost:11434`
- DeepEval installed in the project environment
- Access to the target application and credentials, managed via `.env`

## Environment configuration
Copy `.env.example` to `.env` and provide the actual values that belong to your environment:

```bash
copy .env.example .env
```

Example values:
```env
APP_URL=https://dna-preprod.hashedin.com/home/me/
APP_USERNAME=your_username
APP_PASSWORD=your_password
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_GENERATION_MODEL=gemma2:2b
OLLAMA_JUDGE_MODEL=gemma2:2b
OLLAMA_TIMEOUT=120
OLLAMA_TEMPERATURE=0
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
DEEP_EVAL_THRESHOLD=0.70
HALLUCINATION_RISK_THRESHOLD=0.30
```

Do not commit `.env` to source control; it is excluded by `.gitignore`.

## Dependency installation
```bash
cd resume_agent_automation
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
```

## Ollama setup
Install Ollama from the official download page and start it.

```bash
ollama serve
ollama pull gemma2:2b
ollama list
```

Verify the service is reachable:
```bash
python -c "import requests; print(requests.get('http://localhost:11434/api/tags', timeout=10).status_code)"
```

## Running the suite
Run only the traceability checks:
```bash
python -m pytest tests/test_resume_agent.py -q
```

Run the live UI automation (requires `RUN_LIVE_UI_TESTS=true` and valid `.env` values):
```bash
set RUN_LIVE_UI_TESTS=true
python -m pytest tests/test_resume_agent.py -q
```

Run the DeepEval checks (requires `USE_DEEPEVAL=true` and a working Ollama judge model):
```bash
set USE_DEEPEVAL=true
python -m pytest tests/test_deepeval.py -q
```

Run the whole suite:
```bash
python -m pytest -q
```

## Execution and evaluation flow
The project implements the required flow:

1. Read Excel manual cases from `test_data/manual_test_cases.xlsx`
2. Validate the case IDs and automation candidate list
3. Prepare the scenario data and approved input pool
4. Use Ollama for generation and data prep when live generation is enabled
5. Execute Playwright automation against the live Resume Studio flow if configured
6. Save each scenario transcript as a JSON file in `transcripts/`
7. Run DeepEval metrics via `integrations/deepeval_judge.py`
8. Produce HTML/CSV reporting under `reports/`
9. Save screenshots under `screenshots/passed` and `screenshots/failed`

## Transcript and report outputs
- JSON transcripts: `resume_agent_automation/transcripts/`
- HTML report: `resume_agent_automation/reports/evaluation_report.html`
- CSV summary: `resume_agent_automation/reports/evaluation_summary.csv`
- Screenshots: `resume_agent_automation/screenshots/passed/` and `/failed`

## DeepEval scoring notes
The project follows the assignment requirement for the Hallucination metric:

- `HallucinationMetric` reports a consistency-oriented score.
- The assignment requires applying the maximum hallucination risk threshold of `0.30`.
- Therefore, the framework calculates:

```python
hallucination_risk = 1 - consistency_score
```

and passes the metric when `hallucination_risk <= 0.30`.

The Answer Relevancy and Faithfulness thresholds are both set to `0.70` in the configuration and in the evaluation runner.

## Verification status and blockers
This project was implemented and validated structurally using the supplied workbook and codebase. The live Resume Studio / Resume Updating Agent UI and the local Ollama service were not available in the current environment during validation, so the full end-to-end UI execution and DeepEval run remain conditional on the following:

- the application exposes the Resume Studio / Resume Agent flow in the target environment
- the `RUN_LIVE_UI_TESTS=true` flag is enabled
- the `.env` file contains valid credentials
- Ollama is running locally and the configured model is installed
- `USE_DEEPEVAL=true` is enabled when evaluation is executed

The framework is ready to run once those conditions are satisfied. It does not assume the app is available or silently skip the required checks without an explicit configuration flag.

## Troubleshooting
- `Connection refused` to `http://localhost:11434`: start Ollama with `ollama serve` and pull the model.
- `APP_USERNAME` and `APP_PASSWORD` missing: populate `.env` before live tests.
- Playwright browser missing: run `python -m playwright install`.
- Test workbook not found: verify `test_data/manual_test_cases.xlsx` exists.
- Resume Studio element not found: confirm the exact active selector in the live app and update `pages/resume_agent_page.py`.

## Final note
The framework is built to the assignment specification and retains explicit traceability from the workbook Test IDs to the automated cases. The project intentionally avoids hardcoded credentials, external paid APIs, and silent success masking.
