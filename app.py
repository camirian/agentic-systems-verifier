import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# from xhtml2pdf import pisa
import base64
import io
import datetime
import time
import os
from core.ingestion import extract_requirements_from_pdf
from core.db import init_db, save_requirements, get_requirements, update_requirement, clear_database, log_event, get_system_logs, get_all_projects, update_generated_code, update_execution_result
from core.verification_engine import VerificationEngine
from core.pdf_utils import convert_md_to_pdf

# Initialize DB
init_db()

# Page Configuration
st.set_page_config(
    page_title="ASV: Agentic Systems Verifier",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Nord Theme & Typography) ---
st.markdown("""
<style>
    /* Reduce Top Padding */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Remove Top Margin from Main Title */
    .stApp > header {
        display: none; /* Hide the Streamlit header bar if visible */
    }
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0rem;
    }
    h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    
    /* Sidebar Title "Mission Control" */
    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
    }
    
    /* Sidebar Subheader "Requirement Inspector" */
    [data-testid="stSidebar"] h3 {
        font-size: 1.3rem !important;
    }
    
    /* Password Input Dots */
    input[type="password"] {
        font-size: 0.8rem !important;
        letter-spacing: 3px !important;
    }
    
    /* File Uploader Text & Icon */
    [data-testid="stFileUploader"] section > div {
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    [data-testid="stFileUploader"] div[role="button"] {
        font-size: 0.85rem !important;
    }
    [data-testid="stFileUploader"] svg {
        width: 1.2rem !important;
        height: 1.2rem !important;
    }
    
    /* Reduce Sidebar Top Padding */
    /* Reduce Sidebar Top Padding */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }

    /* Base Text (Paragraphs, Captions) */
    .stMarkdown p, .stText, .stCaption {
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
        color: #ECEFF4 !important;
    }
    
    /* Headers */
    h1, h2, h3 { color: #88C0D0 !important; } /* Frost Cyan Headers */
    h1 { font-size: 2.2rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.8rem !important; font-weight: 600 !important; }
    h3 { font-size: 1.5rem !important; font-weight: 600 !important; }
    
    /* Sidebar Elements */
    [data-testid="stSidebar"] {
        font-size: 1.1rem !important;
        background-color: #3B4252 !important; /* Secondary Dark */
    }
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 1.05rem !important;
    }
    
    /* Input Fields & Buttons */
    .stTextInput input, .stSelectbox div, .stMultiSelect div, button {
        font-size: 1.1rem !important;
        color: #ECEFF4 !important;
    }
    
    /* Tabs Styling (Nord) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent !important;
        border-radius: 0px !important;
        border-top: 3px solid transparent !important;
        border-bottom: none !important;
        color: rgba(236, 239, 244, 0.6) !important; /* Inactive opacity */
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        border-top: 3px solid #88C0D0 !important; /* Frost Cyan */
        color: #ECEFF4 !important; /* Snow Storm */
        font-weight: 600 !important;
    }
    
    /* Expander Headers */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #81A1C1 !important; /* Glacial Blue */
    }
    
    /* Dataframe/Table adjustments */
    [data-testid="stDataFrame"] {
        transform: scale(1.0);
    }
    
    /* Alert Boxes (Info, Success, Warning, Error) High Contrast */
    [data-testid="stAlert"] {
        background-color: #4C566A !important; /* Nord Bright Black */
        color: #ECEFF4 !important; /* Snow Storm Text */
        border: 1px solid #81A1C1 !important;
    }
    [data-testid="stAlert"] p {
        color: #ECEFF4 !important;
    }
    
    /* --- Sidebar High Density --- */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    /* Remove gap between widgets */
    .st-emotion-cache-16idsys p {
        margin-bottom: 0px;
    }

    /* Force Streamlit Dataframe Column Menu to be visible */
    button[title="Column menu"] {
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
    }

    /* Fix Multiselect Tag Contrast */
    span[data-baseweb="tag"] {
        background-color: #88C0D0 !important; /* Keep the Nord Frost Cyan */
        color: #2E3440 !important; /* Force Text to Nord Dark Grey */
    }
    /* Fix the "X" (Close) icon color to match */
    span[data-baseweb="tag"] svg {
        fill: #2E3440 !important;
    }

    /* Force Dark Text on Primary (Cyan) Buttons */
    div.stButton > button[kind="primary"] {
        color: #2E3440 !important; /* Nord Dark Grey */
        font-weight: 700 !important; /* Bold */
        border: 1px solid #81A1C1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Management
if 'requirements' not in st.session_state:
    # Load from DB
    db_data = get_requirements()
    if db_data:
        st.session_state['requirements'] = pd.DataFrame(db_data)
    else:
        # Initialize with empty DataFrame
        st.session_state['requirements'] = pd.DataFrame(columns=[
            "ID", "Requirement Name", "Requirement", "Status", "Priority", "Source", 
            "Verification Method", "Rationale", "Generated Code", 
            "Verification Status", "Execution Log", "Select"
        ])

    # Enforce Schema (Ensure all columns exist)
    required_cols = [
        "ID", "Requirement Name", "Requirement", "Status", "Priority", "Source", 
        "Verification Method", "Rationale", "Generated Code", 
        "Verification Status", "Execution Log", "Select"
    ]
    
    for col in required_cols:
        if col not in st.session_state['requirements'].columns:
            if col == "Select":
                st.session_state['requirements'][col] = False
            else:
                st.session_state['requirements'][col] = ""

if 'system_logs' not in st.session_state:
    # Initial log if empty
    # get_system_logs returns a list of dicts, so simple truthiness check works
    if not get_system_logs(limit=1):
        log_event("System initialized.")
        log_event("Database connected.")
        log_event("Waiting for user input...")

def render_documentation():
    st.title("📚 Project Knowledge Base")
    
    # --- CSS Injection for Branded Typography ---
    st.markdown("""
        <style>
        /* Force Markdown Headers to match Brand Color */
        div.stMarkdown h1, div.stMarkdown h2, div.stMarkdown h3 {
            color: #88C0D0 !important; /* Nord Frost Cyan */
            font-family: 'Helvetica Neue', sans-serif;
        }
        /* Add a subtle border to the bottom of H1s */
        div.stMarkdown h1 {
            border-bottom: 1px solid #4C566A;
            padding-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. Narrative Ordering & Icons
    doc_map = {
        "💰 Grant Narrative": "docs/pitch/GRANT_APPLICATION_ANSWERS.md",
        "📄 Whitepaper Abstract": "docs/pitch/WHITEPAPER_ABSTRACT.md",
        "🏗️ Architecture (ADR)": "docs/pitch/ADR_001_ARCHITECTURE.md",
        "📖 User Manual": "docs/UI_USER_MANUAL.md",
        "📂 Main Readme": "README.md"
    }
    
    # 2. High-Visibility Navigation
    # Using radio with horizontal=True for a tab-like experience
    selected_doc = st.radio(
        "Select Artifact", 
        options=list(doc_map.keys()), 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    file_path = doc_map[selected_doc]
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
            
        # 3. Visual Flourish (Download Button)
        col1, col2 = st.columns([3, 1])
        with col1:
            pass # Clean UI - No debug path
        with col2:
            # Convert to PDF on the fly
            with st.spinner("Generating PDF..."):
                pdf_data = convert_md_to_pdf(content)
            
            if pdf_data:
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_data,
                    file_name=f"{os.path.splitext(os.path.basename(file_path))[0]}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("PDF Generation Failed")
            
        st.markdown(content, unsafe_allow_html=True)
    else:
        st.error(f"File not found: {file_path}")

def render_mission_control():
    # Sidebar Layout
    with st.sidebar:
        # --- Global Project Selector ---
        st.markdown("---")
        
        # --- Project Selection (Global) ---
        st.sidebar.header("📂 Active Specification")
        
        # Fetch projects with metadata
        projects = get_all_projects() # Returns list of dicts
        
        # Create mapping for Rich Dropdown
        # Map filename -> "📄 Title (Count Reqs)"
        project_map = {p['filename']: p for p in projects}
        
        # Add "All Projects" option
        all_projects_option = "All Projects"
        options = [all_projects_option] + list(project_map.keys())
        
        def format_project(filename):
            if filename == all_projects_option:
                return "🌍 All Projects"
            p = project_map.get(filename)
            if p and p['title']:
                return f"📄 {p['title']} ({p['req_count']} Reqs)"
            return f"📄 {filename}"

        if 'selected_spec' not in st.session_state:
            st.session_state['selected_spec'] = all_projects_option
            
        # Ensure current selection is valid
        if st.session_state['selected_spec'] not in options:
             st.session_state['selected_spec'] = all_projects_option

        def on_project_change():
            spec = st.session_state['spec_selector']
            st.session_state['selected_spec'] = spec
            # Reload data
            db_data = get_requirements(source_file=spec)
            st.session_state['requirements'] = pd.DataFrame(db_data) if db_data else pd.DataFrame(columns=["ID", "Requirement Name", "Requirement", "Status", "Priority", "Source"])
            st.session_state['selected_req_id'] = None
            st.toast(f"Switched to project: {spec}", icon="🔄")

        st.sidebar.selectbox(
            "Select Project",
            options=options,
            format_func=format_project,
            index=options.index(st.session_state['selected_spec']),
            key='spec_selector',
            on_change=on_project_change,
            label_visibility="collapsed"
        )
        st.divider()
        

        st.divider()

        # --- Mission Phase Tracker (Logic Only) ---
        reqs = st.session_state['requirements']
        current_phase = 0 # Setup
        if not reqs.empty:
            current_phase = 1 # Analysis
            # Check if any are verified/failed (implies verification ran)
            if len(reqs[reqs['Status'].isin(['Verified', 'Failed'])]) > 0:
                current_phase = 2 # Report
        with st.expander("ℹ️ Workflow Methodology"):
            st.markdown("""
            **Automating the V-Model:**
            
            * **Phase 1 (Decomposition):** We ingest the raw PDF ("Left-V") and extract atomic "Shall" requirements.
            * **Phase 2 (Analysis & Planning):** AI Agents act as **Lead Systems Engineers**, analyzing each requirement to determine the correct Verification Method (Test, Inspection, Analysis).
            * **Phase 3 (Traceability):** We generate the dynamic **VCRM** (Verification Cross-Reference Matrix) to prove compliance coverage ("Right-V").
            """)
        
        # 1. API Key (Hidden in Expander)
        # 1. API Key (Hidden in Expander)
        with st.expander("🔐 API Credentials", expanded=False):
            # Check for secret key (Demo Mode)
            default_key = st.secrets.get("GOOGLE_API_KEY", "")
            api_key = st.text_input("Google API Key", value=default_key, type="password", help="Required for AI Extraction. Leave empty to use system default if configured.")
        
        # 2. Mission Setup (Grouped)
        # Auto-collapse if we are past the setup phase
        with st.expander("📄 Specification Ingestion", expanded=(current_phase == 0)):
            uploaded_file = st.file_uploader("Upload Spec (PDF)", type=["pdf"])
            
            if uploaded_file:
                # Token Estimator (Heuristic: 1 byte ~= 0.25 tokens)
                est_tokens = uploaded_file.size / 4
                st.caption(f"📊 Size: {uploaded_file.size/1024:.1f} KB | Est. Tokens: {est_tokens:,.0f}")
            
            target_section = st.text_input(
                "Target Section", 
                value="", 
                help="Verify specific section to manage context window"
            )
            
            if st.button("🚀 Start Ingestion", use_container_width=True):
                log_event(f"Initializing agents for Section {target_section}...")
                
                if uploaded_file:
                    # Save the file with original name (sanitized)
                    safe_filename = os.path.basename(uploaded_file.name)
                    save_path = os.path.join("data", safe_filename)
                    os.makedirs("data", exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    log_event(f"Saved spec to {save_path}")
                    log_event("Ingesting PDF with Smart Regex Engine...")
                    
                    if not api_key:
                        st.error("Please enter a Google API Key.")
                    else:
                        progress_bar = st.progress(0.0)
                        status_text = st.empty()
                        
                        def update_progress(p, text):
                            progress_bar.progress(p)
                            status_text.caption(f"🔄 {text}")
                        
                        # Call Ingestion (Now returns tuple)
                        extracted_data, doc_title = extract_requirements_from_pdf(
                            save_path, 
                            api_key, 
                            target_section=target_section,
                            progress_callback=update_progress
                        )
                        
                        if extracted_data:
                            # Save to DB with Title
                            save_requirements(extracted_data, source_file=safe_filename, section=target_section, doc_title=doc_title)
                            
                            # Update Session State
                            st.session_state['requirements'] = pd.DataFrame(get_requirements(source_file=safe_filename))
                            st.session_state['selected_spec'] = safe_filename # Auto-switch to new project
                            
                            log_event(f"Found {len(extracted_data)} requirements.")
                            st.toast(f"Ingested {len(extracted_data)} Requirements", icon="✅")
                            st.success(f"✅ Successfully ingested {len(extracted_data)} requirements from '{doc_title}'!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            log_event("Warning: No requirements found matching criteria.", level="WARN")
                            st.error("No requirements found in the PDF.")
                        
                else:
                    st.warning("Please upload a PDF to initialize.")

        st.divider()
        
        # 3. Execution Controls
        st.markdown("#### 🚀 Execution")
        
        # Session State for Verification Loop
        if 'is_verifying' not in st.session_state:
            st.session_state['is_verifying'] = False

        if st.session_state['is_verifying']:
            # STOP BUTTON
            if st.button("⏹️ Stop Verification", type="secondary", use_container_width=True):
                st.session_state['is_verifying'] = False
                st.rerun()
            
            # Verification Logic (Runs automatically when state is True)
            if not api_key:
                st.error("API Key required for verification.")
                st.session_state['is_verifying'] = False
                st.stop()
            else:
                # Default to None if empty (Verify All)
                section_scope = target_section if target_section else None
                
                engine = VerificationEngine(api_key)
                
                # Progress UI
                progress_text = "Starting Verification Plan..."
                my_bar = st.progress(0, text=progress_text)
                status_text = st.empty()
                
                # Check if a single requirement is selected in the UI
                selected_id = st.session_state.get('selected_req_id')
                
                try:
                    if selected_id:
                        # Verify ONLY the selected requirement
                        for log_msg in engine.verify_single_requirement(selected_id):
                            status_text.text(log_msg)
                    else:
                        # Verify based on section scope (or all)
                        for log_msg in engine.verify_section(section_scope):
                            status_text.text(log_msg)
                            
                    my_bar.progress(100, text="Verification Complete!")
                    st.success("Verification Analysis Complete.")
                    time.sleep(1)
                    
                    # Reset state after success
                    st.session_state['is_verifying'] = False
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Verification Failed: {e}")
                    log_event(f"Verification Failed: {e}", level="ERROR")
                    st.session_state['is_verifying'] = False

        else:
            # START BUTTON
            if st.button("▶️ Generate Verification Plan", use_container_width=True, type="primary"):
                if not api_key:
                    st.error("API Key required for verification.")
                else:
                    st.session_state['is_verifying'] = True
                    st.rerun()

    # Main Layout
    # Main Layout
    st.title("ASV: Agentic Systems Verifier")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Requirements Trace", "🧠 Agent Cortex", "✅ Verification Report"])

    with tab1:
        st.subheader("Requirements Traceability Matrix")
        
        # Ensure 'Select' column exists in session state (Initialize early)
        if 'Select' not in st.session_state['requirements'].columns:
            st.session_state['requirements']['Select'] = False
        
        # Capture previous state for comparison (CM)
        previous_df = st.session_state['requirements'].copy()
        
        # --- Documentation ---
        with st.expander("📘 User Guide & Legend"):
            st.markdown("""
            ### 🎮 How to Control the Matrix
            * **Sort:** Click any Column Header (e.g., "Priority") to sort A-Z or Z-A.
            * **Filter & Pin (The 3 Dots):** Click the **⋮** (vertical dots) icon on the right of any header to:
                * Filter specific values (e.g., Status = "Pending").
                * Pin columns to the left.
                * Group data by category.
            * **Resize:** Drag the vertical lines between headers to expand columns.
            * **Search:** Use the 🔍 icon (top right of table) for global text search.
            """)
        
        # --- Filters ---
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            filter_status = st.multiselect("Filter by Status", options=["Verified", "Failed", "Pending", "Analyzed"], default=[])
        with col_f2:
            filter_priority = st.multiselect("Filter by Priority", options=["Critical", "High", "Medium", "Low"], default=[])
        with col_f3:
            filter_source = st.multiselect("Filter by Source", options=["Original", "Modified", "⚠️ Modified"], default=[])
        with col_f4:
            # Dynamically get available methods or use standard list
            filter_method = st.multiselect("Filter by Method", options=["Test", "Analysis", "Inspection", "Demonstration"], default=[])

        # Apply Filters
        df_view = st.session_state['requirements'].copy()
        if not df_view.empty:
            if filter_status:
                df_view = df_view[df_view["Status"].isin(filter_status)]
            if filter_priority:
                df_view = df_view[df_view["Priority"].isin(filter_priority)]
            if filter_source:
                df_view = df_view[df_view["Source"].isin(filter_source)]
            if filter_method and 'Verification Method' in df_view.columns:
                df_view = df_view[df_view["Verification Method"].isin(filter_method)]

        # --- Interactive Dataframe ---
        # Action Bar (Custom Toolbar)
        col_act1, col_act2, col_act3 = st.columns([2, 2, 1])
        with col_act1:
            st.caption("👇 Click checkboxes to select rows. Use 'Select All' to bulk select.")
        with col_act2:
            search_query = st.text_input("Search", placeholder="🔍 Search ID, Name, or Text...", label_visibility="collapsed")
            if search_query:
                df_view = df_view[
                    df_view["ID"].str.contains(search_query, case=False, na=False) |
                    df_view["Requirement Name"].str.contains(search_query, case=False, na=False) |
                    df_view["Requirement"].str.contains(search_query, case=False, na=False)
                ]
        with col_act3:
            # Custom Export Button (High Visibility)
            # Ensure evidence columns are included
            export_cols = [c for c in df_view.columns if c != "Select"]
            csv_data = df_view[export_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Export to CSV",
                data=csv_data,
                file_name=f"requirements_trace_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download the currently filtered requirements matrix for external analysis.",
                use_container_width=True
            )
        
        # --- Selection Logic (Multi-Select Support) ---
        # (Select column initialization moved to top of function)

        def handle_selection_change():
            # Get the edited rows from the data_editor state
            editor_state = st.session_state.get("data_editor", {})
            edited_rows = editor_state.get("edited_rows", {})
            
            # Update the main dataframe based on user clicks
            for idx, changes in edited_rows.items():
                if "Select" in changes:
                    # idx is the index in df_view. We need to map it to the main dataframe index.
                    # Since df_view is a filtered view, we need the ID to find the row in main DF.
                    if idx in df_view.index:
                        req_id = df_view.loc[idx, "ID"]
                        # Update main dataframe
                        main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == req_id].index[0]
                        st.session_state['requirements'].at[main_idx, 'Select'] = changes["Select"]

        # Add Select All Button Logic
        if st.button("✅ Select All Shown", key="select_all_btn"):
            # Set Select=True for all IDs in the current view
            shown_ids = df_view['ID'].tolist()
            st.session_state['requirements'].loc[st.session_state['requirements']['ID'].isin(shown_ids), 'Select'] = True
            st.rerun()
            
        if st.button("❌ Deselect All", key="deselect_all_btn"):
            st.session_state['requirements']['Select'] = False
            st.rerun()

        # Prepare View
        # We must sync df_view's Select column with the main dataframe
        # (df_view is a copy, so we need to ensure it has the latest Select values)
        # Actually, we created df_view from session_state['requirements'] at line 531.
        # So it already has the 'Select' column if we added it.
        
        # Reorder Columns: Select first
        cols = ['Select'] + [c for c in df_view.columns if c != 'Select']
        df_view = df_view[cols]
        cols_to_show = ['Select', 'ID', 'Verification Method', 'Requirement Name', 'Requirement', 'Rationale', 'Status', 'Priority', 'Source']
        # Filter to only columns that actually exist in df_view (avoid key error)
        cols_to_show = [c for c in cols_to_show if c in df_view.columns]
        df_view = df_view[cols_to_show]
        
        # We use st.data_editor
        edited_df = st.data_editor(
            df_view,
            use_container_width=True,
            height=850,
            on_change=handle_selection_change,
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", width="small"),
                "ID": st.column_config.TextColumn("ID", width="small", disabled=True),
                "Verification Method": st.column_config.SelectboxColumn(
                    "Method", 
                    width="small", 
                    options=["Test", "Analysis", "Inspection", "Demonstration"],
                    required=True,
                    help="Verification Method (T/A/I/D)"
                ),
                "Requirement Name": st.column_config.TextColumn("Name", width="medium", disabled=True),
                "Requirement": st.column_config.TextColumn(
                    "Requirement", 
                    width="large", 
                    disabled=False,
                    help="Double-click to edit or view full text in Inspector"
                ),
                "Rationale": st.column_config.TextColumn(
                    "AI Rationale", 
                    width="large", 
                    disabled=True,
                    help="Double-click to view full text in Inspector"
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status", 
                    width="small", 
                    options=["Pending", "Analyzed", "Verified", "Failed"],
                    required=True
                ),
                "Priority": st.column_config.SelectboxColumn(
                    "Priority", 
                    width="small", 
                    options=["Critical", "High", "Medium", "Low"],
                    required=True
                ),
                "Source": st.column_config.TextColumn("Source", width="small", disabled=True)
            },
            disabled=["ID", "Source", "Requirement Name", "Rationale"], # ID and Source are immutable, Name/Rationale are AI generated
            hide_index=True,
            key="data_editor"
        )
        
        # --- Audit Trail Logic (Change Detection) ---
        # Compare edited_df with the original df_view to detect changes
        # We drop 'Select' column for comparison to avoid triggering audit on selection
        df_view_core = df_view.drop(columns=["Select"])
        edited_df_core = edited_df.drop(columns=["Select"])
        
        if not edited_df_core.equals(df_view_core):
            # List of columns to watch for changes
            watch_cols = ["Requirement", "Priority", "Status", "Verification Method"]
            
            for index, row in edited_df_core.iterrows():
                original_row = df_view_core.loc[index]
                
                # Check if ANY watched column has changed
                has_changed = False
                for col in watch_cols:
                    if row[col] != original_row[col]:
                        has_changed = True
                        break
                
                if has_changed:
                    # Data was modified!
                    req_id = row['ID']
                    
                    # Update DB
                    update_requirement(
                        req_id=req_id,
                        text=row['Requirement'],
                        status=row['Status'],
                        priority=row['Priority'],
                        source_type="⚠️ Modified"
                    )
                    
                    # Update Session State
                    main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == req_id].index[0]
                    st.session_state['requirements'].at[main_idx, 'Requirement'] = row['Requirement']
                    st.session_state['requirements'].at[main_idx, 'Status'] = row['Status']
                    st.session_state['requirements'].at[main_idx, 'Priority'] = row['Priority']
                    if 'Verification Method' in row:
                        st.session_state['requirements'].at[main_idx, 'Verification Method'] = row['Verification Method']
                    st.session_state['requirements'].at[main_idx, 'Source'] = "⚠️ Modified"
                    
                    st.toast(f"Requirement {req_id} updated & Audit Trail logged", icon="✏️")
                    st.rerun()
        
        # --- Inspector Logic (Sidebar) ---
        # Find selected rows based on the 'Select' column
        selected_rows = edited_df[edited_df['Select'] == True]
        
        with st.sidebar:
            st.divider()
            
            # --- HELP / USER GUIDE ---
            with st.expander("❓ User Guide & Workflow"):
                st.markdown("""
                **1. Select Requirements**
                Check the boxes in the table to select requirements.
                
                **2. Generate Verification Plans**
                - **Inspection:** For manual checks (no code).
                - **Test:** For automated checks (requires code).
                - *Note: You can change the method in "Manual Overrides".*
                
                **3. Execute & Verify**
                Click **"Generate Test Case"** (if Test) and then **"Run Verification"**.
                
                **4. Export Evidence**
                Use the "Export to CSV" button to download the full report, including generated code and execution logs.
                """)
            
            st.divider()

            if selected_rows.empty:
                st.info("👈 Select requirements in the table to view details or perform actions.")
            
            elif len(selected_rows) > 1:
                # --- BULK ACTIONS ---
                st.markdown(f"#### 📦 Bulk Actions ({len(selected_rows)} items)")
                
                try:
                    # CRITICAL FIX: selected_rows (from UI) lacks 'Generated Code' column.
                    # We must fetch the full data from session state using the IDs.
                    selected_ids = selected_rows['ID'].tolist()
                    full_selected_rows = st.session_state['requirements'][
                        st.session_state['requirements']['ID'].isin(selected_ids)
                    ]
                    
                    # Local Failsafe: Ensure columns exist in the slice
                    if 'Generated Code' not in full_selected_rows.columns:
                        full_selected_rows['Generated Code'] = ""
                    if 'Verification Method' not in full_selected_rows.columns:
                        full_selected_rows['Verification Method'] = ""

                    # DEBUG: Show what we found
                    with st.expander("🐞 Debug Data", expanded=True):
                        st.write("Selected IDs:", selected_ids)
                        st.write("Full Rows Found:", len(full_selected_rows))
                        if not full_selected_rows.empty:
                            st.dataframe(full_selected_rows[['ID', 'Verification Method', 'Generated Code']])
                    
                    # 1. Bulk Generate (Show for ALL Test items, allowing regeneration)
                    # Robust check: handle NaN, whitespace, case
                    test_candidates = full_selected_rows[
                        full_selected_rows['Verification Method'].fillna('').astype(str).str.strip().eq('Test')
                    ]
                    
                    actions_available = False
                    
                    if not test_candidates.empty:
                        actions_available = True
                        # Count how many are missing code
                        missing_count = test_candidates['Generated Code'].fillna('').eq('').sum()
                        btn_label = f"⚡ Generate Code for {len(test_candidates)} Items"
                        if missing_count < len(test_candidates):
                            btn_label += f" ({len(test_candidates) - missing_count} will be overwritten)"
                        
                        if st.button(btn_label, type="primary", use_container_width=True):
                            if not api_key:
                                st.error("API Key required.")
                            else:
                                progress_bar = st.progress(0)
                                engine = VerificationEngine(api_key)
                                
                                for i, (index, row) in enumerate(test_candidates.iterrows()):
                                    with st.spinner(f"Generating for {row['ID']}..."):
                                        code = engine.generate_test_code(row['Requirement'])
                                        update_generated_code(row['ID'], code)
                                        
                                        # Update Session State
                                        main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == row['ID']].index[0]
                                        st.session_state['requirements'].at[main_idx, 'Generated Code'] = code
                                    
                                    progress_bar.progress((i + 1) / len(test_candidates))
                                
                                st.success("Bulk Generation Complete!")
                                time.sleep(1)
                                st.rerun()
                    
                    # 2. Bulk Execute (Show for items with code)
                    # Robust check for non-empty code
                    ready_to_run = full_selected_rows[full_selected_rows['Generated Code'].fillna('').ne('')]
                    
                    if not ready_to_run.empty:
                        actions_available = True
                        st.markdown(f"**Ready to Execute:** {len(ready_to_run)} items")
                        if st.button(f"▶️ Run Verification for {len(ready_to_run)} Items", type="secondary", use_container_width=True):
                            if not api_key:
                                st.error("API Key required.")
                            else:
                                progress_bar = st.progress(0)
                                engine = VerificationEngine(api_key)
                                
                                for i, (index, row) in enumerate(ready_to_run.iterrows()):
                                    with st.spinner(f"Executing {row['ID']}..."):
                                        result = engine.execute_test_code(row['Generated Code'])
                                        update_execution_result(row['ID'], result['status'], result['log'])
                                        
                                        # Update Session State
                                        main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == row['ID']].index[0]
                                        st.session_state['requirements'].at[main_idx, 'Verification Status'] = result['status']
                                        st.session_state['requirements'].at[main_idx, 'Execution Log'] = result['log']
                                    
                                    progress_bar.progress((i + 1) / len(ready_to_run))
                                
                                st.success("Bulk Execution Complete!")
                                time.sleep(1)
                                st.rerun()
                                
                    if not actions_available:
                        st.warning("No actions available. Ensure items are set to 'Test' method.")
                        
                except Exception as e:
                    st.error(f"Bulk Actions Error: {str(e)}")
                    st.exception(e)

            else:
                # --- SINGLE ITEM INSPECTOR (Existing Logic) ---
                selected_row = selected_rows.iloc[0]
                st.markdown("#### 🔍 Requirement Inspector")
                
                # --- Compact Metadata Card ---
                # Safely get method and rationale
                method = selected_row.get('Verification Method', 'N/A')
                if pd.isna(method) or method == "": method = "N/A"
                
                rationale = selected_row.get('Rationale', 'No rationale provided.')
                if pd.isna(rationale) or rationale == "": rationale = "No rationale provided."
                
                # HTML Rendering
                st.markdown(f"""
<div style="margin-bottom: 10px;">
    <small style="color: #81A1C1;">ID: {selected_row['ID']}</small><br>
    <strong style="font-size: 16px; color: #ECEFF4;">{selected_row['Requirement Name']}</strong>
</div>

<div style="display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap;">
    <span style="background-color: #2E3440; padding: 4px 8px; border-radius: 4px; border: 1px solid #88C0D0; color: #88C0D0; font-size: 11px;">{selected_row['Status']}</span>
    <span style="background-color: #2E3440; padding: 4px 8px; border-radius: 4px; border: 1px solid #A3BE8C; color: #A3BE8C; font-size: 11px;">{method}</span>
    <span style="background-color: #2E3440; padding: 4px 8px; border-radius: 4px; border: 1px solid #EBCB8B; color: #EBCB8B; font-size: 11px;">{selected_row['Priority']}</span>
    <span style="background-color: #2E3440; padding: 4px 8px; border-radius: 4px; border: 1px solid #5E81AC; color: #5E81AC; font-size: 11px;">{selected_row['Source']}</span>
</div>

<div style="margin-bottom: 15px;">
    <small style="color: #81A1C1; font-weight: bold;">REQUIREMENT TEXT</small><br>
    <div style="background-color: #3B4252; padding: 10px; border-radius: 5px; border-left: 4px solid #88C0D0; color: #ECEFF4;">
        {selected_row['Requirement']}
    </div>
</div>

<div>
    <small style="color: #81A1C1; font-weight: bold;">AI RATIONALE</small><br>
    <div style="background-color: #2E3440; padding: 10px; border-radius: 5px; color: #D8DEE9; font-style: normal;">
        "{rationale}"
    </div>
</div>
<br>
""", unsafe_allow_html=True)
                
                # --- On-Demand Code Generator ---
                if method == "Test":
                    st.markdown("#### ⚡ Code Generator")
                    
                    # Check if code already exists
                    existing_code = selected_row.get('Generated Code', '')
                    if pd.isna(existing_code): existing_code = ""
                    
                    if st.button("Generate Test Case", use_container_width=True, type="primary"):
                        if not api_key:
                            st.error("Google API Key required.")
                        else:
                            with st.spinner("Writing pytest script..."):
                                engine = VerificationEngine(api_key)
                                generated_code = engine.generate_test_code(selected_row['Requirement'])
                                
                                # Save to DB
                                update_generated_code(selected_row['ID'], generated_code)
                                
                                # Update Session State
                                main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == selected_row['ID']].index[0]
                                st.session_state['requirements'].at[main_idx, 'Generated Code'] = generated_code
                                
                                st.success("Code Generated!")
                                st.rerun()
                    
                    if existing_code:
                        st.caption("✅ Generated Verification Script")
                        st.code(existing_code, language="python")
                        
                        # --- Execution Control ---
                        col_run, col_status = st.columns([1, 2])
                        with col_run:
                            if st.button("▶️ Run Verification", type="secondary", use_container_width=True):
                                with st.spinner("Executing tests..."):
                                    engine = VerificationEngine(api_key)
                                    result = engine.execute_test_code(existing_code)
                                    
                                    # Save result
                                    update_execution_result(selected_row['ID'], result['status'], result['log'])
                                    
                                    # Update Session State
                                    main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == selected_row['ID']].index[0]
                                    st.session_state['requirements'].at[main_idx, 'Verification Status'] = result['status']
                                    st.session_state['requirements'].at[main_idx, 'Execution Log'] = result['log']
                                    
                                    if result['status'] == "Pass":
                                        st.toast("Verification Passed!", icon="✅")
                                    else:
                                        st.toast("Verification Failed!", icon="❌")
                                    st.rerun()

                        # Display Status
                        exec_status = selected_row.get('Verification Status', None)
                        if pd.isna(exec_status): exec_status = None
                        
                        with col_status:
                            if exec_status == "Pass":
                                st.success("✅ VERIFICATION PASSED")
                            elif exec_status == "Fail":
                                st.error("❌ VERIFICATION FAILED")
                            elif exec_status == "Error":
                                st.warning("⚠️ EXECUTION ERROR")
                        
                        # Display Logs
                        exec_log = selected_row.get('Execution Log', None)
                        if pd.isna(exec_log): exec_log = None
                        
                        if exec_log:
                            with st.expander("📜 Execution Logs", expanded=(exec_status != "Pass")):
                                st.code(exec_log, language="text")
                
                # --- Manual Controls (Moved to Bottom) ---
                st.divider()
                with st.expander("🛠️ Manual Overrides"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        new_status = st.selectbox(
                            "Status", 
                            options=["Pending", "Analyzed", "Verified", "Failed"], 
                            index=["Pending", "Analyzed", "Verified", "Failed"].index(selected_row['Status']) if selected_row['Status'] in ["Pending", "Analyzed", "Verified", "Failed"] else 0,
                            key=f"status_{selected_row['ID']}"
                        )
                    
                    with col2:
                        new_priority = st.selectbox(
                            "Priority", 
                            options=["Low", "Medium", "High", "Critical"], 
                            index=["Low", "Medium", "High", "Critical"].index(selected_row['Priority']) if selected_row['Priority'] in ["Low", "Medium", "High", "Critical"] else 1,
                            key=f"priority_{selected_row['ID']}"
                        )

                    with col3:
                        # Handle case where method might be empty or not in list
                        method_opts = ["Test", "Analysis", "Inspection", "Demonstration"]
                        current_method = selected_row.get('Verification Method', 'Analysis')
                        if current_method not in method_opts: current_method = "Analysis"
                        
                        new_method = st.selectbox(
                            "Method", 
                            options=method_opts, 
                            index=method_opts.index(current_method),
                            key=f"method_{selected_row['ID']}"
                        )
                    
                    # Check for changes
                    current_status = selected_row['Status']
                    current_priority = selected_row['Priority']
                    current_method_val = selected_row.get('Verification Method', '')
                    
                    if (new_status != current_status) or (new_priority != current_priority) or (new_method != current_method_val):
                        if st.button("💾 Save Overrides", use_container_width=True):
                            # Update DB
                            update_requirement(
                                req_id=selected_row['ID'],
                                text=selected_row['Requirement'],
                                status=new_status,
                                priority=new_priority,
                                source_type="⚠️ Modified",
                                verification_method=new_method
                            )
                            
                            # Update Session State
                            main_idx = st.session_state['requirements'][st.session_state['requirements']['ID'] == selected_row['ID']].index[0]
                            st.session_state['requirements'].at[main_idx, 'Status'] = new_status
                            st.session_state['requirements'].at[main_idx, 'Priority'] = new_priority
                            st.session_state['requirements'].at[main_idx, 'Verification Method'] = new_method
                            st.session_state['requirements'].at[main_idx, 'Source'] = "⚠️ Modified"
                            
                            st.toast("Manual Override Saved", icon="💾")
                            st.rerun()


        # --- Global Debug Footer ---
        st.divider()
        with st.expander("🐞 Debug & System Info", expanded=False):
            st.caption(f"App Version: {datetime.datetime.now().strftime('%H:%M:%S')}")
            st.write("Selection Count:", len(selected_rows))
            if not selected_rows.empty:
                st.write("Selected IDs:", selected_rows['ID'].tolist())
                # Show method for first few
                st.dataframe(selected_rows[['ID', 'Verification Method']].head())
            else:
                st.write("No rows selected.")
            
            if mod_count > 0:
                st.divider()
                with st.expander(f"📝 Change Manifest ({mod_count} items pending review)", expanded=False):
                    st.caption("These items have been manually overridden from the AI baseline.")
                    st.dataframe(
                        modified_rows.style.apply(lambda x: ['background-color: #332b00'] * len(x), axis=1),
                        use_container_width=True
                    )

    with tab2:
        # --- HUD Legend ---
        st.markdown("""
        <div style="background-color: #3B4252; padding: 15px; border-left: 5px solid #88C0D0; border-radius: 5px; margin-bottom: 20px;">
            <strong style="color: #ECEFF4;">🧠 Agent Cortex - System Audit Log</strong><br>
            <span style="color: #D8DEE9; font-size: 14px;">
            This is the immutable "Flight Data Recorder" tracking autonomous decisions.<br>
            <span style="color: #88C0D0;">● [INFO]</span> State transitions, database commits, and routine orchestrator events.<br>
            <span style="color: #A3BE8C;">● [ANALYSIS]</span> Chain-of-Thought reasoning, verification logic, and AI decision pathways.<br>
            <span style="color: #EBCB8B;">● [WARN]</span> Rate limits, retries, or non-critical data anomalies.<br>
            <span style="color: #BF616A;">● [ERROR]</span> API exceptions, validation failures, or safety interlock triggers.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # --- Log Controls ---
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            selected_levels = st.multiselect(
                "Filter by Level", 
                ["INFO", "ANALYSIS", "WARN", "ERROR"], 
                default=["INFO", "ANALYSIS", "WARN", "ERROR"],
                label_visibility="collapsed",
                placeholder="Filter by Level"
            )
        with c2:
            search_query = st.text_input(
                "Search Logs", 
                placeholder="Search logs (e.g., BPv7-016)...", 
                label_visibility="collapsed"
            )
        
        # Fetch Logs (Increased limit for filtering)
        logs = get_system_logs(limit=200)
        
        # Apply Filters
        filtered_logs = []
        for log in logs:
            # Level Filter
            if log['level'] not in selected_levels:
                continue
            
            # Search Filter
            if search_query and search_query.lower() not in log['message'].lower():
                continue
                
            filtered_logs.append(log)
            
        with c3:
            # Export Logic
            csv_data = "Timestamp,Level,Message\n" + "\n".join([f"{l['timestamp']},{l['level']},{l['message']}" for l in filtered_logs])
            st.download_button(
                "📥 Export CSV", 
                data=csv_data, 
                file_name="audit_log.csv", 
                mime="text/csv", 
                use_container_width=True
            )

        # --- Scrolling Log Container ---
        # Fixed height to maximize vertical space (approx 70vh or 600px)
        log_container = st.container(height=750, border=True)
        with log_container:
            if not filtered_logs:
                st.caption("No logs match your filters.")
            
            # Helper for Sanitization
            def sanitize_log(msg):
                if "429" in msg and "quota" in msg.lower():
                    return "⚠️ API Rate Limit Exceeded - Retrying (Auto-Throttle active)"
                if "googleapis.com" in msg:
                    return "🔄 API Connectivity Handshake"
                return msg

            for log in filtered_logs:
                # 1. Sanitize
                clean_msg = sanitize_log(log['message'])
                
                # 2. Color Logic
                level_color = "#88C0D0" # Default/Info (Cyan)
                if "ANALYSIS" in log['level']: level_color = "#A3BE8C" # Green
                if "WARN" in log['level']: level_color = "#EBCB8B" # Yellow
                if "ERROR" in log['level'] or "FAIL" in log['message']: level_color = "#BF616A" # Red
                
                # 3. Render with Grid
                st.markdown(f"""
                    <div style="display: flex; border-bottom: 1px solid #3B4252; padding: 4px 0; font-family: 'Roboto Mono', monospace; font-size: 12px;">
                        <div style="min-width: 160px; color: #6F7995;">{log['timestamp']}</div>
                        <div style="min-width: 90px; font-weight: bold; color: {level_color};">[{log['level']}]</div>
                        <div style="color: #ECEFF4; word-wrap: break-word; flex: 1;">{clean_msg}</div>
                    </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.subheader("Verification Plan Analysis")
        
        # --- Dashboard Guide ---
        with st.expander("📊 How to interpret this report", expanded=False):
            st.markdown("""
            **Strategic Insight:**
            * **Planning Progress:** Shows the % of requirements that have been analyzed by the AI.
            * **Tests Identified:** These are requirements that require **executable Python code**. This drives the development schedule.
            * **Risk Profile:** The Stacked Bar Chart shows which verification methods have the highest concentration of **Critical/High** priority items.
            """)
        
        # Calculate Metrics
        df = st.session_state['requirements']
        total = len(df)
        
        # Status Counts
        analyzed = len(df[df['Status'] == 'Analyzed'])
        pending = len(df[df['Status'] == 'Pending'])
        
        # Method Counts
        if 'Verification Method' in df.columns:
            method_counts = df['Verification Method'].value_counts()
            test_count = method_counts.get('Test', 0)
            analysis_count = method_counts.get('Analysis', 0)
            inspection_count = method_counts.get('Inspection', 0)
            demo_count = method_counts.get('Demonstration', 0)
        else:
            test_count = 0
            analysis_count = 0
            inspection_count = 0
            demo_count = 0
            
        planning_progress = analyzed / total if total > 0 else 0
        non_code_methods = analysis_count + inspection_count
        
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Planning Progress", f"{planning_progress:.0%}", help="Percentage of requirements with a Verification Plan")
        col2.metric("Tests Identified", test_count, help="Requirements classified as 'Test' (T). These require automated script generation.")
        col3.metric("Non-Code Verification", non_code_methods, help="Number of requirements verified by non-code methods (Inspection/Analysis).")
        
        st.divider()
        
        # Charts Row
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### Coverage Status")
            # Donut Chart (Gauge Style)
            if total > 0:
                import plotly.graph_objects as go
                
                fig_status = go.Figure(data=[go.Pie(
                    labels=['Analyzed', 'Pending'],
                    values=[analyzed, pending],
                    hole=.7,
                    marker=dict(colors=['#88C0D0', '#4C566A']), # Nord Cyan, Nord Grey
                    textinfo='none', # Hide labels on chart
                    hoverinfo='label+value+percent'
                )])
                
                fig_status.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0), 
                    height=300,
                    showlegend=False,
                    annotations=[dict(text=f"{planning_progress:.0%}", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="#ECEFF4")]
                )
                st.plotly_chart(fig_status, use_container_width=True)
                
        with c2:
            st.markdown("#### Test Complexity & Risk")
            # Stacked Bar Chart (Method x Priority)
            if analyzed > 0 and 'Verification Method' in df.columns and 'Priority' in df.columns:
                import plotly.express as px
                
                # Prepare Data for Plotly Express
                counts_df = df.groupby(['Verification Method', 'Priority']).size().reset_index(name='Count')
                
                fig_bar = px.bar(
                    counts_df, 
                    x="Verification Method", 
                    y="Count", 
                    color="Priority", 
                    color_discrete_map={
                        "Critical": "#BF616A", # Nord Red
                        "High": "#D08770",     # Nord Orange
                        "Medium": "#EBCB8B",   # Nord Yellow
                        "Low": "#81A1C1"       # Nord Blue
                    }
                )
                
                fig_bar.update_layout(
                    margin=dict(t=30, b=0, l=0, r=0), 
                    height=300,
                    xaxis_title="Verification Method",
                    yaxis_title="Count",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text='')
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Run verification to see risk analysis.")

        # --- Export Report ---
        st.divider()
        c_ex1, c_ex2, c_ex3 = st.columns([6, 2, 2])
        with c_ex3:
            csv_report = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export VCRM (.csv)",
                data=csv_report,
                file_name=f"VCRM_Report_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    # --- Sidebar Footer ---
    with st.sidebar:
        # --- System Administration ---
        with st.expander("⚙️ System Administration"):
            st.warning("These actions are irreversible.")
            if st.button("⚠️ Reset Database", type="primary", use_container_width=True):
                clear_database()
                st.session_state['requirements'] = pd.DataFrame(columns=["ID", "Requirement Name", "Requirement", "Status", "Priority", "Source"])
                st.session_state['selected_req_id'] = None
                st.toast("Database cleared successfully.", icon="🗑️")
                time.sleep(1) # Give time for toast
                st.rerun()

 
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #4C566A; font-size: 10px; margin-top: 20px;">
                🟢 System Online | 🧠 Gemini 1.5 Flash | v1.1.0
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Main Dispatch ---
with st.sidebar:
    page = st.radio("Navigation", ["🚀 Mission Control", "📚 Documentation"], label_visibility="collapsed", horizontal=True)

if page == "🚀 Mission Control":
    render_mission_control()
else:
    render_documentation()
