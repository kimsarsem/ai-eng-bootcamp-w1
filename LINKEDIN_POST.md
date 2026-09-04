# LinkedIn post (screenshots only — no curl)

Paste this into LinkedIn and attach **only** screenshots (Streamlit UI answer + metrics, and the guardrail catch). Do not attach terminal/curl images.

---

Shipped my Week 1 AI Eng project: a research Q&A app with a real API + Streamlit UI.

What it does:
• Ask a question in the UI
• Backend researches with OpenAI web search (GPT-5.6 Terra)
• Returns answer + tokens_used + estimated cost_usd
• Output guardrail blocks bad answers — demoed with force_bad

Why Terra: frontier-quality research without Sol pricing. Typical short research call lands around a cent; simple answers are fractions of a cent.

Live UI + API on Render (links in comments / first comment).

#AIEngineering #FastAPI #Streamlit #OpenAI #BuildInPublic

---

Suggested screenshot set (attach in this order):
1. Streamlit UI with a real answer + Tokens used + Cost (USD) + Model
2. Streamlit UI with “Force bad output” on — red guardrail error + blocked answer
3. (Optional) Render dashboard or live URL in the browser chrome
