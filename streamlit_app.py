import os

import requests
import streamlit as st

DEFAULT_API_URL = os.getenv(
    "ASK_API_URL",
    "https://ai-eng-bootcamp-w1.onrender.com",
).rstrip("/")

st.set_page_config(page_title="Research Ask", page_icon="🔎", layout="centered")
st.title("Research Ask")
st.caption("Streamlit UI for the Week 1 `/ask` research endpoint")

api_url = st.sidebar.text_input("API base URL", value=DEFAULT_API_URL)

# Optional: /?q=...&auto=1 pre-fills and runs a request (useful for demos/screenshots)
default_question = st.query_params.get("q", "")
auto_ask = st.query_params.get("auto", "0") == "1"

with st.form("ask_form", clear_on_submit=False):
    question = st.text_area(
        "Question",
        value=default_question,
        placeholder="Ask something to research…",
        height=120,
    )
    submitted = st.form_submit_button("Ask", type="primary", use_container_width=True)

should_ask = (submitted or auto_ask) and bool(question.strip())

if submitted and not question.strip():
    st.warning("Enter a question first.")

if should_ask:
    with st.spinner("Researching…"):
        try:
            response = requests.post(
                f"{api_url}/ask",
                json={"question": question.strip()},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            st.error(f"Request failed: {exc}")
        else:
            st.subheader("Answer")
            st.write(data.get("answer", ""))

            col1, col2, col3 = st.columns(3)
            col1.metric("Tokens used", data.get("tokens_used", "—"))
            col2.metric("Cost (USD)", f"{float(data.get('cost_usd', 0)):.6f}")
            col3.metric("Model", data.get("model", "—"))

            sources = data.get("sources") or []
            if sources:
                st.subheader("Sources")
                for url in sources:
                    st.markdown(f"- [{url}]({url})")

            with st.expander("Raw JSON"):
                st.json(data)
