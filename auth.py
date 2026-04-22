from __future__ import annotations

import streamlit as st


def login_widget() -> bool:
    st.sidebar.subheader("Authentication")
    if st.session_state.get("is_authenticated"):
        st.sidebar.success(f"Logged in as {st.session_state.get('user_email')}")
        if st.sidebar.button("Log out"):
            st.session_state.is_authenticated = False
            st.session_state.user_email = ""
            st.rerun()
        return True

    email = st.sidebar.text_input("Email", key="login_email")
    if st.sidebar.button("Login"):
        if email and "@" in email:
            st.session_state.is_authenticated = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.sidebar.error("Please enter a valid email.")
    return False
