#!/usr/bin/env python
# coding: utf-8

# TODO:
#    - [x] перевести формирование счетчика навыков в функцию
#    - [ ] добавить обьединенную сортировку по заработной плате
#    - [ ] на основе вышеприведенных пунктов: добавить просмотр навыков по 0.XX самым высокооплачиваемым вакансиям
#    - [x] try - except блок при загрузке данных с сайта
#    - [ ] сделать приложением?

# In[1]:


import requests
from tqdm.notebook import tqdm
from datetime import datetime
from dateutil.parser import parse

import re
import time
from collections import Counter

import pandas as pd


# In[2]:





# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


BREAK_STOP_LEVEL = 3


# In[4]:


addr = 'https://api.hh.ru/vacancies'
head = {'User-Agent': 'NoApp StudyPro/0.0.1'}


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


# In[6]:





# In[7]:


element = vacancies_list[0]
answ = requests.get(addr, params={'text':element}, headers = head)


# In[13]:


answ.json().keys()


# In[14]:


answ.json()['pages']


# In[ ]:





# In[ ]:





# 'area': {'id': '1', 'name': 'Москва'...}    
# 'salary': {'from': 300000, 'to': None, 'currency': 'RUR', 'gross': False}    
# 'description': {'......'}    
# 'key_skills': [{'name': 'Мат стат'}, {'name': 'Мат анализ'}, {'name': 'Python'}, {'name': 'Git'}]     
# 'published_at': YYYY-MM-DDThh:mm:ss±hhmm
answ_pages.json()['items'][0].keys()
'id', 'premium', 'billing_type', 'relations', 'name', 'insider_interview', 'response_letter_required', 'area', 'salary', 'salary_range', 'type', 'address', 'allow_messages', 'experience', 'schedule', 'employment', 'department', 'show_contacts', 'contacts', 'description', 'branded_description', 'vacancy_constructor_template', 'key_skills', 'accept_handicapped', 'accept_kids', 'archived', 'response_url', 'specializations', 'professional_roles', 'code', 'hidden', 'quick_responses_allowed', 'driver_license_types', 'accept_incomplete_resumes', 'employer', 'published_at', 'created_at', 'initial_created_at', 'negotiations_url', 'suitable_resumes_url', 'apply_alternate_url', 'has_test', 'test', 'alternate_url', 'working_days', 'working_time_intervals', 'working_time_modes', 'accept_temporary', 'languages', 'approved', 'employment_form', 'fly_in_fly_out_duration', 'internship', 'night_shifts', 'work_format', 'work_schedule_by_days', 'working_hours', 'show_logo_in_search'
# In[31]:


class VacancySkillsClass():
    """
    """
    def __init__(self):
        """
        """
        self.__clr = lambda x: (re.sub(r'<.*?>', '', str(x)))

        self.__all_id_list  = list()
        self.__new_id_list  = list()
        self.__area_list   = list()
        self.__descr_list  = list()
        self.__salary_from_list = list()
        self.__salary_to_list   = list()
        self.__salary_cur_list  = list()
        #self.__key_skills_list  = list()
        
        self.__date_list = list()
        pass


    def __clear_spec_simbols(self, inp_str: str) -> str:
        """
        """
        return self.__clr(inp_str_)


    def check_id(self, inp_id) -< bool:
        """
        """
        return inp_id in self.__all_id_list


    def collect_data(self, inp_vacancy: dict) -> None:
        """
        """
        #self.__all_id_list.add(inp_vacancy['id'])
        
        self.__new_id.append(inp_vacancy['id'])
        self.__vac_name.append(inp_vacancy['name'])
        descr = self.__clear_spec_simbols(inp_vacancy['description'])
        self.__descr.append(descr)
        self.__role.append(inp_vacancy['professional_roles']['name'])
        self.__experience.append(inp_vacancy['experience']['id'])
        self.__date_created.append(inp_vacancy['created_at'])
        self.__date_published.append(inp_vacancy['published_at'])
        self.__salary_cur.append(inp_vacancy['salary'])
        #skills.salary_from_list
        #skills.salary_to_list
        self.__url.append(inp_vacancy['alternate_url'])
        self.__area.append(inp_vacancy['area']['name'])



class VacancyClass():
    """
    """
    def __init__(self):
        """
        """
        self.__clr = lambda x: (re.sub(r'<.*?>', '', str(x)))

        self.__id_list     = list()
        
        self.__key_skills_list  = list()
        
        self.__date_list = list()
        
        pass


    def __clear_spec_simbols(self, inp_str: str):
        """
        """
        return self.__clr(inp_str_)




#_grade
__new_id = ['id']
__vac_name = ['name']
__area = ['area']['name']
__experience = ['experience']['id']
__role = ['professional_roles']['name']
skills.__date_created = ['created_at']
__date_published = ['published_at']
skills.__descr = ['description']
skills.__all_id_list = ['id']
#skills.key_skills_list
skills.__salary_cur = ['salary']
#skills.salary_from_list
#skills.salary_to_list
__url = ['alternate_url']


# In[ ]:





# ### Забираем данные по вакансиям с hh

# In[17]:


skills = VacancySkillsClass()


# In[13]:


element = vacancies_list[0]

try:
    answ = requests.get(addr, params={'text':element}, headers = head)
    if answ.status_code != 200:
        print('Error get info with ' + element + ' tag')
except:
    print('exception try to get list of vacansies for profession')
    breaks_count += 1
    print('end')


info_tag = answ.json()
amnt_pages = info_tag['pages']
amnt_found = info_tag['found']

print('stage 1')

page = 0
try:
    page = requests.get(addr, params={'text':element, 'page':page}, headers = head)
    print(page.status_code)
    if page.status_code != 200:
        print('Error get info with ' + element + ' tag on page ' + str(page))
except:
    print(f'exception try to get next list of vacansies for {element}')
    breaks_count += 1
    
info_tag_page = page.json()
info_tag_page = info_tag_page['items']

#going through all vacancies on page
vac_idx = 0
try:
    #print(info_tag_page[vac]['id'])
    vacancy = requests.get(addr + '/' + info_tag_page[vac_idx]['id'], headers = head)
    if vacancy.status_code != 200:
        print('Error get info about vacancia ' + info_tag_page[going]['id'])
except:
    print('exception try to get vacancy description')
    breaks_count += 1



# In[19]:


__new_id = ['id']
__vac_name = ['name']
__area = ['area']['name']
__experience = ['experience']['id']
__role = ['professional_roles']['name']
skills.__date_created = ['created_at']
__date_published = ['published_at']
skills.__descr = ['description']
skills.__all_id_list = ['id']
#skills.key_skills_list
skills.__salary_cur = ['salary']
#skills.salary_from_list
#skills.salary_to_list
__url = ['alternate_url']


'salary_range'


# In[21]:


vacancy.json()


# In[ ]:





# In[30]:


get_ipython().run_cell_magic('time', '', '\nid_list = list()\nbreaks_count = 0\n\n# going through all vacancies name\n#for element in vacancies_list:\nfor element in [vacancies_list[0]]:\n    new_ones = 0\n    \n    #getting amount of all vacancies\n    try:\n        answ = requests.get(addr, params={\'text\':element}, headers = head)\n        if answ.status_code != 200:\n            print(\'Error get info with \' + element + \' tag\')\n            break\n    except:\n        print(\'exception try to get list of vacansies for profession\')\n        breaks_count += 1\n        print(\'end\')\n        break\n        \n    print(answ.url)\n    time.sleep(1)\n    \n    info_tag = answ.json()\n    amnt_pages = info_tag[\'pages\']\n    amnt_found = info_tag[\'found\']\n    \n    # going through all pages\n    #for page in tqdm(range(amnt_pages)):\n    for page in tqdm(range(2)):\n        try:\n            answ = requests.get(addr, params={\'text\':element, \'page\':page}, headers = head)\n            if answ.status_code != 200:\n                print(\'Error get info with \' + element + \' tag on page \' + str(page))\n                break\n        except:\n            print(f\'exception try to get next list of vacansies for {element}\')\n            breaks_count += 1\n            if breaks_count > BREAK_STOP_LEVEL:\n                break\n            continue\n            \n        info_tag_page = answ.json()\n        info_tag_page = info_tag_page[\'items\']\n        if len(info_tag_page) == 0:\n            break\n\n\n        #id_list\n        #area_list\n        #descr_list\n        #salary_from_list\n        #salary_to_list\n        #salary_cur_list\n        #key_skills_list\n\n        #going through all vacancies on page\n        for vac_idx in range( len(info_tag_page) ):\n            if info_tag_page[vac_idx][\'id\'] in id_list:\n                break\n            \n            try:\n                #print(info_tag_page[vac][\'id\'])\n                answ = requests.get(addr + \'/\' + info_tag_page[vac_idx][\'id\'], headers = head)\n                if answ.status_code != 200:\n                    print(\'Error get info about vacancia \' + info_tag_page[vac_idx][\'id\'])\n                    break  \n            except:\n                print(\'exception try to get vacancy description\')\n                breaks_count += 1\n                if breaks_count > BREAK_STOP_LEVEL:\n                    break\n                continue\n            vacancy = answ.json()\n            \n            id_list.append(vacancy[\'id\'])\n\n\n            #if not isinstance(vacancy[\'salary\'], type(None)):\n            #    print(\'salary \', vacancy[\'salary\'])\n\n            #if not isinstance(vacancy[\'salary_range\'], type(None)):\n            #    print(\'salary_range \', vacancy[\'salary_range\'])\n\n            new_ones += 1\n                   \n    print(\'Found \' + str(amnt_found) + \' vacancies with key words "\' + element + \'" with \' + str(new_ones) + \' not in list\')\n    \n    \nprint(\'\\nDone\')\n')

Стажер Младший Руководитель Директор Тимлид
Intern Junior Middle Senior Head
# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[39]:


get_ipython().run_cell_magic('time', '', '\nbreaks_count = 0\n\n# going through all vacancies name\nfor element in vacancies_list:\n    new_ones = 0\n    \n    #getting amount of all vacancies\n    try:\n        answ = requests.get(addr, params={\'text\':element}, headers = head)\n        if answ.status_code != 200:\n            print(\'Error get info with \' + element + \' tag\')\n            break\n    except:\n        print(\'exception try to get list of vacansies for profession\')\n        breaks_count += 1\n        print(\'end\')\n        break\n        \n    print(answ.url)\n    time.sleep(1)\n    \n    info_tag = answ.json()\n    amnt_pages = info_tag[\'pages\']\n    amnt_found = info_tag[\'found\']\n    \n    # going through all pages\n    for page in tqdm(range(amnt_pages)):\n        try:\n            answ = requests.get(addr, params={\'text\':element, \'page\':page}, headers = head)\n            if answ.status_code != 200:\n                print(\'Error get info with \' + element + \' tag on page \' + str(page))\n                break\n        except:\n            print(f\'exception try to get next list of vacansies for {element}\')\n            breaks_count += 1\n            if breaks_count > BREAK_STOP_LEVEL:\n                break\n            continue\n            \n        info_tag_page = answ.json()\n        info_tag_page = info_tag_page[\'items\']\n        if len(info_tag_page) == 0:\n            break\n\n\n        #id_list\n        #area_list\n        #descr_list\n        #salary_from_list\n        #salary_to_list\n        #salary_cur_list\n        #key_skills_list\n\n        #going through all vacancies on page\n        for vac in range( len(info_tag_page) ):\n            if info_tag_page[vac][\'id\'] in skills.__id_list:\n                break\n            \n            try:\n                #print(info_tag_page[vac][\'id\'])\n                answ = requests.get(addr + \'/\' + info_tag_page[vac][\'id\'], headers = head)\n                if answ.status_code != 200:\n                    print(\'Error get info about vacancia \' + info_tag_page[vac][\'id\'])\n                    break  \n            except:\n                print(\'exception try to get vacancy description\')\n                breaks_count += 1\n                if breaks_count > BREAK_STOP_LEVEL:\n                    break\n                continue\n            vacancy = answ.json()\n            \n            skills.id_list.append(vacancy[\'id\'])\n            \n            if isinstance(vacancy[\'area\'], type(None)):\n                skills.area_list.append(\'\')\n            else:\n                skills.area_list.append(  vacancy[\'area\'][\'name\'].lower())  # id name\n            \n            if isinstance(vacancy[\'description\'], type(None)):\n                skills.descr_list.append(\'\')\n            else:\n                skills.descr_list.append(  clr(vacancy[\'description\']).lower())  # id name\n            \n            \n            if isinstance(vacancy[\'salary\'], type(None)):\n                skills.salary_from_list.append( None )   # from to\n                skills.salary_to_list.append(   None )   # from to\n                skills.salary_cur_list.append(  None )\n            else:\n                skills.salary_from_list.append( vacancy[\'salary\'][\'from\']) # from to\n                skills.salary_to_list.append(   vacancy[\'salary\'][\'to\'])   # from to\n                skills.salary_cur_list.append(  vacancy[\'salary\'][\'currency\'].lower())\n            \n                        \n            #if len(vacancy[\'key_skills\']) > 0:\n            #    for skill in range( len(vacancy[\'key_skills\']) ):   # name name name name.....\n            #        key_skills_list.append(  vacancy[\'key_skills\'][skill][\'name\'].lower())\n            skills.key_skills_list.append(  vacancy[\'key_skills\'] )   \n            \n            skills.date_list.append( parse(vacancy[\'published_at\'], ignoretz = True) )\n            new_ones += 1\n                   \n    print(\'Found \' + str(amnt_found) + \' vacancies with key words "\' + element + \'" with \' + str(new_ones) + \' not in list\')\n    \n    \nprint(\'\\nDone\')\n')

answ_pages.json()['items'][0].keys()
dict_keys(['id', 'premium', 'name', 'department', 'has_test', 'response_letter_required', 'area', 'salary', 'salary_range', 'type', 'address', 'response_url', 'sort_point_distance', 'published_at', 'created_at', 'archived', 'apply_alternate_url', 'branding', 'show_logo_in_search', 'show_contacts', 'insider_interview', 'url', 'alternate_url', 'relations', 'employer', 'snippet', 'contacts', 'schedule', 'working_days', 'working_time_intervals', 'working_time_modes', 'accept_temporary', 'fly_in_fly_out_duration', 'work_format', 'working_hours', 'work_schedule_by_days', 'night_shifts', 'professional_roles', 'accept_incomplete_resumes', 'experience', 'employment', 'employment_form', 'internship', 'adv_response_url', 'is_adv_vacancy', 'adv_context'])
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




