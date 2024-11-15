import streamlit as st

def custom_callout(type, title, message):
    colors = {
        "info": ("#e6f3ff", "#0066cc", "ℹ️"),
        "warning": ("#fff3e6", "#cc6600", "⚠️"),
        "error": ("#ffe6e6", "#cc0000", "❌"),
        "success": ("#e6ffe6", "#006600", "✅")
    }
    bg_color, border_color, icon = colors.get(type)
    
    st.markdown(f"""
        <div style='padding:1rem; background-color:{bg_color}; 
                    border-radius:0.5rem; border-left:4px solid {border_color};'>
            <h4 style='margin:0'>{icon} {title}</h4>
            <p style='margin:0.5rem 0 0 0'>{message}</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    custom_callout("info", "참고사항", "이것은 정보 메시지입니다")
    custom_callout("warning", "주의", "이것은 경고 메시지입니다")