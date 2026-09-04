# AI Eng Bootcamp — Week 1

Research Q&A API + Streamlit UI. Ask a question, the backend researches with OpenAI web search, returns an answer with token usage and estimated cost, and runs an **output guardrail** before the client sees the text.

## Live links

| Layer | URL |
| --- | --- |
| **API** | https://ai-eng-bootcamp-w1.onrender.com |
| **API docs** | https://ai-eng-bootcamp-w1.onrender.com/docs |
| **Streamlit UI** | https://ai-eng-bootcamp-w1-ui.onrender.com |

- API = FastAPI backend (`POST /ask`)
- UI = browser front end that calls the API

> Free Render services sleep when idle — the first request after idle can take ~30–60s.

## Why GPT-5.6 Terra

| Option | Tradeoff |
| --- | --- |
| **gpt-5.6-sol** | Strongest quality, highest $/token |
| **gpt-5.6-terra** (chosen) | Frontier behavior + web research quality at a mid price |
| **gpt-5.6-luna** | Cheapest, weaker for multi-step research |

Terra fits this app: short research answers with web search, without Sol pricing. Pricing used for `cost_usd` (short context):

- Input: **$2.00 / 1M** tokens  
- Cached input: **$0.20 / 1M**  
- Output: **$12.00 / 1M**

### Typical per-call cost

From live runs against `/ask`:

| Workload | Tokens (approx.) | Cost (approx.) |
| --- | --- | --- |
| Short factual (no search) | ~4.5k | **~$0.001–0.002** |
| Short research + sources | ~8–9k | **~$0.01** |

`force_bad` demos are **$0.00** (no model call).

## Output guardrail + `force_bad`

Before returning model text, `/ask` runs `run_output_guardrail()` and blocks:

- empty / too-short answers  
- the demo `FORCE_BAD_OUTPUT` marker  
- fabricated `totally-fake-news.example` sources  
- the known false claim used in the demo payload  

Set `"force_bad": true` to inject bad output on purpose. The API **does not** return the bad text — it returns a blocked message with:

```json
{
  "guardrail_passed": false,
  "guardrail_reason": "force_bad_marker",
  "tokens_used": 0,
  "cost_usd": 0.0
}
```

In the Streamlit sidebar, enable **Force bad output (demo guardrail)**.

## Quick start (local)

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY
uvicorn main:app --reload --host 127.0.0.1 --port 8000
streamlit run streamlit_app.py
```

`.env` is gitignored — never commit API keys.

## API shape

`POST /ask`

```json
{ "question": "What is FastAPI?", "force_bad": false }
```

Response fields: `answer`, `tokens_used`, `cost_usd`, `model`, `sources`, `guardrail_passed`, `guardrail_reason`.

## Repo layout

- `main.py` — FastAPI `/ask`, usage/cost, guardrail  
- `streamlit_app.py` — UI client  
- `render.yaml` — API Blueprint  
- `.env.example` — env template  
