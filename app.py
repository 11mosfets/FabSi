import streamlit as st
import pandas as pd
import sqlite3
import time
import altair as alt
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Fab18 Digital Twin",
    page_icon="🏭",
    layout="wide"
)

def get_data():
    try:
        db_path = 'backend_cache/local_data.db'
        if not os.path.exists(db_path):
            st.warning("Local cache not found. Please run `python backend_cache/update_sqlite_db.py` first.")
            return pd.DataFrame()
        
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM digital_twin_data;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            cols = ['yield_percentage', 'cvd_temp', 'target_temp', 'litho_focus', 'thickness', 'humidity']
            df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error reading from local cache: {e}")
        return pd.DataFrame()

st.title("🏭 Fab18 Live Digital Twin")
st.markdown(f"**Status:** System Online | **Last Update:** {time.strftime('%H:%M:%S UTC')}")
st.divider()

df = get_data()

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    current_yield = df['yield_percentage'].iloc[0]
    avg_yield_7d = df['yield_percentage'].mean()
    
    with col1:
        st.metric("Latest Lot Yield", f"{current_yield:.2f}%", f"{current_yield - avg_yield_7d:.2f}%")
    with col2:
        st.metric("7-Day Average Yield", f"{avg_yield_7d:.2f}%")
    with col3:
        st.metric("Lots Processed (7d)", len(df))
    with col4:
        mean_thick = df['thickness'].mean()
        std_thick = df['thickness'].std()
        cpk = (105 - mean_thick) / (3 * std_thick) if std_thick > 0 else 0
        st.metric("Process Cpk (CVD)", f"{cpk:.2f}")

    st.divider()
    st.subheader("📈 Factory Yield Trend")
    
    yield_trend = df[['timestamp', 'yield_percentage']].sort_values('timestamp')
    
    st.area_chart(
        yield_trend.set_index('timestamp'),
        color="#29B5E8", 
        height=300
    )
    st.caption("Tracking the yield recovery after the simulated excursion events.")

    st.divider()

    st.subheader("📉 Process Control (SPC)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### CVD Temperature: Actual vs Ideal")
        
        base = alt.Chart(df).encode(x='timestamp')
        
        line_actual = base.mark_line(color='#FF4B4B').encode(
            y=alt.Y('cvd_temp', 
                    scale=alt.Scale(zero=False, padding=1),
                    title='Temperature (°C)')
        )
        
        line_target = base.mark_line(color='#2ECC71', strokeDash=[5,5]).encode(
            y='target_temp'
        )
        
        chart = (line_actual + line_target).interactive()
        st.altair_chart(chart, use_container_width=True)
        st.caption("Green: Ideal (600°C) | Red: Actual. (Y-Axis zoomed to show drift)")

    with c2:
        st.markdown("##### Environmental Impact on Litho")
        chart_data = df[['timestamp', 'litho_focus', 'humidity']].set_index('timestamp')
        st.line_chart(chart_data)
        st.caption("Blue: Litho Focus | Red: Humidity.")

    st.divider()
    st.subheader("🔍 Excursion Analysis")
    st.markdown("Yield vs Thickness (Humidity)")
    st.scatter_chart(df, x='thickness', y='yield_percentage', color='humidity', size=100)

else:
    st.warning("Waiting for data...")

if st.button('Refresh Data'):
    st.rerun()