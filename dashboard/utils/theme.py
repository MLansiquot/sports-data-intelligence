import streamlit as st


def apply_theme():
    """Inject some light styling helpers used across pages."""
    st.markdown(
        """
        <style>
        .metric-card {
            background-color: #f5f5f5;
            padding: 0.7rem 1rem;
            border-radius: 0.8rem;
            border: 1px solid #e0e0e0;
        }
        .metric-big-number {
            font-size: 1.6rem;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
