#!/usr/bin/env python
# coding: utf-8

# TODO:
#    - [x] перевести формирование счетчика навыков в функцию
#    - [ ] добавить обьединенную сортировку по заработной плате
#    - [ ] на основе вышеприведенных пунктов: добавить просмотр навыков по 0.XX самым высокооплачиваемым вакансиям
#    - [x] try - except блок при загрузке данных с сайта
#    - [ ] сделать приложением?

# In[1]:


import os
import time
from tqdm.notebook import tqdm

import re
from collections import Counter

import polars as pl
from matplotlib import pyplot as plt
import plotly.graph_objects as go


# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


DATA_PATH = os.path.join('.', 'data')


# In[4]:


clr = lambda x: (re.sub(r'[<>.,_+*?!/()]', ' ', str(x))).strip().lower()


# In[ ]:





# In[ ]:





# In[5]:


vacancies = pl.read_csv(os.path.join(DATA_PATH, 'vacancies.csv'), try_parse_dates = True)
vacancies = vacancies.with_columns(
    pl.col('date_created').dt.date().alias('date'),
    pl.col('date_created').dt.weekday().alias('weekday'),
    pl.col('date_created').dt.week().alias('week'),
)


# In[ ]:





# In[6]:


Counter(vacancies['role'])


# In[7]:


#vacancies.filter(pl.col('role') == 'Аналитик')


# In[8]:


#skills.filter(pl.col('vacancy_id') == 120074614)


# In[ ]:





# In[23]:


tmp = vacancies.group_by('date').agg(pl.col('vacancy_id').count()).sort(by='date')
#plt.plot(y=tmp['date'], x=tmp['vacancy_id'])
plt.figure(figsize=(15, 6))
plt.plot(tmp['date'], tmp['vacancy_id'],)
plt.title('Кол-во вакансий по дням')


# In[49]:


tmp = vacancies.group_by(['date', 'grade']).agg(pl.col('vacancy_id').count()).sort(by='date')

fig = go.Figure()

tmp_grade = tmp.filter(pl.col('grade') == 'intern').sort(by='date')
fig.add_trace(go.Scatter(x=tmp_grade['date'], 
                         y=tmp_grade['vacancy_id'], 
                         name='intern'))
#fig = go.Figure(data=go.Scatter(x=tmp_grade['date'], 
#                                y=tmp_grade['vacancy_id'], 
#                                name='intern'))

tmp_grade = tmp.filter(pl.col('grade') == 'junior').sort(by='date')
fig.add_trace(go.Scatter(x=tmp_grade['date'], 
                         y=tmp_grade['vacancy_id'], 
                         name='junior'))

tmp_grade = tmp.filter(pl.col('grade') == 'moddle').sort(by='date')
fig.add_trace(go.Scatter(x=tmp_grade['date'], 
                         y=tmp_grade['vacancy_id'], 
                         name='middle'))

tmp_grade = tmp.filter(pl.col('grade') == 'senior').sort(by='date')
fig.add_trace(go.Scatter(x=tmp_grade['date'], 
                         y=tmp_grade['vacancy_id'], 
                         name='senior'))

tmp_grade = tmp.filter(pl.col('grade') == 'head').sort(by='date')
fig.add_trace(go.Scatter(x=tmp_grade['date'], 
                         y=tmp_grade['vacancy_id'], 
                         name='head'))
fig.update_layout(width=1400, 
                  height=600)
fig.show()


# In[ ]:




tmp = vacancies.group_by(['date', 'grade']).agg(pl.col('vacancy_id').count()).sort(by='date')
#plt.plot(y=tmp['date'], x=tmp['vacancy_id'])
plt.figure(figsize=(15, 6))
plt.plot(tmp.filter(pl.col('grade') == 'intern')['date'], 
         tmp.filter(pl.col('grade') == 'intern')['vacancy_id'],
         label='intern',
        )
plt.plot(tmp.filter(pl.col('grade') == 'junior')['date'], 
         tmp.filter(pl.col('grade') == 'junior')['vacancy_id'],
         label='junior',
        )
plt.plot(tmp.filter(pl.col('grade') == 'middle')['date'], 
         tmp.filter(pl.col('grade') == 'middle')['vacancy_id'],
         label='middle',
        )
plt.plot(tmp.filter(pl.col('grade') == 'senior')['date'], 
         tmp.filter(pl.col('grade') == 'senior')['vacancy_id'],
         label='senior',
        )
plt.title('Кол-во вакансий по дням в разрезе грейдов')
plt.legend()
plt.show()
# In[10]:


tmp = vacancies.group_by('week').agg(pl.col('vacancy_id').count()).sort(by='week')
#plt.plot(y=tmp['date'], x=tmp['vacancy_id'])
#plt.figure(figsize=(15, 6))
plt.plot(tmp['week'], tmp['vacancy_id'])
plt.title('Сумарное кол-во вакансий по неделям')
plt.show()


# In[11]:


tmp = vacancies.group_by(['week', 'weekday']).agg(pl.col('vacancy_id').count())\
                    .sort(by=['week', 'weekday'])\
                .group_by('weekday').agg(pl.col('vacancy_id').mean())\
                    .sort(by='weekday')
#plt.figure(figsize=(15, 6))
plt.plot(tmp['weekday'], tmp['vacancy_id'])
plt.title('Среднее кол-во вакансий по дням недели')
plt.show()


# In[ ]:





# In[20]:


only_roles = set(['intern', 'junior', 'middle', 'senior', 'head'])
colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
order = {'intern': 0, 'junior': 1, 'middle': 2, 'senior': 3, 'head': 4,
         'noExperience': 0, 'between1And3': 1, 'between3And6': 2, 'moreThan6': 3,
        }


# In[21]:


tmp = vacancies.filter(pl.col('grade').is_in(only_roles))['grade'].value_counts(normalize=True)
#tmp = tmp.with_columns(pl.col('grade').map_elements(lambda x: order[x], return_dtype=pl.Int8)
#                                        .alias('order')
#                      ).sort('order')

fig = go.Figure(data=[go.Pie(labels=tmp['grade'], values=tmp['proportion'])])
fig.update_traces(textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)),
                 )
fig.update_layout(title=dict(text='Разбивка по грейдам всех вакансий'),
                  legend_traceorder='normal',
                  font=dict(size=18),
                  margin=dict(t=70, b=70, l=0, r=0), 
                  width=600, height=500,
                 )
fig.show()


# In[ ]:





# In[15]:


tmp = vacancies['experience'].value_counts(normalize=True)

fig = go.Figure(data=[go.Pie(labels=tmp['experience'], values=tmp['proportion'])])
fig.update_traces(textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)),
                 )
fig.update_layout(title=dict(text='Разбивка по требуемому опыту всех вакансий'),
                  legend_traceorder='normal',
                  font=dict(size=18),
                  margin=dict(t=70, b=70, l=0, r=0), 
                  width=700, height=500,
                 )
fig.show()


# In[ ]:





# In[58]:


vacancies.filter((pl.col('salary_from') != -1) | (pl.col('salary_to') != -1))['salary_currency'].value_counts()


# In[60]:


vacancies['date_created'].min()


# In[ ]:





# In[ ]:





# ### Зачищаем вакансии так, что бы при наличии в одной вакансии нескольких библиотек js, оставался бы только один js. и т.п.

# In[ ]:





# In[10]:


skills = pl.read_csv(os.path.join(DATA_PATH, 'skills.csv'))


# In[78]:


Counter(skills['key_skills'])


# In[76]:


skill_dict = {
    'ml': 'machine learning', 'машинное обучение': 'machine learning',
    'cv': 'computer vision', 'computer vision engineer': 'computer vision', 'компьютерное зрение': 'computer vision',
    'machine learning engineer': 'machine learning', 'классическое машинное обучение': 'machine learning',
    'методы машинного обучения': 'machine learning', 'standard ml stack': 'machine learning',
    'ml-модели': 'machine learning',
    'deep learning engineer': 'deep learning', 'dl': 'deep learning',
    'recommender systems': 'recsys', 'рекомендательные системы': 'recsys',
    'алгоритмы': 'алгоритмы и структуры данных', 'data structures': 'алгоритмы и структуры данных',
    'sklearn': 'scikit-learn',
    'lgbm': 'lightgbm',
    'mysql' : 'sql', 'ms sql': 'sql',
    'standard nlp stack': 'natural language processing', 'nlp models': 'natural language processing', 
    'nlp': 'natural language processing',
    'a/b-тестирование': 'a/b тесты', 'а/в-тестирования': 'a/b тесты', 'аб тестирование': 'a/b тесты',
    'a/b-тестирования': 'a/b тесты',
    'docker/docker compose': 'docker',
    'ии': 'ai', 'c': 'c/c++', 'с++': 'c/c++', 'c++': 'c/c++',
    'английский b1': 'английский язык', 'разговорный английский': 'английский язык', 'english': 'английский язык',
    'data mining: statistica': 'data mining',
    'github': 'git', 'gitlab': 'git', 'gitlab ci': 'git',
    'k8s': 'kubernetes',
    'ml flow': 'mlflow',
    'apache airflow': 'airflow',
    'android sdk': 'android', 'android studio': 'android',
    'go': 'golang',
    '.net framework': '.net', '.net core': '.net', 'asp.net core': '.net', 'asp.net': '.net',
    'powershell': 'shell',
    'ms power bi': 'power bi', 'bi': 'power bi',
    'информационные технологии': 'it',
    'olap (online analytical processing)': 'olap', 'olap-кубы': 'olap', 
    '1с: предприятие 8': '1с', '1c: erp': '1с', '1с: бухгалтерия': '1с', '1c: управление холдингом': '1с',
    '1с программирование': '1с', '1с зуп': '1с', '1с упп': '1с','1с: розница': '1с',
    'ds': 'data science',
    'html': 'html5',
}


# In[77]:


skills = skills.with_columns(
    pl.col('key_skills').replace_strict(skill_dict, 
                                        default=pl.col("key_skills")
                                       )
)


# In[20]:


#Counter(skills['key_skills'])


# In[189]:


# для обьединения
javascript_list = ['javascript', 'node.js', 'js', 'react', 'react.js', 'reactjs', 'jquery', 'angularjs', 'jquery', 'vue.js', 'vuejs', 'vue', 'backbone', 'redux']

skill_dict = {'анализ данных':'data analysis', 'машинное обучение':'machine learning',
              'ml':'machine learning', 'разработка по':'software development',
              'data scientist': 'data science',
              'opencv': 'computoe vision', 'cv': 'computoe vision', 'компьютерное зрение': 'computoe vision',
              'анализ данных':'data analysis', 'бизнес-анализ':'business analysis',
              'базы данных':'работа с базами данных', 'html5':'html', 
              'проведение презентаций':'presentation skills',
              #?'тестирование': 'a/b', 'qa'
              'kubernetes': 'kubernates',
              'k8s': 'kubernates',
              'marketing analysis': 'маркетинговый анализ',
              'analytical skills': 'аналитическое мышление',
              'cистемы управления базами данных': 'cубд',
              'ms access': 'office', 'ms powerpoint': 'office', 'ms excel': 'office',
              'ms office': 'office', 'ms visio': 'office', 'ms outlook': 'office',#'ms project': 'office', 
              'ms sharepoint': 'office', 
              'powerbi': 'ms power bi',
              'power bi': 'ms power bi',
              'rest api': 'rest',
              'ruby on rails': 'ruby',
              'natural language processing': 'nlp',
              'go': 'golang',
              'negotiation skills': 'ведение переговоров',
              'bigquery': 'google bigquery',
             }
for_change = skill_dict.keys()


# In[249]:


def get_skill_counter(inp_skill_list):
    key_skills = Counter()
    #for el in tqdm(inp_skill_list):
    for el in (inp_skill_list):
        if len(el) > 1:
            skills = []
            for ind in range(len(el)):
                element = el[ind]['name'].lower()

                if 'sql' in element and 'nosql' not in element:
                    skills.append('sql')
                elif 'english' in element:
                    skills.append('английский язык')
                elif 'c++' in element or 'c' == element:
                    skills.append('c/c++')
                elif element in javascript_list:   # should be earlie then 'java'
                    skills.append('javascript')
                elif element.startswith('java'):
                    skills.append('java')
                elif element.startswith('hadoop'):
                    skills.append('hadoop')

                elif element.startswith('css'):
                    skills.append('css')

                elif 'nosql' in element:
                    skills.append('nosql')
                elif element.startswith('qa'):
                    skills.append('qa')
                elif element.startswith('a/b'):
                    skills.append('a/b')
                elif 'тест' in element:
                    skills.append('qa')
                elif 'nlp' in element:
                    skills.append('nlp')
                elif 'продаж' in element or 'холод' in element:
                    skills.append('ignored skills')
                else:
                    skills.append(element)

                #if skills[-1] in for_change:
                #    skills[-1] = skill_dict[skills[-1]]

                if skill_dict.get(skills[-1], False) :
                    skills[-1] = skill_dict.get(skills[-1], '')

            key_skills += Counter(set(skills))
        
    return key_skills


# Посмотрим на требуемые скилы в вакансиях

# In[250]:


#%%timeit -n 100
key_skills_counter = get_skill_counter(key_skills_list)


# In[235]:


show_butch = 0 # какую группу по 50 скилов отображать

for_print = key_skills_counter.most_common()[show_butch*50 : show_butch*50 + 50]
#for_print = key_skills.most_common()[-1*show_butch*50 - 50 : -1*show_butch*50 ]
for el in for_print:
    print(f'{el[1]:3}  {el[0]}')


# 586  python   
# 522  sql   
# 241  английский язык   
# 166  linux   
# 159  java   
# 155  data mining   
# 144  git   
# 139  data analysis   
# 130  c/c++   
# 127  javascript   
# 113  machine learning   
# 107  office   
#  92  математическая статистика    
#  72  работа с базами данных   
#  66  data science   
#  64  аналитическое мышление   
#  61  управление проектами   
#  59  agile project management   
#  58  hadoop   
#  58  c#   
#  56  big data   
#  50  docker   
#  49  spark   
#  48  html   
#  47  css   
#  45  spring framework   
#  42  project management   
#  41  tensorflow   
#  41  qa   
#  40  математический анализ    
#  40  scala   
#  39  business analysis   
#  38  matlab   
#  37  aws   
#  35  аналитические исследования   
#  35  статистический анализ   
#  35  kubernates   
#  34  google analytics   
#  33  pandas   
#  33  crm   
#  32  работа в команде   
#  32  mongodb   
#  32  product management   
#  32  .net framework   
#  31  математическое моделирование   
#  31  nlp   
#  31  team management   
#  30  разработка технических заданий   
#  30  leadership skills   
#  27  pytorch   

# ### Посмотрим на оплату

# In[192]:


df_slr = pd.DataFrame({'slr_from':salary_from_list, 'slr_to':salary_to_list, 'slr_cur':salary_cur_list})
df_slr.shape


# In[193]:


df_slr.head()


# In[224]:


LOWER_BORDER = 30000
UPPER_BORDER = 800000


# In[194]:


df_slr[df_slr.slr_cur == 'rur'].slr_from.dropna().shape, df_slr[['slr_from', 'slr_to']].slr_from.dropna().shape


# In[195]:


plt.boxplot( df_slr[df_slr.slr_cur == 'rur'].slr_from.drop(df_slr[df_slr.slr_cur == 'rur'].slr_from.idxmax()).dropna() )


# In[196]:


#plt.boxplot( df_slr[df_slr.slr_cur == 'rur'].slr_to.dropna() )
plt.boxplot( df_slr[df_slr.slr_cur == 'rur'].slr_to.drop(df_slr[df_slr.slr_cur == 'rur'].slr_to.idxmax()).dropna() )


# если предположить, что все вакансии с оплатой больше 30000 в рублях

# In[227]:


plt.boxplot( df_slr.query('slr_from <= @UPPER_BORDER and slr_from > @LOWER_BORDER').slr_from.dropna())


# In[228]:


plt.boxplot( df_slr.query('slr_from <= @UPPER_BORDER and slr_from > @LOWER_BORDER').slr_to.dropna())


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# #### test

# In[6]:


answ = requests.get(addr, params = {'text':'ML'}, headers = head)
print(len(answ.json(), answ.status_code)


# In[8]:


answ.status_code


# In[9]:


info = answ.json()
print( info['found'] )
print( info['pages'] )
print( len(info['items']) )

print( info['items'][0]['id'] )


# In[ ]:





# In[15]:


answ = requests.get(addr + '/' + str(35218725), headers = head)
vac = answ.json()
#vac


# In[25]:


vac


# In[8]:


print(len(id_list))
print(id_list[:5])
print(area_list[:5])
#print(descr_list[:5])
print(salary_from_list[:5])
print(salary_to_list[:5])
print(salary_cur_list[:5])
print(key_skills_list[:5])
print(date_list[:5])


# In[ ]:


vacancy


# In[ ]:





# In[ ]:


#data_ks[0].value_counts()[60:120]


# In[ ]:




