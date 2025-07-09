'''Дашборд для обзора ключевых скилов'''

import datetime
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
ONLY_ROLES = set(['intern', 'junior', 'middle', 'senior', 'head'])
MONTH_NAME = ['', 'Январь', 'Февраль', 'Март', 'Апрель',
              'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
              'Октябрь', 'Ноябрь', 'Декабрь']


def load_and_prepare_data() -> pl.DataFrame:
    '''
    Загрузка и преобразование исходных данных для отображения
    return
        pl.DataFrame - подготовленные для отображения данные
    '''
    ret_df = pl.read_csv(os.path.join(DATA_PATH, 'skills_prepared.csv'),
                         try_parse_dates=True,
                         )
    ret_df = ret_df.with_columns(
        pl.col('date_created').dt.date().alias('date'),
        pl.col('date_created').dt.weekday().alias('weekday'),
        pl.col('date_created').dt.day().alias('day'),
        pl.col('date_created').dt.week().alias('week'),
        pl.col('date_created').dt.month().alias('month'),
        pl.col('date_created').dt.year().alias('year'),
    )
    return ret_df


def trend_table(inp_df: pl.DataFrame) -> pl.DataFrame:
    '''
    args
    return
    '''
    if inp_df['month'].max() < 2:
        # new year cross
        year = 1
        month = 1
    else:
        year = inp_df['year'].max()
        month = inp_df['month'].max() - 2

    tmp = inp_df.filter(pl.col('date_created') >= datetime.date(year, month, 1))\
                .filter(pl.col('grade').is_in(ONLY_ROLES))

    # tmp = tmp.
    tmp = tmp.group_by('month').agg(pl.col('key_skills').value_counts(normalize=True))\
             .explode('key_skills')\
             .with_columns(pl.col('key_skills').map_elements(lambda x: x['key_skills'],
                                                             return_dtype=pl.String)
                                               .alias('key_skills'),
                           pl.col('key_skills').map_elements(lambda x: x['proportion'],
                                                             return_dtype=pl.Float32)
                                               .alias('proportion'),
                           )\
             .sort(by='proportion', descending=True)\
             .filter(pl.col('proportion') >= 0.01)

    key_skills = tmp['key_skills'].unique()
    key_skills = key_skills.to_frame()\
            .join(tmp.filter(pl.col('month') == month)[['key_skills', 'proportion']],
                  on='key_skills',
                  how='left',
                  suffix=f'_m0',
                  )\
            .join(tmp.filter(pl.col('month') == (month + 1))[['key_skills', 'proportion']],
                  on='key_skills',
                  how='left',
                  suffix=f'_m1',
                  )\
            .join(tmp.filter(pl.col('month') == (month + 2))[['key_skills', 'proportion']],
                  on='key_skills',
                  how='left',
                  suffix=f'_m2',
                  )

    key_skills.columns = ['key_skills', f'{month}', f'{month + 1}', f'{month + 2}']
    key_skills = key_skills.with_columns((pl.col(f'{month + 1}') - pl.col(f'{month}')).alias('diff_1'),
                                         (pl.col(f'{month + 2}') - pl.col(f'{month + 1}')).alias('diff_2'),
                                         (pl.col(f'{month + 2}') - pl.col(f'{month}')).alias('diff_3'),
                                         )\
                           .with_columns(pl.mean_horizontal('diff_1', 'diff_2', 'diff_3',
                                                            ignore_nulls=False)\
                                           .alias('trend')
                                         )\
                           .sort('trend', descending=True)\
                           .drop_nans('trend')

    return key_skills


def get_trend_options(inp_len: int) -> list[dict]:
    '''
    Получение опций количества возможных отображений
    трендовых скилов
    args
        inp_len: int - кол-во трендов, доступных к отображению
    return
        опции для отображения в dcc.Dropdown
    '''
    if inp_len > 40:
        inp_len = 40

    sections = [f'{el*(10) + 1}-{(el + 1)*10}' for el in range(inp_len // 10)]
    if inp_len % 10 > 0:
        tmp = (inp_len // 10)
        sections.append(f'{tmp*10 + 1}-{tmp*10 + (inp_len % 10)}')

    sections = [{'label': f'{el}', 'value': f'{el}'} for el in sections]

    return sections


skills = load_and_prepare_data()
min_date = str(skills['date_created'].min().date())
max_date = str(skills['date_created'].max().date())
header_text = 'Обзор ключевых скилов в вакансиях data scientist/ML c hh.ru'\
                + f' за период c {min_date} по {max_date}'
table = skills['key_skills'].value_counts(normalize=True)\
                            .sort(by='proportion', descending=True)[:80]
# table = table.with_columns(pl.col('proportion')
#                              .map_elements(lambda x: round(100*x, 2),
#                                            return_dtype=pl.Float32)
#                            )[:80]
# table.columns = ['Ключевые скилы', 'Процент в вакансиях']
trends = trend_table(skills)
trend_options = get_trend_options(trends.shape[0])


percentage = dash_table.FormatTemplate.percentage(2)
columns = [
    dict(id='key_skills', name='Ключевые скилы'),
    dict(id='proportion', name='Процент в вакансиях',
         type='numeric', format=percentage),
]


layout = html.Div([
    html.H1(header_text),
    html.Br(),

    # Блок отображения облака скилов
    html.H2('Облако слов ключевых вакансий'),
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
                 value=True, clearable=False,
                 ),
    html.Br(),
    html.Br(),

    # Блок отображения трендов скилов
    html.H2('Максимальные тренды скилов (за 3 месяца, не менее 1% вакансий)'),
    dcc.Graph(figure={}, id='skills_trends'),
    html.P('Отображать топ N скилов:'),
    dcc.Dropdown(id='trends_part',
                 # options=['1-10', '11-20', '21-30'],
                 options=trend_options,
                 value='1-10', clearable=False,
                 ),
    # html.P('Отображать тренды по грейду:'),
    # dcc.Dropdown(id='trend_by_grade',
    #              options=['Суммарно', 'intern', 'junior', 'middle', 'senior'],
    #              value='Суммарно', clearable=False,
    #              ),
    html.Br(),
    html.Br(),

    # Блок отображения таблицы скилов
    html.H2('Процент ключевых скилов в вакансиях'),
    dash_table.DataTable(style_data={'width': '300',
                                     'maxWidth': '300px',
                                     'minWidth': '300px',
                                     },
                         # style_table={'overflowX': 'auto'
                         #              },
                         data=table.to_dicts(),
                         columns=columns,
                         page_size=20,
                         fill_width=False,
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
    Input(component_id='trends_part', component_property='value'),
    # Input(component_id='trends_by_grade', component_property='value'),
)
def scatter_trend_skills(trends_part: str):  # trends_by_grade: str
    '''
    Отображение трендов скилов по частям и грейдам
    args
        trends_part: str - отображать топ 0-20 / 21-40 / 41-60 скилов
        trends_by_grade: str - отображать общее / по грейдам
                         (не используется в виду малого кол-ва данных)
    return
        go.Figure - подготовленный для отображения график
    '''
    fig = go.Figure()
    nfrom = int(trends_part.split('-')[0])
    nto = int(trends_part.split('-')[1])

    data = trends[nfrom - 1 : nto]
    # if trends_part == '1-10':
    #     data = trends[:10]
    # elif trends_part == '11-20':
    #     data = trends[11:20]
    # else:  # trends_part == '21-30':
    #     data = trends[21:30]

    month = int(data.columns[1])
    x = [MONTH_NAME[month], MONTH_NAME[month+1], MONTH_NAME[month+2]]
    skill_names = set(data['key_skills'])

    ttl = f'Отображение трендов топ {trends_part} скилов'
    for el in skill_names:
        tmp = data.filter(pl.col('key_skills') == el)\
                            [[f'{month}', f'{month + 1}', f'{month + 2}']]
        fig.add_trace(go.Scatter(x=x,
                                 y=tmp.to_numpy()[0],
                                 mode='lines',
                                 name=el,
                                 # line={'color': COLORS_GRADE[el],
                                 #       'width': 2,
                                 #       },
                                 )
                      )

    fig.update_layout(title_text=ttl,
                      title_x=0.5,
                      # font={'size': 18},
                      width=1400,
                      height=600,
                      )

    return fig
