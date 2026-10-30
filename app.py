import json
from pathlib import Path
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "initiatives.json"
DATA_FILE.parent.mkdir(exist_ok=True)

st.set_page_config(page_title="ВЕКТОР — навигатор инициатив", page_icon="🧭", layout="wide")

# ---------- Дизайн ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');
:root { --forest:#242329; --pine:#51445D; --sage:#A99AB8; --sand:#C6A779; --cream:#F6F3EE; --ink:#302D33; }
.stApp { background: #F6F3EE; color: var(--ink); font-family: 'Manrope', sans-serif; }
[data-testid="stSidebar"] { background: #242329; }
[data-testid="stSidebar"] * { color: #F6F3EE !important; }
[data-testid="stSidebar"] .stRadio label { padding: 7px 4px; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; color: #242329; }
.hero { background: linear-gradient(120deg,#242329 0%,#51445D 72%,#796786 100%); padding: 34px 36px; border-radius: 22px; box-shadow: 0 14px 36px rgba(36,35,41,.12); color: #F6F3EE; margin-bottom: 22px; }
.hero h1 { color:#F6F3EE !important; font-family:'Playfair Display',serif !important; font-size:43px; letter-spacing:-.04em; margin:0; }
.hero p { color:#D5E0D8; font-size:15px; margin:8px 0 0 0; }
.metric { background:#FFFEFC; border:1px solid #E8E2DA; border-radius:17px; padding:21px 22px; min-height:116px; box-shadow: 0 5px 18px rgba(36,35,41,.035); }
.metric-label { color:#817985; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.07em; }
.metric-value { color:#242329; font-size:31px; font-weight:800; margin-top:7px; }
.metric-note { color:#938B96; font-size:12px; margin-top:2px; }
.panel { background:#FFFEFC; border:1px solid #E8E2DA; border-radius:17px; padding:22px; box-shadow: 0 5px 18px rgba(36,35,41,.035); }
.tag { display:inline-block; background:#EEE8F0; color:#665271; border-radius:20px; padding:5px 10px; font-size:11px; font-weight:700; }
.small-muted { color:#7B867F; font-size:12px; }
div.stButton > button[kind="primary"] { background:#51445D; border:0; border-radius:11px; color:white; font-weight:700; padding:.65rem 1.1rem; box-shadow:0 5px 14px rgba(81,68,93,.16); }
div.stButton > button[kind="primary"]:hover { background:#665572; color:white; border:0; }
.stProgress > div > div > div > div { background:#A99AB8; }
hr { border-color:#E8E2DA; }
</style>
""", unsafe_allow_html=True)

CRITERIA = [
    ("Актуальность проблемы", 20, "Насколько значима проблема, на решение которой направлена инициатива?"),
    ("Потенциальный эффект", 20, "Какой измеримый результат может дать инициатива?"),
    ("Целевая аудитория", 15, "Насколько ясно определены пользователи или благополучатели?"),
    ("Готовность к реализации", 15, "Есть ли план, этапы и понятная модель реализации?"),
    ("Компетенции команды", 10, "Есть ли у команды необходимые знания и опыт?"),
    ("Ресурсное обеспечение", 10, "Понятны ли необходимые ресурсы и источники их получения?"),
    ("Масштабируемость", 10, "Можно ли расширить инициативу или повторить её в других организациях?"),
]
STATUSES = ["Новая", "На оценке", "Требует доработки", "Готова к запуску", "В реализации"]
DIRECTIONS = ["Наука", "Образование", "Технологическое предпринимательство"]

def score_index(scores):
    return round(sum(scores.get(name, 1) * weight for name, weight, _ in CRITERIA) / 5)

def recommendation(index, scores):
    weakest = sorted([(name, scores.get(name, 1)) for name, _, _ in CRITERIA], key=lambda x: x[1])[:2]
    if index >= 80:
        title = "Готова к переходу к реализации"
        action = "Сформировать дорожную карту, закрепить ответственных и определить контрольные показатели."
    elif index >= 60:
        title = "Перспективная инициатива"
        action = "Провести точечную доработку слабых критериев и повторную экспертную оценку."
    elif index >= 40:
        title = "Нужно методическое сопровождение"
        action = "Помочь команде уточнить целевую аудиторию, ожидаемый эффект и план реализации."
    else:
        title = "Требуется существенная проработка"
        action = "Организовать установочную консультацию и пересобрать концепцию инициативы."
    weak_text = ", ".join(f"{n} ({v}/5)" for n, v in weakest)
    return title, action, weak_text

def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    seed = [
        {"id":1,"name":"Лаборатория прикладных исследований","direction":"Наука","owner":"Ирина Волкова","description":"Создание междисциплинарной лаборатории для прикладных исследований и работы со студентами.","status":"На оценке","created":str(date.today()),"scores":{"Актуальность проблемы":5,"Потенциальный эффект":4,"Целевая аудитория":4,"Готовность к реализации":4,"Компетенции команды":5,"Ресурсное обеспечение":3,"Масштабируемость":4}},
        {"id":2,"name":"Школа технологических лидеров","direction":"Образование","owner":"Алексей Миронов","description":"Практическая программа развития компетенций для студентов и молодых специалистов.","status":"Требует доработки","created":str(date.today()),"scores":{"Актуальность проблемы":4,"Потенциальный эффект":4,"Целевая аудитория":5,"Готовность к реализации":3,"Компетенции команды":4,"Ресурсное обеспечение":2,"Масштабируемость":4}},
        {"id":3,"name":"Студенческий pre-seed акселератор","direction":"Технологическое предпринимательство","owner":"Мария Орлова","description":"Поддержка команд на ранней стадии разработки технологических продуктов.","status":"Готова к запуску","created":str(date.today()),"scores":{"Актуальность проблемы":5,"Потенциальный эффект":5,"Целевая аудитория":4,"Готовность к реализации":4,"Компетенции команды":4,"Ресурсное обеспечение":4,"Масштабируемость":5}},
        {"id":4,"name":"Открытый курс научной коммуникации","direction":"Образование","owner":"Дмитрий Соколов","description":"Курс по популяризации научных результатов и работе с широкой аудиторией.","status":"В реализации","created":str(date.today()),"scores":{"Актуальность проблемы":4,"Потенциальный эффект":3,"Целевая аудитория":4,"Готовность к реализации":5,"Компетенции команды":4,"Ресурсное обеспечение":4,"Масштабируемость":3}},
    ]
    save_data(seed)
    return seed

def save_data(items):
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

if "initiatives" not in st.session_state:
    st.session_state.initiatives = load_data()
if "draft_result" not in st.session_state:
    st.session_state.draft_result = None

items = st.session_state.initiatives

with st.sidebar:
    st.markdown("<div style='padding:8px 4px 24px'><div style='font-size:12px;letter-spacing:.22em;color:#C6A779;font-weight:800'>PROJECT INTELLIGENCE</div><div style='font-family:Playfair Display;font-size:35px;font-weight:700;color:#F6F3EE'>ВЕКТОР</div><div style='font-size:12px;color:#D8CFDE'>Навигатор инициатив</div></div>", unsafe_allow_html=True)
    page = st.radio("РАЗДЕЛЫ", ["Главная", "Оценить инициативу", "Банк инициатив", "Аналитика"], label_visibility="visible")
    st.markdown("---")
    st.caption("ДЕМО-ВЕРСИЯ · 1.0")
    st.caption("Экспертная оценка по прозрачной балльной модели.")

def hero(title, subtitle):
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)

def metric(label, value, note=""):
    st.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)

def index_of(item):
    return score_index(item.get("scores", {}))

if page == "Главная":
    hero("От идеи — к реализации.", "Единая точка входа для оценки, развития и сопровождения научных и образовательных инициатив.")
    total = len(items)
    avg = round(sum(index_of(x) for x in items)/total) if total else 0
    in_review = sum(x["status"] in ["Новая","На оценке","Требует доработки"] for x in items)
    ready = sum(index_of(x) >= 80 for x in items)
    c = st.columns(4)
    with c[0]: metric("Всего инициатив", total, "В банке инициатив")
    with c[1]: metric("Средняя готовность", f"{avg}%", "Взвешенный индекс")
    with c[2]: metric("На сопровождении", in_review, "Новые и требующие внимания")
    with c[3]: metric("Высокая готовность", ready, "Индекс 80% и выше")
    st.write("")
    left, right = st.columns([1.25,1])
    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Последние инициативы")
        if items:
            df = pd.DataFrame([{"Инициатива":x["name"],"Направление":x["direction"],"Статус":x["status"],"Готовность":index_of(x)} for x in sorted(items,key=lambda x:x.get("id",0), reverse=True)[:5]])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Пока нет инициатив. Добавьте первую в разделе «Оценить инициативу».")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Структура банка")
        if items:
            counts = pd.DataFrame([{"Направление":x["direction"]} for x in items]).value_counts().reset_index(name="Количество")
            fig = px.pie(counts, names="Направление", values="Количество", hole=.62, color_discrete_sequence=["#51445D","#A99AB8","#C6A779"])
            fig.update_layout(margin=dict(t=5,b=5,l=5,r=5), legend_title=None, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#302D33")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Диаграмма появится после добавления инициатив.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Индекс готовности — результат взвешенной экспертной оценки по семи критериям. Это не прогноз успеха и не решение о финансировании.")

elif page == "Оценить инициативу":
    hero("Оценить инициативу", "Заполните карточку, чтобы получить индекс готовности и рекомендации по дальнейшим действиям.")
    with st.form("assessment_form"):
        a,b = st.columns(2)
        with a:
            name = st.text_input("Название инициативы *", placeholder="Например, Центр инженерных компетенций")
            direction = st.selectbox("Направление", DIRECTIONS)
            owner = st.text_input("Ответственный специалист", placeholder="Фамилия Имя")
        with b:
            status = st.selectbox("Текущий статус", STATUSES, index=1)
            created = st.date_input("Дата поступления", value=date.today())
        description = st.text_area("Краткое описание", placeholder="Какую проблему решает инициатива? Для кого и каким способом?", height=100)
        st.markdown("### Экспертная оценка")
        st.caption("Оцените каждый критерий от 1 (низкая проработанность) до 5 (высокая). Вес критерия учитывается автоматически.")
        scores = {}
        for i,(criterion,weight,help_text) in enumerate(CRITERIA):
            col1,col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{i+1}. {criterion}** · вес {weight}%")
                st.caption(help_text)
            with col2:
                scores[criterion] = st.select_slider(criterion, options=[1,2,3,4,5], value=3, label_visibility="collapsed", key=f"score_{i}")
        submitted = st.form_submit_button("Рассчитать индекс и сохранить", type="primary", use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("Укажите название инициативы.")
        else:
            idx = score_index(scores)
            title,action,weak = recommendation(idx,scores)
            new_item = {"id":max([x.get("id",0) for x in items], default=0)+1,"name":name.strip(),"direction":direction,"owner":owner.strip() or "Не назначен","description":description.strip(),"status":status,"created":str(created),"scores":scores}
            items.append(new_item)
            save_data(items)
            st.session_state.draft_result = {"index":idx,"title":title,"action":action,"weak":weak,"name":name.strip()}
            st.success("Инициатива сохранена в банке.")
    if st.session_state.draft_result:
        r = st.session_state.draft_result
        st.markdown("---")
        st.subheader(f"Результат оценки: {r['name']}")
        x,y = st.columns([1,2])
        with x:
            st.metric("Индекс готовности", f"{r['index']}%")
            st.progress(r["index"]/100)
        with y:
            st.markdown(f"### {r['title']}")
            st.write(r["action"])
            st.caption(f"Критерии для первоочередной проработки: {r['weak']}.")

elif page == "Банк инициатив":
    hero("Банк инициатив", "Все поступившие идеи в одном пространстве — с поиском, фильтрами и понятным статусом.")
    f1,f2,f3 = st.columns([2,1,1])
    with f1: query = st.text_input("Поиск", placeholder="Название, описание или ответственный...")
    with f2: dir_filter = st.selectbox("Направление", ["Все"]+DIRECTIONS)
    with f3: status_filter = st.selectbox("Статус", ["Все"]+STATUSES)
    filtered = [x for x in items if (query.lower() in (x["name"]+" "+x.get("description","")+" "+x.get("owner","")).lower()) and (dir_filter=="Все" or x["direction"]==dir_filter) and (status_filter=="Все" or x["status"]==status_filter)]
    st.caption(f"Найдено инициатив: {len(filtered)}")
    if not filtered:
        st.info("По заданным условиям ничего не найдено.")
    for item in filtered:
        idx = index_of(item)
        with st.expander(f"{item['name']}  ·  {idx}% готовности  ·  {item['status']}"):
            l,r = st.columns([2,1])
            with l:
                st.markdown(f"**Направление:** {item['direction']}  \n**Ответственный:** {item.get('owner','Не назначен')}  \n**Дата поступления:** {item.get('created','—')}")
                st.write(item.get("description") or "Описание не добавлено.")
                st.progress(idx/100)
            with r:
                st.markdown("**Изменить статус**")
                new_status = st.selectbox("Статус", STATUSES, index=STATUSES.index(item["status"]), key=f"status_{item['id']}", label_visibility="collapsed")
                if st.button("Сохранить статус", key=f"save_{item['id']}"):
                    item["status"] = new_status
                    save_data(items)
                    st.success("Статус обновлён.")
                    st.rerun()
                if st.button("Удалить инициативу", key=f"del_{item['id']}"):
                    st.session_state.initiatives = [x for x in items if x["id"] != item["id"]]
                    save_data(st.session_state.initiatives)
                    st.rerun()

elif page == "Аналитика":
    hero("Аналитика", "Сводная картина по портфелю инициатив для принятия управленческих решений.")
    if not items:
        st.info("Добавьте инициативы, чтобы увидеть аналитику.")
    else:
        df = pd.DataFrame([{"Инициатива":x["name"],"Направление":x["direction"],"Статус":x["status"],"Индекс готовности":index_of(x),"Ответственный":x.get("owner","")} for x in items])
        avg = round(df["Индекс готовности"].mean())
        c1,c2,c3 = st.columns(3)
        with c1: metric("Средняя готовность",f"{avg}%","По текущему портфелю")
        with c2: metric("Максимальный индекс",f"{df['Индекс готовности'].max()}%","Лучшая оценка")
        with c3: metric("Инициатив с низким индексом",int((df["Индекс готовности"]<40).sum()),"Нуждаются в глубокой проработке")
        left,right = st.columns(2)
        with left:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.subheader("Готовность по инициативам")
            fig = px.bar(df.sort_values("Индекс готовности"), x="Индекс готовности", y="Инициатива", orientation="h", color="Индекс готовности", color_continuous_scale=["#C6A779","#A99AB8","#51445D"], range_color=[0,100])
            fig.update_layout(margin=dict(t=5,b=5,l=5,r=5), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.subheader("Распределение по статусам")
            status_df = df["Статус"].value_counts().reset_index()
            status_df.columns = ["Статус","Количество"]
            fig2 = px.pie(status_df,names="Статус",values="Количество",hole=.58,color_discrete_sequence=["#51445D","#A99AB8","#C6A779","#B9AFC1","#D7C9B7"])
            fig2.update_layout(margin=dict(t=5,b=5,l=5,r=5),legend_title=None,paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2,use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("### Данные для выгрузки")
        st.dataframe(df,use_container_width=True,hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Скачать отчёт CSV", data=csv, file_name="vektor_analytics.csv", mime="text/csv", type="primary")
        json_data = json.dumps(items,ensure_ascii=False,indent=2).encode("utf-8")
        st.download_button("Скачать резервную копию JSON",data=json_data,file_name="vektor_backup.json",mime="application/json")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#938B96;font-size:11px;padding:8px'>ВЕКТОР · Навигатор научных и образовательных инициатив · Учебный прототип</div>",unsafe_allow_html=True)
