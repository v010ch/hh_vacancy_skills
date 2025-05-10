"""hh"""

import os
from dash import Dash, dcc, html, Output, Input
import polars as pl
from plotly import graph_objects as go
from plotly.subplots import make_subplots


DATA_PATH = os.path.join('.', 'data')
only_roles = set(['intern', 'junior', 'middle', 'senior', 'head'])
color4 = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
color5 = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'darkmagenta']
colors_grade = {'intern': 'gold', 'junior': 'magenta',
                'middle': 'mediumturquoise', 'senior': 'darkorange', 
                'head': 'lightgreen'
                }

app = Dash()


def load_and_prepare_data() -> pl.DataFrame:
    """
    """
    ret_df = pl.read_csv(os.path.join(DATA_PATH, 'vacancies.csv'),
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
    """
    """
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


def time_graph():
    """
    """
    global vacancies
    tmp = vacancies.group_by('date').agg(pl.col('vacancy_id').count()).sort(by='date')
    fig = go.Figure(data=go.Scatter(x=tmp['date'], y=tmp['vacancy_id']))

    return fig


vacancies = load_and_prepare_data()
fig_pies = pie_graphs(vacancies)
# fig_time = time_graph()

app.layout = [
    html.H1('Yes!'),
    html.Br(),
    html.Div(children=[dcc.Graph(figure=fig_pies)]
             ),
    # dcc.Graph(figure=fig_time),
    html.Br(),
    dcc.Graph(figure={}, id='time_graph'),
    html.P("Отображать по периоду:"),
    dcc.Dropdown(id='by_period',
                 options=['День', 'Неделя', 'Месяц',],
                 value='День', clearable=False,
                 ),
    html.P("Отображать по грейду:"),
    dcc.Dropdown(id='by_grade', 
                 options=['Суммарно', 'По грейдам'],
                 value='Суммарно', clearable=False,
                 ),
    html.Br(),
    html.Br(),
    html.Br(),
]


@app.callback(
    Output(component_id='time_graph', component_property='figure'),
    Input(component_id='by_period', component_property='value'),
    Input(component_id='by_grade', component_property='value'),
 )
def cnt_vacancies(by_period: str, by_grade: str):
    """
    """
    # global vacancies
    pediod_dict = {'День': 'date', 'Неделя': 'week', 'Месяц': 'month'}
    ttl_word = {'День': 'дням', 'Неделя': 'неделям', 'Месяц': 'месяцам'}
    ttl_incert = ttl_word[by_period]
    by_period = pediod_dict[by_period]

    if by_grade == 'Суммарно':
        ttl = f'Кол-во вакансий по {ttl_incert}'
        tmp = vacancies.group_by(by_period).agg(pl.col('vacancy_id').count()).sort(by=by_period)
        fig = go.Figure(data=go.Scatter(x=tmp[by_period], y=tmp['vacancy_id']))
    else:
        ttl = f'Кол-во вакансий по {ttl_incert} и грейдам'
        fig = go.Figure()
        tmp = vacancies.group_by([by_period, 'grade']).agg(pl.col('vacancy_id').count()).sort(by=by_period)
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


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
