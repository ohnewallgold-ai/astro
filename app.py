import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 기본 설정 ---
st.set_page_config(page_title="케플러 법칙 시뮬레이션", layout="wide")

# 행성 기본 데이터 (장반경 a (AU), 실제 이심률 e)
planets_data = {
    "수성 (Mercury)": {"a": 0.387, "e": 0.2056},
    "금성 (Venus)": {"a": 0.723, "e": 0.0067},
    "지구 (Earth)": {"a": 1.000, "e": 0.0167},
    "화성 (Mars)": {"a": 1.524, "e": 0.0934},
    "목성 (Jupiter)": {"a": 5.204, "e": 0.0489},
    "가상의 혜성 (Comet)": {"a": 2.000, "e": 0.8000}
}

# --- 케플러 방정식 풀이 함수 ---
def solve_kepler(M, e, tol=1e-6):
    """
    뉴턴-랩슨 법을 이용하여 케플러 방정식(M = E - e*sin(E))의 편심 이각(E)을 구합니다.
    (M: 평균 이각, e: 이심률)
    """
    E = M
    for _ in range(10):
        delta_E = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        E = E - delta_E
        if np.max(np.abs(delta_E)) < tol:
            break
    return E

# --- 사이드바 UI ---
st.sidebar.title("🪐 행성 궤도 설정")

selected_planet = st.sidebar.selectbox("행성 선택", list(planets_data.keys()), index=2)
default_a = planets_data[selected_planet]["a"]
default_e = planets_data[selected_planet]["e"]

st.sidebar.markdown("---")
st.sidebar.subheader("궤도 매개변수 조절")

# 장반경은 선택된 행성 유지, 이심률은 사용자가 조절 가능하도록 설정
a = default_a
e = st.sidebar.slider("이심률 (Eccentricity)", min_value=0.0, max_value=0.95, value=default_e, step=0.01,
                      help="0에 가까울수록 원에 가깝고, 1에 가까울수록 납작한 타원이 됩니다.")

st.sidebar.markdown(f"**현재 선택된 행성 기준 반경 (a)**: {a} AU")

# --- 데이터 생성 ---
# 일정한 시간 간격(dt)으로 평균 이각(M) 생성 (0부터 2pi까지)
# 시간이 일정하게 흐르므로, 애니메이션에서의 속도 변화가 실제 우주에서의 공전 속도 변화를 나타냅니다.
num_frames = 100
M = np.linspace(0, 2 * np.pi, num_frames)
E = solve_kepler(M, e)

# 초점(태양)을 원점(0,0)으로 두었을 때의 행성 좌표 (x, y)
x = a * (np.cos(E) - e)
y = a * np.sqrt(1 - e**2) * np.sin(E)

# 근일점과 원일점 좌표
perihelion_x, perihelion_y = x[0], y[0]               # M=0, E=0
aphelion_x, aphelion_y = x[num_frames//2], y[num_frames//2] # M=pi, E=pi

# --- Plotly 애니메이션 그래프 구성 ---
fig = go.Figure()

# 1. 타원 궤도 선 그리기
fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="궤도", line=dict(color="royalblue", width=2, dash="dot")))

# 2. 태양 (초점 위치: 0, 0)
fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", name="태양", marker=dict(size=20, color="gold", symbol="star")))

# 3. 근일점 표시
fig.add_trace(go.Scatter(x=[perihelion_x], y=[perihelion_y], mode="markers+text", name="근일점",
                         text=["근일점 (가장 빠름)"], textposition="bottom center",
                         marker=dict(size=10, color="red", symbol="x")))

# 4. 원일점 표시
fig.add_trace(go.Scatter(x=[aphelion_x], y=[aphelion_y], mode="markers+text", name="원일점",
                         text=["원일점 (가장 느림)"], textposition="top center",
                         marker=dict(size=10, color="blue", symbol="x")))

# 5. 애니메이션 초기 상태 (행성 및 면적을 휩쓰는 선)
fig.add_trace(go.Scatter(x=[x[0]], y=[y[0]], mode="markers", name="행성", marker=dict(size=15, color="green")))
fig.add_trace(go.Scatter(x=[0, x[0]], y=[0, y[0]], mode="lines", name="동경 벡터", line=dict(color="orange", width=2)))

# --- 애니메이션 프레임 생성 ---
frames = []
for i in range(num_frames):
    frame_data = [
        go.Scatter(x=x, y=y), # 궤도 유지
        go.Scatter(x=[0], y=[0]), # 태양 유지
        go.Scatter(x=[perihelion_x], y=[perihelion_y]), # 근일점 유지
        go.Scatter(x=[aphelion_x], y=[aphelion_y]), # 원일점 유지
        go.Scatter(x=[x[i]], y=[y[i]]), # 움직이는 행성
        go.Scatter(x=[0, x[i]], y=[0, y[i]]) # 움직이는 동경 벡터
    ]
    frames.append(go.Frame(data=frame_data, name=str(i)))

fig.frames = frames

# --- 레이아웃 및 플레이 버튼 설정 ---
axis_range = [-a * (1 + e) - 0.5, a * (1 + e) + 0.5]

fig.update_layout(
    xaxis=dict(range=axis_range, title="x (AU)", zeroline=False),
    yaxis=dict(range=axis_range, title="y (AU)", zeroline=False, scaleanchor="x", scaleratio=1),
    title=f"<b>{selected_planet}의 궤도 시뮬레이션 (이심률: {e:.3f})</b>",
    hovermode="closest",
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        y=1.1, x=0.1,
        buttons=[
            dict(label="▶ 재생", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), transition=dict(duration=0), fromcurrent=True, mode="immediate")]),
            dict(label="⏸ 정지", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))])
        ]
    )]
)

# --- 메인 화면 렌더링 ---
st.title("🌍 케플러 법칙과 행성 운동 시뮬레이션")
st.markdown("""
이 시뮬레이션은 **케플러 제1법칙(타원 궤도의 법칙)**과 **제2법칙(면적 속도 일정의 법칙)**을 시각적으로 보여줍니다.  
▶ **재생** 버튼을 눌러 행성의 움직임을 관찰해 보세요!
""")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("💡 학습 포인트: 이심률을 증가시키면 공전속도는 어떻게 변할까?")
st.markdown("""
왼쪽 사이드바에서 **이심률(Eccentricity)** 슬라이더를 $0$에서 $0.8$ 이상으로 서서히 올려보세요. 궤도가 점점 찌그러진 타원 모양으로 변합니다. 애니메이션을 재생해보면 다음 사실을 확인할 수 있습니다.

1. **근일점(태양과 가장 가까운 곳)**: 행성이 **매우 빠르게** 휙 지나갑니다.
2. **원일점(태양과 가장 먼 곳)**: 행성이 **매우 느리게** 이동합니다.

**왜 그럴까요?**  
케플러 제2법칙에 따르면 행성과 태양을 연결하는 선(주황색 선)은 **같은 시간 동안 항상 같은 면적**을 휩쓸고 지나가야 합니다. 
* 태양과 가까울 때는 반지름이 짧으므로, 같은 면적을 채우려면 각도를 많이 움직여야 해서 **속도가 빨라집니다.**
* 태양과 멀어지면 반지름이 길어지므로 조금만 움직여도 넓은 면적을 채우게 되어 **속도가 느려집니다.**

**결론:** 이심률이 커질수록 근일점과 원일점의 거리 차이가 커지게 되며, 이에 따라 **최대 공전 속도(근일점)와 최소 공전 속도(원일점)의 극적인 차이가 발생**하게 됩니다!
""")
