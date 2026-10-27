# FICHE DESIGN CORRIGÉE (Sans sauts de ligne problématiques pour Streamlit)
    card_html = f"""
    <div style="background-color: #0E1726; border: 1px solid #1E293B; border-radius: 12px; padding: 22px; margin-top: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">🏨 {selected_row['name']}</div>
        <div style="font-size: 0.9rem; color: #94A3B8; margin-top: 4px; margin-bottom: 20px;">{selected_row['brand']} · {selected_row['group']} · <span style="color: #CBD5E1;">{stars_str}</span></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
            <div><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Score</div><div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{avg_score:.2f}/5</div></div>
            <div><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Reviews</div><div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{total_reviews}</div></div>
            <div><div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">Positive</div><div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.1;">{positive_share:.0f}%</div></div>
        </div>
        <div style="font-size: 0.92rem; color: #E2E8F0; line-height: 1.8; margin-bottom: 20px;">
            ⚠️ <strong>Weakest aspect:</strong> {weakest_aspect_str}<br/>
            🚨 <strong>Negative mentions:</strong> {neg_alerts}<br/>
            🗣️ <strong>Main review language:</strong> {top_language}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.link_button("📍 Open in Google Maps", google_maps_url, use_container_width=True)