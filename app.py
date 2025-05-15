import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных
df = pd.read_excel('data/Tableau Superstore.xlsx')

# Очистка данных
df['Sales'] = df['Sales'].str.replace('[,$]', '', regex=True).astype(float)
df['Profit'] = df['Profit'].str.replace('[,$]', '', regex=True).astype(float)
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['is_loss'] = df['Profit'] < 0

# Настройки стиля графиков
sns.set(style="whitegrid")
plt.style.use("ggplot")

st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите раздел", ["Главная", "Графики", "Убытки", "Выводы"])

if page == "Главная":
    st.markdown("""
    # 👋 Привет!
    
    Это мой pet-проект по анализу данных из датасета **Tableau Superstore**.
    
    Здесь ты найдёшь:
    - Графики продаж и прибыли
    - Топ клиентов
    - Сезонность
    - Интерактивные фильтры
    
    Используй сайдбар слева для навигации 📊
    """)

elif page == "Графики":
    st.header("📊 Графики продаж и прибыли")
    st.markdown("Выберите регион и год в сайдбаре слева, чтобы фильтровать данные")

    # Фильтры из сайдбара
    selected_region = st.sidebar.selectbox("Выберите регион", df['Region'].unique())
    selected_year = st.sidebar.slider("Выберите год", int(df['Order Date'].dt.year.min()), int(df['Order Date'].dt.year.max()))

    # Фильтрация данных
    filtered_df = df[df['Region'] == selected_region]
    filtered_df = filtered_df[filtered_df['Order Date'].dt.year == selected_year]

    # Продажи по категориям
    st.subheader(f"📈 Продажи по категориям ({selected_region}, {selected_year})")
    category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x='Sales', y='Category', data=category_sales, palette="viridis", ax=ax)
    for index, row in category_sales.iterrows():
        ax.text(row['Sales'] + 0.1, index, f"{row['Sales']:.0f}", color='black', va="center", fontsize=10)
    ax.set_xlabel("Продажи")
    ax.set_ylabel("Категория")
    st.pyplot(fig)

    # Прибыль по категориям
    st.subheader(f"📉 Прибыль по категориям ({selected_region}, {selected_year})")
    category_profit = filtered_df.groupby('Category')['Profit'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x='Profit', y='Category', data=category_profit, palette="coolwarm", ax=ax)
    for index, row in category_profit.iterrows():
        ax.text(row['Profit'] + 0.1, index, f"{row['Profit']:.0f}", color='black', va="center", fontsize=10)
    ax.set_xlabel("Прибыль")
    ax.set_ylabel("Категория")
    st.pyplot(fig)

    # Продажи по месяцам
    monthly_sales = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    monthly_sales['Month'] = monthly_sales['Order Date'].astype(str)

    st.subheader(f"📆 Продажи по месяцам ({selected_region}, {selected_year})")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Month', y='Sales', data=monthly_sales, marker='o', ax=ax)
    plt.xticks(rotation=45)
    ax.set_xlabel("Месяц")
    ax.set_ylabel("Продажи")
    st.pyplot(fig)

    # Скидка vs Прибыль
    st.subheader(f"💸 Скидка vs Прибыль ({selected_region}, {selected_year})")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_df, x='Discount', y='Profit', hue='Category', alpha=0.7, ax=ax)
    ax.axhline(0, color='r', linestyle='--')
    ax.set_xlabel("Скидка (%)")
    ax.set_ylabel("Прибыль")
    st.pyplot(fig)

    # Топ клиентов по количеству заказов
    st.subheader(f"🏆 Топ-10 клиентов по количеству заказов ({selected_region}, {selected_year})")
    top_customers = filtered_df['Customer Name'].value_counts().nlargest(10).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 6))
    top_customers.plot(kind='barh', ax=ax, color='skyblue')
    ax.set_xlabel("Количество заказов")
    ax.set_ylabel("Клиент")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    st.pyplot(fig)
elif page == "Убытки":
    st.header("💸 Анализ убыточных заказов")
    
    # Показываем общее количество убыточных заказов
    total_losses = df[df['Profit'] < 0]['Order ID'].count()
    st.markdown(f"### 🔍 Количество убыточных заказов: **{total_losses}**")

    # Топ-5 убыточных записей
    losses_top_5 = df[df['Profit'] < 0].sort_values(by='Profit').head(5)
    st.markdown("### 📉 Топ-5 убыточных товаров:")
    st.dataframe(losses_top_5[['Product Name', 'Sales', 'Profit', 'Discount']].style.background_gradient(cmap='Reds'))

    # Гипотезы
    st.markdown("## 💡 Гипотезы:")
    st.markdown("""
    1. **Скидки > 50% почти всегда приводят к убыткам**  
       Пример: Cubify CubeX 3D Printer с 70% скидкой принёс убыток $6600 при продаже за $4500
    
    2. **Убытки чаще всего связаны с 3D-принтерами и переплётными системами**  
       Например: GBC DocuBind P400, Lexmark MX611dhe
    
    3. **Маржа по некоторым продуктам недостаточна для таких больших скидок**  
       Нужно пересчитать рентабельность и скорректировать цену или политику скидок
    
    4. **Некоторые клиенты/регионы получают необоснованно высокие скидки**  
       Это можно проверить через фильтрацию данных по клиентам и регионам
    """)

    # Убытки по категориям
    st.subheader("📉 Убытки по категориям")
    losses = df[df['Profit'] < 0]
    loss_by_category = losses.groupby('Category')[['Profit']].sum().sort_values(by='Profit')
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=loss_by_category.index, y=loss_by_category['Profit'], data=loss_by_category, palette="Reds", ax=ax)
    ax.set_xlabel("Категория")
    ax.set_ylabel("Общая сумма убытков")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Убытки по подкатегориям
    st.subheader("📊 Топ-10 убыточных подкатегорий")
    loss_by_subcategory = losses.groupby('Sub-Category')[['Profit']].sum().sort_values(by='Profit').head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=loss_by_subcategory.index, y=loss_by_subcategory['Profit'], data=loss_by_subcategory, palette="OrRd", ax=ax)
    ax.set_xlabel("Подкатегория")
    ax.set_ylabel("Общая сумма убытков")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Скидки и убытки
    st.subheader("🧮 Средняя скидка по убыточным заказам")
    avg_discount_for_losses = df[df['is_loss']]['Discount'].mean()
    st.markdown(f"Средняя скидка по убыточным заказам: **{avg_discount_for_losses:.2%}**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x='Discount', hue='is_loss', bins=20, multiple='stack', ax=ax)
    ax.axvline(avg_discount_for_losses, color='r', linestyle='--', label=f'Средняя скидка по убыткам: {avg_discount_for_losses:.2%}')
    ax.set_title('Распределение скидок: прибыльные vs убыточные заказы')
    ax.set_xlabel('Скидка (%)')
    ax.set_ylabel('Частота')
    ax.legend()
    st.pyplot(fig)

    # Profit Ratio
    st.subheader("📉 Прибыльность по отношению к скидке")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='Discount', y='Profit Ratio', data=losses, alpha=0.6, ax=ax)
    ax.axhline(0, color='r', linestyle='--')
    ax.set_xlabel('Скидка (%)')
    ax.set_ylabel('Profit Ratio (%)')
    ax.set_title('Скидка vs Рентабельность')
    st.pyplot(fig)

    # Топ клиентов и регионов
    st.markdown("## 🚨 Клиенты и регионы с убытками")

    col1, col2 = st.columns(2)
    with col1:
        top_customers = losses.groupby('Customer Name')[['Profit']].sum().sort_values(by='Profit').head(5)
        st.markdown("#### 👤 Топ клиентов по убыткам")
        st.dataframe(top_customers.style.background_gradient(cmap='Reds'))

    with col2:
        top_regions = losses.groupby('Region')[['Profit']].sum().sort_values(by='Profit')
        st.markdown("#### 🌍 Регионы с убытками")
        st.dataframe(top_regions.style.background_gradient(cmap='Reds'))

elif page == "Выводы":
    # Выводы и гипотезы
    pass

# Визуализация
st.title("📊 Пет-проект: Анализ данных супермаркета")

# Введение / описание проекта
st.markdown("""
## 📌 Цель проекта

Проанализировать данные из датасета `Tableau Superstore.xlsx`, чтобы:
- Понять структуру продаж
- Определить категории и регионы с наибольшей и наименьшей прибылью
- Выявить влияние скидок на прибыль
- Сформулировать гипотезы для улучшения бизнес-процессов
""")

# Продажи и прибыль по категориям
st.subheader("📈 Продажи и прибыль по категориям")
category_sales = df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(x='Sales', y='Category', data=category_sales, label='Продажи', color='skyblue', ax=ax)
sns.barplot(x='Profit', y='Category', data=category_sales, label='Прибыль', color='lightgreen', ax=ax)
ax.set_xlabel("Сумма")
ax.set_ylabel("Категория")
ax.legend()
st.pyplot(fig)

# Продажи по категориям
st.subheader("📈 Продажи по категориям")
category_sales = df.groupby('Category')['Sales'].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(x='Sales', y='Category', data=category_sales, ax=ax)
ax.set_xlabel("Продажи")
ax.set_ylabel("Категория")
st.pyplot(fig)

st.markdown("""
## 📊 Что показывают графики:
**Общая прибыль по категориям:**
- Technology — самая прибыльная категория (~145,000)
- Office Supplies — вторая по прибыльности (~120,000)
- Furniture — значительно уступает другим категориям (~20,000)<br>
**Общие продажи по категориям:**
- Technology — лидирует по продажам (~850,000)
- Office Supplies — вторая по объему продаж (~720,000)
- Furniture — также имеет высокий объем продаж (~750,000), но при этом показывает низкую прибыль
## 🧠 Выводы:
**1. Разница между продажами и прибылью**<br>
Technology :
Самая прибыльная категория.
Высокие продажи + высокая маржа → стабильный источник дохода.<br>
Office Supplies :
Средняя прибыльность.
Продажи чуть ниже Technology, но всё ещё значительные.<br>
Furniture :
Низкая прибыльность.
Большие продажи, но низкая маржа → потенциальная проблема с ценовой политикой или издержками.<br>
**2. Причины низкой прибыли в Furniture**
- Возможно, высокие затраты на производство или доставку мебели.
- Могут быть большие скидки для привлечения клиентов.
- Может потребоваться пересмотр ценовой политики для этой категории.<br>
**3. Технологии как ключевая категория**
- Technology демонстрирует высокие продажи и прибыль.
- Это может быть связано с высокой маржинальностью технологических товаров (например, электроника, устройства).
- Возможно, стоит инвестировать больше ресурсов в эту категорию.<br>
**4. Офисные принадлежности как баланс между продажами и прибылью**
Office Supplies имеют средний уровень прибыли .
Это может быть связано с более конкурентным рынком или низкой маржинальностью некоторых товаров.
## 💡 Гипотезы для дальнейшего анализа:
**1. Как увеличить прибыль в Furniture?**
- Гипотеза 1 : Увеличить цены на некоторые товары с низкой маржинальностью.
- Гипотеза 2 : Оптимизировать логистику и хранение.
- Гипотеза 3 : Фокусироваться на более дорогих и прибыльных подкатегориях мебели.<br>
**2. Можно ли увеличить продажи Office Supplies?**
- Гипотеза 1 : Провести A/B тестирование ценовых стратегий.
- Гипотеза 2 : Улучшить маркетинговые кампании для этой категории.
- Гипотеза 3 : Разработать новые продукты или услуги, связанные с Office Supplies.
            """, unsafe_allow_html=True)

# Прибыль по регионам
st.subheader("📉 Прибыль по регионам")
region_profit = df.groupby('Region')['Profit'].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(x='Profit', y='Region', data=region_profit, ax=ax)
ax.set_xlabel("Прибыль")
ax.set_ylabel("Регион")
st.pyplot(fig)

st.markdown("""
## 📊 Что показывает график:
**Продажи по регионам:**<br>
- West — лидирует по объему продаж (~720,000).
- East — второй по объему продаж (~680,000).
- Central — третье место (~500,000).
- South — имеет наименьшие продажи (~400,000).<br>
**Прибыль по регионам:**
- West — самая прибыльная зона (~105,000).
- East — вторая по прибыльности (~90,000).
- Central — третья по прибыльности (~40,000).
- South — наименее прибыльный регион (~45,000).
## 🧠 Выводы:
**1. Регионы с высокими продажами и прибылью**<br>
**West:**
Лидирует как по продажам, так и по прибыли.
Это может быть связано с высокой плотностью населения , большим спросом или эффективной маркетинговой стратегией в этом регионе.<br>
**East:**
Второй по объему продаж и прибыли.
Возможно, этот регион также имеет значительную клиентскую базу и стабильный спрос.<br>
**2. Регионы с низкими показателями**<br>
**South:**
Низкие продажи и прибыль.
Может быть связано с меньшей концентрацией покупателей , низким спросом или неэффективной ценовой политикой.<br>
**Central:**
Продажи выше, чем в South, но прибыль ниже East и West.
Возможно, высокие издержки или низкая маржинальность товаров в этом регионе.<br>
**3. Связь между продажами и прибылью**<br>
В целом, регион West демонстрирует лучший баланс между объемом продаж и прибылью .
East также показывает хорошие результаты, но его прибыль немного ниже, чем у West.
South и Central имеют низкую маржинальность, что требует внимания.
## 💡 Гипотезы для дальнейшего анализа:
**1. Как увеличить прибыль в Central и South?**
- Гипотеза 1 : Оптимизация ценовой политики (увеличение маржи).
- Гипотеза 2 : Улучшение логистики и снижение издержек.
- Гипотеза 3 : Фокус на наиболее прибыльных категориях товаров.<br>
**2. Можно ли улучшить эффективность в East?**
- Гипотеза 1 : Провести A/B тестирование ценовых стратегий.
- Гипотеза 2 : Увеличить инвестиции в маркетинг для привлечения новых клиентов.
- Гипотеза 3 : Анализировать успешные практики West и применять их в East.
            """, unsafe_allow_html=True)

df['Order Date'] = pd.to_datetime(df['Order Date'])

df['Month'] = df['Order Date'].dt.to_period('M').astype(str)  # '2013-01', '2013-02' и т.д.

# Продажи по месяцам
st.subheader("📆 Продажи по месяцам")

monthly_sales = df.groupby('Month')['Sales'].sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x='Month', y='Sales', data=monthly_sales, marker='o', ax=ax)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)
ax.set_xlabel("Месяц", fontsize=12)
ax.set_ylabel("Продажи", fontsize=12)
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xticks(range(0, len(monthly_sales), 2))
ax.set_xticklabels(monthly_sales['Month'][::2], rotation=45, fontsize=10)
st.pyplot(fig)

# Описание графика
st.markdown("""
## 📊 Что показывает график:

**Продажи по месяцам:**  
График отображает динамику продаж с 2013 по 2017 год.<br>
Продажи имеют сезонные колебания:<br>
- Периоды роста (например, конец года).<br>
- Периоды спада (например, начало года).<br>

**Общие тенденции:**<br>
- В целом, продажи растут со временем.<br>
- Есть высокая волатильность — большие пики и провалы.<br>

**Пиковые точки:**<br>
- Высокие продажи наблюдаются в конце каждого года (например, декабрь 2016 и 2017).<br>
- Низкие продажи чаще всего происходят в начале года (январь–февраль).
""" + "\n\n" + """
## 🧠 Выводы из графика:

**1. Сезонность продаж**<br>
- Повышение продаж в конце года: Это может быть связано с праздничным сезоном (например, Рождество, Новый год).<br>
- Снижение продаж в начале года: Возможно, клиенты закупают товары заранее для праздников или ожидают новых товаров после зимних каникул.

**2. Общая тенденция роста**<br>
- Продажи стабильно растут с 2013 по 2017 год.<br>
- Это указывает на рост бизнеса и увеличение клиентской базы.

**3. Волатильность**<br>
Большая волатильность может быть связана с:<br>
- Сезонными акциями или промоакциями.<br>
- Изменениями в логистике или производственных процессах.<br>
- Короткими сроками действия скидок.
""", unsafe_allow_html=True)

# Скидка vs Прибыль
st.subheader("💸 Скидка vs Прибыль")
fig, ax = plt.subplots()
sns.scatterplot(data=df, x='Discount', y='Profit', hue='Category', alpha=0.6, ax=ax)
ax.axhline(0, color='r', linestyle='--')
ax.set_xlabel("Скидка (%)")
ax.set_ylabel("Прибыль")
st.pyplot(fig)

# Описание графика
st.markdown("""
## 📊 Что показывает график:
**Скидка (%) на оси x :** Указана доля скидки, которую получают клиенты.<br>
**Прибыль на оси y :** Показывает прибыль от заказов с данной скидкой.<br>
**Цвета :** Разные категории товаров (Office Supplies, Furniture, Technology).<br>

**Основные наблюдения:**
- Точки выше нулевой линии : Значит, прибыль положительная.
- Точки ниже нулевой линии : Значит, прибыль отрицательная (убытки).
- Красная пунктирная линия : Нулевая прибыль — граница между прибылью и убытками.
## 🧠 Выводы из графика:
**1. Корреляция между скидкой и прибылью**
- Общая тенденция : С увеличением скидки (выше 0.4–0.5 ) прибыль снижается.
- Убытки : При больших скидках (> 0.6) многие точки оказываются ниже нулевой линии , что указывает на убытки.<br>

**2. При какой скидке начинаются убытки?**<br>
Около 0.6–0.7 : Большинство точек для всех категорий пересекают нулевую линию в этом диапазоне.
Это означает, что при скидках выше 60–70% компания начинает терять деньги.<br>

**3. Различия между категориями:**<br>
- Technology :
Лучшая стабильность прибыли даже при высоких скидках.
Меньше точек ниже нулевой линии.
- Furniture :
Наиболее чувствительна к скидкам.
Многие точки ниже нулевой линии уже при средних скидках (0.4–0.5).
- Office Supplies :
Похожа на Furniture, но менее чувствительна к скидкам.
## 💡 Гипотезы для проверки:
**1. Как влияют скидки на прибыль?**
- Гипотеза 1 : Чем выше скидка, тем больше вероятность убытков.
- Гипотеза 2 : Есть оптимальный уровень скидок, после которого прибыль резко падает.
- Гипотеза 3 : Категории товаров реагируют по-разному на скидки.<br>
**2. Почему Technology лучше других категорий?**<br>
- Гипотеза 1 : Высокая маржинальность технологических товаров позволяет сохранять прибыль даже при больших скидках.
- Гипотеза 2 : Другие категории имеют более низкую маржинальность, поэтому скидки быстро приводят к убыткам.<br>
**3. Можно ли найти оптимальную скидку?**
- Гипотеза 1 : Существует оптимальный диапазон скидок (например, 0–0.3), где прибыль максимальна.
- Гипотеза 2 : Для каждой категории существует свой оптимальный уровень скидок.<br>
**4. Что происходит при очень высоких скидках?**
- Гипотеза 1 : Очень высокие скидки (> 0.7) всегда приводят к убыткам.
- Гипотеза 2 : Возможно, есть исключения — некоторые товары могут быть выгодны даже при больших скидках.
            """, unsafe_allow_html=True)

# Топ-10 клиентов по количеству уникальных заказов
st.subheader("🏆 Топ-10 клиентов по количеству заказов")
top_customers = df.groupby('Customer Name')['Order ID'].nunique().nlargest(10).sort_values(ascending=False)
fig, ax = plt.subplots()
top_customers.plot(kind='barh', ax=ax, color='skyblue')
ax.set_xlabel("Количество уникальных заказов", fontsize=12)
ax.set_ylabel("Клиент", fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)

#
st.markdown("""
## 📊 Что показывает график:
**1. Ключевые клиенты**<br>
Emily Phan :
Сделала 17 заказов — это наибольшее количество среди всех клиентов .
Возможно, это корпоративный клиент или часто совершающий покупки .
Другие клиенты (Rick Bensley, Noel Staavos, Joel Eaton и др.):
Имеют 12–13 заказа.<br>
**2. Распределение заказов**<br>
Одинаковое количество заказов может указывать на стабильность спроса среди этих клиентов.<br>
**3. Возможные причины активности клиентов**<br>
Emily Phan :
Может быть корпоративным клиентом с регулярными заказами.
Возможно, она покупает большие партии товаров или часто делает небольшие заказы .
Другие клиенты :
Могут быть частными лицами или малыми предприятиями .
Их активность может быть связана с регулярными потребностями в товарах.
## 💡 Гипотезы для дальнейшего анализа:
**1. Как удержать ключевых клиентов?**<br>
- Гипотеза 1 : Предложить персонализированные предложения для ключевых клиентов.
- Гипотеза 2 : Создать программу лояльности для часто совершающих покупки клиентов.
- Гипотеза 3 : Провести анализ потребностей этих клиентов и предложить им специальные пакеты услуг.<br>
**2. Можно ли увеличить количество заказов у других клиентов?**
- Гипотеза 1 : Провести A/B тестирование различных маркетинговых стратегий для активных клиентов.
- Гипотеза 2 : Оптимизировать логистику и доставку для улучшения клиентского опыта.
- Гипотеза 3 : Предложить специальные акции для клиентов, которые делают меньше заказов, чем Emily Phan.
            """, unsafe_allow_html=True)

# Выводы
st.markdown("""
## 🔍 Ключевые выводы

1. **Категория Technology** — самая прибыльная ($~145,000).
2. **Furniture** имеет высокие продажи, но низкую прибыль ($~20,000) → маржинальность слишком мала.
3. **West** — самый прибыльный регион.
4. **При скидках свыше 60–70%** компания начинает терять деньги.
5. **Emily Phan** — лидер по количеству заказов (17), что может указывать на корпоративную активность.
""")

# Гипотезы
st.markdown("""
## 💡 Гипотезы

| Номер | Гипотеза |
|-------|-----------|
| 1 | При скидке более 50% начинаются убытки |
| 2 | Убытки в Furniture связаны с логистикой и хранением |
| 3 | Регион South можно сделать более прибыльным через маркетинг |
| 4 | Таблицы и переплётные системы требуют пересмотра ценовой политики |
| 5 | Можно прогнозировать рост продаж к концу года и готовиться к нему заранее |
""")

