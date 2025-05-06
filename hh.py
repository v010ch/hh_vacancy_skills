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
import requests
from tqdm.notebook import tqdm
from datetime import datetime
from dateutil.parser import parse

import re
import time
from collections import Counter

import polars as pl
#import pandas as pd


# In[ ]:





# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


BREAK_STOP_LEVEL = 3
DATA_PATH = os.path.join('.', 'data')


# In[4]:


addr = 'https://api.hh.ru/vacancies'
head = {'User-Agent': 'NoApp StudyPro/0.9.1'}


# In[5]:


vacancies_list = ['Data scientist',
                  'Data science',
                  'Дата Саентист',
                  'Machine learning',
                  'ML',
                  'Ml-engeneer',
                  'CV-engeneer',
                  'NLP',
                 ]


# In[ ]:





# 'area': {'id': '1', 'name': 'Москва'...}    
# 'salary': {'from': 300000, 'to': None, 'currency': 'RUR', 'gross': False}    
# 'description': {'......'}    
# 'key_skills': [{'name': 'Мат стат'}, {'name': 'Мат анализ'}, {'name': 'Python'}, {'name': 'Git'}]     
# 'published_at': YYYY-MM-DDThh:mm:ss±hhmm
answ_pages.json()['items'][0].keys()
'id', 'premium', 'billing_type', 'relations', 'name', 'insider_interview', 'response_letter_required', 'area', 'salary', 'salary_range', 'type', 'address', 'allow_messages', 'experience', 'schedule', 'employment', 'department', 'show_contacts', 'contacts', 'description', 'branded_description', 'vacancy_constructor_template', 'key_skills', 'accept_handicapped', 'accept_kids', 'archived', 'response_url', 'specializations', 'professional_roles', 'code', 'hidden', 'quick_responses_allowed', 'driver_license_types', 'accept_incomplete_resumes', 'employer', 'published_at', 'created_at', 'initial_created_at', 'negotiations_url', 'suitable_resumes_url', 'apply_alternate_url', 'has_test', 'test', 'alternate_url', 'working_days', 'working_time_intervals', 'working_time_modes', 'accept_temporary', 'languages', 'approved', 'employment_form', 'fly_in_fly_out_duration', 'internship', 'night_shifts', 'work_format', 'work_schedule_by_days', 'working_hours', 'show_logo_in_search'
# In[ ]:





# In[7]:


class UtilityClass():
    def __init__(self):
        self._clr = lambda x: (re.sub(r'[<>.,_+*?!/()]', ' ', str(x))).strip().lower()


    def _grade(self, inp_vac_name: str) -> str:
        """
        """
        name = self._clr(inp_vac_name)

        if 'стажер' in name or\
           'стажёр' in name or\
           'intern' in name:
            return 'intern'

        if 'junior' in name or\
           'младший' in name:
            return 'junior'

        if 'middle' in name:
            return 'middle'

        if 'старший' in name or\
           'senior' in name:
            return 'senior'

        if 'head' in name or\
           'директор' in name or\
           'руководитель' in name:
            return 'head'

        if 'leader' in name or\
           'лидер' in name:
            return 'team-leader'

        return 'unknown' # middle?


    def _salary(self, inp_salary: dict) -> tuple:
        """
        """
        ret_from = -1
        ret_to = -1
        ret_currency = '-1'
        if 'from' in inp_salary.keys() and\
            not isinstance(inp_salary['from'], type(None)):
            ret_from = inp_salary['from']

        if 'to' in inp_salary.keys() and\
            not isinstance(inp_salary['to'], type(None)):
            ret_to = inp_salary['to']

        if 'currency' in inp_salary.keys() and\
            not isinstance(inp_salary['currency'], type(None)):
            ret_currency = inp_salary['currency']

        return (ret_from, ret_to, ret_currency)



class VacancyClass(UtilityClass):
    """
    """
    def __init__(self):
        super().__init__()
        self.__all_id = set()
        self.__new_id = list()
        self.__area = list()
        self.__date_created = list()
        self.__date_published = list()
        self.__descr = list()
        self.__experience = list()
        self.__role = list()
        self.__salary_from = list()
        self.__salary_to = list()
        self.__salary_cur = list()
        self.__vac_name = list()
        self.__url = list()

        if os.path.exists(os.path.join(DATA_PATH, 'vacancies.csv')):
            tmp_df = pl.read_csv(os.path.join(DATA_PATH, 'vacancies.csv'), columns=['vacancy_id'])
            self.__all_id = set(tmp_df.unique().to_numpy().reshape(-1))
            print('all_id ', len(self.__all_id))


    def add_id(self, inp_id: int) -> None:
        """
        """
        self.__all_id.add(inp_id)


    def check_id(self, inp_id: int) -> bool:
        """
        """
        return inp_id in self.__all_id


    def collect_data(self, inp_vacancy: dict) -> None:
        """
        """
        self.__new_id.append(int(inp_vacancy['id']))
        self.__vac_name.append(inp_vacancy['name'].lower())
        descr = self._clr(inp_vacancy['description'])
        self.__descr.append(descr)
        self.__role.append(inp_vacancy['professional_roles'][0]['name'])
        self.__experience.append(inp_vacancy['experience']['id'])
        self.__date_created.append(inp_vacancy['created_at'])
        self.__date_published.append(inp_vacancy['published_at'])
        self.__url.append(inp_vacancy['alternate_url'])
        self.__area.append(inp_vacancy['area']['name'])

        if isinstance(inp_vacancy['salary'], type(None)):
            self.__salary_from.append(-1)
            self.__salary_to.append(-1)
            self.__salary_cur.append('-1')
        else:
            (s_from, s_to, s_cur) = self._salary(inp_vacancy['salary'])
            self.__salary_from.append(s_from)
            self.__salary_to.append(s_to)
            self.__salary_cur.append(s_cur)


    def reset(self) -> None:
        """
        """
        self.__new_id = list()
        self.__area = list()
        self.__date_created = list()
        self.__date_published = list()
        self.__descr = list()
        self.__experience = list()
        self.__role = list()
        self.__salary_from = list()
        self.__salary_to = list()
        self.__salary_cur = list()
        self.__vac_name = list()
        self.__url = list()


    def savevacancies(self) -> None:
        """
        """
        if len(self.__new_id) <= 0:
            return 

        new_data = pl.DataFrame({
                    'vacancy_id': self.__new_id,
                    'vacancy_name': self.__vac_name,
                    'role': self.__role,
                    'experience': self.__experience,
                    'date_created': self.__date_created,
                    'date_published': self.__date_published,
                    'salary_from': self.__salary_from,
                    'salary_to': self.__salary_to,
                    'salary_currency': self.__salary_cur,
                    'url': self.__url,
                    'area': self.__area,
                    'description': self.__descr,
                         })
        new_data = new_data.with_columns(
            pl.col('vacancy_name').map_elements(self._grade, return_dtype=pl.String).\
                alias('grade'),
            #pl.col('vacancy_id').cast(pl.Int64)),
        )
        #change column order for better view
        new_data = new_data.select(['vacancy_id', 'vacancy_name', 'role', 'grade', 'experience',
                                    'date_created', 'date_published', 
                                    'salary_from', 'salary_to', 'salary_currency',
                                    'url', 'area', 'description'
                                   ])

        if os.path.exists(os.path.join(DATA_PATH, 'vacancies.csv')):
            data = pl.read_csv(os.path.join(DATA_PATH, 'vacancies.csv'))
            data = pl.concat([data, new_data])
        else:
            data = new_data


        data.write_csv(os.path.join(DATA_PATH, 'vacancies.csv'))



class VacancySkillsClass(UtilityClass):
    """
    """
    def __init__(self):
        super().__init__()
        self.__id = list()
        self.__name = list()
        self.__key_skills = list()
        self.__date_created = list()
        self.__date_published = list()


    def collect_skills(self, inp_vacancy: dict) -> None:
        """
        """
        if len(inp_vacancy['key_skills']) == 0:
            return

        for skill in inp_vacancy['key_skills']:
            self.__key_skills.append(skill['name'].lower())
            self.__id.append(int(inp_vacancy['id']))
            self.__name.append(inp_vacancy['name'].lower())
            self.__date_created.append(inp_vacancy['created_at'])
            self.__date_published.append(inp_vacancy['published_at'])


    def reset(self) -> None:
        """
        """
        self.__id = list()
        self.__name = list()
        self.__key_skills = list()
        self.__date_created = list()
        self.__date_published = list()


    def saveskills(self) -> None:
        """
        """
        if len(self.__id) <= 0:
            return

        new_data = pl.DataFrame({
                    'vacancy_id': self.__id,
                    'vacancy_name': self.__name,
                    'key_skills': self.__key_skills,
                    'date_created': self.__date_created,
                    'date_published': self.__date_published,
                         })
        new_data = new_data.with_columns(
            pl.col('vacancy_name').map_elements(self._grade, return_dtype=pl.String).\
                alias('grade'),
            #pl.col('vacancy_id').cast(pl.Int64)),
            )
        #change column order for better view
        new_data = new_data.select(['vacancy_id', 'vacancy_name', 'grade',
                                   'key_skills', 'date_created', 'date_published'])
        
        if os.path.exists(os.path.join(DATA_PATH, 'skills.csv')):
            data = pl.read_csv(os.path.join(DATA_PATH, 'skills.csv'))
            data = pl.concat([data, new_data])
        else:
            data = new_data
        data.write_csv(os.path.join(DATA_PATH, 'skills.csv'))


# In[ ]:





# # Забираем данные по вакансиям с hh

# In[8]:


vacancy = VacancyClass()
skills = VacancySkillsClass()


# In[ ]:





# In[11]:


get_ipython().run_cell_magic('time', '', 'vacancy.reset()\nskills.reset()\nbreaks_count = 0\n\n# going through all vacancies name\n#for element in vacancies_list:\nfor element in [vacancies_list[0]]:\n    new_ones = 0\n    \n    #getting amount of all vacancies\n    try:\n        answ = requests.get(addr, params={\'text\':element}, headers = head)\n        if answ.status_code != 200:\n            print(\'Error get info with \' + element + \' tag\')\n            break\n    except:\n        print(\'exception try to get list of vacansies for profession\')\n        breaks_count += 1\n        print(\'end\')\n        break\n        \n    print(answ.url)\n    time.sleep(1)\n    \n    info_tag = answ.json()\n    amnt_pages = info_tag[\'pages\']\n    amnt_found = info_tag[\'found\']\n    \n    # going through all pages\n    #for page in tqdm(range(amnt_pages)):\n    for page in tqdm(range(4)):\n        try:\n            answ = requests.get(addr, params={\'text\':element, \'page\':page}, headers = head)\n            if answ.status_code != 200:\n                print(\'Error get info with \' + element + \' tag on page \' + str(page))\n                break\n        except:\n            print(f\'exception try to get next list of vacansies for {element}\')\n            breaks_count += 1\n            if breaks_count > BREAK_STOP_LEVEL:\n                break\n            continue\n            \n        info_tag_page = answ.json()\n        info_tag_page = info_tag_page[\'items\']\n        if len(info_tag_page) == 0:\n            break\n\n        #going through all vacancies on page\n        for vac_idx in range( len(info_tag_page) ):\n            #print(info_tag_page[vac_idx][\'id\'])\n            if vacancy.check_id(info_tag_page[vac_idx][\'id\']):\n                #print(info_tag_page[vac_idx][\'id\'])\n            #if info_tag_page[vac_idx][\'id\'] in id_list:\n                break\n            \n            try:\n                #print(info_tag_page[vac][\'id\'])\n                answ = requests.get(addr + \'/\' + info_tag_page[vac_idx][\'id\'], headers = head)\n                if answ.status_code != 200:\n                    print(\'Error get info about vacancia \' + info_tag_page[vac_idx][\'id\'] +\\\n                          \'code \' + answ.status_code)\n                    break  \n            except:\n                print(\'exception try to get vacancy description\')\n                breaks_count += 1\n                if breaks_count > BREAK_STOP_LEVEL:\n                    break\n                continue\n            vac = answ.json()\n            \n            vacancy.collect_data(vac)\n            skills.collect_skills(vac)\n            vacancy.add_id(info_tag_page[vac_idx][\'id\'])\n            new_ones += 1\n    \n    print(\'Found \' + str(amnt_found) + \' vacancies with key words "\' + element + \'" with \' + str(new_ones) + \' not in list\')\n\nskills.saveskills()\nvacancy.savevacancies()\nprint(\'\\nDone\')\n')


# In[ ]:





# # TODO below

# ### Зачищаем вакансии так, что бы при наличии в одной вакансии нескольких библиотек js, оставался бы только один js. и т.п.

# In[188]:


key_skills_list[:5]


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


# In[ ]:





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





# In[ ]:




