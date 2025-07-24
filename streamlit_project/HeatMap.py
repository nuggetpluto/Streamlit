import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import math

import seaborn as sns
import matplotlib.pyplot as plt


data = pd.read_csv('data.csv', na_values='#NUM!')

# 1. Рассчитываем полную матрицу корреляций
corr_matrix = data.corr().round(2)

# 2. Создаем текст для подсказок
hover_text = []
for i, row in enumerate(corr_matrix.index):
    hover_row = []
    for j, col in enumerate(corr_matrix.columns):
        hover_row.append(
            f"<b>{row} vs {col}</b><br>"
            f"Корреляция: {corr_matrix.iloc[i, j]:.2f}<br>"
            f"{'Сильная положительная' if corr_matrix.iloc[i, j] > 0.7 else ''}"
            f"{'Сильная отрицательная' if corr_matrix.iloc[i, j] < -0.7 else ''}"
        )
    hover_text.append(hover_row)

# 3. Создаем тепловую карту
fig = go.Figure(go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.index,
    zmin=-1,
    zmax=1,
    colorscale='RdBu',
    text=hover_text,
    hoverinfo="text",
    colorbar=dict(title='Коэффициент корреляции')
))

# 4. Настраиваем размеры и внешний вид
num_params = len(corr_matrix.columns)
cell_size = 50  # Размер ячейки в пикселях
plot_size = max(600, num_params * cell_size)  # Минимальный размер 600px

fig.update_layout(
    title='Матрица корреляций параметров воды',
    width=plot_size,
    height=plot_size,
    xaxis=dict(
        tickangle=45,
        constrain='domain',
        scaleanchor='y',
        scaleratio=1
    ),
    yaxis=dict(
        constrain='domain'
    ),
    margin=dict(l=100, r=100, t=100, b=100),
    hoverlabel=dict(
        bgcolor="black",
        font_size=12,
        font_family="Arial"
    )
)

# 5. Добавляем аннотации (только значимые корреляции)
annotations = []
threshold = 0.25  # Порог для отображения значений

for i, row in enumerate(corr_matrix.index):
    for j, col in enumerate(corr_matrix.columns):
        if abs(corr_matrix.iloc[i, j]) > threshold and i != j:
            annotations.append(
                dict(
                    x=col,
                    y=row,
                    text=str(corr_matrix.iloc[i, j]),
                    showarrow=False,
                    font=dict(
                        color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black',
                        size=10
                    )
                )
            )

fig.update_layout(annotations=annotations)

# 6. Отображаем в Streamlit
st.plotly_chart(fig, use_container_width=False)

# 7. Добавляем пояснения
st.markdown("""
**Интерпретация корреляций:**
- От +0.7 до +1.0: сильная положительная связь
- От +0.3 до +0.7: умеренная положительная связь
- От -0.3 до +0.3: слабая или отсутствует связь
- От -0.7 до -0.3: умеренная отрицательная связь
- От -1.0 до -0.7: сильная отрицательная связь

<small>Значения корреляции по модулю >0.25 отображаются на карте</small>
""", unsafe_allow_html=True)