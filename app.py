import streamlit as st
import time
from llm_service import analyze_code, get_available_models
import hashlib

if 'code_input_value' not in st.session_state:
    st.session_state.code_input_value = ""

# Initialize session state variables
if 'history' not in st.session_state:
    st.session_state.history = []

def cache_key(code):
    """Create a unique hash for the code to use as cache key"""
    return hashlib.md5(code.encode()).hexdigest()

def main():
    st.set_page_config(
        page_title="Code Analysis App",
        page_icon="💻",
        layout="wide"
    )
    
    st.title("💻 Code Analysis App")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        models = get_available_models()
        selected_model = st.selectbox("Select Model", models, index=0)
        
        st.subheader("Analysis History")
        if st.session_state.history:
            if st.button("Clear History"):
                st.session_state.history = []
                st.experimental_rerun()
        else:
            st.info("No analysis history yet")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Code Input")
        
        # Example button before text area
        if st.button("📝 Load Example", use_container_width=True):
            st.session_state.code_input_value = """def fibonacci(n):
        if n <= 0:
            return "Input must be positive"
        elif n == 1:
            return 0
        elif n == 2:
            return 1
        else:
            return fibonacci(n-1) + fibonacci(n-2)
            """
            st.rerun()
        
        # Text area that uses the session state value
        code_input = st.text_area("Enter your code snippet:", 
                                value=st.session_state.code_input_value,
                                height=300, 
                                placeholder="Paste your code here...")
        
        analyze_button = st.button("🔍 Analyze Code", type="primary", use_container_width=True)

    with col2:
        st.subheader("Analysis Result")
        if analyze_button:
            if code_input.strip():
                # Check cache first
                key = cache_key(code_input)
                cached_result = st.session_state.get(key)
                
                if cached_result:
                    analysis_result, metrics = cached_result
                    st.success("Retrieved from cache!")
                else:
                    # Start timing
                    start_time = time.time()
                    
                    # Show a progress bar
                    progress_bar = st.progress(0)
                    for i in range(100):
                        # Simulating progress
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    with st.spinner("Analyzing code..."):
                        try:
                            analysis_result, metrics = analyze_code(code_input, model=selected_model)
                            
                            # Calculate latency
                            latency = time.time() - start_time
                            metrics["latency"] = f"{latency:.2f} seconds"
                            
                            # Cache the result
                            st.session_state[key] = (analysis_result, metrics)
                            
                            # Add to history
                            st.session_state.history.append({
                                "code_snippet": code_input[:50] + "..." if len(code_input) > 50 else code_input,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "key": key
                            })
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            return
                
                # Display the result
                st.markdown(analysis_result)
                
                # Display metrics
                st.subheader("Performance Metrics")
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.metric("Latency", metrics.get("latency", "N/A"))
                    st.metric("Input Tokens", metrics.get("input_tokens", "N/A"))
                
                with metrics_col2:
                    st.metric("Output Tokens", metrics.get("output_tokens", "N/A"))
                    st.metric("Model", metrics.get("model", "N/A"))
            else:
                st.error("Please enter some code to analyze.")
    
    # Display history in sidebar
    with st.sidebar:
        for i, item in enumerate(reversed(st.session_state.history)):
            if st.button(f"{item['timestamp']} - {item['code_snippet']}", key=f"history_{i}"):
                cached_result = st.session_state.get(item['key'])
                if cached_result:
                    with col2:
                        st.markdown(cached_result[0])
                        
                        # Display metrics
                        st.subheader("Performance Metrics")
                        metrics = cached_result[1]
                        metrics_col1, metrics_col2 = st.columns(2)
                        
                        with metrics_col1:
                            st.metric("Latency", metrics.get("latency", "N/A"))
                            st.metric("Input Tokens", metrics.get("input_tokens", "N/A"))
                        
                        with metrics_col2:
                            st.metric("Output Tokens", metrics.get("output_tokens", "N/A"))
                            st.metric("Model", metrics.get("model", "N/A"))
    
    # Footer
    st.markdown("---")
    st.markdown("This app uses local LLMs to analyze code snippets. No data is sent to external servers.")

if __name__ == "__main__":
    main()