#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[1]:


import os
import polars as pl

from datetime import date

from skills_synonym_dict import skills_synonym_dict


# In[ ]:





# In[2]:


DATA_PATH = os.path.join('.', 'data')


# eur  https://www.val.ru/valhistory.asp?tool=978   
# kzt  https://www.val.ru/valhistory.asp?tool=398   
# usd  https://www.val.ru/valhistory.asp?tool=840   
# byr  https://www.val.ru/valhistory.asp?tool=125396   

# In[ ]:





# In[ ]:


def prepare_er(inp_df: pl.DataFrame, inp_curr: str) -> pl.DataFrame:
    '''
    Подготовка валют - сведение всех курсов в один dataframe.
    Заполнение пропусков.
    args
        inp_df: pl.DataFrame - dataframe со всеми датами вакансий
    return
        dataframe - dataframe со всеми крусами за нуобходимые даты
    '''
    csv_path = os.path.join(DATA_PATH, f'{inp_curr}.csv')
    if not os.path.exists(csv_path):
        raise Exception(f'No such currency csv ({csv_path})')

    cur = pl.read_csv(csv_path)
    cur = cur.with_columns(pl.col('date').str.to_date('%d.%m.%y')) 

    # cnt column != 1
    if inp_curr == 'kzt':
        cur = cur.with_columns((pl.col('er') / pl.col('cnt'))\
                          .alias('er'))        

    inp_df = inp_df.join(cur[['date', 'er']], 
                         how='left', on='date', 
                         suffix=f'_{inp_curr}')

    if f'er_{inp_curr}' in inp_df.columns:
        inp_df = inp_df.with_columns(pl.col(f'er_{inp_curr}').forward_fill())
    else:
        inp_df = inp_df.with_columns(pl.col('er').forward_fill())

    return inp_df

def prepare_salary_from(inp_vals: dict) -> pl.Int64:
    '''
    Приведение нижней границы зарплаты к рублю
    args
        inp_vals: dict - нижняя граница зарплаты и валюта зарплаты
    return
        pl.Int64 - нижняя граница зарплаты в рублях
    '''
    s_from = inp_vals['salary_from']
    s_curr = inp_vals['salary_currency']
    s_date = inp_vals['date_created']

    if s_from == -1:
        return -1

    if s_curr.lower() == 'rur':
        return s_from

    exchange_rate = er.filter(pl.col('date') == s_date.date())
    exchange_rate = exchange_rate[f'er_{s_curr.lower()}'].item()

    return int(s_from * exchange_rate)


def prepare_salary_to(inp_vals: dict) -> pl.Int64:
    '''
    Приведение верхней границы зарплаты к рублю
    args
        inp_vals: dict - верхняя граница зарплаты и валюта зарплаты
    return
        pl.Int64 - верхняя граница зарплаты в рублях
    '''
    s_to = inp_vals['salary_to']
    s_curr = inp_vals['salary_currency']
    s_date = inp_vals['date_created']

    if s_to == -1:
        return -1

    if s_curr.lower() == 'rur':
        return s_to

    exchange_rate = er.filter(pl.col('date') == s_date.date())
    exchange_rate = exchange_rate[f'er_{s_curr.lower()}'].item()

    return int(s_to * exchange_rate)


# In[ ]:


er = pl.DataFrame(pl.date_range(date(2025, 4, 1), 
                                date.today(), eager=True
                               ).alias('date'))

er = prepare_er(er, 'usd')
er = prepare_er(er, 'eur')
er = prepare_er(er, 'kzt')
er = prepare_er(er, 'byr')

cols = er.columns
cols[1] = 'er_usd'
er.columns = cols


# In[ ]:





# In[ ]:


tmp_date = date(2025, 4, 5)

er.filter(pl.col('date') == tmp_date)['er_usd'].item()


# In[ ]:





# ## Vacancies

# In[ ]:


vacancies = pl.read_csv(os.path.join(DATA_PATH, 'vacancies.csv'), try_parse_dates=True)
vacancies = vacancies.with_columns(
    pl.struct('salary_from', 'salary_currency', 'date_created')\
        .map_elements(prepare_salary_from, return_dtype=pl.Int64)\
        .alias('salary_from_rur'),
    pl.struct('salary_to', 'salary_currency', 'date_created')\
        .map_elements(prepare_salary_to, return_dtype=pl.Int64)\
        .alias('salary_to_rur'),
)


# In[ ]:


#vacancies.columns


# In[ ]:





# In[ ]:


vacancies.write_csv(os.path.join(DATA_PATH, 'vacancies_prepared.csv'))


# In[ ]:





# ## Skills

# In[5]:


skills = pl.read_csv(os.path.join(DATA_PATH, 'skills.csv'))


# In[16]:


skills = skills.with_columns(
    pl.col('key_skills').replace_strict(skills_synonym_dict, 
                                        default=pl.col("key_skills")
                                        )
                             )


# In[17]:


skills = skills.unique(subset=['vacancy_id', 'key_skills'])


# In[19]:


skills.write_csv(os.path.join(DATA_PATH, 'skills_prepared.csv'))


# In[ ]:




