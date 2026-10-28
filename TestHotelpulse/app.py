import random
from datetime import datetime, timedelta
from urllib.parse import quote_plus

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="HotelPulse AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.8rem; padding-bottom: 2.5rem; }

    /* Executive AI Summary Banner */
    .ai-summary-box {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-left: 4px solid #0284c7;
        border: 1px solid #e2e8f0;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    }
    .ai-summary-title { font-size: 0.85rem; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 6px; }
    .ai-summary-text { font-size: 1.05rem; line-height: 1.5; color: #0f172a; }

    /* Light Theme KPI Cards */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card-alert {
        background-color: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 6px solid #e11d48;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(225, 29, 72, 0.06);
        height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #64748b; }
    .kpi-value { font-size: 1.7rem; font-weight: 700; color: #0f172a; line-height: 1.2; }
    .kpi-subtext-positive { font-size: 0.8rem; font-weight: 600; color: #16a34a; }
    .kpi-subtext-negative { font-size: 0.8rem; font-weight: 600; color: #dc2626; }
    .kpi-subtext-neutral { font-size: 0.8rem; font-weight: 500; color: #475569; }
    .kpi-alert-value { font-size: 1.0rem; font-weight: 700; color: #be123c; line-height: 1.3; }
    .kpi-alert-subtext { font-size: 0.78rem; font-weight: 500; color: #9f1239; }

    /* Light Theme Action Matrix Cards */
    .action-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.04);
    }
    .action-high { border-left: 7px solid #ef4444; }
    .action-medium { border-left: 7px solid #f59e0b; }
    .action-low { border-left: 7px solid #10b981; }
    .action-addressed { border-left: 7px solid #64748b; background-color: #f8fafc; opacity: 0.88; }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .badge-high { background-color: #fee2e2; color: #b91c1c; }
    .badge-medium { background-color: #fef3c7; color: #b45309; }
    .badge-low { background-color: #d1fae5; color: #047857; }
    .badge-dept { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }

    .action-headline { font-size: 1.05rem; font-weight: 600; color: #0f172a; margin: 8px 0 4px 0; }
    .action-meta { font-size: 0.83rem; color: #64748b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# REAL HOTEL METADATA
# ==========================================
HOTELS_METADATA = pd.DataFrame([
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
    {"name": "citizenM Paris Gare de Lyon", "brand": "citizenM", "group": "Lifestyle", "stars": 4, "lat": 48.8448, "lon": 2.3721},
    {"name": "Hôtel des Grands Boulevards", "brand": "Experimental Group", "group": "Boutique", "stars": 4, "lat": 48.8708, "lon": 2.3450},
    {"name": "Meliá Paris La Défense", "brand": "Meliá", "group": "Premium", "stars": 4, "lat": 48.8897, "lon": 2.2530},
    {"name": "Hôtel Rochechouart", "brand": "Orso Hotels", "group": "Boutique", "stars": 4, "lat": 48.8825, "lon": 2.3392},
    {"name": "Hôtel Les Bains Paris", "brand": "Independent", "group": "Boutique", "stars": 5, "lat": 48.8631, "lon": 2.3551},
    {"name": "Mama Shelter Paris East", "brand": "Mama Shelter", "group": "Lifestyle", "stars": 3, "lat": 48.8596, "lon": 2.4011},
    {"name": "Hôtel Britannique", "brand": "Independent", "group": "Midscale", "stars": 3, "lat": 48.8582, "lon": 2.3455},
    {"name": "Hôtel de la Porte Dorée", "brand": "Independent", "group": "Midscale", "stars": 3, "lat": 48.8354, "lon": 2.4068},
    {"name": "Hôtel Jeanne d'Arc", "brand": "Independent", "group": "Midscale", "stars": 3, "lat": 48.8559, "lon": 2.3615},
    {"name": "Hôtel Caron de Beaumarchais", "brand": "Independent", "group": "Boutique", "stars": 3, "lat": 48.8568, "lon": 2.3571},
    {"name": "Le Royal Monceau - Raffles Paris", "brand": "Raffles", "group": "Accor Luxury", "stars": 5, "lat": 48.8763, "lon": 2.3004},
    {"name": "Sofitel Paris Le Faubourg", "brand": "Sofitel", "group": "Accor Luxury", "stars": 5, "lat": 48.8687, "lon": 2.3218},
    {"name": "Pullman Paris Tour Eiffel", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8554, "lon": 2.2929},
    {"name": "Pullman Paris Montparnasse", "brand": "Pullman", "group": "Accor Premium", "stars": 4, "lat": 48.8396, "lon": 2.3228},
    {"name": "Hotel Novotel Paris les Halles", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8606, "lon": 2.3461},
    {"name": "Novotel Paris Centre Tour Eiffel", "brand": "Novotel", "group": "Accor Midscale", "stars": 4, "lat": 48.8507, "lon": 2.2825},
    {"name": "Mercure Paris Montmartre Sacre-Coeur", "brand": "Mercure", "group": "Accor Midscale", "stars": 4, "lat": 48.8858, "lon": 2.3312},
    {"name": "ibis Paris Bastille Opera", "brand": "ibis", "group": "Accor Economy", "stars": 3, "lat": 48.8553, "lon": 2.3689},
])

if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = "Ritz Paris"

if "action_states" not in st.session_state:
    st.session_state.action_states = {}

# ==========================================
# DATASET GENERATOR
# ==========================================
@st.cache_data
def load_review_dataset(hotel_name: str) -> pd.DataFrame:
    """
    Generates a realistic mock dataset containing Google, TripAdvisor, and Booking.com reviews
    to populate the dashboard dynamically for the selected hotel, with properly translated text.
    """
    random.seed(hash(hotel_name))
    
    platforms = ["Google Reviews", "TripAdvisor", "Booking.com"]
    languages = ["English", "French", "Spanish", "German", "Italian"]
    departments = ["Front Desk", "F&B", "Housekeeping", "Maintenance", "Concierge"]
    
    aspects = {
        "Front Desk": ["Check-in speed", "Staff friendliness", "Billing accuracy", "Welcome experience"],
        "F&B": ["Breakfast quality", "Room service promptness", "Restaurant ambiance", "Menu variety"],
        "Housekeeping": ["Room cleanliness", "Bathroom amenities", "Turndown service", "Bed comfort"],
        "Maintenance": ["AC/Heating functionality", "Wi-Fi speed", "Plumbing", "Elevator availability"],
        "Concierge": ["Local recommendations", "Booking assistance", "Valet service", "Luggage handling"]
    }

    templates = {
        "English": {
            "Positive": "Outstanding {aspect}. The {dept} team exceeded expectations.",
            "Neutral": "Decent stay, but {aspect} was just average.",
            "Negative": "Disappointed with the {aspect}. The {dept} needs better management."
        },
        "French": {
            "Positive": "{aspect} exceptionnel. L'équipe de {dept} a dépassé nos attentes.",
            "Neutral": "Séjour correct, mais {aspect} était juste moyen.",
            "Negative": "Déçu par {aspect}. L'équipe de {dept} doit s'améliorer."
        },
        "Spanish": {
            "Positive": "{aspect} excepcional. El equipo de {dept} superó las expectativas.",
            "Neutral": "Estancia decente, pero {aspect} fue simplemente normal.",
            "Negative": "Decepcionado con {aspect}. {dept} necesita una mejor gestión."
        },
        "German": {
            "Positive": "Hervorragendes {aspect}. Das {dept}-Team hat die Erwartungen übertroffen.",
            "Neutral": "Guter Aufenthalt, aber {aspect} war nur durchschnittlich.",
            "Negative": "Enttäuscht von {aspect}. {dept} benötigt besseres Management."
        },
        "Italian": {
            "Positive": "{aspect} eccezionale. Il team di {dept} ha superato le aspettative.",
            "Neutral": "Soggiorno decente, ma {aspect} era solo nella media.",
            "Negative": "Deluso da {aspect}. {dept} necessita di una migliore gestione."
        }
    }
    
    num_reviews = random.randint(120, 350)
    data = []
    today = datetime(2026, 10, 27)
    
    for _ in range(num_reviews):
        dept = random.choice(departments)
        aspect = random.choice(aspects[dept])
        lang = random.choice(languages)
        
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 8, 12, 35, 40])[0]
        
        if rating >= 4:
            sentiment = "Positive"
        elif rating == 3:
            sentiment = "Neutral"
        else:
            sentiment = "Negative"
            
        orig_text = templates[lang][sentiment].format(aspect=aspect.lower(), dept=dept.lower())
        eng_text = templates["English"][sentiment].format(aspect=aspect.lower(), dept=dept.lower())
            
        date = today - timedelta(days=random.randint(0, 365))
        
        data.append({
            "Date": date.date(),
            "Platform": random.choice(platforms),
            "Original Language": lang,
            "Original Text": orig_text,
            "Auto-Translated English Text": eng_text,
            "Extracted Aspect": aspect,
            "Sentiment": sentiment,
            "Rating": rating,
            "Department": dept
        })
        
    df = pd.DataFrame(data)
    df.sort_values(by="Date", ascending=False, inplace=True)
    return df

def get_dynamic_hotel_actions(hotel_name: str, filtered_df: pd.DataFrame):
    if filtered_df.empty:
        return []

    neg_df = filtered_df[filtered_df["Sentiment"] == "Negative"]
    dept_neg_counts = neg_df["Department"].value_counts()
    
    if dept_neg_counts.empty:
        return []
        
    top_depts = dept_neg_counts.index.tolist()
    
    dept_heads = {
        "Front Desk": "Alexandre D.",
        "Maintenance": "David Dubois",
        "F&B": "Chef Jerome",
        "Housekeeping": "Marie-Therese",
        "Concierge": "Sarah Jenkins"
    }

    rec_map = {
        "Check-in speed": "Address frequent guest complaints regarding slow check-in by deploying mobile check-in ambassadors.",
        "Staff friendliness": "Conduct immediate customer service retraining based on multiple reviews citing unhelpful staff.",
        "Billing accuracy": "Audit the automated billing system following several guest reports of incorrect charges.",
        "Welcome experience": "Revamp the arrival protocol to ensure guests feel welcomed immediately upon entry.",
        "Breakfast quality": "Overhaul hot breakfast options and ingredient sourcing after consistent negative guest feedback.",
        "Room service promptness": "Restructure room service logistics to reduce delivery times cited in recent reviews.",
        "Restaurant ambiance": "Adjust lighting and seating arrangements to address guest complaints about the dining atmosphere.",
        "Menu variety": "Expand dietary options on the menu following reviews mentioning limited choices.",
        "Room cleanliness": "Implement a strict dual-check house inspection protocol due to recurring cleanliness complaints.",
        "Bathroom amenities": "Upgrade toiletry brands and ensure consistent restocking based on guest feedback.",
        "Turndown service": "Standardize evening turndown schedules after reviews noted missed services.",
        "Bed comfort": "Assess mattress quality in affected rooms following specific guest complaints about sleep comfort.",
        "AC/Heating functionality": "Conduct a full diagnostic of HVAC sensors in response to guest reports of temperature issues.",
        "Wi-Fi speed": "Upgrade local Wi-Fi repeaters on problematic floors cited in recent negative reviews.",
        "Plumbing": "Schedule urgent maintenance for room plumbing fixtures mentioned in recent guest complaints.",
        "Elevator availability": "Optimize elevator dispatching logic and service schedules due to reported wait times.",
        "Local recommendations": "Update the concierge knowledge base after guests reported outdated local advice.",
        "Booking assistance": "Review partner booking SLAs to resolve issues highlighted by guests regarding reservations.",
        "Valet service": "Increase valet staffing during peak hours to address complaints about slow vehicle retrieval.",
        "Luggage handling": "Improve luggage delivery coordination to rooms following reports of delayed bags."
    }

    actions = []
    priorities = [("High Priority", "high"), ("Medium Priority", "medium"), ("Low Priority", "low")]

    for idx, dept in enumerate(top_depts[:3]):
        head = dept_heads.get(dept, "Manager")
        pri_label, pri_level = priorities[min(idx, 2)]
        
        dept_reviews = filtered_df[filtered_df["Department"] == dept]
        neg_dept_reviews = dept_reviews[dept_reviews["Sentiment"] == "Negative"]
        
        if not neg_dept_reviews.empty:
            root_aspect = neg_dept_reviews["Extracted Aspect"].mode()[0]
        else:
            root_aspect = "Operations"
            
        rec = rec_map.get(root_aspect, f"Review operational protocols regarding {root_aspect.lower()} based on guest feedback.")
        
        affected_langs = dept_reviews["Original Language"].value_counts().to_dict()
        lang_str = ", ".join([f"{k} ({v})" for k, v in affected_langs.items()])
        
        lift = round(len(neg_dept_reviews) / max(len(filtered_df), 1) * 0.8, 2)

        actions.append({
            "id": f"card_{idx+1}",
            "priority": pri_label,
            "priority_level": pri_level,
            "department": dept,
            "dept_head": head,
            "recommendation": rec,
            "impact": f"Estimated +{lift} overall score lift | Root Focus: {root_aspect}",
            "languages_affected": lang_str if lang_str else "English (0)",
        })
    return actions

def generate_ai_summary(hotel_name: str, df: pd.DataFrame) -> str:
    if df.empty:
        return f"Insufficient review data to generate an AI summary for {hotel_name}. Please connect your dataset."
    
    avg_score = df["Rating"].mean()
    total_reviews = len(df)
    negative_df = df[df["Sentiment"] == "Negative"]
    
    if not negative_df.empty:
        top_complaint = negative_df["Department"].mode()[0]
        complaint_aspect = negative_df[negative_df["Department"] == top_complaint]["Extracted Aspect"].mode()[0]
        bottleneck_text = f"However, {top_complaint} ({complaint_aspect.lower()}) accounts for the majority of guest friction."
    else:
        bottleneck_text = "Operations are performing well with minimal negative feedback across all departments."

    trend_text = "trending positively" if avg_score >= 4.0 else ("neutral" if avg_score >= 3.0 else "requiring intervention")
    return f"Based on {total_reviews} analyzed reviews, overall guest satisfaction is {trend_text} at {avg_score:.2f}/5.0. {bottleneck_text}"

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("## HotelPulse AI")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### Property Selection")
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
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("### Review Platforms")
    plat_google = st.checkbox("Google Reviews", value=True)
    plat_tripadvisor = st.checkbox("TripAdvisor", value=True)
    plat_booking = st.checkbox("Booking.com", value=True)

    selected_platforms = []
    if plat_google: selected_platforms.append("Google Reviews")
    if plat_tripadvisor: selected_platforms.append("TripAdvisor")
    if plat_booking: selected_platforms.append("Booking.com")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    selected_date_range = st.selectbox("Date Range Window", options=["Last 30 Days", "Q3 2026", "Full Year 2026", "Custom Date Range"], index=2)

    today = datetime(2026, 10, 27).date()
    if selected_date_range == "Last 30 Days":
        start_date, end_date = today - timedelta(days=30), today
    elif selected_date_range == "Q3 2026":
        start_date, end_date = datetime(2026, 7, 1).date(), datetime(2026, 9, 30).date()
    elif selected_date_range == "Full Year 2026":
        start_date, end_date = datetime(2026, 1, 1).date(), today
    else:
        custom_dates = st.date_input("Custom Date Range", value=(today - timedelta(days=30), today))
        start_date, end_date = custom_dates if len(custom_dates) == 2 else (custom_dates[0], custom_dates[0])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📚 Model & Open Data Citations")
    st.markdown(
        """
        - **Data Corpus**: Simulated Aggregation Engine via Streamlit Cache
        - **NLP & Sentiment**: TextBlob / VADER Sentiment Analyzer integration ready
        - **Repository**: [GitHub Source Code](https://github.com/)
        """
    )

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

raw_df = load_review_dataset(selected_hotel)
if not raw_df.empty:
    filtered_df = raw_df[
        (raw_df["Date"] >= pd.to_datetime(start_date).date()) & 
        (raw_df["Date"] <= pd.to_datetime(end_date).date()) &
        (raw_df["Platform"].isin(selected_platforms))
    ]
else:
    filtered_df = pd.DataFrame(columns=raw_df.columns)

total_reviews = len(filtered_df)
avg_score = filtered_df["Rating"].mean() if total_reviews > 0 else 0.0
neg_alerts = len(filtered_df[filtered_df["Sentiment"] == "Negative"]) if total_reviews > 0 else 0
actions = get_dynamic_hotel_actions(selected_hotel, filtered_df)

# ==========================================
# MAIN LAYOUT
# ==========================================
st.title("HotelPulse AI: Operations & Sentiment Engine")
st.markdown(f"**Selected Property:** {selected_hotel} &nbsp;|&nbsp; **Window:** {start_date} to {end_date}")
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

    if total_reviews == 0:
        trend_class = "kpi-subtext-neutral"
        trend_label = "No Data Available"
    elif avg_score >= 4.0:
        trend_class = "kpi-subtext-positive"
        trend_label = "Trend Positive"
    elif avg_score >= 3.0:
        trend_class = "kpi-subtext-neutral"
        trend_label = "Trend Stable"
    else:
        trend_class = "kpi-subtext-negative"
        trend_label = "Trend Negative"

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Satisfaction Score</div><div class="kpi-value">{avg_score:.2f} / 5.0</div><div class="{trend_class}">{trend_label}</div></div>', unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Review Volume</div><div class="kpi-value">{total_reviews}</div><div class="kpi-subtext-neutral">Analyzed NLP records</div></div>', unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f'<div class="kpi-card-alert"><div class="kpi-title" style="color: #9f1239;">Urgent Alerts</div><div class="kpi-alert-value">{neg_alerts} Negative Mentions</div><div class="kpi-alert-subtext">Action Required</div></div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Action Matrix", "Department Ratings", "Multilingual Feed"])

    with tab1:
        st.subheader("Priority Action Matrix")
        if not actions:
            st.info("No urgent actions identified or insufficient review data connected.")
        else:
            hotel_states = st.session_state.action_states[selected_hotel]
            
            for idx, item in enumerate(actions):
                card_id = item["id"]
                current_state = hotel_states.get(card_id, {}).get("status", "Open")
                assigned_person = hotel_states.get(card_id, {}).get("assigned_to", None)
                
                border_class = "action-addressed" if current_state == "Addressed" else f"action-{item['priority_level']}"
                status_text = "Completed" if current_state == "Addressed" else ("Assigned" if assigned_person else "Open")

                st.markdown(
                    f"""
                    <div class="action-card {border_class}">
                        <div>
                            <span class="badge badge-{item['priority_level']}">{item["priority"]}</span>
                            <span class="badge badge-dept">{item["department"]}</span>
                            <span style="font-size: 0.8rem; color: #64748b; float: right;">Status: {status_text}</span>
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
                st.markdown("<hr style='border-color: #f1f5f9;'>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Departmental Aspect Scores")
        if total_reviews > 0:
            aspect_df = filtered_df.groupby("Extracted Aspect")["Rating"].mean().reset_index()
            aspect_df.columns = ["Extracted Aspect", "Score"]
            aspect_df = aspect_df.sort_values(by="Score", ascending=True)

            fig_aspects = px.bar(
                aspect_df, x="Score", y="Extracted Aspect", orientation="h", text=aspect_df["Score"].round(2),
                color="Score", color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                title="Computed Aspect Ratings (1-5 Scale)"
            )
            fig_aspects.update_layout(
                xaxis=dict(range=[0, 5.5]), height=420, margin=dict(l=10, r=10, t=35, b=10)
            )
            st.plotly_chart(fig_aspects, use_container_width=True)
        else:
            st.info("Please adjust filters or date range to view aspect scores.")

    with tab3:
        st.subheader("Live Customer Review Stream")
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
            st.info("No matching reviews for current selections.")

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
                color="black" if is_selected else "blue",
                icon="star" if is_selected else "info-sign",
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
        weakest_aspect_str = top_language = "N/A"

    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(selected_row['name'] + ' Paris')}"
    stars_str = "★" * int(selected_row['stars'])

    card_html = (
        f'<div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; margin-top: 15px; box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);">'
        f'<div style="font-size: 1.4rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">🏨 {selected_row["name"]}</div>'
        f'<div style="font-size: 0.9rem; color: #64748b; margin-top: 4px; margin-bottom: 20px;">{selected_row["brand"]} · {selected_row["group"]} · <span style="color: #475569;">{stars_str}</span></div>'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">'
        f'<div><div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Score</div><div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1.1;">{avg_score:.2f}/5</div></div>'
        f'<div><div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Reviews</div><div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1.1;">{total_reviews}</div></div>'
        f'<div><div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Positive</div><div style="font-size: 2.2rem; font-weight: 800; color: #0f172a; line-height: 1.1;">{positive_share:.0f}%</div></div>'
        f'</div>'
        f'<div style="font-size: 0.92rem; color: #334155; line-height: 1.8; margin-bottom: 20px;">'
        f'⚠️ <strong>Weakest aspect:</strong> {weakest_aspect_str}<br/>'
        f'🚨 <strong>Negative mentions:</strong> {neg_alerts}<br/>'
        f'🗣️ <strong>Main review language:</strong> {top_language}'
        f'</div></div>'
    )
    
    st.markdown(card_html, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.link_button("📍 Open in Google Maps", google_maps_url, use_container_width=True)