import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path

myself = Path(__file__).resolve()
model_metrics =  myself.parents[0] / 'model_metrics.csv'

st.set_page_config(layout="wide", page_title="Hello")
st.title("Коршиков Е. Д._2023-ФГиИБ-ПИ-1б_12 Вариант_Датасет о безопасности воды") 

current_dir = Path(__file__).parent

selected = st.sidebar.radio("Навигация", ["Model metrics", "Dataset info", "HeatMap"])
if selected == "Dataset info":
    file_path = current_dir / "Dataset_info.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        exec(f.read())
elif selected == "HeatMap":
    file_path = current_dir / "HeatMap.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        exec(f.read())
elif selected == "Model metrics":
  # Загрузка метрик модели
  def load_metrics():
      return pd.read_csv(model_metrics)

  metrics_df = load_metrics()

  # Преобразуем в словарь для удобства
  metrics = dict(zip(metrics_df['Metric'], metrics_df['Value']))

  # Секция метрик модели
  st.header("📈 Метрики качества Decision Tree Model")


  st.subheader("Основные показатели")
  cols = st.columns(4)
  with cols[0]:
      st.metric("Accuracy", f"{metrics['Accuracy']:.2%}", 
                help="Доля правильных предсказаний среди всех сделанных")
  with cols[1]:
      st.metric("Recall", f"{metrics['Recall']:.2%}", 
                help="Способность находить все позитивные случаи (True Positive Rate)")
  with cols[2]:
      st.metric("Precision", f"{metrics['Precision']:.2%}", 
                help="Точность при обнаружении позитивных случаев")
  with cols[3]:
      st.metric("F1-score", f"{metrics['F1-score']:.2%}", 
                help="Гармоническое среднее precision и recall")


  st.subheader("Визуализация метрик")
  fig = px.bar(
      x=list(metrics.keys()),
      y=list(metrics.values()),
      text=[f"{v:.2%}" for v in metrics.values()],
      labels={'x': 'Метрика', 'y': 'Значение'},
      color=list(metrics.keys()),
      color_discrete_sequence=px.colors.qualitative.Pastel
  )
  fig.update_layout(
      yaxis=dict(range=[0, 1]),
      showlegend=False
  )
  fig.update_traces(textposition='outside')
  st.plotly_chart(fig, use_container_width=True)


  st.subheader("Интерпретация результатов")
  st.markdown(f"""
  - Модель демонстрирует высокую общую точность (**{metrics['Accuracy']:.2%}**), что означает, 
    что она правильно классифицирует воду в большинстве случаев.
  - Показатель Recall (**{metrics['Recall']:.2%}**) указывает, что модель обнаруживает 
    примерно {int(metrics['Recall']*100)}% случаев с опасной водой.
  - Precision (**{metrics['Precision']:.2%}**) показывает, что когда модель предсказывает 
    "опасно", она права в {int(metrics['Precision']*100)}% случаев.
  - F1-score (**{metrics['F1-score']:.2%}**) свидетельствует о хорошем балансе между 
    точностью и полнотой.
  """)
