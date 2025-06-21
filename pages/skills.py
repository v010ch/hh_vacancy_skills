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
# ONLY_ROLES = set(['intern', 'junior', 'middle', 'senior', 'head'])


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
table = skills['key_skills'].value_counts(normalize=True)\
                            .sort(by='proportion', descending=True)

layout = html.Div([
    html.H1(header_text),
    html.Br(),

    # Блок отображения облака скилов
    dcc.Graph(figure={}, id='wordcloud'),
    html.P('Отображать облако скилов по грейду:'),
    dcc.Dropdown(id='by_grade',
                 options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
                 value='Суммарно', clearable=False,
                 ),
    html.P('Отображать с учетом скилов:'),
    dcc.Dropdown(id='exclude',
                 # options=['Всех', 'Без самых очевидных'],
                 options=[{'label': 'Всех', 'value': False},
                          {'label': 'Без самых очевидных', 'value': True},
                          ],
                 value=False, clearable=False,
                 ),
    html.Br(),
    html.Br(),

    # Блок отображения трендов скилов
    dcc.Graph(figure={}, id='skills_trends'),
    html.P('Отображать топ N скилов:'),
    dcc.Dropdown(id='trend_by_grade',
                 options=['0-20', '21-40', '41-60'],
                 value='0-20', clearable=False,
                 ),
    html.P('Отображать тренды по грейду:'),
    dcc.Dropdown(id='trend_by_grade',
                 options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
                 value='Суммарно', clearable=False,
                 ),

    # Блок отображения таблицы скилов
    dash_table.DataTable(data=table.to_dicts(),  # to_dict(), # 'records'
                         columns=[{'name': i, 'id': i} for i in table.columns],
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


@callback(
    Output(component_id='skills_trends', component_property='figure'),
    Input(component_id='trends_by_grade', component_property='value'),
    Input(component_id='trends_part', component_property='value'),
)
def scatter_trend_skills(trends_by_grade: str, trends_part: str):
    '''
    Отображение трендов скилов по частям и грейдам
    args
        trends_part: str - отображать топ 0-20 / 21-40 / 41-60 скилов
        trends_by_grade: str - отображать общее / по грейдам
    return
        go.Figure - подготовленный для отображения график
    '''
    fig = go.Figure()

    # ttl_incert = ttl_word[by_period]
    ttl = f'Отображение трендов топ {trends_part} скилов' + \
           ' для {trends_by_grade} грейда(ов)'
    fig.add_trace(go.Scatter(x=tmp_grade[by_period],
                             y=tmp_grade['vacancy_id'],
                             line={'color': COLORS_GRADE[el],
                                   'width': 2,
                                   },
                             name=el))

    fig.update_layout(title_text=ttl,
                      title_x=0.5,
                      font={'size': 18},
                      width=1400,
                      height=600)

    return fig
