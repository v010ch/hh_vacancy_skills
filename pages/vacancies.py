'''Дашборд для обзора вакансий'''

import os
from dash import register_page, callback, dcc, html, Output, Input
import polars as pl
from plotly import graph_objects as go
from plotly.subplots import make_subplots

register_page(__name__,
              path='/',
              title='Vacancies Dashboard',
              name='Обзор вакансий',
              )


DATA_PATH = os.path.join('.', 'data')
only_roles = set(['intern', 'junior', 'middle', 'senior', 'head'])
color4 = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
color5 = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'coral']
colors_grade = {'intern': 'gold', 'junior': 'lightcoral',
                'middle': 'mediumturquoise', 'senior': 'darkorange',
                'head': 'lightgreen',
                }


def load_and_prepare_data() -> pl.DataFrame:
    '''
    Загрузка и преобразование исходных данных для отображения
    return
        pl.DataFrame - подготовленные для отображения данные
    '''
    ret_df = pl.read_csv(os.path.join(DATA_PATH, 'vacancies_prepared.csv'),
                         try_parse_dates=True,
                         )
    ret_df = ret_df.with_columns(
        pl.col('date_created').dt.date().alias('date'),
        pl.col('date_created').dt.weekday().alias('weekday'),
        pl.col('date_created').dt.week().alias('week'),
        pl.col('date_created').dt.month().alias('month'),
    )
    return ret_df


def pie_graphs(inp_df: pl.DataFrame):
    '''
    Построение кусочного графика распределения вакансий по заданным параметрам
    args
        pl.DataFrame - исходный dataframe для построения графика
    return
        go.Figure - подготовленный для отображения график
    '''
    tmp = inp_df.filter(pl.col('grade').is_in(only_roles))\
        ['grade'].value_counts(normalize=True)
    # tmp = tmp.with_columns(pl.col('grade').map_elements(lambda x: order[x], return_dtype=pl.Int8)
    #                                        .alias('order')
    #                      ).sort('order')
    pie_grade = go.Pie(labels=tmp['grade'], values=tmp['proportion'],
                       textinfo='label+percent',
                       )

    tmp = inp_df['experience'].value_counts(normalize=True)
    pie_exp = go.Pie(labels=tmp['experience'], values=tmp['proportion'],
                     textinfo='label+percent',
                     )

    two_in_one = make_subplots(rows=1, cols=2, 
                               specs=[[{'type': 'domain'}, {'type': 'domain'}]]
                               )
    two_in_one.add_trace(pie_grade, 1, 1)
    two_in_one.add_trace(pie_exp, 1, 2)
    two_in_one.update_traces(textfont_size=20,
                             marker=dict(colors=color5, line=dict(color='#000000', width=2)),
                             )
    two_in_one.update_layout(
                title_text='Разбивка всех вакансий по грейдам и требуемому опыту',
                title_x=0.5,
                showlegend=False,
                font=dict(size=18),
                margin=dict(t=70, b=70, l=0, r=0),
                width=1400, height=600,
                )

    return two_in_one


def violin_salary(inp_df: pl.DataFrame):
    '''
    Построение pie plot предлагаемых зарплат по грейдами
    args
        pl.DataFrame - исходный dataframe для построения графика
    return
        go.Figure - график, готовый к отображению
    '''
    roles = set(['intern', 'junior', 'middle', 'senior'])
    fig = go.Figure()

    tmp = inp_df.filter(pl.col('salary_from_rur') > 0)
    tmp = tmp.filter(pl.col('grade').is_in(roles))
    tmp = tmp[['date_created', 'grade', 'salary_from_rur',]]
    fig.add_trace(go.Violin(x=tmp['grade'],
                            y=tmp['salary_from_rur'],
                            line_color='black', fillcolor='mediumturquoise',
                            opacity=0.8,
                            legendgroup='from', scalegroup='from', name='от',
                            side='negative',
                            )
                  )

    tmp = inp_df.filter(pl.col('salary_to_rur') > 0)
    tmp = tmp.filter(pl.col('grade').is_in(roles))
    tmp = tmp[['date_created', 'grade', 'salary_to_rur',]]
    fig.add_trace(go.Violin(x=tmp['grade'],
                            y=tmp['salary_to_rur'],
                            line_color='black', fillcolor='gold',
                            opacity=0.8,
                            legendgroup='to', scalegroup='to', name='до',
                            side='positive',
                            )
                  )
    fig.update_traces(meanline_visible=True, 
                      )
    #fig.update_traces(textfont_size=20,
    #                  marker=dict(colors=color5, line=dict(color='#000000', width=2)),
    #                  )
    fig.update_layout(
                title_text='Разбивка всех зарплат по грейдам',
                title_x=0.5,
                # showlegend=True,
                font=dict(size=18),
                margin=dict(t=70, b=70, l=0, r=0),
                width=1400, height=600,
                )

    return fig


vacancies = load_and_prepare_data()
min_date = str(vacancies['date_created'].min().date())
max_date = str(vacancies['date_created'].max().date())
header_text = 'Обзор вакансий data scientist/ML c hh.ru'\
                + f' за период c {min_date} по {max_date}'

fig_pies = pie_graphs(vacancies)
fig_violin_salary = violin_salary(vacancies)


layout = html.Div([
    html.H1(header_text),
    html.Br(),

    # Блок отображения процента распределения грейдов и требуемого опыта
    html.Div(children=[dcc.Graph(figure=fig_pies)]),

    # Блок отображения графиков кол-ва вакансий по заданным параметрам
    dcc.Graph(figure={}, id='time_graph'),
    html.P('Отображать по периоду:'),
    dcc.Dropdown(id='by_period',
                 options=[
                     {'label': 'День', 'value': 'date'},
                     {'label': 'Неделя', 'value': 'week'},
                     {'label': 'Месяц', 'value': 'month'},
                 ],
                 value='date', clearable=False,
                 ),
    html.P('Отображать по грейду:'),
    dcc.Dropdown(id='by_grade',
                 options=['Суммарно', 'По грейдам'],
                 value='Суммарно', clearable=False,
                 ),
    html.Br(),
    html.Br(),
    html.Br(),

    # Блок отображения violin plot предлагаемых зарплат
    html.Div(children=[dcc.Graph(figure=fig_violin_salary)]
             ),
])


@callback(
    Output(component_id='time_graph', component_property='figure'),
    Input(component_id='by_period', component_property='value'),
    Input(component_id='by_grade', component_property='value'),
 )
def scatter_cnt_vacancies(by_period: str, by_grade: str):
    '''
    График кол-ва вакансий, построенный по заданным параметрам
    args
        by_period: str - париод отсчета (день, неделя, месяц)
        by_grade: str - грейд, по которому отображать (суммарно, по грейдам)
    return
        go.Figure - график, готовый к отображению
    '''
    #pediod_dict = {'День': 'date', 'Неделя': 'week', 'Месяц': 'month'}
    ttl_word = {'date': 'дням', 'week': 'неделям', 'month': 'месяцам'}
    ttl_incert = ttl_word[by_period]
    #by_period = pediod_dict[by_period]

    if by_grade == 'Суммарно':
        ttl = f'Кол-во вакансий по {ttl_incert}'
        tmp = vacancies.group_by(by_period)\
                       .agg(pl.col('vacancy_id').count())\
                       .sort(by=by_period)
        fig = go.Figure(data=go.Scatter(x=tmp[by_period], y=tmp['vacancy_id']))
    else:
        ttl = f'Кол-во вакансий по {ttl_incert} и грейдам'
        fig = go.Figure()
        tmp = vacancies.group_by([by_period, 'grade'])\
                       .agg(pl.col('vacancy_id').count())\
                       .sort(by=by_period)
        for el in ['intern', 'junior', 'middle', 'senior', 'head']:
            tmp_grade = tmp.filter(pl.col('grade') == el).sort(by=by_period)
            fig.add_trace(go.Scatter(x=tmp_grade[by_period],
                                     y=tmp_grade['vacancy_id'],
                                     line=dict(color=colors_grade[el],
                                               width=2,
                                               ),
                                     name=el))

    fig.update_layout(title_text=ttl,
                      title_x=0.5,
                      font=dict(size=18),
                      width=1400,
                      height=600)

    return fig
