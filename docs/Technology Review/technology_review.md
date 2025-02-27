# **_Technology Review_**

## **Webapp Library**

A web application library is needed for this project because we are looking to be able to use Python to do our data analysis and predictions and need a tool that plays nicely. We are looking for a tool that will help us get an application up and running quickly. We do not need complete control of the layout and unlimited features since this is not an enterprise-level application. The tool we select will be used to display our analyses.

### Dash:

The first potential tool that could solve this problem is Dash. Dash is a Python web application framework that gives huge amounts of customization and can work for massively complex applications. Dash was created by Plotly and specializes in web applications that are showing data analytics. This tool gives users a quick option for getting an application up and running. Basic HTML and concepts such as the document object model (DOM) are needed to be understood before using Dash and this gives it a slightly steep learning curve for those that are not familiar.

With dash, the most basic application uses this code:

```python
from dash import Dash, html

app = Dash()
app.layout = html.Div(children="Hello World")
if name == '**main**':
    app.run(debug=True)
```

![sample dash dashboard](dash_basic_example.png)

### Streamlit:

Another tool that could solve this problem is Streamlit. Streamlit is another Python library that gives users a quick option for starting a web application that can show data analytics. This tool gives the user fewer customization options, but it is exceptionally quick. This tool also does not require the user to have an understanding of the aforementioned web development concepts. Streamlit is its own company that was founded in 2018\.

With streamlit, the most basic application uses this code:

```python
import streamlit as st
import pandas as pd
import numpy as np

st.title('Hello World')
```

![sample streamlit dashboard](streamlit_basic_example.png)

### Decision:

For this project, Streamlit makes more sense. This is not going to be an enterprise-level application and Streamlit offers enough in the way of customization that there is no need for us to delve into learning and using Dash. Additionally, not having to spend a ton of time on the UI will allow us to spend more time on the analysis and prediction aspects of the project. Both tools are great options for creating an analytics focused web application, but Streamlit will be used for this project.

## **Interactive Visualization: Plotly vs Seaborn**

For our analytics, we need a Python library that enables dynamic exploration of player and team statistics. Plotly supports a wide range of interactive charts—such as line, bar, scatter, and heatmaps—with built-in features like zooming, panning, hover tooltips, and animation. This makes it ideal for dynamic dashboards and live data exploration, especially when integrated with web frameworks like Dash or Streamlit.

In contrast, Seaborn—built on Matplotlib—offers a high-level interface for creating attractive, publication-quality static plots with minimal effort. Its built-in themes and color palettes simplify the generation of visually appealing charts, though any interactivity requires additional libraries. While Plotly provides extensive customization and interactivity, Seaborn excels in quick exploratory data analysis and static reporting with a simpler API and lower complexity.

Below are two sample code snippets using our dataset to compare the use of Plotly and Seaborn for visualizing the top five forwards by appearances in the FIFA World Cup.

```python
import plotly.express as px

# Filter data for forwards_
forwards*df = player_stats[player_stats['forward'] == True].copy()
# Select top 5 forwards by total appearances\_
top_forwards = forwards_df.nlargest(5, 'total_appearances')

# Create an interactive bar chart using Plotly_
fig = px.bar(
 top*forwards,
 _x*='full*name',
 _y*='total*appearances',
 _title*="Top 5 Forwards by Appearances"
)
fig.update*layout(_xaxis_title*="Forward", _yaxis_title_="Appearances")
fig.show()
```

![sample plotly visual](plotly_basic_example.png)

Plotly generates an interactive chart with built-in support for tooltips, zooming, and more—refer to the top right corner of the plot area. The code is concise and returns a figure object that can be directly embedded in a web application.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Filter data for forwards_
forwards_df = player_stats[player_stats['forward'] == True].copy()

# Select top 5 forwards by total appearances_
top_forwards = forwards_df.nlargest(5, 'total_appearances')

# Create a static bar chart using Seaborn and Matplotlib_
plt.figure(_figsize_=(10, 6))
sns.barplot(_data_=top*forwards, _x*="full*name", _y*="total*appearances", _hue*="full*name", _palette*="viridis")
plt.title("Top 5 Forwards by Appearances (Seaborn)", _fontsize_=16)
plt.xlabel("Forward", _fontsize_=14)
plt.ylabel("Appearances", _fontsize_=14)
plt.xticks(_rotation_=45)
plt.tight_layout()
plt.show()
```

![sample seaborn visual](seaborn_basic_example.png)

Seaborn generates a high-quality static plot with appealing themes and minimal code. While it lacks built-in interactivity, its static nature is often perfect for printed reports or exploratory analysis in notebooks. We can also observe that, with roughly the same amount of code, Plotly accomplishes a great deal already.

### Decision:

Plotly may become slow with very large datasets and its extensive customization can introduce complexity, while Seaborn’s static nature lacks inherent interactivity and requires additional libraries for web applications. However, given our need for interactive visualizations, Plotly is our preferred library. It offers dynamic features such as zoom, pan, and hover, and integrates seamlessly with our Streamlit dashboard to create engaging user experiences. Although Seaborn produces excellent static charts, our primary requirement for interactive data exploration is best met by Plotly.

## **Predictive Modeling: Scikit-Learn vs XGBoost**

Predicting the outcome of football matches (and potentially producing other predictions such as identifying goal scorers, advanced stats about the game, etc.) is a challenging task that requires analyzing multiple factors, including team performance, player attributes, and external conditions like weather. To make these predictions accessible and interactive, we will be developing a web app that will allow users to input relevant match details and receive real-time predictions. The core technology requirement for producing these predictions is a machine-learning library that balances speed and accuracy ensuring that predictions are generated quickly without sacrificing performance. Given the structured nature of the data, an efficient model inference library is essential to handle user inputs dynamically and provide meaningful insights into match outcomes. Here are the two libraries that we will focus on:

### Scikit \- Learn:

Initially authored by David Cournapeau in 2007, the library is currently managed by INRIA and is a popular ML library focusing on classical models such as random forests, regression models, etc. It is relatively lightweight and easy to set up but struggles with complex data.

![baseline sklearn model](sklearn_baseline_model.png)

### XGBoost:

Created by Tianqi Chen of the DMLC community, this library is focused on gradient-boosting techniques and is known to perform well on tabular data like our use case. However, it is slightly harder to set up and train due to the importance and complexity of hyperparameter tuning.

![baseline xgboost model](xgboost_baseline_model.png)

### Decision:

Upon comparing the baseline models, both models perform similarly but the random forest model is faster and less computationally expensive to set up. Additionally, utilizing scikit-learn will provide us access to several functions that will make pre-processing our data easier. This is why we have decided to continue with scikit-learn as the library that we will use for our predictive modeling.

However, there are a few concerns that we have when choosing this library. Currently, our dataset isn’t terribly large, but we are still in the process of feature engineering and this could change. A larger dataset will lead to the model from the library becoming more computationally expensive and potentially slower. Additionally, as we continue to introduce more features into our training data there is a chance that the XGBboost library will become more accurate but it is hard to be certain of it now. While we plan on continuing with scikit-learn for now, we plan on re-testing model performance once we have finalized the feature engineering stage.
