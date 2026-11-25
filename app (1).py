"""Streamlit UI. Run: streamlit run app.py"""
import streamlit as st

import llm
import rag

st.set_page_config(page_title="AI Coding Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Coding Assistant")

LANGS = ["Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust", "C#", "SQL"]
with st.sidebar:
    language = st.selectbox("Language", LANGS)
    st.caption("Upload a file or paste code in any tab.")
    upload = st.file_uploader("Upload a code file")


def code_input(key: str) -> str:
    default = upload.getvalue().decode("utf-8", "ignore") if upload else ""
    return st.text_area("Code", value=default, height=300, key=key)


tabs = st.tabs(["Generate", "Explain", "Find bugs", "Improve", "Tests", "Chat with repo"])

with tabs[0]:
    req = st.text_area("What should the code do?",
                       placeholder="Create a Python program for factorial")
    if st.button("Generate", key="b0") and req:
        with st.spinner("Thinking..."):
            st.markdown(llm.generate_code(req, language))

for i, (name, fn) in enumerate([("Explain", llm.explain_code),
                                ("Analyze", llm.find_bugs),
                                ("Improve", llm.improve_code)], start=1):
    with tabs[i]:
        code = code_input(f"c{i}")
        if st.button(name, key=f"b{i}") and code.strip():
            with st.spinner("Thinking..."):
                st.markdown(fn(code, language))

with tabs[4]:
    code = code_input("c4")
    fw = st.text_input("Test framework", "pytest")
    if st.button("Generate tests", key="b4") and code.strip():
        with st.spinner("Thinking..."):
            st.markdown(llm.generate_tests(code, language, fw))

with tabs[5]:
    url = st.text_input("GitHub repo URL", placeholder="https://github.com/user/repo")
    if st.button("Index repository") and url:
        with st.spinner("Cloning and embedding..."):
            try:
                n = rag.index_repo(url)
                st.session_state["repo"] = url
                st.success(f"Indexed {n} code chunks.")
            except Exception as e:
                st.error(f"Failed: {e}")
    if "repo" in st.session_state:
        q = st.text_input("Ask about the repo",
                          placeholder="Where is the login functionality?")
        if st.button("Ask") and q:
            with st.spinner("Searching code..."):
                chunks = rag.retrieve(st.session_state["repo"], q)
                st.markdown(llm.answer_repo_question(q, chunks))
                with st.expander("Sources"):
                    for c in chunks:
                        st.code(f"{c['path']}:{c['start']}-{c['end']}")
