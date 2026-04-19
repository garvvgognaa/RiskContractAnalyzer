import os
import streamlit as st

if not os.path.exists("models/best_model.joblib"):
    st.warning("Warning: ML model not found. The app will use rule-based risk detection until models are pushed/trained.")

import time
import json
import streamlit as st

from app_config import (
    APP_TITLE,
    APP_SUBTITLE,
    COLOUR,
    SIDEBAR_HOW_TO,
    SIDEBAR_DISCLAIMER,
)
from utils.file_handler import extract_text_from_upload, get_file_metadata
from utils.clause_segmenter import segment_document
from utils.risk_predictor import analyze_clauses, compute_summary_stats
from utils.export_handler import generate_pdf_report
from components.result_display import (
    inject_card_styles,
    render_summary_metrics,
    render_clause_list,
)

                     
from src.agents.legal_agent import LegalAgent, AgentState

                                                                             
                                            
                                                                             
st.set_page_config(
    page_title="Legal Risk Analyzer",
    page_icon="[Risk]",
    layout="wide",
    initial_sidebar_state="expanded",
)


                                                                             
                              
                                                                             
if "agent_report" not in st.session_state:
    st.session_state.agent_report = None
if "last_analyzed_file" not in st.session_state:
    st.session_state.last_analyzed_file = None


                                                                             
                      
                                                                             
def _inject_global_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        /* Background */
        .stApp {{
            background: linear-gradient(135deg, #0E1117 0%, #141824 100%);
        }}

        /* Hero banner */
        .hero-banner {{
            background: linear-gradient(135deg, #1a1040 0%, #0f2040 50%, #0d1f3c 100%);
            border: 1px solid rgba(124,106,247,0.3);
            border-radius: 16px;
            padding: 38px 44px;
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }}
        .hero-banner::before {{
            content: '';
            position: absolute;
            top: -80px; right: -80px;
            width: 280px; height: 280px;
            background: radial-gradient(circle, rgba(124,106,247,0.18) 0%, transparent 70%);
            pointer-events: none;
        }}
        .hero-title {{
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(90deg, #B8B0FF 0%, #7C6AF7 50%, #4FC3F7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 8px 0;
            line-height: 1.15;
        }}
        .hero-subtitle {{
            color: {COLOUR['text_secondary']};
            font-size: 1.05rem;
            font-weight: 400;
            margin: 0;
        }}

        /* Upload zone */
        [data-testid="stFileUploader"] {{
            background: {COLOUR['bg_card']};
            border: 2px dashed rgba(124,106,247,0.45);
            border-radius: 14px;
            padding: 12px;
            transition: border-color 0.3s ease;
        }}
        [data-testid="stFileUploader"]:hover {{
            border-color: {COLOUR['accent']};
        }}

        /* Section heading */
        .section-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {COLOUR['text_primary']};
            border-bottom: 2px solid {COLOUR['accent']};
            padding-bottom: 8px;
            margin: 28px 0 20px 0;
            display: inline-block;
        }}

        /* File info chip */
        .file-chip {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: {COLOUR['bg_card']};
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
            color: {COLOUR['text_secondary']};
            margin-bottom: 20px;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {COLOUR['bg_card']};
            border-right: 1px solid rgba(255,255,255,0.06);
        }}

        /* Toggle label */
        .stCheckbox label {{
            color: {COLOUR['text_secondary']};
            font-size: 14px;
        }}

        /* Progress / spinner */
        .stProgress > div > div {{
            background: {COLOUR['accent']};
        }}

        /* Divider */
        hr {{
            border-color: rgba(255,255,255,0.06);
        }}

        /* Filter tab styling */
        .stTabs [data-baseweb="tab"] {{
            color: {COLOUR['text_secondary']};
            font-size: 14px;
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            color: {COLOUR['accent_light']} !important;
            border-bottom-color: {COLOUR['accent']} !important;
        }}
        
        /* Agent Report Styles */
        .agent-card {{
            background: {COLOUR['bg_card']};
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .agent-severity-high {{ border-left: 5px solid {COLOUR['border_risky']}; }}
        .agent-severity-medium {{ border-left: 5px solid #F5A623; }}
        .agent-severity-low {{ border-left: 5px solid {COLOUR['border_safe']}; }}
        
        .agent-label {{
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 800;
            letter-spacing: 1px;
            padding: 4px 8px;
            border-radius: 4px;
            margin-bottom: 12px;
            display: inline-block;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


                                                                             
         
                                                                             
def _render_sidebar() -> bool:
                                                                             
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 16px 0 24px;">
                <div style="font-size:2.8rem;">[Risk]</div>
                <div style="font-weight:800;font-size:1.1rem;color:{COLOUR['text_primary']};">
                    Contract Analyzer
                </div>
                <div style="font-size:11px;color:{COLOUR['text_secondary']};margin-top:4px;">
                    Powered by Trained ML & Agentic AI
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(SIDEBAR_HOW_TO)
        st.markdown("---")

        st.markdown("### ⚙️ Display Options")
        show_safe = st.checkbox("Show safe clauses", value=True)

        st.markdown("---")

        st.markdown("### Risk Legend")
        st.markdown(
            f"""
            <div style="display:flex;flex-direction:column;gap:8px;font-size:13px;">
                <div>
                    <span style="color:{COLOUR['border_risky']};font-weight:700;">[!] RISKY</span>
                    &nbsp;— Flagged by ML Model
                </div>
                <div>
                    <span style="color:{COLOUR['border_safe']};font-weight:700;">[OK] SAFE</span>
                    &nbsp;— High confidence safe
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(SIDEBAR_DISCLAIMER)

    return show_safe


                                                                             
             
                                                                             
def _render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero-banner">
            <p class="hero-title">{APP_TITLE}</p>
            <p class="hero-subtitle">{APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


                                                                             
                     
                                                                             
def _render_upload_section():
    st.markdown('<div class="section-title">Upload Contract Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Drag & drop your contract here, or click to browse",
        type=["pdf", "txt"],
        help="Supported formats: PDF (.pdf) and plain text (.txt)",
        label_visibility="visible",
    )
    return uploaded_file


                                                                             
                   
                                                                             
def _run_pipeline(uploaded_file):
           
    meta = get_file_metadata(uploaded_file)

                                        
    if st.session_state.last_analyzed_file != meta['name']:
        st.session_state.agent_report = None
        st.session_state.last_analyzed_file = meta['name']

                    
    st.markdown(
        f"""
        <div class="file-chip">
            <span>[File]</span>
            <strong>{meta['name']}</strong>
            &nbsp;|&nbsp; {meta['file_type']} &nbsp;|&nbsp; {meta['size_kb']} KB
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        with st.status("Preprocessing & Risk Prediction", expanded=True) as status:
                                  
            st.write("Searching document and extracting text...")
            time.sleep(0.3)
            text = extract_text_from_upload(uploaded_file)

            if not text or not text.strip():
                status.update(label="Analysis failed", state="error", expanded=True)
                st.error("Could not extract any text from the document.")
                return None, None, None, None

                                     
            st.write("Segmenting document into logical clauses...")
            time.sleep(0.3)
            clauses = segment_document(text)

            if not clauses:
                status.update(label="Analysis failed", state="error", expanded=True)
                st.warning("No distinct clauses could be extracted.")
                return None, None, None, None

                                             
            st.write("Running trained ML classifier...")
            time.sleep(0.3)
            analyzed = analyze_clauses(clauses)
            stats    = compute_summary_stats(analyzed)

            status.update(label=f"Risk Identification Complete (Using {stats['predictor']})", state="complete", expanded=False)

        return analyzed, stats, meta, text

    except Exception as e:
        st.error(f"❌ Unexpected error during pipeline: {e}")
        return None, None, None, None


                                                                             
                       
                                                                             
def _run_agent_analysis(text: str, clauses: list):
                                                                 
    risky_clauses = [c for c in clauses if c['label'] == 'Risky']
    
    if not risky_clauses:
        st.info("No risky clauses found for deep analysis.")
        return

    agent = LegalAgent()
    
    with st.status("Agentic AI Legal Assistant", expanded=True) as status:
                                            
        def update_status(state: AgentState):
            status.update(label=f"Agent Status: {state.value}...")
            st.write(f"Current Phase: **{state.value}**")

        agent.state_callback = update_status
        report = agent.run_analysis(text, risky_clauses)
        
        if report:
            st.session_state.agent_report = report
            status.update(label="Deep Analysis Complete", state="complete", expanded=False)
        else:
            status.update(label="Agent Analysis Failed", state="error", expanded=True)
            st.error("The legal agent encountered an error during analysis.")


                                                                             
                 
                                                                             
def _render_results(analyzed_clauses, stats, meta, text, show_safe: bool) -> None:
    st.markdown("---")

    col_title, col_btn = st.columns([0.7, 0.3])
    with col_title:
        st.markdown('<div class="section-title" style="margin-top:0;">📊 Analysis Dashboard</div>', unsafe_allow_html=True)
    with col_btn:
        pdf_bytes = generate_pdf_report(analyzed_clauses, stats, meta)
        st.download_button(
            label="Download Assessment",
            data=pdf_bytes,
            file_name=f"Risk_Assessment_{meta.get('name', 'Report')}.pdf",
            mime="application/pdf"
        )

                       
    render_summary_metrics(stats)

    st.markdown("<br>", unsafe_allow_html=True)

                
    risk_pct = stats["risk_percentage"]
    gauge_color = COLOUR["border_risky"] if risk_pct >= 50 else "#F5A623" if risk_pct >= 25 else COLOUR["border_safe"]
    st.markdown(
        f"""
        <div style="background:{COLOUR['bg_card']};border-radius:12px;padding:18px 24px;border:1px solid rgba(255,255,255,0.08);margin-bottom:28px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                <span style="font-size:14px;color:{COLOUR['text_secondary']};font-weight:500;">Overall Contract Risk Profile</span>
                <span style="font-size:14px;color:{gauge_color};font-weight:700;">{risk_pct}%</span>
            </div>
            <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:10px;">
                <div style="width:{risk_pct}%;background:linear-gradient(90deg,{gauge_color}88,{gauge_color});height:10px;border-radius:6px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

          
    tab_all, tab_risky, tab_agent = st.tabs([
        f"All ({stats['total']})",
        f"Risks Identified ({stats['risky_count']})",
        "AI Deep Analysis"
    ])

    with tab_all:
        render_clause_list(analyzed_clauses, show_safe=show_safe)

    with tab_risky:
        risky_clauses = [c for c in analyzed_clauses if c["label"] == "Risky"]
        if risky_clauses:
            render_clause_list(risky_clauses, show_safe=False)
        else:
            st.success("No risky clauses were identified by the ML model.")

    with tab_agent:
        st.markdown("### AI Deep Analysis")
        st.markdown("Get clause-level explanations, risk severity assessments, and mitigation strategies powered by RAG and LLMs.")
        
        if st.session_state.agent_report is None:
            if stats['risky_count'] > 0:
                if st.button("Run AI Deep Analysis", use_container_width=True):
                    _run_agent_analysis(text, analyzed_clauses)
                    st.rerun()
            else:
                st.info("No risky clauses found to analyze.")
        else:
            report = st.session_state.agent_report
            meta_data = report.get('report_metadata', {})
            
                         
            st.markdown(f"""
            <div class="agent-card">
                <h4 style="margin-top:0;color:{COLOUR['accent_light']};">Contract Executive Summary</h4>
                <p style="font-size:14px;line-height:1.6;color:{COLOUR['text_primary']};">
                    {meta_data.get('contract_summary', 'No summary generated.')}
                </p>
                <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1);font-size:12px;color:{COLOUR['text_secondary']};">
                    <b>Ethical Disclaimer:</b> {meta_data.get('legal_disclaimer', 'Not legal advice.')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Re-run Analysis", key="rerun_agent"):
                st.session_state.agent_report = None
                st.rerun()
            
            st.markdown("#### Detailed Clause Assessments")
            for clause in report.get('risky_clauses', []):
                sev = clause.get('risk_severity', 'Medium')
                sev_class = f"agent-severity-{sev.lower()}"
                
                st.markdown(f"""
                <div class="agent-card {sev_class}">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span class="agent-label" style="background:{COLOUR['border_risky'] if sev=='High' else '#F5A623' if sev=='Medium' else COLOUR['border_safe']};">
                            {sev} Intensity Risk
                        </span>
                        <span style="font-size:12px;color:{COLOUR['text_secondary']};">Clause #{clause.get('id', '?')}</span>
                    </div>
                    <p style="font-weight:600;font-size:14px;margin-bottom:12px;">Original Clause:</p>
                    <div style="font-style:italic;font-size:13px;color:{COLOUR['text_secondary']};background:rgba(0,0,0,0.2);padding:12px;border-radius:6px;margin-bottom:16px;">
                        "{clause.get('text', '')}"
                    </div>
                    <p style="font-weight:600;font-size:14px;margin-bottom:4px;">AI Explanation:</p>
                    <p style="font-size:14px;margin-bottom:16px;">{clause.get('explanation', '')}</p>
                    <p style="font-weight:600;font-size:14px;margin-bottom:4px;">Recommended Mitigation:</p>
                    <p style="font-size:14px;margin-bottom:0;">{clause.get('mitigation', '')}</p>
                </div>
                """, unsafe_allow_html=True)


                                                                             
                  
                                                                             
def main() -> None:
    _inject_global_styles()
    inject_card_styles()

    show_safe = _render_sidebar()
    _render_hero()

    uploaded_file = _render_upload_section()

    if uploaded_file is not None:
        analyzed_clauses, stats, meta, text = _run_pipeline(uploaded_file)
        if analyzed_clauses is not None:
            _render_results(analyzed_clauses, stats, meta, text, show_safe)
    else:
        st.session_state.agent_report = None
        st.markdown(
            f"""
            <div style="text-align:center;padding:60px 20px;color:{COLOUR['text_secondary']};">
                <div style="font-size:5rem;margin-bottom:16px;">(No File)</div>
                <div style="font-size:1.3rem;font-weight:600;color:{COLOUR['text_primary']};margin-bottom:8px;">
                    No document uploaded yet
                </div>
                <div style="font-size:14px;max-width:420px;margin:0 auto;">
                    Upload a PDF or TXT contract file to start the ML-powered risk analysis and Agentic AI assistance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

            
    st.markdown(
        f"""
        <div style="text-align:center;padding:40px 0 20px;color:{COLOUR['text_secondary']};font-size:12px;">
            Legal Contract Risk Analyzer |
            Milestone 2 Agentic Edition |
            Not legal advice
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
