"""hh_skills dash app"""

import os
from dash import register_page, callback, Dash, dash_table, dcc, html, Output, Input
import polars as pl
from plotly import graph_objects as go
from wordcloud import WordCloud

register_page(__name__,
              path="/skills-dashboard",
              title='',
              name='Обзор требуемых умений (скилов)',
              )

DATA_PATH = os.path.join('.', 'data')
only_roles = set(['intern', 'junior', 'middle', 'senior', 'head'])


# app = Dash()


def load_and_prepare_data() -> pl.DataFrame:
    """
    """
    ret_df = pl.read_csv(os.path.join(DATA_PATH, 'skills.csv'),
                         try_parse_dates=True,
                         )
    ret_df = ret_df.with_columns(
        pl.col('date_created').dt.date().alias('date'),
        pl.col('date_created').dt.weekday().alias('weekday'),
        pl.col('date_created').dt.week().alias('week'),
        pl.col('date_created').dt.month().alias('month'),
    )
    return ret_df


skills = load_and_prepare_data()

min_date = str(skills['date_created'].min().date())
max_date = str(skills['date_created'].max().date())
header_text = 'Обзор ключевых скилов в вакансиях data scientist/ML c hh.ru'\
                + f' за период c {min_date} по {max_date}'


# @app.callback(
@callback(
    Output(component_id='wordcloud', component_property='figure'),
    Input(component_id='by_grade', component_property='value'),
    Input(component_id='exclude', component_property='value'),
 )
def figure_wordcloud(inp_grade: str, inp_exclude: str):
    """
    """
    to_exclude = set(['python', 'sql', 'pandas', 'data science', 'git', 
                      'математическая статистика', 'numpy', 'big data', 
                      'английский язык', 'it', 'scikit-learn', 
                      'data analysis', 'matplotlib',
                      ])

    tmp = skills
    if inp_exclude:
        tmp = tmp.filter(~pl.col('key_skills').is_in(to_exclude))

    if inp_grade != 'Суммарно':
        tmp = tmp.filter(pl.col('grade') == inp_grade)

    all_skills = ' '.join(tmp['key_skills'].to_list())
    wcloud = WordCloud().generate(all_skills)

    fig = go.Figure()
    fig.add_trace(go.Image(z=wcloud))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    return fig


# @app.callback(
@callback(
    Output(component_id='skills', component_property='data'),
    Input(component_id='table_by_grade', component_property='value'),
 )
def table_to_show(inp_grade: str):
    """
    """
    tmp_table = skills

    if inp_grade != 'Суммарно':
        tmp_table = skills.filter(pl.col('grade') == inp_grade)

    tmp_table = tmp_table['key_skills'].value_counts(normalize=True)\
                                       .sort(by='proportion',
                                             descending=True)
    tmp_table = tmp_table.slice(0, 50)

    return tmp_table.to_dict(as_series=False)


# app.layout = [
layout = [
    html.H1(header_text),
    html.Br(),
    html.P("Отображать по грейду:"),
    dcc.Dropdown(id='by_grade',
                 options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
                 value='Суммарно', clearable=False,
                 ),
    html.P("С учетом скилов:"),
    dcc.Dropdown(id='exclude',
                 options=['Всех', 'Без самых очевидных'],
                 value='Всех', clearable=False,
                 ),
    dcc.Graph(figure={}, id='wordcloud'),
    html.Br(),
    html.Br(),
    dcc.Dropdown(id='table_by_grade',
                 options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
                 value='Суммарно', clearable=False,
                 ),
    dash_table.DataTable(id='skills',
                         data={},
                         ),
    html.Br(),
    html.Br(),
    html.Br(),
]


# if __name__ == '__main__':
#     app.run()