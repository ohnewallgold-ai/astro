import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# --- Streamlit page configuration ---
st.set_page_config(
    page_title="금성의 위상 및 크기 변화 시뮬레이터 (천동설 vs 지동설)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #facc15;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 25px;
    }
    .model-header-helio {
        background-color: rgba(30, 58, 138, 0.4);
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 15px;
        text-align: center;
    }
    .model-header-geo {
        background-color: rgba(120, 53, 4, 0.4);
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #f59e0b;
        margin-bottom: 15px;
        text-align: center;
    }
    .info-box {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.markdown('<div class="main-title">🪐 금성의 위상 및 크기 변화 시뮬레이터</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">지구 중심설(천동설)과 태양 중심설(지동설) 모델에 따른 금성의 시직경 및 위상 비교</div>', unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.title("🛠️ 시뮬레이션 제어")

# Play / Animation controls
if 'day' not in st.session_state:
    st.session_state.day = 0

autoplay = st.sidebar.checkbox("🔄 애니메이션 자동 재생", value=False)

if autoplay:
    # Increment day smoothly
    st.session_state.day = (st.session_state.day + 4) % 584
    time.sleep(0.03)

day = st.sidebar.slider(
    "시간 경과 (일, Day)",
    min_value=0,
    max_value=584,
    value=st.session_state.day,
    step=1,
    help="금성의 회합 주기(약 584일)를 기준으로 한 주기 동안의 변화를 관찰합니다."
)

if not autoplay:
    st.session_state.day = day

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 💡 관찰 포인트
1. **태양 중심설(지동설)**:
   - 금성이 태양 뒤로 갈 때(원거리) **작은 보름달** 모양이 나타납니다.
   - 금성이 지구와 가까워질 때(근거리) **크고 얇은 그믐달/초승달** 모양이 나타납니다.
   
2. **지구 중심설(천동설)**:
   - 금성이 항상 지구와 태양 사이에 묶여 있어, **보름달이나 반달(상현/하현) 모양이 절대 나타날 수 없으며** 오직 그믐달/초승달 모양만 반복됩니다.
""")

# --- Mathematical modeling of the orbits ---
def calculate_positions(day):
    # --- Heliocentric Model ---
    # Earth orbit: radius 1.0 AU, period 365.25 days
    theta_E = 2 * np.pi * (day / 365.25)
    # Venus orbit: radius 0.723 AU, period 224.7 days
    theta_V = 2 * np.pi * (day / 224.7)
    
    x_E_hel = 1.0 * np.cos(theta_E)
    y_E_hel = 1.0 * np.sin(theta_E)
    
    x_V_hel = 0.723 * np.cos(theta_V)
    y_V_hel = 0.723 * np.sin(theta_V)
    
    # Distance and Phase
    d_hel = np.sqrt((x_V_hel - x_E_hel)**2 + (y_V_hel - y_E_hel)**2)
    
    # Phase angle calculation (angle Earth-Venus-Sun)
    v_VS_hel = np.array([-x_V_hel, -y_V_hel])
    v_VE_hel = np.array([x_E_hel - x_V_hel, y_E_hel - y_V_hel])
    cos_alpha_hel = np.dot(v_VS_hel, v_VE_hel) / (np.linalg.norm(v_VS_hel) * np.linalg.norm(v_VE_hel))
    phase_hel = (1 + cos_alpha_hel) / 2
    
    # --- Geocentric Model (Ptolemaic) ---
    # Sun orbits Earth: radius 1.0 AU, period 365.25 days
    theta_S = 2 * np.pi * (day / 365.25)
    # Venus Epicycle Center locked to Earth-Sun line: radius 0.58 AU
    R_C = 0.58
    # Venus Epicycle Radius: 0.33 AU
    r_v = 0.33
    # Venus completes one synodic cycle in 583.92 days relative to Earth-Sun line
    phi_V = theta_S + np.pi + 2 * np.pi * (day / 583.92)
    
    x_S_geo = 1.0 * np.cos(theta_S)
    y_S_geo = 1.0 * np.sin(theta_S)
    
    x_C_geo = R_C * np.cos(theta_S)
    y_C_geo = R_C * np.sin(theta_S)
    
    x_V_geo = x_C_geo + r_v * np.cos(phi_V)
    y_V_geo = y_C_geo + r_v * np.sin(phi_V)
    
    # Distance and Phase
    d_geo = np.sqrt(x_V_geo**2 + y_V_geo**2)
    
    # Phase angle calculation in Geocentric (Sun is light source, Earth is observer)
    v_VS_geo = np.array([x_S_geo - x_V_geo, y_S_geo - y_V_geo])
    v_VE_geo = np.array([-x_V_geo, -y_V_geo])
    cos_alpha_geo = np.dot(v_VS_geo, v_VE_geo) / (np.linalg.norm(v_VS_geo) * np.linalg.norm(v_VE_geo))
    phase_geo = (1 + cos_alpha_geo) / 2
    
    return {
        "hel": {
            "E": (x_E_hel, y_E_hel),
            "V": (x_V_hel, y_V_hel),
            "S": (0.0, 0.0),
            "distance": d_hel,
            "phase": phase_hel
        },
        "geo": {
            "E": (0.0, 0.0),
            "V": (x_V_geo, y_V_geo),
            "S": (x_S_geo, y_S_geo),
            "C": (x_C_geo, y_C_geo),
            "distance": d_geo,
            "phase": phase_geo
        }
    }

data = calculate_positions(st.session_state.day)

# Helper function to generate smooth 2D phase coordinates for Plotly
def get_phase_coords(phase, radius, steps=100):
    t_right = np.linspace(-np.pi/2, np.pi/2, steps)
    x_right = radius * np.cos(t_right)
    y_right = radius * np.sin(t_right)
    
    t_left = np.linspace(np.pi/2, 3*np.pi/2, steps)
    # The terminator modulates the x-coordinate based on the phase
    x_left = radius * (2 * phase - 1) * np.cos(t_left)
    y_left = radius * np.sin(t_left)
    
    x = np.concatenate([x_right, x_left])
    y = np.concatenate([y_right, y_left])
    return x, y

# --- Two-column layout for comparison ---
col1, col2 = st.columns(2)

# ==================== COLUMN 1: HELIOCENTRIC ====================
with col1:
    st.markdown('<div class="model-header-helio"><h3>🌞 태양 중심설 (지동설)</h3></div>', unsafe_allow_html=True)
    
    # 1. Heliocentric Orbit Plot
    hel_data = data["hel"]
    x_E, y_E = hel_data["E"]
    x_V, y_V = hel_data["V"]
    
    fig_hel_orbit = go.Figure()
    
    # Orbits
    t = np.linspace(0, 2*np.pi, 200)
    fig_hel_orbit.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode="lines", name="지구 궤도", line=dict(color="#3b82f6", dash="dash", width=1.5)))
    fig_hel_orbit.add_trace(go.Scatter(x=0.723*np.cos(t), y=0.723*np.sin(t), mode="lines", name="금성 궤도", line=dict(color="#f59e0b", dash="dash", width=1.5)))
    
    # Celestial Bodies
    fig_hel_orbit.add_trace(go.Scatter(x=[0], y=[0], mode="markers", name="태양", marker=dict(size=18, color="#ef4444", symbol="star")))
    fig_hel_orbit.add_trace(go.Scatter(x=[x_E], y=[y_E], mode="markers+text", name="지구", text=["지구"], textposition="top right", marker=dict(size=12, color="#3b82f6")))
    fig_hel_orbit.add_trace(go.Scatter(x=[x_V], y=[y_V], mode="markers+text", name="금성", text=["금성"], textposition="top right", marker=dict(size=10, color="#f59e0b")))
    
    # Line of sight
    fig_hel_orbit.add_trace(go.Scatter(x=[x_E, x_V], y=[y_E, y_V], mode="lines", name="시선 (지구-금성)", line=dict(color="rgba(255,255,255,0.4)", width=1.5)))
    
    fig_hel_orbit.update_layout(
        title="<b>행성 궤도 탑뷰 (우주에서 본 시점)</b>",
        xaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_hel_orbit, use_container_width=True)
    
    # 2. Heliocentric Telescope View
    # Apparent size is proportional to 1/distance
    # Minimum distance is 0.277 AU, Maximum is 1.723 AU
    # Let's scale visual radius between 0.5 (smallest) and 3.0 (largest)
    base_radius = 0.8 / hel_data["distance"]
    
    fig_hel_tel = go.Figure()
    
    # Base circle (dark side of Venus)
    t_circle = np.linspace(0, 2*np.pi, 100)
    fig_hel_tel.add_trace(go.Scatter(
        x=base_radius * np.cos(t_circle),
        y=base_radius * np.sin(t_circle),
        fill="toself",
        fillcolor="#1e293b",
        line=dict(color="#475569", width=1),
        showlegend=False,
        hoverinfo="skip"
    ))
    
    # Phase overlay (illuminated side)
    x_ph, y_ph = get_phase_coords(hel_data["phase"], base_radius)
    fig_hel_tel.add_trace(go.Scatter(
        x=x_ph,
        y=y_ph,
        fill="toself",
        fillcolor="#fef08a",
        line=dict(color="#fef08a", width=0),
        showlegend=False,
        hoverinfo="skip"
    ))
    
    fig_hel_tel.update_layout(
        title=f"<b>지구에서 본 금성 망원경 뷰 (시직경 및 위상)</b><br>거리: {hel_data['distance']:.3f} AU | 위상: {hel_data['phase']*100:.1f}%",
        xaxis=dict(range=[-3.5, 3.5], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-3.5, 3.5], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        height=350,
        plot_bgcolor="#090d16",
        paper_bgcolor="#090d16"
    )
    
    st.plotly_chart(fig_hel_tel, use_container_width=True)


# ==================== COLUMN 2: GEOCENTRIC ====================
with col2:
    st.markdown('<div class="model-header-geo"><h3>🌍 지구 중심설 (천동설)</h3></div>', unsafe_allow_html=True)
    
    # 1. Geocentric Orbit Plot
    geo_data = data["geo"]
    x_E, y_E = geo_data["E"]
    x_V, y_V = geo_data["V"]
    x_S, y_S = geo_data["S"]
    x_C, y_C = geo_data["C"]
    
    fig_geo_orbit = go.Figure()
    
    # Orbits & Deferents
    t = np.linspace(0, 2*np.pi, 200)
    fig_geo_orbit.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode="lines", name="태양 궤도", line=dict(color="#ef4444", dash="dash", width=1.5)))
    fig_geo_orbit.add_trace(go.Scatter(x=0.58*np.cos(t), y=0.58*np.sin(t), mode="lines", name="금성 인도원(Deferent)", line=dict(color="#94a3b8", dash="dash", width=1.2)))
    
    # Epicycle path at current position
    fig_geo_orbit.add_trace(go.Scatter(x=x_C + 0.33*np.cos(t), y=y_C + 0.33*np.sin(t), mode="lines", name="주전원(Epicycle)", line=dict(color="#f59e0b", dash="dot", width=1.2)))
    
    # Celestial Bodies
    fig_geo_orbit.add_trace(go.Scatter(x=[0], y=[0], mode="markers+text", name="지구", text=["지구"], textposition="top right", marker=dict(size=14, color="#3b82f6")))
    fig_geo_orbit.add_trace(go.Scatter(x=[x_S], y=[y_S], mode="markers+text", name="태양", text=["태양"], textposition="top right", marker=dict(size=16, color="#ef4444", symbol="star")))
    fig_geo_orbit.add_trace(go.Scatter(x=[x_C], y=[y_C], mode="markers", name="주전원 중심", marker=dict(size=6, color="#94a3b8", symbol="x")))
    fig_geo_orbit.add_trace(go.Scatter(x=[x_V], y=[y_V], mode="markers+text", name="금성", text=["금성"], textposition="top right", marker=dict(size=10, color="#f59e0b")))
    
    # Lines
    fig_geo_orbit.add_trace(go.Scatter(x=[0, x_S], y=[0, y_S], mode="lines", name="지구-태양 선", line=dict(color="rgba(239, 68, 68, 0.3)", width=1.5)))
    fig_geo_orbit.add_trace(go.Scatter(x=[0, x_V], y=[0, y_V], mode="lines", name="시선 (지구-금성)", line=dict(color="rgba(255,255,255,0.4)", width=1.5)))
    
    fig_geo_orbit.update_layout(
        title="<b>행성 궤도 탑뷰 (우주에서 본 시점)</b>",
        xaxis=dict(range=[-1.4, 1.4], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.4, 1.4], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_geo_orbit, use_container_width=True)
    
    # 2. Geocentric Telescope View
    # Map distance (0.25 to 0.91) to apparent radius (0.5 to 3.0)
    base_radius_geo = 0.8 / geo_data["distance"]
    
    fig_geo_tel = go.Figure()
    
    # Base circle (dark side of Venus)
    fig_geo_tel.add_trace(go.Scatter(
        x=base_radius_geo * np.cos(t_circle),
        y=base_radius_geo * np.sin(t_circle),
        fill="toself",
        fillcolor="#1e293b",
        line=dict(color="#475569", width=1),
        showlegend=False,
        hoverinfo="skip"
    ))
    
    # Phase overlay (illuminated side)
    x_ph_g, y_ph_g = get_phase_coords(geo_data["phase"], base_radius_geo)
    fig_geo_tel.add_trace(go.Scatter(
        x=x_ph_g,
        y=y_ph_g,
        fill="toself",
        fillcolor="#fef08a",
        line=dict(color="#fef08a", width=0),
        showlegend=False,
        hoverinfo="skip"
    ))
    
    fig_geo_tel.update_layout(
        title=f"<b>지구에서 본 금성 망원경 뷰 (시직경 및 위상)</b><br>거리: {geo_data['distance']:.3f} AU | 위상: {geo_data['phase']*100:.1f}%",
        xaxis=dict(range=[-3.5, 3.5], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-3.5, 3.5], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        height=350,
        plot_bgcolor="#090d16",
        paper_bgcolor="#090d16"
    )
    
    st.plotly_chart(fig_geo_tel, use_container_width=True)

# --- Educational Explanations ---
st.markdown('<div class="info-box">', unsafe_allow_html=True)
st.subheader("💡 갈릴레오 갈릴레이의 '스모킹 건(Smoking Gun)': 금성의 위상 변화")
st.markdown("""
1610년, **갈릴레오 갈릴레이**는 스스로 제작한 망원경으로 금성을 관측하다가 역사적인 발견을 하게 됩니다. 
금성이 달처럼 **그믐달에서 시작해 반달을 거쳐 거의 완전한 보름달 모양(Gibbous to Full)**으로 변하는 전체 위상 주기를 목격한 것입니다.

### 🔍 두 우주관의 결정적 증거 비교

* **지구 중심설(천동설)의 한계**:
  천동설(프톨레마이오스 모델)에 따르면, 금성의 주전원 중심은 항상 **지구와 태양을 잇는 일직선상**에 묶여 있어야 합니다. 즉, 금성은 언제나 지구와 태양 사이에 존재하게 됩니다. 
  따라서 태양 빛은 항상 금성의 뒷면(지구 반대편)을 비추므로, 지구에서는 금성의 **그믐달이나 초승달(Crescent) 모양**만 관측되어야 하며, **반달(50%)보다 더 채워진 형태(Gibbous)나 보름달(Full)은 물리적으로 절대 볼 수 없습니다.**

* **태양 중심설(지동설)의 완벽한 증명**:
  반면 지동설(코페르니쿠스 모델)에서는 금성이 태양 주위를 공전합니다. 
  금성이 태양의 반대편(외합 부근)으로 갈 때는 태양 빛을 정면으로 받아 **보름달에 가까운 모습**으로 보입니다. 비록 거리가 멀어져서 크기(시직경)는 아주 작아지지만 말이죠. 
  반대로 금성이 지구와 태양 사이(내합 부근)로 올 때는 거리가 가까워져 **매우 거대한 크기의 그믐달**로 보입니다.

**시뮬레이터에서 '애니메이션 자동 재생'을 켜거나 '시간 슬라이더'를 움직이며 두 망원경 뷰의 차이를 확인해 보세요!** 지동설 모델에서만 금성이 작아지면서 보름달(위상 90% 이상) 모양이 되는 것을 직접 관찰하실 수 있습니다. 이 단순한 기하학적 차이가 수천 년간 지속된 천동설을 무너뜨리는 결정적인 열쇠가 되었습니다.
""")
st.markdown('</div>', unsafe_allow_html=True)
