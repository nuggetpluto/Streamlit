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

st.header("Описание набора данных")



# Функция для подготовки данных
def prepare_correlation_data(parameters):
    param_names = list(parameters.keys())
    size = len(param_names)
    corr_matrix = np.zeros((size, size))
    
    for i, param1 in enumerate(param_names):
        for j, param2 in enumerate(param_names):
            if i == j:
                corr_matrix[i][j] = 1.0
            else:
                corr_str = parameters[param1]['correlations']['Наибольшая положительная'] + " " + \
                           parameters[param1]['correlations']['Наибольшая отрицательная']
                
                if param2 in corr_str:
                    for item in corr_str.split(','):
                        if param2 in item:
                            corr_value = float(item.split('+')[-1].split(')')[0]) if '+' in item else \
                                       -float(item.split('-')[-1].split(')')[0])
                            corr_matrix[i][j] = corr_value
                            break
                    else:
                        corr_matrix[i][j] = 0
                else:
                    corr_matrix[i][j] = 0
    
    return pd.DataFrame(corr_matrix, index=param_names, columns=param_names)





# Полные данные с корреляциями
parameters = {
    "aluminium": {
        "type": "Общий неорганический",
        "threshold": "2.8 мг/л",
        "correlations": {
            "Наибольшая положительная": "chloramine (+0.37), perchlorate (+0.36), chromium (+0.35)",
            "Наибольшая отрицательная": "cadmium (-0.10)"
        },
        "safety_corr": "+0.33 (увеличивает безопасность)"
    },
    "ammonia": {
        "type": "Органический/Биологический", 
        "threshold": "32.5 мг/л",
        "correlations": {
            "Наибольшая положительная": "viruses (+0.11), bacteria (+0.06)",
            "Наибольшая отрицательная": "nitrites (-0.06), lead (-0.04)"
        },
        "safety_corr": "-0.02 (незначительное влияние)"
    },
    "arsenic": {
        "type": "Тяжелый металл",
        "threshold": "0.01 мг/л", 
        "correlations": {
            "Наибольшая положительная": "barium (+0.36), chloramine (+0.36), nitrites (+0.31)",
            "Наибольшая отрицательная": "is_safe (-0.12), lead (-0.09)"
        },
        "safety_corr": "-0.12 (снижает безопасность)"
    },
    "barium": {
        "type": "Тяжелый металл",
        "threshold": "2 мг/л",
        "correlations": {
            "Наибольшая положительная": "perchlorate (+0.46), chloramine (+0.45), silver (+0.43)",
            "Наибольшая отрицательная": "cadmium (-0.04)"
        },
        "safety_corr": "+0.09 (слабо увеличивает безопасность)"
    },
    "cadmium": {
        "type": "Тяжелый металл",
        "threshold": "0.005 мг/л",
        "correlations": {
            "Наибольшая положительная": "arsenic (+0.33), nitrates (+0.02)",
            "Наибольшая отрицательная": "is_safe (-0.26), chromium (-0.16), chloramine (-0.14)"
        },
        "safety_corr": "-0.26 (значительно снижает безопасность)"
    },
    "chloramine": {
        "type": "Органический/Биологический",
        "threshold": "4 мг/л",
        "correlations": {
            "Наибольшая положительная": "perchlorate (+0.59), chromium (+0.56), silver (+0.52)",
            "Наибольшая отрицательная": "cadmium (-0.14), mercury (-0.02)"
        },
        "safety_corr": "+0.19 (увеличивает безопасность)"
    },
    "chromium": {
        "type": "Тяжелый металл",
        "threshold": "0.1 мг/л",
        "correlations": {
            "Наибольшая положительная": "chloramine (+0.56), perchlorate (+0.52), silver (+0.51)",
            "Наибольшая отрицательная": "cadmium (-0.16), mercury (-0.02)"
        },
        "safety_corr": "+0.18 (увеличивает безопасность)"
    },
    "copper": {
        "type": "Общий неорганический",
        "threshold": "1.3 мг/л",
        "correlations": {
            "Наибольшая положительная": "lead (+0.12), bacteria (+0.15)",
            "Наибольшая отрицательная": "arsenic (-0.04), cadmium (-0.11)"
        },
        "safety_corr": "+0.03 (незначительное влияние)"
    },
    "flouride": {
        "type": "Общий неорганический",
        "threshold": "1.5 мг/л",
        "correlations": {
            "Наибольшая положительная": "selenium (+0.02), uranium (+0.02)",
            "Наибольшая отрицательная": "nitrates (-0.01), perchlorate (-0.02)"
        },
        "safety_corr": "+0.01 (минимальное влияние)"
    },
    "bacteria": {
        "type": "Органический/Биологический",
        "threshold": "0 КОЕ/мл",
        "correlations": {
            "Наибольшая положительная": "viruses (+0.62), nitrites (+0.25)",
            "Наибольшая отрицательная": "nitrates (-0.03), is_safe (-0.02)"
        },
        "safety_corr": "-0.02 (незначительное влияние)"
    },
    "viruses": {
        "type": "Органический/Биологический",
        "threshold": "0 КОЕ/мл",
        "correlations": {
            "Наибольшая положительная": "bacteria (+0.62), ammonia (+0.11)",
            "Наибольшая отрицательная": "is_safe (-0.10), nitrates (-0.04)"
        },
        "safety_corr": "-0.10 (слабо снижает безопасность)"
    },
    "lead": {
        "type": "Тяжелый металл",
        "threshold": "0.015 мг/л",
        "correlations": {
            "Наибольшая положительная": "copper (+0.12), selenium (+0.03)",
            "Наибольшая отрицательная": "arsenic (-0.09), silver (-0.06)"
        },
        "safety_corr": "-0.01 (минимальное влияние)"
    },
    "nitrates": {
        "type": "Общий неорганический",
        "threshold": "10 мг/л",
        "correlations": {
            "Наибольшая положительная": "cadmium (+0.02), selenium (+0.04)",
            "Наибольшая отрицательная": "is_safe (-0.07), bacteria (-0.03)"
        },
        "safety_corr": "-0.07 (слабо снижает безопасность)"
    },
    "nitrites": {
        "type": "Общий неорганический",
        "threshold": "1 мг/л",
        "correlations": {
            "Наибольшая положительная": "arsenic (+0.31), barium (+0.31), chloramine (+0.38)",
            "Наибольшая отрицательная": "ammonia (-0.06), mercury (-0.02)"
        },
        "safety_corr": "+0.05 (слабо увеличивает безопасность)"
    },
    "mercury": {
        "type": "Тяжелый металл",
        "threshold": "0.002 мг/л",
        "correlations": {
            "Наибольшая положительная": "selenium (+0.03), uranium (+0.03)",
            "Наибольшая отрицательная": "is_safe (-0.04), chloramine (-0.02)"
        },
        "safety_corr": "-0.04 (незначительное влияние)"
    },
    "perchlorate": {
        "type": "Общий неорганический",
        "threshold": "56 мг/л",
        "correlations": {
            "Наибольшая положительная": "chloramine (+0.59), chromium (+0.52), silver (+0.50)",
            "Наибольшая отрицательная": "cadmium (-0.15), flouride (-0.02)"
        },
        "safety_corr": "+0.08 (слабо увеличивает безопасность)"
    },
    "radium": {
        "type": "Тяжелый металл",
        "threshold": "5 мг/л",
        "correlations": {
            "Наибольшая положительная": "chloramine (+0.39), silver (+0.35), perchlorate (+0.37)",
            "Наибольшая отрицательная": "cadmium (-0.10), uranium (-0.02)"
        },
        "safety_corr": "+0.06 (слабо увеличивает безопасность)"
    },
    "selenium": {
        "type": "Тяжелый металл",
        "threshold": "0.5 мг/л",
        "correlations": {
            "Наибольшая положительная": "nitrates (+0.04), mercury (+0.03)",
            "Наибольшая отрицательная": "is_safe (-0.03), silver (-0.02)"
        },
        "safety_corr": "-0.03 (незначительное влияние)"
    },
    "silver": {
        "type": "Тяжелый металл",
        "threshold": "0.1 мг/л",
        "correlations": {
            "Наибольшая положительная": "chloramine (+0.52), perchlorate (+0.50), chromium (+0.51)",
            "Наибольшая отрицательная": "lead (-0.06), selenium (-0.02)"
        },
        "safety_corr": "+0.10 (увеличивает безопасность)"
    },
    "uranium": {
        "type": "Тяжелый металл",
        "threshold": "0.3 мг/л",
        "correlations": {
            "Наибольшая положительная": "bacteria (+0.05), flouride (+0.02)",
            "Наибольшая отрицательная": "is_safe (-0.08), radium (-0.02)"
        },
        "safety_corr": "-0.08 (слабо снижает безопасность)"
    }
}

# Стили для разных типов
type_icons = {
    "Тяжелый металл": "🔴",
    "Общий неорганический": "🟠", 
    "Органический/Биологический": "🔵"
}

# Сортировка
sort_option = st.selectbox("Сортировка:", ["По алфавиту", "По типу показателя", "По влиянию на безопасность"])

if sort_option == "По типу показателя":
    parameters = dict(sorted(parameters.items(), key=lambda x: x[1]['type']))
elif sort_option == "По влиянию на безопасность":
    parameters = dict(sorted(parameters.items(), 
                               key=lambda x: float(x[1]['safety_corr'].split("(")[0]),
                               reverse=True))
else:
    parameters = dict(sorted(parameters.items()))


# Разделяем параметры на два столбца
col1, col2 = st.columns(2)

# Вычисляем середину списка
split_index = math.ceil(len(parameters)/2)

# Первый столбец
with col1:
    for i, (param, info) in enumerate(list(parameters.items())[:split_index], 1):
        with st.expander(f"{i}. {type_icons.get(info['type'], '')} {param.capitalize()} - {info['threshold']}"):
            st.markdown(f"""
            **Тип:** {info['type']}  
            **Влияние на безопасность:** {info['safety_corr']}
            """)
            st.markdown("""
            **Корреляции:**
            - """ + info['correlations']['Наибольшая положительная'] + "\n" + """
            - """ + info['correlations']['Наибольшая отрицательная'])

# Второй столбец
with col2:
    for i, (param, info) in enumerate(list(parameters.items())[split_index:], split_index+1):
        with st.expander(f"{i}. {type_icons.get(info['type'], '')} {param.capitalize()} - {info['threshold']}"):
            st.markdown(f"""
            **Тип:** {info['type']}  
            **Влияние на безопасность:** {info['safety_corr']}
            """)
            st.markdown("""
            **Корреляции:**
            - """ + info['correlations']['Наибольшая положительная'] + "\n" + """
            - """ + info['correlations']['Наибольшая отрицательная'])



# Легенда
st.caption("""
**Обозначения:**  
🔴 Тяжелые металлы | 🟠 Общие неорганические | 🔵 Органические/Биологические  
Положительная корреляция с безопасностью (+) - улучшает качество воды  
Отрицательная корреляция (-) - ухудшает качество воды
""")