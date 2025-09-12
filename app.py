import streamlit as st
import os
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.pages.main_page import MainPage
from src.utils.styling import apply_custom_styling


def main():
    st.set_page_config(
        page_title="DataSierra - AI Data Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_styling()
    
    main_page = MainPage()
    main_page.render()


if __name__ == "__main__":
    main()