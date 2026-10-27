import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# ==========================================
# PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="HotelPulse AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0B132B !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #060913 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #FFFFFF; }
    div.stButton > button:first-child {
        background-color: #0066FF !important; color: #FFFFFF !important;
        border: 1px solid #0066FF !important; border-radius: 4px !important;
        font-weight: 600 !important; transition: all 0.3s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #00E5FF !important; border-color: #00E5FF !important;
        color: #0B132B !important; box-shadow: 0 0 12px rgba(0, 229, 255, 0.6) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #151e32 !important; color: white !important; border-color: #2d3748 !important;
    }
    .block-container { padding-top: 2rem; padding-bottom: 2.5rem; }
    
    .ai-summary-box { background: linear-gradient(135deg, #1E293B, #0F172A); border-left: 4px solid #00E5FF; padding: 20px; border-radius: 6px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .ai-summary-title { font-size: 0.9rem; font-weight: 700; color: #00E5FF; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .ai-summary-text { font-size: 1.1rem; line-height: 1.5; color: #F8FAFC; }

    .kpi-card { background-color: #151E32; border: 1px solid #2D3748; border-radius: 8px; padding: 16px 20px; height: 125px; display: flex; flex-direction: column; justify-content: space-between; }
    .kpi-card-alert { background-color: #1A1118; border: 1px solid #4A1525; border-left: 6px solid #E11D48; border-radius: 8px; padding: 16px 20px; height: 125px; display: flex; flex-direction: column; justify-content: space-between; }
    .kpi-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #94A3B8; }
    .kpi-value { font-size: 1.7rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; }
    .kpi-subtext-positive { font-size: 0.8rem; font-weight: 600; color: #10B981; }
    .kpi-subtext-neutral { font-size: 0.8rem; font-weight: 500; color: #94A3B8; }
    .kpi-alert-value { font-size: 1.0rem; font-weight: 700; color: #F43F5E; line-height: 1.3; }
    .kpi-alert-subtext { font-size: 0.78rem; font-weight: 500; color: #FDA4AF; }

    .action-card { background-color: #151E32; border-radius: 8px; padding: 18px 20px; margin-bottom: 12px; border: 1px solid #2D3748; }
    .action-high { border-left: 6px solid #EF4444; }
    .action-medium { border-left: 6px solid #F59E0B; }
    .action-low { border-left: 6px solid #10B981; }
    .action-addressed { border-left: 6px solid #475569; opacity: 0.6; }

    .badge { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-right: 8px; }
    .badge-high { background-color: #451a1a; color: #fca5a5; }
    .badge-medium { background-color: #452a0a; color: #fcd34d; }
    .badge-low { background-color: #064e3b; color: #6ee7b7; }
    .badge-dept { background-color: #172554; color: #93c5fd; border: 1px solid #1e3a8a; }
    
    .action-headline { font-size: 1.05rem; font-weight: 600; color: #F8FAFC; margin: 10px 0 6px 0; }
    .action-meta { font-size: 0.85rem; color: #CBD5E1; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# METADATA & SESSION STATE
# ==========================================
HOTELS_METADATA = pd.DataFrame([
    {"name": "Ritz Paris", "brand": "Independent", "group": "Palace", "stars": 5},
    {"name": "Le Bristol Paris", "brand": "Oetker Collection", "group": "Palace", "stars": 5},
    {"name": "Four Seasons Hotel George V", "brand": "Four Seasons", "group": "Luxury", "stars": 5},
    {"name": "Shangri-La Paris", "brand": "Shangri-La", "group": "Luxury", "stars": 5},
    {"name": "The Peninsula Paris", "brand": "The Peninsula", "group": "Palace", "stars": 5},
    {"name": "Hôtel Lutetia", "brand": "The Set Collection", "group": "Palace", "stars": 5},
    {"name": "citizenM Paris Gare de Lyon", "brand": "citizenM", "group": "Lifestyle", "stars": 4},
    {"name": "Hôtel des Grands Boulevards", "brand": "Experimental Group", "group": "Boutique", "stars": 4},
    {"name": "Meliá Paris La Défense", "brand": "Meliá", "group": "Premium", "stars": 4},
    {"name": "Hôtel Britannique", "brand": "Independent", "group": "Midscale", "stars": 3},
    {"name": "Hôtel de la Porte Dorée", "brand": "Independent", "group": "Midscale", "stars": 3},
    {"name": "Le Royal Monceau - Raffles Paris", "brand": "Raffles", "group": "Accor Luxury", "stars": 5},
    {"name": "Sofitel Paris Le Faubourg", "brand": "Sofitel", "group": "Accor Luxury", "stars": 5},
    {"name": "Pullman Paris Tour Eiffel", "brand": "Pullman", "group": "Accor Premium", "stars": 4},
    {"name": "Hotel Novotel Paris les Halles", "brand": "Novotel", "group": "Accor Midscale", "stars": 4},
    {"name": "Mercure Paris Montmartre Sacre-Coeur", "brand": "Mercure", "group": "Accor Midscale", "stars": 4},
    {"name": "ibis Paris Bastille Opera", "brand": "ibis", "group": "Accor Economy", "stars": 3},
])

if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = "Ritz Paris"

if "action_states" not in st.session_state:
    st.session_state.action_states = {}

# ==========================================
# AI LOGIC & REALISTIC DATA GENERATION
# ==========================================
def generate_ai_summary(hotel_name: str, df: pd.DataFrame) -> str:
    """Simulates an LLM summarizing the filtered dataset."""
    if df.empty:
        return f"Insufficient review data to generate an AI summary for {hotel_name} within this time frame."
    
    avg_score = df["Rating"].mean()
    total_reviews = len(df)
    
    negative_df = df[df["Sentiment"] == "Negative"]
    if not negative_df.empty:
        top_complaint = negative_df["Department"].mode()[0]
        complaint_aspect = negative_df[negative_df["Department"] == top_complaint]["Extracted Aspect"].mode()[0]
        bottleneck_text = f"However, {top_complaint} ({complaint_aspect.lower()}) remains a critical bottleneck requiring immediate operational attention."
    else:
        bottleneck_text = "Operations are running flawlessly with minimal negative sentiment detected across all core departments."

    trend_text = "trending positively" if avg_score >= 4.0 else ("stabilizing" if avg_score >= 3.0 else "facing severe challenges")
    
    return f"Based on {total_reviews} recent reviews, overall guest satisfaction at {hotel_name} is {trend_text} with a score of {avg_score:.2f}/5.0. {bottleneck_text}"

@st.cache_data
def generate_synthetic_review_dataset(hotel_name: str, count: int = 150):
    """Generates realistic synthetic review text for the multilingual feed."""
    np.random.seed(abs(hash(hotel_name)) % (2**32))
    today = datetime(2026, 10, 27)
    platforms = ["Google Reviews", "TripAdvisor", "Booking.com"]
    languages = ["English", "French", "German", "Spanish"]
    
    dept_aspects = {
        "Front Desk": ["Check-in Speed", "Staff Politeness", "Arrival Flow"],
        "Housekeeping": ["Room Cleanliness", "Bedding Comfort", "Bathroom Space"],
        "Maintenance": ["Wi-Fi Speed", "Air Conditioning", "Elevator Delay"],
        "F&B": ["Breakfast Variety", "Coffee Quality", "Room Service Speed"],
    }

    # Realistic sentence templates based on sentiment
    review_templates = {
        "Positive": [
            "Absolutely outstanding experience. The {aspect} was flawless.",
            "We were very impressed by the {aspect} during our stay in Paris.",
            "Five stars! The {aspect} really exceeded our expectations.",
            "Wonderful hotel. I specifically want to praise the {aspect}.",
            "Great location and the {aspect} was perfectly managed."
        ],
        "Neutral": [
            "The stay was decent, but the {aspect} was just average.",
            "Okay experience overall. The {aspect} could be slightly improved.",
            "Nothing terrible, but the {aspect} didn't blow me away.",
            "A standard hotel experience. The {aspect} was fine."
        ],
        "Negative": [
            "Terrible experience regarding the {aspect}. Needs immediate fixing.",
            "I was very disappointed with the {aspect}. Would not return.",
            "Completely unacceptable {aspect}. Management needs to step up.",
            "Ruined our trip to Paris. The {aspect} was a disaster.",
            "Very frustrating {aspect}. Not worth the price we paid."
        ]
    }

    records = []
    for _ in range(count):
        review_date = (today - timedelta(days=int(np.random.randint(0, 300)))).date()
        dept = np.random.choice(list(dept_aspects.keys()))
        aspect = np.random.choice(dept_aspects[dept])
        platform = np.random.choice(platforms)
        lang = np.random.choice(languages, p=[0.45, 0.35, 0.10, 0.10])
        
        rating_val = np.random.choice([5, 4, 3, 2, 1], p=[0.45, 0.25, 0.15, 0.10, 0.05])
        sentiment = "Positive" if rating_val >= 4 else ("Neutral" if rating_val == 3 else "Negative")
        
        # Select a realistic sentence and format it
        template = np.random.choice(review_templates[sentiment])
        review_text = template.format(aspect=aspect.lower())

        records.append({
            "Date": review_date, 
            "Platform": platform, 
            "Original Language": lang,
            "Original Text": f"[{lang} original text simulated]", # Placeholder for foreign text
            "Auto-Translated English Text": review_text,
            "Extracted Aspect": aspect, 
            "Sentiment": sentiment, 
            "Rating": rating_val, 
            "Department": dept,
        })
    return pd.DataFrame(records)

def get_hotel_actions(hotel_name: str, filtered_df: pd.DataFrame):
    np.random.seed(abs(hash(hotel_name)) % (2**32))
    lang_counts = filtered_df["Original Language"].value_counts().to_dict()
    en_cnt = lang_counts.get("English", 8)
    
    action_pool = [
        ("Front Desk", "Alexandre D.", "Queue Management", "Deploy mobile check-in ambassadors during peak arrival times."),
        ("F&B", "Chef Jerome", "Dining Variety", "Overhaul the late-night room service menu to include more hot options."),
        ("Housekeeping", "Marie-Therese", "Room Comfort", "Perform a full audit of premium bedding replacements on high floors."),
        ("Maintenance", "David Dubois", "Facility Upkeep", "Schedule immediate preventative maintenance for in-room HVAC sensors."),
        ("Guest Relations", "Sophie M.", "VIP Welcome", "Upgrade welcome amenities for returning elite loyalty members.")
    ]
    
    chosen_indices = np.random.choice(len(action_pool), 3, replace=False)
    priorities = [("High Priority", "high", 0.25), ("Medium Priority", "medium", 0.14), ("Low Priority", "low", 0.05)]
    
    actions = []
    for i in range(3):
        dept, head, root, rec = action_pool[chosen_indices[i]]
        pri_label, pri_level, lift = priorities[i]
        actions.append({
            "id": f"card_{i+1}", "priority": pri_label, "priority_level": pri_level, "department": dept,
            "dept_head": head, "recommendation": f"[{hotel_name}] {rec}",
            "impact": f"Estimated +{lift} overall lift | Root Aspect: {root}",
            "languages_affected": f"English ({en_cnt-i})",
        })
    return actions

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("## HotelPulse AI")
    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)
    
    st.markdown("### Property Filters")
    selected_stars = st.multiselect("Filter by Star Rating", options=[3, 4, 5], default=[3, 4, 5], format_func=lambda x: f"{x} Stars")
    available_brands = sorted(HOTELS_METADATA["brand"].unique().tolist())
    selected_brands = st.multiselect("Filter by Brand", options=available_brands, default=available_brands)

    filtered_hotels_df = HOTELS_METADATA[(HOTELS_METADATA["stars"].isin(selected_stars)) & (HOTELS_METADATA["brand"].isin(selected_brands))]

    if filtered_hotels_df.empty:
        st.error("No properties match your filters.")
        st.stop()

    hotel_names_list = filtered_hotels_df["name"].tolist()
    if st.session_state.selected_hotel not in hotel_names_list:
        st.session_state.selected_hotel = hotel_names_list[0]

    st.selectbox("Select Property Details", options=hotel_names_list, key="selected_hotel")
    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)
    
    st.markdown("### Data Filters")
    selected_platforms = st.multiselect("Review Platforms", options=["Google Reviews", "TripAdvisor", "Booking.com"], default=["Google Reviews", "TripAdvisor", "Booking.com"])

    selected_date_range = st.selectbox("Date Range Window", options=["Last 30 Days", "Q3 2026", "Full Year 2026", "Custom Date Range"], index=0)

    today = datetime(2026, 10, 27).date()
    if selected_date_range == "Last 30 Days":
        start_date, end_date = today - timedelta(days=30), today
    elif selected_date_range == "Q3 2026":
        start_date, end_date = datetime(2026, 7, 1).date(), datetime(2026, 9, 30).date()
    elif selected_date_range == "Full Year 2026":
        start_date, end_date = datetime(2026, 1, 1).date(), today
    else:
        custom_dates = st.date_input("Select Custom Date Range", value=(today - timedelta(days=7), today))
        start_date, end_date = custom_dates if len(custom_dates) == 2 else (custom_dates[0], custom_dates[0])

# ==========================================
# DATA PROCESSING
# ==========================================
selected_hotel = st.session_state.selected_hotel

if selected_hotel not in st.session_state.action_states:
    st.session_state.action_states[selected_hotel] = {
        "card_1": {"status": "Open", "assigned_to": None},
        "card_2": {"status": "Open", "assigned_to": None},
        "card_3": {"status": "Open", "assigned_to": None},
    }

raw_df = generate_synthetic_review_dataset(selected_hotel)

filtered_df = raw_df[
    (raw_df["Date"] >= start_date) & 
    (raw_df["Date"] <= end_date) &
    (raw_df["Platform"].isin(selected_platforms))
]

total_reviews = len(filtered_df)
avg_score = filtered_df["Rating"].mean() if total_reviews > 0 else 0.0
neg_alerts = len(filtered_df[filtered_df["Sentiment"] == "Negative"])
actions = get_hotel_actions(selected_hotel, filtered_df)

# ==========================================
# MAIN LAYOUT
# ==========================================
st.title("HotelPulse AI: Operations & Sentiment Engine")
st.markdown(f"<span style='color:#94A3B8;'>Selected Property:</span> <strong>{selected_hotel}</strong> &nbsp;|&nbsp; <span style='color:#94A3B8;'>Window:</span> <strong>{start_date} to {end_date}</strong>", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ------------------------------------------
# EXECUTIVE AI SUMMARY
# ------------------------------------------
ai_summary_text = generate_ai_summary(selected_hotel, filtered_df)
st.markdown(
    f"""
    <div class="ai-summary-box">
        <div class="ai-summary-title">✨ Executive AI Summary</div>
        <div class="ai-summary-text">{ai_summary_text}</div>
    </div>
    """, 
    unsafe_allow_html=True
)

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Satisfaction Score</div><div class="kpi-value">{avg_score:.2f} / 5.0</div><div class="kpi-subtext-positive">Trend Positive</div></div>', unsafe_allow_html=True)
with kpi_col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Review Volume</div><div class="kpi-value">{total_reviews}</div><div class="kpi-subtext-neutral">Total captured records</div></div>', unsafe_allow_html=True)
with kpi_col3:
    st.markdown(f'<div class="kpi-card-alert"><div class="kpi-title" style="color: #FDA4AF;">Urgent Alerts</div><div class="kpi-alert-value">{neg_alerts} Negative Mentions</div><div class="kpi-alert-subtext">Action Required</div></div>', unsafe_allow_html=True)
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Action Matrix", "Department Ratings", "🌍 Multilingual Feed"])

with tab1:
    st.subheader("Priority Actions")
    hotel_states = st.session_state.action_states[selected_hotel]
    
    for idx, item in enumerate(actions):
        card_id = item["id"]
        current_state = hotel_states[card_id]["status"]
        assigned_person = hotel_states[card_id]["assigned_to"]
        
        border_class = "action-addressed" if current_state == "Addressed" else f"action-{item['priority_level']}"
        status_text = "Completed" if current_state == "Addressed" else ("Assigned" if assigned_person else "Open")

        st.markdown(
            f"""
            <div class="action-card {border_class}">
                <div>
                    <span class="badge badge-{item['priority_level']}">{item["priority"]}</span>
                    <span class="badge badge-dept">{item["department"]}</span>
                    <span style="font-size: 0.8rem; color: #94A3B8; float: right;">Status: {status_text}</span>
                </div>
                <div class="action-headline">Action {idx + 1}: {item["recommendation"]}</div>
                <div class="action-meta">
                    <strong>Impact:</strong> {item["impact"]} <br/>
                    <strong>Languages Affected:</strong> {item["languages_affected"]}
                </div>
            </div>
            """, unsafe_allow_html=True
        )

        btn_col1, btn_col2, _ = st.columns([2, 2, 8])
        with btn_col1:
            is_done = current_state == "Addressed"
            if st.button("Revert Status" if is_done else "Mark Addressed", key=f"btn_done_{selected_hotel}_{card_id}", use_container_width=True):
                st.session_state.action_states[selected_hotel][card_id]["status"] = "Open" if is_done else "Addressed"
                st.rerun()
        with btn_col2:
            if st.button("Assign Lead", key=f"btn_assign_{selected_hotel}_{card_id}", use_container_width=True, disabled=is_done):
                st.session_state.action_states[selected_hotel][card_id]["assigned_to"] = item["dept_head"]
                st.rerun()
        st.markdown("<hr style='border-color: #1E293B;'>", unsafe_allow_html=True)

with tab2:
    st.subheader("Departmental Aspect Scores")
    if total_reviews > 0:
        aspect_df = filtered_df.groupby("Extracted Aspect")["Rating"].mean().reset_index()
        aspect_df.columns = ["Extracted Aspect", "Score"]
        aspect_df = aspect_df.sort_values(by="Score", ascending=True)

        fig_aspects = px.bar(
            aspect_df, x="Score", y="Extracted Aspect", orientation="h", text=aspect_df["Score"].round(2),
            color="Score", color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            title="Computed Aspect Ratings (1-5 Scale)"
        )
        fig_aspects.update_layout(
            xaxis=dict(range=[0, 5.5]), height=450, margin=dict(l=10, r=10, t=35, b=10),
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_aspects, use_container_width=True)
    else:
        st.info("No reviews available in this date range or platform selection.")

with tab3:
    st.subheader("Live Customer Review Stream (Auto-Translated)")
    st.caption("AI detects the native language and automatically standardizes text to English for centralized analysis.")
    if total_reviews > 0:
        feed_cols = ["Date", "Platform", "Original Language", "Auto-Translated English Text", "Extracted Aspect", "Sentiment", "Rating"]
        st.dataframe(
            filtered_df[feed_cols], use_container_width=True, hide_index=True, height=600,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Sentiment": st.column_config.TextColumn("Sentiment", help="AI-derived sentiment")
            }
        )
    else:
        st.info("No reviews available in this date range or platform selection.")