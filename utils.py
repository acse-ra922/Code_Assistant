import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import time
from datetime import datetime, timedelta

def apply_custom_css():
    """Apply custom CSS to the Streamlit app"""
    with open("custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def create_performance_chart(history_metrics):
    """
    Create a performance chart based on historical metrics
    
    Args:
        history_metrics: List of metric dictionaries
        
    Returns:
        fig: Matplotlib figure
    """
    if not history_metrics:
        return None
    
    # Extract latency values and timestamps
    latencies = []
    timestamps = []
    
    for metrics in history_metrics:
        if "latency" in metrics:
            try:
                # Extract the numeric value from the latency string
                latency_value = float(metrics["latency"].split()[0])
                latencies.append(latency_value)
                
                # Use current time if timestamp not available
                timestamp = metrics.get("timestamp", datetime.now())
                timestamps.append(timestamp)
            except (ValueError, IndexError):
                pass
    
    if not latencies:
        return None
    
    # Create dataframe
    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Latency (s)": latencies
    })
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Timestamp"], df["Latency (s)"], marker='o', linestyle='-', linewidth=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Latency (seconds)")
    ax.set_title("Response Latency Over Time")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Tight layout to prevent clipping of labels
    fig.tight_layout()
    
    return fig

def log_activity(action, details=None):
    """
    Log user activity for tracking and debugging
    
    Args:
        action: String describing the action
        details: Optional dictionary with additional details
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []
    
    log_entry = {
        "timestamp": timestamp,
        "action": action
    }
    
    if details:
        log_entry.update(details)
    
    st.session_state.activity_log.append(log_entry)