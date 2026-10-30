import json
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "initiatives.json"
DATA_FILE.parent.mkdir(exist_ok=True)

st.set_page_config(page_title="ВЕКТОР | Project Intelligence", page_icon="◈", layout="wide")

# ── Visual system ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#17172b; --ink2:#26264a; --panel:#ffffff; --line:#e6e7f0; --blue:#5146f5; --lime:#c8f169; --mint:#baf3df; --lav:#dcd7ff; --muted:#777b91; --white:#fbfbff; }
.stApp { background:radial-gradient(ellipse at 90% 0%,#e9e8ff 0%,#f6f6fb 38%,#f8f8f4 100%); color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#17172b; border-right:1px solid #29294b; }
[data-testid="stSidebar"] * { color:#f5f5ff !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#aaaac8 !important; }
h1,h2,h3,h4,p,label,span { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { color:#19192f !important; letter-spacing:-.045em; }
h1 { font-weight:800 !important; }
p,label { color:#4f5269; }
.stCaption,[data-testid="stCaptionContainer"] { color:#85879a !important; }
.hero { position:relative; overflow:hidden; background:linear-gradient(115deg,#5146f5 0%,#6259f8 58%,#8378ff 100%); border:0; border-radius:25px; padding:35px 38px; margin:4px 0 24px; box-shadow:0 20px 48px rgba(81,70,245,.18); }
.hero:after { content:""; position:absolute; width:320px; height:320px; right:-45px; top:-170px; border:1px solid rgba(255,255,255,.3); border-radius:50%; box-shadow:0 0 0 30px rgba(255,255,255,.07),0 0 0 65px rgba(255,255,255,.045); }
.eyebrow { color:#d9ff9c; text-transform:uppercase; letter-spacing:.2em; font-size:10px; font-weight:800; margin-bottom:11px; }
.hero h1 { color:#fff !important; font-size:clamp(30px,4vw,45px); margin:0; line-height:1.1; }
.hero p { color:#e3e1ff; margin:11px 0 0; font-size:14px; max-width:720px; }
.metric { background:rgba(255,255,255,.92); border:1px solid #e8e8f2; border-radius:19px; padding:20px; min-height:128px; box-shadow:0 9px 28px rgba(35,35,70,.055); }
.metric-label { color:#85879d; font-size:10px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
.metric-value { color:#242344; font-size:34px; line-height:1.2; font-weight:800; margin-top:11px; letter-spacing:-.05em; }
.metric-note { color:#9294a7; font-size:11px; margin-top:5px; }
.panel { background:rgba(255,255,255,.88); border:1px solid #e8e8f2; border-radius:20px; padding:22px 23px; box-shadow:0 10px 30px rgba(35,35,70,.045); }
.panel-kicker { color:#5146f5; font-size:10px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.pill { display:inline-block; background:#effbdc; color:#42631a; padding:5px 10px; border-radius:30px; font-size:10px; font-weight:800; letter-spacing:.04em; }
div.stButton > button,div.stDownloadButton > button { border-radius:11px; border:1px solid #dcdcf0; background:#fff; color:#29294b; font-weight:700; transition:all .2s ease; }
div.stButton > button:hover,div.stDownloadButton > button:hover { border-color:#5146f5; color:#5146f5; background:#f7f6ff; }
div.stButton > button[kind="primary"],div.stFormSubmitButton > button { background:linear-gradient(105deg,#5146f5,#756bff); border:0; color:white; font-weight:800; box-shadow:0 8px 20px rgba(81,70,245,.2); }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#5146f5,#b9ee63); }
[data-baseweb="input"] > div,[data-baseweb="select"] > div,[data-baseweb="textarea"] > div { background:#fff !important; border-color:#dedfee !important; border-radius:10px !important; }
input,textarea { color:#242344 !important; }
[data-testid="stDataFrame"] { border:1px solid #e5e5f0; border-radius:13px; overflow:hidden; }
[data-testid="stExpander"] { border:1px solid #e5e5f0; border-radius:13px; background:#fff; }
[data-testid="stMetric"] { background:#fff; padding:14px 15px; border:1px solid #e7e7f0; border-radius:13px; }
hr { border-color:#e4e5ef; }
.stRadio label { color:#e3e3f6 !important; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

CRITERIA = [
    ("Актуальность проблемы", 20, "Насколько значима проблема, которую решает инициатива?"),
    ("Потенциальный эффект", 20, "Какой измеримый результат может дать инициатива?"),
    ("Целевая аудитория", 15, "Насколько ясно определены пользователи или благополучатели?"),
    ("Готовность к реализации", 15, "Есть ли план, этапы и понятная модель реализации?"),
    ("Компетенции команды", 10, "Есть ли у команды необходимые знания и опыт?"),
    ("Ресурсное обеспечение", 10, "Понятны ли необходимые ресурсы и источники их получения?"),
    ("Масштабируемость", 10, "Можно ли расширить инициативу или повторить её в других организациях?"),
]
STATUSES = ["Новая", "На оценке", "Требует доработки", "Готова к запуску", "В реализации", "Завершена"]
DIRECTIONS = ["Наука", "Образование", "Технологическое предпринимательство"]

def score_index(scores):
    return round(sum(int(scores.get(n, 1)) * w for n, w, _ in CRITERIA) / 5)

def recommendation(index, scores):
    weakest = sorted([(n, int(scores.get(n, 1))) for n, _, _ in CRITERIA], key=lambda x: x[1])[:2]
    if index >= 80:
        title, action = "Высокая готовность", "Сформируйте дорожную карту, закрепите ответственных и определите контрольные показатели."
    elif index >= 60:
        title, action = "Перспективная инициатива", "Проведите точечную доработку слабых критериев и повторную экспертную оценку."
    elif index >= 40:
        title, action = "Нужно методическое сопровождение", "Помогите команде уточнить целевую аудиторию, ожидаемый эффект и план реализации."
    else:
        title, action = "Требуется существенная проработка", "Организуйте установочную консультацию и пересоберите концепцию инициативы."
    return title, action, weakest

def make_plan(scores):
    tasks = {
        "Актуальность проблемы": "Подготовить краткое обоснование проблемы и подтверждающие данные",
        "Потенциальный эффект": "Сформулировать 2–3 измеримых показателя результата",
        "Целевая аудитория": "Описать целевые группы и провести короткие интервью",
        "Готовность к реализации": "Разбить реализацию на этапы и определить контрольные точки",
        "Компетенции команды": "Составить карту компетенций и закрыть недостающие роли",
        "Ресурсное обеспечение": "Составить предварительную смету и определить источники ресурсов",
        "Масштабируемость": "Описать сценарий тиражирования и потенциальных партнёров",
    }
    weak = sorted([(n, int(scores.get(n, 1))) for n, _, _ in CRITERIA], key=lambda x: x[1])[:3]
    return [{"task": tasks[n], "criterion": n, "score": s} for n, s in weak]

def load_data():
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_data(items):
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def idx(item):
    return score_index(item.get("scores", {}))

def hero(title, subtitle, kicker="PROJECT INTELLIGENCE / VEKТOR"):
    st.markdown(f"<div class='hero'><div class='eyebrow'>{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)

def metric(label, value, note):
    st.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)

def panel_title(kicker, title):
    st.markdown(f"<div class='panel-kicker'>{kicker}</div>", unsafe_allow_html=True)
    st.subheader(title)

if "initiatives" not in st.session_state:
    st.session_state.initiatives = load_data()
if "last_result" not in st.session_state:
    st.session_state.last_result = None
items = st.session_state.initiatives

with st.sidebar:
    st.markdown("<div style='padding:12px 5px 24px'><div style='font-size:10px;letter-spacing:.2em;color:#c8f169;font-weight:800'>PROJECT INTELLIGENCE</div><div style='font-size:34px;font-weight:800;letter-spacing:-.06em;color:#f5f5ff'>ВЕКТОР<span style='color:#c8f169'>.</span></div><div style='font-size:11px;color:#aaaac8'>Навигатор инициатив</div></div>", unsafe_allow_html=True)
    page = st.radio("РАБОЧЕЕ ПРОСТРАНСТВО", ["Обзор", "Новая оценка", "Банк инициатив", "Аналитика", "О проекте"], label_visibility="visible")
    st.markdown("---")
    st.markdown("<div style='font-size:10px;color:#c8f169;letter-spacing:.12em;font-weight:800'>DEMO EDITION · 2.0</div>", unsafe_allow_html=True)
    st.caption("Инструмент экспертной оценки и сопровождения проектных инициатив.")

if page == "Обзор":
    hero("От идеи — к измеримому результату.", "Рабочая панель команды: оценивайте потенциал инициатив, отслеживайте портфель и определяйте следующие шаги.")
    total = len(items)
    avg = round(sum(idx(x) for x in items) / total) if total else 0
    active = sum(x.get("status") not in ["Завершена"] for x in items)
    ready = sum(idx(x) >= 80 for x in items)
    attention = sum(idx(x) < 60 for x in items)
    c = st.columns(4)
    for col, args in zip(c, [("ПОРТФЕЛЬ", total, "Всего инициатив"), ("СРЕДНЯЯ ГОТОВНОСТЬ", f"{avg}%", "Взвешенный индекс"), ("В РАБОТЕ", active, "Активные инициативы"), ("ЗОНА ВНИМАНИЯ", attention, "Индекс ниже 60%")]):
        with col: metric(*args)
    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        panel_title("PORTFOLIO / 01", "Последние инициативы")
        if items:
            recent = sorted(items, key=lambda x: x.get("id", 0), reverse=True)[:6]
            df = pd.DataFrame([{"Инициатива": x["name"], "Направление": x["direction"], "Статус": x["status"], "Готовность": f"{idx(x)}%"} for x in recent])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Портфель пока пуст. Создайте первую инициативу в разделе «Новая оценка».")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        panel_title("PORTFOLIO / 02", "Структура портфеля")
        if items:
            counts = pd.DataFrame([{"Направление": x["direction"]} for x in items]).value_counts().reset_index(name="Количество")
            fig = px.pie(counts, names="Направление", values="Количество", hole=.68, color_discrete_sequence=["#5146f5", "#b9ee63", "#ff8e83"])
            fig.update_layout(margin=dict(t=5,b=5,l=0,r=0), legend_title=None, paper_bgcolor="rgba(0,0,0,0)", font_color="#dce8f8", height=260)
            fig.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='padding:40px 5px;color:#8197b2;text-align:center'>Диаграмма появится после добавления данных</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    panel_title("QUICK INSIGHT / 03", "На что обратить внимание")
    if items:
        weakest_item = min(items, key=idx)
        weak = make_plan(weakest_item.get("scores", {}))[0]
        st.markdown(f"**{weakest_item['name']}** — самая низкая готовность в портфеле ({idx(weakest_item)}%).")
        st.caption(f"Рекомендуемый следующий шаг: {weak['task'].lower()}.")
    else:
        st.write("Добавьте инициативу, чтобы получить первую рекомендацию по портфелю.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Индекс — прозрачная экспертная балльная модель. Он не является прогнозом успеха или автоматическим решением о финансировании.")

elif page == "Новая оценка":
    hero("Новая оценка инициативы", "Заполните карточку проекта. ВЕКТОР рассчитает индекс готовности и предложит конкретные действия.")
    with st.form("assessment"):
        a, b = st.columns(2)
        with a:
            name = st.text_input("Название инициативы *", placeholder="Например, Центр инженерных компетенций")
            direction = st.selectbox("Направление", DIRECTIONS)
            owner = st.text_input("Ответственный специалист", placeholder="Имя Фамилия")
        with b:
            status = st.selectbox("Текущий статус", STATUSES, index=1)
            created = st.date_input("Дата поступления", value=date.today())
            priority = st.selectbox("Приоритет", ["Высокий", "Средний", "Низкий"], index=1)
        description = st.text_area("Краткое описание и решаемая проблема", placeholder="Для кого создаётся инициатива? Какую проблему она решает?", height=100)
        st.markdown("### Экспертная оценка")
        st.caption("Шкала от 1 до 5. Вес каждого критерия автоматически учитывается в итоговом индексе.")
        scores = {}
        for i, (criterion, weight, help_text) in enumerate(CRITERIA):
            x, y = st.columns([3, 1])
            with x:
                st.markdown(f"**{i+1}. {criterion}** · {weight}%")
                st.caption(help_text)
            with y:
                scores[criterion] = st.select_slider("Оценка", options=[1,2,3,4,5], value=3, key=f"new_score_{i}")
        submitted = st.form_submit_button("Рассчитать и сохранить инициативу", type="primary", use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("Укажите название инициативы.")
        else:
            new = {"id": max([x.get("id", 0) for x in items], default=0)+1, "name": name.strip(), "direction": direction, "owner": owner.strip() or "Не назначен", "description": description.strip(), "status": status, "created": str(created), "priority": priority, "scores": scores}
            items.append(new)
            save_data(items)
            st.session_state.last_result = new
            st.success("Инициатива добавлена в портфель.")
    if st.session_state.last_result:
        r = st.session_state.last_result
        score = idx(r)
        title, action, weak = recommendation(score, r["scores"])
        st.markdown("---")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        panel_title("ASSESSMENT RESULT", f"Результат: {r['name']}")
        x, y = st.columns([1, 2])
        with x:
            st.metric("Индекс готовности", f"{score}%")
            st.progress(score/100)
        with y:
            st.subheader(title)
            st.write(action)
            st.caption("Критерии для первоочередной проработки: " + ", ".join(f"{n} ({s}/5)" for n,s in weak))
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("### Персональный план сопровождения")
        plan = make_plan(r["scores"])
        for n, task in enumerate(plan, 1):
            st.markdown(f"**{n}. {task['task']}**  \n<small style='color:#8197b2'>Критерий: {task['criterion']} · оценка {task['score']}/5</small>", unsafe_allow_html=True)
        report = f"# Паспорт инициативы: {r['name']}\\n\\n- Направление: {r['direction']}\\n- Ответственный: {r['owner']}\\n- Статус: {r['status']}\\n- Приоритет: {r.get('priority','Средний')}\\n- Дата: {r['created']}\\n- Индекс готовности: {score}%\\n\\n## Описание\\n{r.get('description','—')}\\n\\n## Рекомендация\\n{title}. {action}\\n\\n## План сопровождения\\n" + "".join(f"- [ ] {t['task']} ({t['criterion']})\\n" for t in plan)
        st.download_button("Скачать паспорт инициативы (.md)", report, file_name="vektor_initiative_report.md", mime="text/markdown")

elif page == "Банк инициатив":
    hero("Банк инициатив", "Единое пространство проектного портфеля — поиск, фильтрация, контроль статусов и планы сопровождения.")
    f1, f2, f3 = st.columns([2,1,1])
    with f1: query = st.text_input("Поиск по портфелю", placeholder="Название, описание или ответственный...")
    with f2: direction_filter = st.selectbox("Направление", ["Все"]+DIRECTIONS)
    with f3: status_filter = st.selectbox("Статус", ["Все"]+STATUSES)
    filtered = [x for x in items if query.lower() in (x["name"]+" "+x.get("description","")+" "+x.get("owner","")).lower() and (direction_filter=="Все" or x["direction"]==direction_filter) and (status_filter=="Все" or x["status"]==status_filter)]
    st.caption(f"Найдено инициатив: {len(filtered)} из {len(items)}")
    if not filtered:
        st.info("Ничего не найдено. Измените фильтры или добавьте новую инициативу.")
    for item in filtered:
        score = idx(item)
        with st.expander(f"{item['name']}  ·  {score}% готовности  ·  {item['status']}"):
            left, right = st.columns([1.6,1])
            with left:
                st.markdown(f"**Направление:** {item['direction']}  \n**Ответственный:** {item.get('owner','Не назначен')}  \n**Поступила:** {item.get('created','—')}  \n**Приоритет:** {item.get('priority','Средний')}")
                st.write(item.get("description") or "Описание не добавлено.")
                st.progress(score/100)
                title, action, weak = recommendation(score, item.get("scores", {}))
                st.info(f"{title}. {action}")
                with st.expander("План сопровождения"):
                    for task in make_plan(item.get("scores", {})):
                        st.markdown(f"- {task['task']} · {task['score']}/5")
            with right:
                new_status = st.selectbox("Изменить статус", STATUSES, index=STATUSES.index(item.get("status","Новая")) if item.get("status","Новая") in STATUSES else 0, key=f"status_{item['id']}")
                if st.button("Сохранить статус", key=f"save_{item['id']}", use_container_width=True):
                    item["status"] = new_status
                    save_data(items)
                    st.success("Статус обновлён.")
                    st.rerun()
                if st.button("Удалить инициативу", key=f"delete_{item['id']}", use_container_width=True):
                    st.session_state.initiatives = [x for x in items if x["id"] != item["id"]]
                    save_data(st.session_state.initiatives)
                    st.rerun()

elif page == "Аналитика":
    hero("Аналитика портфеля", "Показатели готовности, структура направлений и распределение инициатив по статусам.")
    if not items:
        st.info("Добавьте инициативы, чтобы сформировать аналитику.")
    else:
        df = pd.DataFrame([{"Инициатива":x["name"], "Направление":x["direction"], "Статус":x["status"], "Индекс":idx(x), "Ответственный":x.get("owner","Не назначен"), "Приоритет":x.get("priority","Средний")} for x in items])
        c = st.columns(4)
        with c[0]: metric("СРЕДНИЙ ИНДЕКС", f"{round(df['Индекс'].mean())}%", "По всему портфелю")
        with c[1]: metric("МАКСИМУМ", f"{df['Индекс'].max()}%", "Наивысшая готовность")
        with c[2]: metric("НИЗКАЯ ГОТОВНОСТЬ", int((df["Индекс"]<40).sum()), "Индекс ниже 40%")
        with c[3]: metric("НА ЗАПУСКЕ", int((df["Статус"]=="Готова к запуску").sum()), "Готовы к следующему этапу")
        left, right = st.columns(2)
        with left:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            panel_title("READINESS / 01", "Индекс по инициативам")
            fig = px.bar(df.sort_values("Индекс"), x="Индекс", y="Инициатива", orientation="h", color="Индекс", range_color=[0,100], color_continuous_scale=["#ff9a8d","#8177ff","#5146f5"])
            fig.update_layout(margin=dict(t=5,b=5,l=0,r=0), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dce8f8", height=350, xaxis=dict(range=[0,100], gridcolor="#203958"), yaxis=dict(gridcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            panel_title("STATUS / 02", "Распределение по статусам")
            status_df = df["Статус"].value_counts().reset_index()
            status_df.columns = ["Статус","Количество"]
            fig2 = px.pie(status_df, names="Статус", values="Количество", hole=.62, color_discrete_sequence=["#5146f5","#b9ee63","#ff8e83","#8c80ff","#63cdb2","#8b91a8"])
            fig2.update_layout(margin=dict(t=5,b=5,l=0,r=0), legend_title=None, paper_bgcolor="rgba(0,0,0,0)", font_color="#dce8f8", height=350)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("### Реестр для управленческого отчёта")
        st.dataframe(df, use_container_width=True, hide_index=True)
        a,b = st.columns(2)
        with a:
            st.download_button("Скачать отчёт CSV", df.to_csv(index=False).encode("utf-8-sig"), "vektor_portfolio.csv", "text/csv", use_container_width=True)
        with b:
            st.download_button("Скачать резервную копию JSON", json.dumps(items,ensure_ascii=False,indent=2).encode("utf-8"), "vektor_backup.json", "application/json", use_container_width=True)

elif page == "О проекте":
    hero("Инструмент для проектных команд.", "ВЕКТОР помогает специалистам научной, образовательной и технологической сфер структурировать поток инициатив и выбирать следующие шаги.")
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    panel_title("PRODUCT CONCEPT", "Какую проблему решает ВЕКТОР")
    st.write("В проектных командах первичная оценка инициатив часто ведётся в разрозненных таблицах и переписках. Из-за этого сложно сравнивать идеи по единым правилам, видеть общую картину портфеля и понимать, кому и какая поддержка нужна.")
    st.write("ВЕКТОР собирает первичную информацию в едином реестре, использует прозрачную взвешенную модель оценки и превращает слабые места инициативы в конкретный план сопровождения.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    panel_title("METHODOLOGY", "Модель оценки")
    st.write("Каждый критерий оценивается по шкале от 1 до 5. Итоговый индекс — сумма произведений баллов на вес критериев, делённая на 5.")
    st.dataframe(pd.DataFrame([{"Критерий":n,"Вес":f"{w}%","Что оценивается":d} for n,w,d in CRITERIA]), use_container_width=True, hide_index=True)
    st.markdown("**Интерпретация индекса:** 80–100% — высокая готовность; 60–79% — точечная доработка; 40–59% — методическое сопровождение; ниже 40% — существенная проработка.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Учебный прототип. Индекс является экспертной оценкой, а рекомендации — вспомогательным инструментом, не заменяющим профессиональное решение.")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#647d99;font-size:10px;letter-spacing:.08em;padding:8px'>ВЕКТОР · PROJECT INTELLIGENCE · EDUCATION / SCIENCE / TECHNOLOGY</div>", unsafe_allow_html=True)
