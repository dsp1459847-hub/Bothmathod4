import streamlit as st
import pandas as pd
from collections import Counter
import numpy as np
from datetime import timedelta

# Page Setup
st.set_page_config(page_title="Shift-Wise Prediction AI", layout="wide")

st.title("🎯 Shift-Wise Winner & Loser Predictor")
st.write("प्रत्येक शिफ्ट (DS, FD, GD...) के लिए अलग नंबर और सटीक तारीख का विश्लेषण।")

# 1. Master Patterns
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

# 2. Sidebar Settings
uploaded_file = st.sidebar.file_uploader("Data File (CSV/Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE']).dt.date
    for col in shifts:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

    # Date Handling
    available_dates = df['DATE'].dropna().unique()
    selected_date = st.sidebar.selectbox("किस तारीख के रिजल्ट से प्रेडिक्शन चाहिए?", options=reversed(available_dates))
    base_idx = df[df['DATE'] == selected_date].index[0]
    
    tomorrow = selected_date + timedelta(days=1)

    # --- HEADER INFO ---
    st.info(f"📅 **आज के नंबर की तारीख:** {selected_date}")
    st.success(f"🎯 **यह नंबर इस तारीख को खेलें:** {tomorrow}")

    # --- CORE SCORING ENGINE ---
    # यहाँ हम पूरी शीट का एक जनरल स्कोर निकालते हैं (Trends के लिए)
    global_scores = np.zeros(100)
    today_nums = df.loc[base_idx, shifts].dropna().to_dict()
    
    for val in today_nums.values():
        for p in master_patterns:
            global_scores[int((val + p) % 100)] += 1

    # --- SHIFT-WISE ANALYSIS ---
    st.divider()
    st.header("🎰 शिफ्ट-वाइज़ प्रेडिक्शन (Shift-wise Numbers)")
    st.write("नीचे हर शिफ्ट के लिए सबसे मजबूत नंबर दिए गए हैं।")

    # Creating Columns for Shits
    tabs = st.tabs(shifts)

    for i, s_name in enumerate(shifts):
        with tabs[i]:
            s_val = today_nums.get(s_name)
            if s_val is not None:
                st.subheader(f"{s_name} स्पेशल (आज का नंबर: {int(s_val)})")
                
                # Calculate numbers specifically for this shift
                s_preds = []
                for p in master_patterns:
                    n = int((s_val + p) % 100)
                    # Score = Global Frequency + Pattern Match
                    s_preds.append({"Number": n, "Power": global_scores[n]})
                
                # Sort and filter
                s_df = pd.DataFrame(s_preds).sort_values("Power", ascending=False)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**✅ खेलने वाले नंबर (Top 5):**")
                    st.table(s_df.head(5))
                with col2:
                    st.write("**💡 लॉजिक:**")
                    st.write(f"ये नंबर सीधे {s_name} के आज के रिजल्ट ({int(s_val)}) पर आधारित हैं।")
            else:
                st.write("इस शिफ्ट का डेटा उपलब्ध नहीं है।")

    # --- LOSER LIST (60-70 NUMBERS) ---
    st.divider()
    st.header("❌ 60-70 'Not Coming' Numbers (Common for All)")
    st.error(f"इन नंबरों के {tomorrow} को आने की संभावना न के बराबर है:")
    
    losers = [n for n in range(100) if global_scores[n] <= 1]
    
    # Display in a clean grid
    loser_grid = [losers[i:i+10] for i in range(0, len(losers), 10)]
    for row in loser_grid:
        st.write(" | ".join(map(str, row)))

    # --- ACCURACY TEST ---
    if base_idx + 1 < len(df):
        st.divider()
        st.header("🧪 प्रेडिक्शन टेस्ट (Backtest)")
        actual = set(df.loc[base_idx + 1, shifts].dropna().values)
        st.write(f"अगले दिन ({tomorrow}) के असली नंबर आए थे: `{list(actual)}`")
        
        # Check overall hits
        all_top_preds = set([n for n in range(100) if global_scores[n] >= 3])
        hits = all_top_preds.intersection(actual)
        if hits:
            st.success(f"🎯 इस प्रेडिक्शन से {len(hits)} नंबर पास हुए: {list(hits)}")
        else:
            st.warning("इस दिन प्रेडिक्शन फेल रही।")

else:
    st.info("शुरू करने के लिए Sidebar में अपनी एक्सेल/CSV फाइल अपलोड करें।")
                  
