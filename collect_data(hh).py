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
import time
from tqdm.notebook import tqdm

import re
from collections import Counter

import polars as pl


# In[ ]:





# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


BREAK_STOP_LEVEL = 3
DATA_PATH = os.path.join('.', 'data')


# In[4]:


addr = 'https://api.hh.ru/vacancies'
head = {'User-Agent': 'NoApp StudyPro/0.9.5'}


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

enabled_professional_roles = set([
    'Дата-сайентист', 'Программист, разработчик', 'Аналитик', 'Другое',
    'BI-аналитик, аналитик данных', 'Научный специалист, исследователь',
    'Специалист по информационной безопасности', 
    'Директор по информационным технологиям (CIO)', 'Технический директор (CTO)',
    'Финансовый аналитик, инвестиционный аналитик'
                                 ])


# In[ ]:





# 'area': {'id': '1', 'name': 'Москва'...}    
# 'salary': {'from': 300000, 'to': None, 'currency': 'RUR', 'gross': False}    
# 'description': {'......'}    
# 'key_skills': [{'name': 'Мат стат'}, {'name': 'Мат анализ'}, {'name': 'Python'}, {'name': 'Git'}]     
# 'published_at': YYYY-MM-DDThh:mm:ss±hhmm
answ_pages.json()['items'][0].keys()
'id', 'premium', 'billing_type', 'relations', 'name', 'insider_interview', 'response_letter_required', 'area', 'salary', 'salary_range', 'type', 'address', 'allow_messages', 'experience', 'schedule', 'employment', 'department', 'show_contacts', 'contacts', 'description', 'branded_description', 'vacancy_constructor_template', 'key_skills', 'accept_handicapped', 'accept_kids', 'archived', 'response_url', 'specializations', 'professional_roles', 'code', 'hidden', 'quick_responses_allowed', 'driver_license_types', 'accept_incomplete_resumes', 'employer', 'published_at', 'created_at', 'initial_created_at', 'negotiations_url', 'suitable_resumes_url', 'apply_alternate_url', 'has_test', 'test', 'alternate_url', 'working_days', 'working_time_intervals', 'working_time_modes', 'accept_temporary', 'languages', 'approved', 'employment_form', 'fly_in_fly_out_duration', 'internship', 'night_shifts', 'work_format', 'work_schedule_by_days', 'working_hours', 'show_logo_in_search'"intern"	"noExperience"	7     "between1And3"	1     
"junior"	"noExperience"	3     "between1And3"	14      "between3And6"	1     
"middle"	                      "between1And3"	11      "between3And6"	17      "moreThan6"	    3
"senior"	                      "between1And3"	4       "between3And6"	50      "moreThan6"	    5
"head"	                          "between1And3"	2	    "between3And6"	6       "moreThan6"	    1
# In[6]:


class UtilityClass():
    """
    """
    def __init__(self):
        self._clr = lambda x: (re.sub(r'[<>.,_+*?!/()]', ' ', str(x))).strip().lower()


    def _grade(self, inp_vals: dict) -> str:
        """
        """
        name = self._clr(inp_vals['vacancy_name'])
    
        if 'intern' in name and\
           'junior' in name:
            return 'intern/junior'
    
        if 'junior' in name and\
           'middle' in name:
            return 'junior/middle'
    
        if 'middle' in name and\
           'senior' in name:
            return 'middle/senior'
    
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
    
        #without grade in headder
        #analysing experience
        experience = inp_vals['experience'].lower()
        if experience == 'noexperience':
            return 'intern'
    
        if experience == 'between1and3':
            return 'junior'
    
        if experience == 'between3and6':    #or senior. think senior should be at header
            return 'middle'
    
        if experience == 'morethan6':
            return 'senior'
    
        #print(name, experience)
        return 'unknown' # cann't be here


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
        #descr = self._clr(inp_vacancy['description'])
        descr = inp_vacancy['description']
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
            pl.struct('vacancy_name', 'experience').map_elements(self._grade, return_dtype=pl.String).\
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
            pl.struct('vacancy_name', 'experience').map_elements(self._grade, return_dtype=pl.String).\
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

# In[7]:


vacancy = VacancyClass()
skills = VacancySkillsClass()


# In[ ]:





# In[8]:


get_ipython().run_cell_magic('time', '', 'vacancy.reset()\nskills.reset()\nbreaks_count = 0\n\n# going through all vacancies name\nfor element in vacancies_list:\n#for element in [vacancies_list[0]]:\n    new_ones = 0\n\n    #getting amount of all vacancies\n    try:\n        answ = requests.get(addr, params={\'text\':element}, headers = head)\n        if answ.status_code != 200:\n            print(\'Error get info with \' + element + \' tag\')\n            break\n    except:\n        print(\'exception try to get list of vacansies for profession\')\n        breaks_count += 1\n        print(\'end\')\n        break\n\n    print(answ.url)\n    time.sleep(1)\n\n    info_tag = answ.json()\n    amnt_pages = info_tag[\'pages\']\n    amnt_found = info_tag[\'found\']\n\n    # going through all pages\n    for page in tqdm(range(amnt_pages)):\n    #for page in tqdm(range(4)):\n        try:\n            answ = requests.get(addr, params={\'text\':element, \'page\':page}, headers = head)\n            if answ.status_code != 200:\n                print(\'Error get info with \' + element + \' tag on page \' + str(page))\n                break\n        except:\n            print(f\'exception try to get next list of vacansies for {element}\')\n            breaks_count += 1\n            if breaks_count > BREAK_STOP_LEVEL:\n                break\n            continue\n            \n        info_tag_page = answ.json()\n        info_tag_page = info_tag_page[\'items\']\n        if len(info_tag_page) == 0:\n            break\n\n        #print(hahahaha)\n        #going through all vacancies on page\n        for vac_idx in range( len(info_tag_page) ):\n            if vacancy.check_id(info_tag_page[vac_idx][\'id\']):\n                break\n\n            role = info_tag_page[vac_idx][\'professional_roles\'][0][\'name\']\n            if not role in enabled_professional_roles:\n                break\n\n            try:\n                #print(info_tag_page[vac][\'id\'])\n                answ = requests.get(addr + \'/\' + info_tag_page[vac_idx][\'id\'], headers = head)\n                if answ.status_code != 200:\n                    print(\'Error get info about vacancia \' + info_tag_page[vac_idx][\'id\'] +\\\n                          \'code \' + answ.status_code)\n                    break  \n            except:\n                print(\'exception try to get vacancy description\')\n                breaks_count += 1\n                if breaks_count > BREAK_STOP_LEVEL:\n                    break\n                continue\n            vac = answ.json()\n\n            vacancy.collect_data(vac)\n            skills.collect_skills(vac)\n            vacancy.add_id(info_tag_page[vac_idx][\'id\'])\n            new_ones += 1\n\n            time.sleep(0.37)\n\n    print(\'Found \' + str(amnt_found) + \' vacancies with key words "\' + element + \'" with \' + str(new_ones) + \' not in list\')\n\nskills.saveskills()\nvacancy.savevacancies()\nprint(\'\\nDone\')\n')


# In[ ]:





# In[ ]:





# In[19]:


#info_tag_page


# In[ ]:




