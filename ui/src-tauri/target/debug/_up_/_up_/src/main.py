import streamlit as st
from pydeck.bindings.map_styles import styles
from functions.processes import process_prompt, copy_to_clipboard, check_api
from dotenv import load_dotenv
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_full_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# Usage
logo_path = "https://raw.githubusercontent.com/devdattatalele/Krya.ai/dd43de46ca6e19e7dfcae0a3eff27d889d984531/assests/krya_logo.svg"
styles_path=get_full_path("UI/style.css")

# Streamlit UI Design
st.set_page_config(page_icon=logo_path,page_title="Krya.ai Automation Console", layout="wide",initial_sidebar_state="expanded")

# Custom CSS for modern look and adjustments
with open(styles_path, 'r') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []
if 'last_execution_result' not in st.session_state:
    st.session_state.last_execution_result = ""

# Sidebar with improved styling
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: 0; align-items: center; height: 15vh; flex-direction: column;">
            <div style="display: flex; align-items: center;">
                <img src="{logo_path}" alt="Logo" style="width: 60px; margin-right: 20px;">
                <h1 style="color: #007acc; font-family:comic sans ms ; font-size: 3rem; margin: 0;">
                      Krya.AI
                </h1></div></div>
        """,
        unsafe_allow_html=True,
    )
    
    # API Key Section
    google_api_key = st.text_input(
        "Enter your Gemini API key:",
        value=st.session_state.get('GOOGLE_API_KEY', ''),
        type="password",
        help="You can find your Gemini API key on the [Gemini API](https://aistudio.google.com/apikey).",
    )
    if google_api_key:
        st.session_state['openai_api_key'] = google_api_key
        with open(".env", "w") as f:
            f.write(f"GOOGLE_API_KEY={google_api_key}")
        st.success("✅ Google API Key saved")

    # Execution Settings
    st.markdown("### ⚙️ Execution Settings")
    max_retries = st.slider("Max Retry Attempts", min_value=1, max_value=5, value=3, 
                           help="Number of times to retry code generation if execution fails")
    
    execution_timeout = st.slider("Execution Timeout (seconds)", min_value=10, max_value=120, value=30,
                                 help="Maximum time to wait for script execution")

    # Status Indicator
    if check_api():
        st.success("🟢 API Status: Connected")
    else:
        st.error("🔴 API Status: Not Connected")

    st.markdown("### 💡 Sample Prompts")
    st.markdown("<div class='sample-prompts'>", unsafe_allow_html=True)
    
    sample_prompts = [
        "Generate a portfolio website in VS Code",
        "Compare Phones Under 20k on different E-commerce websites", 
        "Type Gmail letter to HR about Leave",
        "Create a simple calculator in PyCharm",
        "Open YouTube and search for Python tutorials"
    ]
    
    for prompt in sample_prompts:
        if st.button(f"📝 {prompt[:30]}...", key=f"sample_{hash(prompt)}"):
            st.session_state['selected_prompt'] = prompt

    st.markdown("</div>", unsafe_allow_html=True)

    # Execution History
    if st.session_state.execution_history:
        st.markdown("### 📊 Recent Executions")
        for i, (prompt, status) in enumerate(st.session_state.execution_history[-3:]):
            status_icon = "✅" if "successful" in status.lower() else "❌"
            st.text(f"{status_icon} {prompt[:30]}...")

    # Social Links
    st.markdown("---")
    st.markdown("       Developed by Devdatta Talele")

    st.markdown("""
        <div class="social-links">
            <a href="https://github.com/devdattatalele/krya.ai" target="_blank" class="social-link">
                <i class="fab fa-github"></i> GitHub
            </a><a href="https://linkedin.com/in/devdatta-talele" target="_blank" class="social-link">
                <i class="fab fa-linkedin"></i> LinkedIn
        </a></div>
    """, unsafe_allow_html=True)

# Main Content Centered
st.markdown("""
    <div class="main-container">
    <h1 style="font-size: 3rem; margin: 0;"> Krya.AI </h1>
    """, unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; font-weight:bold; font-family:comic sans ms; padding-top: 0rem;'> \
            Automated interactions and code execution on local machine </h3>", unsafe_allow_html=True)

# Enhanced input section
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Enter your prompt:", 
        placeholder="e.g., Generate a portfolio website in VS Code",
        value=st.session_state.get('selected_prompt', ''),
        key="main_input"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    execute_button = st.button("🚀 Execute", type="primary", use_container_width=True)

# Clear selected prompt after use
if 'selected_prompt' in st.session_state and st.session_state.selected_prompt:
    st.session_state.selected_prompt = ""

# Execution Section
if execute_button:
    load_dotenv()
    if check_api():
        if user_input:
            # Create placeholder for dynamic updates
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            try:
                with st.spinner("🔄 Processing your request..."):
                    progress_bar.progress(25)
                    try:
                        # Try with max_retries parameter (new version)
                        code, execution_status = process_prompt(user_input, max_retries=max_retries)
                    except TypeError as e:
                        if "unexpected keyword argument 'max_retries'" in str(e):
                            # Fallback to old version without max_retries
                            st.warning("⚠️ Using legacy mode - some features may be limited")
                            code, execution_status = process_prompt(user_input)
                        else:
                            raise e
                    progress_bar.progress(100)
                
                # Store in history
                st.session_state.execution_history.append((user_input, execution_status))
                
                # Display results
                st.markdown("""<style> .stTextArea {margin-top: -25px;}</style>""", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📝 Generated Code")
                    if code:
                        st.code(code, language="python")
                        copy_to_clipboard(code, "copy_code")
                    else:
                        st.error("❌ No code was generated")
                
                with col2:
                    st.subheader("📊 Execution Status")
                    
                    # Color-code the execution status
                    if "✅" in execution_status or "successful" in execution_status.lower():
                        st.success("Execution completed successfully!")
                    elif "❌" in execution_status or "error" in execution_status.lower():
                        st.error("Execution encountered errors")
                    elif "⚠️" in execution_status:
                        st.warning("Execution completed with warnings")
                    else:
                        st.info("Execution status:")
                    
                    st.text_area("", execution_status, height=300, key="execution_status")
                    copy_to_clipboard(execution_status, "copy_status")
                
                # Additional controls
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Retry with Same Prompt"):
                        st.rerun()
                
                with col2:
                    if st.button("🛠️ Modify and Retry"):
                        st.session_state['selected_prompt'] = user_input
                        st.rerun()
                
                with col3:
                    if st.button("📋 View Generated File"):
                        try:
                            script_path = os.path.join(os.getcwd(), "generated_output", "generated_output.py")
                            if os.path.exists(script_path):
                                with open(script_path, 'r') as f:
                                    file_content = f.read()
                                st.code(file_content, language="python")
                            else:
                                st.warning("Generated file not found")
                        except Exception as e:
                            st.error(f"Error reading file: {e}")
                            
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
                st.info("💡 Try refreshing the page or checking your API key")
        else:
            st.warning("⚠️ Please enter a prompt before executing")
    else:
        st.error("❌ API not found. Please enter your API key in the sidebar")
        st.stop()

st.markdown("</div>", unsafe_allow_html=True)

# Footer with system info
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔄 Total Executions", len(st.session_state.execution_history))

with col2:
    successful_executions = sum(1 for _, status in st.session_state.execution_history 
                               if "successful" in status.lower() or "✅" in status)
    st.metric("✅ Successful", successful_executions)

with col3:
    if st.session_state.execution_history:
        success_rate = (successful_executions / len(st.session_state.execution_history)) * 100
        st.metric("📈 Success Rate", f"{success_rate:.1f}%")