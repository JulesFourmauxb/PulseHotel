import zlib
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

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
    /* Dark Mode: Night Blue Background & White Text */
    .stApp { background-color: #0B132B !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #060913 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #FFFFFF; }

    /* Electric Blue Buttons */
    div.stButton > button:first-child {
        background-color: #0066FF !important; color: #FFFFFF !important;
        border: 1px solid #0066FF !important; border-radius: 4px !important;
        font-weight: 600 !important; transition: all 0.3s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #00E5FF !important; border-color: #00E5FF !important;
        color: #0B132B !important; box-shadow: 0 0 12px rgba(0, 229, 255, 0.6) !important;
    }

    /* Dark Mode Selectboxes & Multiselects */
    .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #151e32 !important; color: white !important; border-color: #2d3748 !important;
    }
    .block-container { padding-top: 2rem; padding-bottom: 2.5rem; }

    /* KPI Cards & AI Summary */
    .ai-summary-box {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-left: 4px solid #00E5FF;
        padding: 18px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .ai-summary-title { font-size: 0.85rem; font-weight: 700; color: #00E5FF; text-transform: uppercase; margin-bottom: 6px; }
    .ai-summary-text { font-size: 1.05rem; line-height: 1.5; color: #F8FAFC; }

    .kpi-card {
        background-color: #151E32; border: 1px solid #2D3748; border-radius: 8px;
        padding: 16px 20px; height: 125px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-card-alert {
        background-color: #1A1118; border: 1px solid #4A1525; border-left: 6px solid #E11D48;
        border-radius: 8px; padding: 16px 20px; height: 125px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #94A3B8; }
    .kpi-value { font-size: 1.7rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; }
    .kpi-subtext-positive { font-size: 0.8rem; font-weight: 600; color: #10B981; }
    .kpi-subtext-neutral { font-size: 0.8rem; font-weight: 500; color: #94A3B8; }
    .kpi-alert-value { font-size: 1.0rem; font-weight: 700; color: #F43F5E; line-height: 1.3; }
    .kpi-alert-subtext { font-size: 0.78rem; font-weight: 500; color: #FDA4AF; }

    /* Action Matrix Cards */
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
# ATOUT FRANCE HOTELS METADATA (27 PROPERTIES)
# ==========================================
HOTELS_METADATA = pd.DataFrame([
    # Luxury & Palaces (Non-Accor)
    {"name": "Ritz Paris", "brand": "Independent", "group": "Palace", "stars": 5, "lat": 48.8682, "lon": 2.3294},
    {"name": "Le Bristol Paris", "brand": "Oetker Collection", "group": "Palace", "stars": 5, "lat": 48.8718, "lon": 2.3146},
    {"name": "Four Seasons Hotel George V", "brand": "Four Seasons", "group": "Luxury", "stars": 5, "lat": 48.8688, "lon": 2.3008},
    {"name": "Shangri-La Paris", "brand": "Shangri-La", "group": "Luxury", "stars": 5, "lat": 48.8635, "lon": 2.2936},
    {"name": "The Peninsula Paris", "brand": "The Peninsula", "group": "Palace", "stars": 5, "lat": 48.8708, "lon": 2.2938},
    {"name": "Hôtel Lutetia", "brand": "The Set Collection", "group": "Palace", "stars": 5, "lat": 48.8512, "lon": 2.3283},
    {"name": "Hôtel de Crillon", "brand": "Rosewood", "group": "Palace", "stars": 5, "lat": 48.8672, "lon": 2.3214},
    {"name": "Mandarin Oriental Paris", "brand": "Mandarin Oriental", "group": "Luxury", "stars": 5, "lat": 48.8675, "lon": 2.3294},
    {"name": "Le Meurice", "brand": "Dorchester Collection", "group": "Palace", "stars": 5, "lat": 48.8648, "lon": 2.3288},
    {"name": "Plaza Athénée", "brand": "Dorchester Collection", "group": "Palace", "stars": 5, "lat": 48.8661, "lon": 2.3048},

    # Premium & Lifestyle (Non-Accor)
    {"name": "citizenM Paris Gare de Lyon", "brand": "citizenM", "group": "Lifestyle", "stars": 4, "lat": 48.8448, "lon": 2.3721},
    {"name": "Hôtel des Grands Boulevards", "brand": "Experimental Group", "group": "Boutique", "stars": 4, "lat": 48.8708, "lon": 2.3450},
    {"name": "Meliá Paris La Défense", "brand": "Meliá", "group": "Premium", "stars": 4, "lat": 48.8897, "lon": 2.2530},
    {"name": "Hôtel Rochechouart", "brand": "Orso Hotels", "group": "Boutique", "stars": 4, "lat": 48.8825, "lon": 2.3392},
    {"name": "Hôtel Les Bains Paris", "brand": "Independent", "group": "Boutique", "stars": 5, "lat": 48.8631, "lon": 2.3551},
    {"name": "Mama Shelter Paris East", "brand": "Mama Shelter", "group": "Lifestyle", "stars": 3, "lat": 48.8596, "lon": 2.4011},

    # Midscale & Economy (Non-Accor)
    {"name": "Hôtel Britannique", "brand": "Independent", "group": "Midscale", "stars": 3, "lat": 48.8582, "lon": 2.3455},
    {"name": "Hôtel de la Porte Dorée", "brand": "Independent", "group": "Midscale", "stars": 3, "lat": 48.8354, "lon": 2.4068},
    {"name": "Hôtel Jeanne d'Arc", "brand": "Independent", "group": "Midscale", "stars": 3, "lat": 48.8559, "lon": 2.3615},
    {"name": "Hôtel Caron de Beaumarchais", "brand": "Independent", "group": "Boutique", "stars": 3, "lat": 48.8568, "lon": 2.3571},

    # Accor Properties
    {"name": "Le Royal Monceau - Raffles Paris", "brand": "Raffles", "group": "Accor Luxury", "stars": 5, "lat": 48.8763, "lon": 2.3004},
    {"name": "Sofitel Paris Le Faubourg", "brand": "Sofitel", "group": "Accor Luxury", "stars": 5, "lat": 48.8687, "lon": 2.3218},
    {"name": "Pullman Paris Tour Eiffel", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8554, "lon": 2.2929},
    {"name": "Pullman Paris Montparnasse", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8396, "lon": 2.3228},
    {"name": "Hotel Novotel Paris les Halles", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8606, "lon": 2.3461},
    {"name": "Novotel Paris Centre Tour Eiffel", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8507, "lon": 2.2825},
    {"name": "Mercure Paris Montmartre Sacre-Coeur", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8858, "lon": 2.3312},
    {"name": "ibis Paris Bastille Opera", "brand": "ibis", "group": "Accor Economy", "stars": 3, "lat": 48.8553, "lon": 2.3689},
])

BRAND_PIN_COLORS = {
    "Raffles": "purple", "Sofitel": "purple", "Oetker Collection": "purple",
    "Four Seasons": "purple", "Shangri-La": "purple", "The Peninsula": "purple", "The Set Collection": "purple",
    "Rosewood": "purple", "Mandarin Oriental": "purple", "Dorchester Collection": "purple",
    "Pullman": "blue", "Meliá": "blue", "Experimental Group": "blue", "citizenM": "blue", "Orso Hotels": "blue",
    "Novotel": "green", "Mama Shelter": "green", "Mercure": "orange", "Independent": "orange", "ibis": "red"
}

if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = "Novotel Paris Centre Tour Eiffel"

if "action_states" not in st.session_state:
    st.session_state.action_states = {}

# ==========================================
# DATA GENERATION & AI LOGIC
# ==========================================
def generate_ai_summary(hotel_name: str, df: pd.DataFrame) -> str:
    if df.empty:
        return f"Insufficient review data to generate an AI summary for {hotel_name}."
    
    avg_score = df["Rating"].mean()
    total_reviews = len(df)
    negative_df = df[df["Sentiment"] == "Negative"]
    
    if not negative_df.empty:
        top_complaint = negative_df["Department"].mode()[0]
        complaint_aspect = negative_df[negative_df["Department"] == top_complaint]["Extracted Aspect"].mode()[0]
        bottleneck_text = f"However, {top_complaint} ({complaint_aspect.lower()}) remains a critical bottleneck requiring immediate operational attention."
    else:
        bottleneck_text = "Operations are running smoothly with minimal negative sentiment detected across all core departments."

    trend_text = "trending positively" if avg_score >= 4.0 else "stabilizing"
    return f"Based on {total_reviews} analyzed reviews, overall guest satisfaction at {hotel_name} is {trend_text} at {avg_score:.2f}/5.0. {bottleneck_text}"

@st.cache_data
def generate_synthetic_review_dataset(hotel_name: str, count: int = 150):
    np.random.seed(zlib.crc32(hotel_name.encode("utf-8")))
    today = datetime(2026, 10, 27)
    platforms = ["Google Reviews", "TripAdvisor", "Booking.com"]
    languages = ["English GB", "French FR", "German DE", "Spanish ES"]
    
    dept_aspects = {
        "Front Desk": ["Check-in Speed", "Staff Politeness", "Arrival Flow"],
        "Housekeeping": ["Room Cleanliness", "Bedding Comfort", "Bathroom Space"],
        "Maintenance": ["Wi-Fi Speed", "Air Conditioning", "Elevator Delay"],
        "F&B": ["Breakfast Variety", "Coffee Quality", "Room Service Speed"],
    }

    review_templates = {
        "Positive": [
            "Outstanding stay at {hotel}. The service regarding {aspect} was absolutely flawless.",
            "Extremely impressed by the overall quality, particularly the {aspect}.",
            "Five stars! The service related to {aspect} far exceeded our expectations."
        ],
        "Neutral": [
            "Decent stay overall, though the {aspect} was fairly average.",
            "Satisfactory experience, but noticeable room for improvement in {aspect}."
        ],
        "Negative": [
            "Very disappointed with the service. Major issues regarding {aspect}.",
            "Unsatisfactory experience; {aspect} fell well below expected standards."
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
        
        template = np.random.choice(review_templates[sentiment])
        review_text = template.format(hotel=hotel_name, aspect=aspect.lower())

        records.append({
            "Date": review_date, 
            "Platform": platform, 
            "Original Language": lang,
            "Original Text": review_text,
            "Auto-Translated English Text": f"Service review regarding {aspect.lower()}.",
            "Extracted Aspect": aspect, 
            "Sentiment": sentiment, 
            "Rating": rating_val, 
            "Department": dept,
        })
    return pd.DataFrame(records).sort_values(by="Date", ascending=False)

def get_hotel_actions(hotel_name: str, filtered_df: pd.DataFrame):
    np.random.seed(zlib.crc32(hotel_name.encode("utf-8")))
    lang_counts = filtered_df["Original Language"].value_counts().to_dict()
    en_cnt = lang_counts.get("English GB", 8)
    fr_cnt = lang_counts.get("French FR", 6)
    
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
            "languages_affected": f"English ({en_cnt-i}), French ({fr_cnt})",
        })
    return actions

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("## HotelPulse AI")
    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)
    
    st.markdown("### Property Filters")
    selected_stars = st.multiselect("Star Rating", options=[3, 4, 5], default=[3, 4, 5], format_func=lambda x: f"{x} Stars")
    available_brands = sorted(HOTELS_METADATA["brand"].unique().tolist())
    selected_brands = st.multiselect("Brand Family", options=available_brands, default=available_brands)

    filtered_hotels_df = HOTELS_METADATA[(HOTELS_METADATA["stars"].isin(selected_stars)) & (HOTELS_METADATA["brand"].isin(selected_brands))]

    if filtered_hotels_df.empty:
        st.error("No properties match your active filters.")
        st.stop()

    hotel_names_list = filtered_hotels_df["name"].tolist()

    if "pending_hotel" in st.session_state:
        st.session_state.selected_hotel = st.session_state.pop("pending_hotel")
    if st.session_state.selected_hotel not in hotel_names_list:
        st.session_state.selected_hotel = hotel_names_list[0]

    st.selectbox("Select Property Details", options=hotel_names_list, key="selected_hotel")
    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)

    # INDIVIDUAL CHECKBOXES FOR PLATFORMS
    st.markdown("### Review Platforms")
    plat_google = st.checkbox("Google Reviews", value=True)
    plat_tripadvisor = st.checkbox("TripAdvisor", value=True)
    plat_booking = st.checkbox("Booking.com", value=True)

    selected_platforms = []
    if plat_google: selected_platforms.append("Google Reviews")
    if plat_tripadvisor: selected_platforms.append("TripAdvisor")
    if plat_booking: selected_platforms.append("Booking.com")

    st.markdown("<hr style='border-color: #2D3748;'>", unsafe_allow_html=True)
    
    selected_date_range = st.selectbox("Date Range Window", options=["Last 30 Days", "Q3 2026", "Full Year 2026", "Custom Date Range"], index=0)

    today = datetime(2026, 10, 27).date()
    if selected_date_range == "Last 30 Days":
        start_date, end_date = today - timedelta(days=30), today
    elif selected_date_range == "Q3 2026":
        start_date, end_date = datetime(2026, 7, 1).date(), datetime(2026, 9, 30).date()
    elif selected_date_range == "Full Year 2026":
        start_date, end_date = datetime(2026, 1, 1).date(), today
    else:
        custom_dates = st.date_input("Custom Date Range", value=(today - timedelta(days=7), today))
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

col_left, col_right = st.columns([1.15, 0.85])

# ------------------------------------------
# LEFT COLUMN: KPI, AI SUMMARY & TABS
# ------------------------------------------
with col_left:
    ai_summary_text = generate_ai_summary(selected_hotel, filtered_df)
    st.markdown(
        f"""
        <div class="ai-summary-box">
            <div class="ai-summary-title">Executive AI Summary</div>
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
    
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Action Matrix", "Department Ratings", "Multilingual Feed"])

    with tab1:
        st.subheader("Priority Action Matrix")
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
                xaxis=dict(range=[0, 5.5]), height=420, margin=dict(l=10, r=10, t=35, b=10),
                template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_aspects, use_container_width=True)
        else:
            st.info("No reviews available for the current filter selection.")

    with tab3:
        st.subheader("Live Customer Review Stream (Auto-Translated)")
        if total_reviews > 0:
            feed_cols = ["Date", "Platform", "Original Language", "Original Text", "Auto-Translated English Text", "Extracted Aspect", "Sentiment", "Rating"]
            st.dataframe(
                filtered_df[feed_cols], use_container_width=True, hide_index=True, height=550,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "Sentiment": st.column_config.TextColumn("Sentiment")
                }
            )
        else:
            st.info("No reviews available for the current filter selection.")

# ------------------------------------------
# RIGHT COLUMN: MAP & DETAILED PROPERTY CARD
# ------------------------------------------
with col_right:
    st.subheader("Interactive Property Map")
    st.caption("Click any hotel pin on the map to switch directly to its dashboard.")

    selected_row = filtered_hotels_df[filtered_hotels_df["name"] == selected_hotel].iloc[0]

    hotel_map = folium.Map(
        location=[float(selected_row["lat"]), float(selected_row["lon"])],
        zoom_start=13,
        tiles="OpenStreetMap",
    )
    for _, h in filtered_hotels_df.iterrows():
        is_selected = h["name"] == selected_hotel
        folium.Marker(
            location=[float(h["lat"]), float(h["lon"])],
            tooltip=f"{h['name']} — {h['brand']} | {h['stars']}★",
            icon=folium.Icon(
                color="black" if is_selected else BRAND_PIN_COLORS.get(h["brand"], "gray"),
                icon="star" if is_selected else "bed",
                prefix="fa",
            ),
        ).add_to(hotel_map)

    map_event = st_folium(
        hotel_map,
        height=380,
        use_container_width=True,
        returned_objects=["last_object_clicked"],
        key="hotel_map",
    )

    clicked = (map_event or {}).get("last_object_clicked")
    if clicked:
        click_pos = (round(clicked["lat"], 5), round(clicked["lng"], 5))
        if click_pos != st.session_state.get("last_map_click"):
            st.session_state.last_map_click = click_pos
            distances = (filtered_hotels_df["lat"] - clicked["lat"]) ** 2 + (filtered_hotels_df["lon"] - clicked["lng"]) ** 2
            clicked_hotel = filtered_hotels_df.loc[distances.idxmin(), "name"]
            if clicked_hotel != selected_hotel:
                st.session_state.pending_hotel = clicked_hotel
                st.rerun()

    # METRIC COMPUTATIONS FOR PROPERTY CARD
    if total_reviews > 0:
        positive_share = (filtered_df["Sentiment"] == "Positive").mean() * 100
        aspect_scores = filtered_df.groupby("Extracted Aspect")["Rating"].mean()
        weakest_aspect_name = aspect_scores.idxmin()
        weakest_aspect_score = aspect_scores.min()
        weakest_aspect_str = f"{weakest_aspect_name} ({weakest_aspect_score:.2f}/5)"
        top_language = filtered_df["Original Language"].value_counts().idxmax()
    else:
        positive_share = 0.0
        weakest_aspect_str = top_language = "—"

    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(selected_row['name'] + ' Paris')}"
    stars_str = "★" * int(selected_row['stars'])

    # EXACT PROPERTY METADATA CARD FORMAT
    card_html = (
        f'<div style="background-color: #0E1726; border: 1px solid #1E293B; border-radius: 12px; padding: 22px; margin-top: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">'
        f'<div style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">🏨 {selected_row["name"]}</div>'
        f'<div style="font-size: 0.9rem; color: #94A3B8; margin-top: 4px; margin-bottom: 20px;">{selected_row["brand"]} · {selected_row["group"]} · <span style="color: #CBD5E1;">{stars_str}</span></div>'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">'
        f'<div><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Score</div><div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{avg_score:.2f}/5</div></div>'
        f'<div><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Reviews</div><div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{total_reviews}</div></div>'
        f'<div><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Positive</div><div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{positive_share:.0f}%</div></div>'
        f'</div>'
        f'<div style="font-size: 0.92rem; color: #E2E8F0; line-height: 1.8; margin-bottom: 20px;">'
        f'⚠️ <strong>Weakest aspect:</strong> {weakest_aspect_str}<br/>'
        f'🚨 <strong>Negative mentions:</strong> {neg_alerts}<br/>'
        f'🗣️ <strong>Main review language:</strong> {top_language}'
        f'</div></div>'
    )
    
    st.markdown(card_html, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.link_button("📍 Open in Google Maps", google_maps_url, use_container_width=True)