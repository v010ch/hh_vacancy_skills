'''
Словарь синонимов скилов для замены и объедидения в логические группы.
Отбираются скилы / написание скилов, начиная с 2-3 упоминаний.
'''

# допустимые скилы
possible_skills = set(['ai', 'airflow', 'android', 'aws', 'big data', 'c/c++', 'chat-bot', 'css', 'cv', 'dl',
                       'docker', 'financial analysis', 'go', 'git', 'hive', 'hugging face', 'it', 'java', 'jira', 'js', 'json',
                       'jupyter notebook',
                       'kubernetes', 'lightgbm', 'ml', 'mlflow', '.net',
                       'nlp', 'numpy', 'office', 'olap', 'php', 'power bi', 'r', 'react.js', 'recsys',
                       'sota', 'scikit-learn', 'spark', 'sql',
                       'tensorflow', 'tensorrt', 'time series', 'vue.js',
                       'алгоритмы и структуры данных', 'английский язык', 'базы данных',
                       'математическая статистика',
                       '1с', 'a/b тесты',
                       ])

#  словарь синонимов скилов для замены и объедидения в логические группы
skills_synonym_dict = {
    # A
    'a/b-experiments': 'a/b тесты',
    'android sdk': 'android', 'android studio': 'android',
    'apache airflow': 'airflow', 'apache spark': 'spark', 'apache hive': 'hive',
    'artificial intelligence': 'ai',
    'asp.net core': '.net', 'asp.net': '.net',
    'atlassian jira': 'jira',
    'amazon web services': 'aws', 'aws s3': 'aws',
    # B
    'bi': 'power bi',
    # C
    'c': 'c/c++', 'c++': 'c/c++', 'chatbots': 'chat-bot',
    'computer vision': 'cv', 'computer vision engineer': 'cv',
    'css3': 'css',
    # D
    'data analysis': 'анализ данных',
    'dataenginer': 'data enginer', 'data engineering': 'data engineer',
    'data enginer': 'data enginer',
    'data structures': 'алгоритмы и структуры данных',
    'data scientist': 'data science', 'ds': 'data science',
    'deep learning': 'dl', 'deepl': 'dl',
    'deep learning engineer': 'dl',
    'django framework': 'django',
    'docker/docker compose': 'docker', 'docker-compose': 'docker',
    'ds/ml': 'ml',
    # E
    'english': 'английский язык', 'excel': 'office',
    # F

    # G
    'github': 'git', 'gitlab': 'git', 'gitlab ci': 'git', 'git flow': 'git',
    'go': 'golang', 'google cloud platform (gcp)': 'gcp',
    # H
    'html5': 'html', 'huggingface': 'hugging face',
    # I

    # J
    'java ee': 'java', 'json api': 'json',
    'javascript': 'js',
    'jupiter': 'jupyter notebook', 'jupyter': 'jupyter notebook',
    # K
    'k8s': 'kubernetes',
    # L
    'lgbm': 'lightgbm',
    # M
    'mathematical statistics': 'математическая статистика',
    'machine learning': 'ml', 'ml-модели': 'ml', 'ml модели': 'ml', 'machine learning engineer': 'ml',
    'mle': 'ml',
    'ml flow': 'mlflow', 'ms power bi': 'power bi', 'ms sql': 'sql', 'mysql': 'sql',
    'ms access': 'office', 'ms exchange': 'office', 'ms excel': 'office',
    'ms powerpoint': 'office', 'ms project': 'office', 'ms office': 'office', 'ms outlook': 'office',
    'ms sharepoint': 'office', 'ms visio': 'office',
    'mssql': 'sql',
    # N
    '.net framework': '.net', '.net core': '.net',
    'nampy': 'numpy',
    'neural nets': 'dl',
    'nlp models': 'nlp', 'natural language processing': 'nlp',
    # O
    'oracle pl/sql': 'sql',
    'olap (online analytical processing)': 'olap', 'olap-кубы': 'olap',
    # P
    'php 7/8': 'php', 'postgres': 'sql', 'pyspark': 'spark',
    # Q

    # R
    'r-language': 'r',
    'recommender systems': 'recsys',
    'reactjs': 'react.js', 'react': 'react.js', 'rest': 'rest api',
    # S
    's3': 'aws', 'sklearn': 'scikit-learn', 'skicit-learn': 'scikit-learn', 'standard ml stack': 'ml', 'standard nlp stack': 'nlp',
    'state-of-the-art in machine learning': 'sota', 'sql lite': 'sql',
    # T
    'tensorflow lite': 'tensorflow',
    'tensorpt': 'tensorrt',
    'time series analysis': 'time series',
    # U

    # V
    'vuejs': 'vue.js',
    # W

    # X

    # Y

    # Z

    # А-Я
    '1с: предприятие 8': '1с', '1c: erp': '1с', '1с: бухгалтерия': '1с',
    '1c: управление холдингом': '1с', '1с программирование': '1с',
    '1с: зарплата и управление персоналом': '1с', '1с erp': '1с',
    '1с зуп': '1с', '1с упп': '1с','1с: розница': '1с',
    'a/b-тестирование': 'a/b тесты', 'а/в-тестирования': 'a/b тесты', 'аб тестирование': 'a/b тесты',
    'a/b-тестирования': 'a/b тесты', 'a/b тестирование': 'a/b тесты',
    'алгоритмы': 'алгоритмы и структуры данных',
    'английский b1': 'английский язык', 'английский в2': 'английский язык',
    
    'временные ряды': 'time series',
    'ии': 'ai', 'искусственный интеллект': 'ai', 'ит': 'it',
    'информационные технологии': 'it',
    'компьютерное зрение': 'cv',
    'классическое машинное обучение': 'ml', 'машинное обучение': 'ml',
    'методы машинного обучения': 'ml',
    'нейросети': 'dl', 'нейронные сети': 'dl',
    'основы баз данных': 'базы данных', 'работа с базами данных': 'базы данных',
    'работа с большим объемом информации': 'big data',
    'разговорный английский': 'английский язык',
    'рекомендательные системы': 'recsys',
    'финансовый анализ': 'financial analysis',
    'чат-бот': 'chat-bot',
}