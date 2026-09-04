import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")

# GPT-5.6 Terra standard short-context rates (USD per 1M tokens)
PRICE_INPUT_PER_M = 2.00
PRICE_CACHED_INPUT_PER_M = 0.20
PRICE_OUTPUT_PER_M = 12.00

app = FastAPI(title="OpenAI Research API")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to research and answer")


class AskResponse(BaseModel):
    answer: str
    tokens_used: int
    cost_usd: float
    model: str
    sources: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message to send to the model")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model name")


class ChatResponse(BaseModel):
    reply: str
    model: str


@lru_cache
def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def extract_sources(response) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()

    for item in response.output:
        if item.type != "web_search_call":
            continue
        action = item.action
        if action is None or action.type != "search" or action.sources is None:
            continue
        for source in action.sources:
            if source.url not in seen:
                seen.add(source.url)
                sources.append(source.url)

    return sources


def usage_metrics(response) -> tuple[int, float]:
    usage = response.usage
    if usage is None:
        return 0, 0.0

    cached = usage.input_tokens_details.cached_tokens if usage.input_tokens_details else 0
    uncached_input = max(usage.input_tokens - cached, 0)
    cost = (
        (uncached_input / 1_000_000) * PRICE_INPUT_PER_M
        + (cached / 1_000_000) * PRICE_CACHED_INPUT_PER_M
        + (usage.output_tokens / 1_000_000) * PRICE_OUTPUT_PER_M
    )
    return usage.total_tokens, round(cost, 6)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        client = get_openai_client()
        response = client.responses.create(
            model=DEFAULT_MODEL,
            tools=[{"type": "web_search"}],
            input=request.question,
            instructions=(
                "You are a research assistant. Use web search to find current, reliable "
                "information, then give a clear and accurate answer. Cite sources when helpful."
            ),
            include=["web_search_call.action.sources"],
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    answer = response.output_text
    if not answer:
        raise HTTPException(status_code=502, detail="OpenAI returned an empty response")

    tokens_used, cost_usd = usage_metrics(response)
    return AskResponse(
        answer=answer,
        tokens_used=tokens_used,
        cost_usd=cost_usd,
        model=DEFAULT_MODEL,
        sources=extract_sources(response),
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    reply = completion.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="OpenAI returned an empty response")

    return ChatResponse(reply=reply, model=request.model)
