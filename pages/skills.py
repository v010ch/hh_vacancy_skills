'''Дашборд для обзора ключевых скилов'''

import os
from dash import register_page, callback, dash_table, dcc, html, Output, Input
import polars as pl
from plotly import graph_objects as go
from wordcloud import WordCloud

register_page(__name__,
              path='/skills_dashboard',
              title='Skills Dashboard',
              name='Обзор требуемых умений (скилов)',
              )

DATA_PATH = os.path.join('.', 'data')
only_roles = set(['intern', 'junior', 'middle', 'senior', 'head'])


def load_and_prepare_data() -> pl.DataFrame:
    '''
    Загрузка и преобразование исходных данных для отображения
    return
        pl.DataFrame - подготовленные для отображения данные
    '''
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


layout = html.Div([
    html.H1(header_text),
    html.Br(),

    # Блок отображения wordcloud скилов
    html.P("Отображать по грейду:"),
    dcc.Dropdown(id='by_grade',
                 options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
                 value='Суммарно', clearable=False,
                 ),
    html.P('С учетом скилов:'),
    dcc.Dropdown(id='exclude',
                 # options=['Всех', 'Без самых очевидных'],
                 options=[{'label': 'Всех', 'value': False},
                          {'label': 'Без самых очевидных', 'value': True},
                          ],
                 value=False, clearable=False,
                 ),
    dcc.Graph(figure={}, id='wordcloud'),
    html.Br(),
    html.Br(),

    # Блок отображения таблицы скилов
    dcc.Dropdown(id='table_by_grade',
                 options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
                 value='Суммарно', clearable=False,
                 ),
])


@callback(
    Output(component_id='wordcloud', component_property='figure'),
    Input(component_id='by_grade', component_property='value'),
    Input(component_id='exclude', component_property='value'),
 )
def figure_wordcloud(inp_grade: str, inp_exclude: bool):
    '''
    Построение фигуры wordcloud по заданным параметрам и исходным данным
    args
        inp_grade: str - грейд, для которого отображать wordcloud
        inp_exclude: book - исключать самые очевидные скилы?
    return
        go.Figure - подготовленный для отображения график
    '''
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
