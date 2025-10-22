import pandas as pd
import os
import hashlib

tests_by_organ_system =  {
    'Сердечно-сосудистая система': {
        'common': ['ЭКГ', 'ЭхоКГ', 'Суточное мониторирование ЭКГ', 'Суточное мониторирование АД'],
        'specific': {
            'Кардиолог': ['Коронароангиография', 'Стресс-эхокардиография', 'Велоэргометрия'],
            'Флеболог': ['УЗДГ вен нижних конечностей', 'Флебография', 'Дуплексное сканирование вен']
        }
    },
    'Дыхательная система': {
        'common': ['Рентген грудной клетки', 'Спирометрия', 'КТ органов грудной клетки'],
        'specific': {
            'Пульмонолог': ['Бронхоскопия', 'Исследование функции внешнего дыхания', 'Плевральная пункция'],
            'Аллерголог': ['Аллергопробы', 'Иммуноглобулин E', 'Спирометрия с бронхолитиком']
        }
    },
    'Пищеварительная система': {
        'common': ['УЗИ брюшной полости', 'ФГДС', 'Колоноскопия', 'Биохимический анализ крови'],
        'specific': {
            'Гастроэнтеролог': ['pH-метрия', 'Дыхательный тест на хеликобактер', 'Эластография печени'],
            'Проктолог': ['Ректороманоскопия', 'Аноскопия', 'Ирригоскопия'],
            'Хирург': ['Диагностическая лапароскопия', 'ЭРХПГ']
        }
    },
    'Нервная система': {
        'common': ['МРТ головного мозга', 'ЭЭГ', 'УЗДГ сосудов головы и шеи'],
        'specific': {
            'Невролог': ['Электронейромиография', 'Вызванные потенциалы', 'Люмбальная пункция'],
            'Нейрохирург': ['КТ головного мозга с контрастом', 'Ангиография сосудов мозга']
        }
    },
    'Опорно-двигательная система': {
        'common': ['Рентген суставов', 'МРТ позвоночника', 'Денситометрия'],
        'specific': {
            'Ортопед': ['Артроскопия', 'КТ суставов', 'УЗИ суставов'],
            'Ревматолог': ['Анализ на ревматоидный фактор', 'АЦЦП', 'С-реактивный белок'],
            'Травматолог': ['КТ костей', 'МРТ мягких тканей']
        }
    },
    'Мочеполовая система': {
        'common': ['УЗИ почек', 'УЗИ мочевого пузыря', 'Общий анализ мочи'],
        'specific': {
            'Уролог': ['Цистоскопия', 'Урофлоуметрия', 'Анализ секрета простаты'],
            'Нефролог': ['Проба Реберга', 'Суточный анализ мочи', 'Биопсия почки'],
            'Гинеколог': ['УЗИ малого таза', 'Кольпоскопия', 'Мазок на флору']
        }
    },
    'Эндокринная система': {
        'common': ['Анализ крови на гормоны', 'УЗИ щитовидной железы', 'Глюкоза крови'],
        'specific': {
            'Эндокринолог': ['Гликированный гемоглобин', 'Тест на толерантность к глюкозе', 'Кортизол'],
            'Диетолог': ['Биоимпедансометрия', 'Липидный профиль', 'Инсулин']
        }
    },
    'Кожа и придатки': {
        'common': ['Соскоб с кожи', 'Дерматоскопия', 'Общий анализ крови'],
        'specific': {
            'Дерматолог': ['Биопсия кожи', 'Посев на грибы', 'Аллергопатчи'],
            'Трихолог': ['Трихоскопия', 'Фототрихограмма', 'Анализ волос на микроэлементы'],
            'Подолог': ['Соскоб с ногтей', 'Микологический посев']
        }
    },
    'Органы чувств': {
        'common': ['Визометрия', 'Тонометрия', 'Аудиометрия'],
        'specific': {
            'Офтальмолог': ['ОКТ сетчатки', 'Периметрия', 'Биомикроскопия'],
            'Отоларинголог': ['Эндоскопия ЛОР-органов', 'Тимпанометрия', 'Вестибулометрия']
        }
    },
    'Иммунная система': {
        'common': ['Иммунограмма', 'Общий анализ крови', 'С-реактивный белок'],
        'specific': {
            'Иммунолог': ['Интерфероновый статус', 'Анализ на цитокины', 'Тест на фагоцитоз'],
            'Аллерголог': ['Иммуноглобулин E', 'Тест на специфические IgE', 'Кожные пробы']
        }
    },
    'Женская половая система': {
        'common': ['УЗИ малого таза', 'Мазок на цитологию', 'Анализ на половые гормоны'],
        'specific': {
            'Гинеколог': ['Гистероскопия', 'Кольпоскопия', 'Анализ на ИППП'],
            'Маммолог': ['Маммография', 'УЗИ молочных желез', 'Биопсия молочной железы']
        }
    },
    'Мужская половая система': {
        'common': ['УЗИ предстательной железы', 'Анализ секрета простаты', 'Спермограмма'],
        'specific': {
            'Уролог': ['ТРУЗИ', 'Анализ на ПСА', 'Биопсия простаты'],
            'Андролог': ['MAR-тест', 'Анализ фрагментации ДНК сперматозоидов', 'Гормональный профиль']
        }
    },
    'Кровь и кроветворная система': {
        'common': ['Общий анализ крови', 'Коагулограмма', 'Биохимический анализ крови'],
        'specific': {
            'Гематолог': ['Стернальная пункция', 'Трепанобиопсия', 'Проточная цитометрия'],
            'Трансфузиолог': ['Проба Кумбса', 'Определение группы крови и резус-фактора']
        }
    },
    'Психическая сфера': {
        'common': ['ЭЭГ', 'МРТ головного мозга', 'Общий анализ крови'],
        'specific': {
            'Психиатр': ['Психологическое тестирование', 'Электроэнцефалография', 'Токсикологический анализ'],
            'Психотерапевт': ['Проективные тесты', 'Опросники тревоги и депрессии']
        }
    },
    'Стоматологическая система': {
        'common': ['Ортопантомограмма', 'КТ челюстей', 'Бактериологический посев'],
        'specific': {
            'Стоматолог': ['Витальное окрашивание зубов', 'ЭОД', 'Пародонтальный индекс'],
            'Ортодонт': ['Телерентгенограмма', 'Анализ моделей челюстей']
        }
    },
    'Реабилитационная система': {
        'common': ['Функциональные пробы', 'ЭНМГ', 'Стабилометрия'],
        'specific': {
            'Физиотерапевт': ['Электромиография', 'Гониометрия', 'Тест мышечной силы'],
            'Реабилитолог': ['Анализ походки', 'Баланс-тест', 'Кардиопульмональный тест']
        }
    },
    'Сомнологическая система': {
        'common': ['Полисомнография', 'ЭЭГ ночного сна', 'Пульсоксиметрия'],
        'specific': {
            'Сомнолог': ['MSLT-тест', 'Респираторный мониторинг', 'Актиграфия']
        }
    },
    'Профессиональные заболевания': {
        'common': ['Спирометрия', 'Аудиометрия', 'Рентген органов грудной клетки'],
        'specific': {
            'Профпатолог': ['Анализ на тяжелые металлы', 'Пылевой анализ', 'Виброметрия']
        }
    },
    'Детские заболевания': {
        'common': ['Общий анализ крови', 'Общий анализ мочи', 'УЗИ органов брюшной полости'],
        'specific': {
            'Педиатр': ['Неонатальный скрининг', 'Анализ на дисбактериоз', 'Копрограмма'],
            'Неонатолог': ['Анализ крови новорожденного', 'Билирубин', 'Газовый состав крови']
        }
    },
    'Возрастные изменения': {
        'common': ['Денситометрия', 'Липидный профиль', 'Глюкоза крови'],
        'specific': {
            'Гериатр': ['Когнитивные тесты', 'Анализ на витамин D', 'Оценка функционального статуса']
        }
    },
    'Эстетические проблемы': {
        'common': ['Дерматоскопия', 'Фототипирование кожи', 'Анализ на гормоны'],
        'specific': {
            'Эстетический врач': ['Анализ состояния кожи', 'Тест на фотостарение', 'Оценка пропорций лица']
        }
    },
    'Нарушения питания': {
        'common': ['Биохимический анализ крови', 'Липидный профиль', 'Гормональный профиль'],
        'specific': {
            'Диетолог': ['Биоимпедансный анализ', 'Калориметрия', 'Анализ основного обмена']
        }
    }
}

organ_systems = {
'Сердечно-сосудистая система': {
'organs': ['сердце', 'кровеносные сосуды', 'артерии', 'вены', 'капилляры', 'аорта'],
'symptoms': [
    'боль в грудной клетке давящего характера',
    'ощущение перебоев в работе сердца',
    'учащенное сердцебиение в покое',
    'одышка при обычной физической нагрузке',
    'отеки на ногах к вечеру',
    'головокружение при смене положения тела',
    'повышение артериального давления',
    'снижение толерантности к физической нагрузке',
    'бледность кожных покровов',
    'похолодание конечностей'
        ]
    },
'Дыхательная система': {
'organs': ['легкие', 'бронхи', 'трахея', 'гортань', 'носоглотка', 'альвеолы'],
'symptoms': [
    'кашель с отделением мокроты',
    'сухой надсадный кашель',
    'одышка в покое',
    'боли в грудной клетке при дыхании',
    'хрипы в грудной клетке',
    'ночные приступы удушья',
    'кровохарканье',
    'повышение температуры тела с ознобом',
    'боль в горле',
    'заложенность носа'
        ]
    },
'Пищеварительная система': {
'organs': ['желудок', 'кишечник', 'печень', 'поджелудочная железа', 'желчный пузырь', 'пищевод'],
'symptoms': [
    'боли в животе спастического характера',
    'тошнота после приема пищи',
    'рвота съеденной пищей',
    'изжога после острой пищи',
    'вздутие живота',
    'нарушение стула (запоры/диарея)',
    'отрыжка воздухом',
    'снижение аппетита',
    'боль в правом подреберье',
    'желтушность кожных покровов'
        ]
    },
'Нервная система': {
'organs': ['головной мозг', 'спинной мозг', 'периферические нервы', 'мозжечок', 'ствол мозга'],
'symptoms': [
    'головная боль напряжения',
    'мигренозные боли с аурой',
    'головокружение системного характера',
    'онемение конечностей',
    'слабость в руках/ногах',
    'нарушение координации движений',
    'шум в ушах',
    'нарушение памяти',
    'тремор конечностей',
    'нарушение речи'
        ]
    },
'Опорно-двигательная система': {
'organs': ['кости', 'суставы', 'мышцы', 'связки', 'позвоночник', 'хрящи'],
'symptoms': [
    'боли в суставах при движении',
    'утренняя скованность в суставах',
    'боли в пояснице при нагрузке',
    'ограничение подвижности в суставах',
    'мышечные боли после физической нагрузки',
    'хруст в суставах при движении',
    'отечность суставов',
    'ночные боли в костях',
    'деформация суставов',
    'слабость в мышцах'
        ]
    },
'Мочеполовая система': {
'organs': ['почки', 'мочевой пузырь', 'мочеточники', 'уретра', 'надпочечники'],
'symptoms': [
    'боли в поясничной области',
    'нарушение мочеиспускания',
    'частые позывы к мочеиспусканию',
    'боли при мочеиспускании',
    'изменение цвета мочи',
    'отеки на лице по утрам',
    'боли внизу живота',
    'нарушение менструального цикла',
    'патологические выделения',
    'нарушение эрекции'
        ]
    },
'Эндокринная система': {
'organs': ['щитовидная железа', 'надпочечники', 'поджелудочная железа', 'гипофиз', 'гипоталамус'],
'symptoms': [
    'повышенная жажда',
    'учащенное мочеиспускание',
    'повышенный аппетит',
    'снижение массы тела',
    'повышенная потливость',
    'нарушение терморегуляции',
    'изменение настроения',
    'нарушение роста волос',
    'изменение тембра голоса',
    'нарушение менструального цикла'
        ]
    },
'Кожа и придатки': {
'organs': ['кожа', 'ногти', 'волосы', 'потовые железы', 'сальные железы'],
'symptoms': [
    'кожные высыпания',
    'зуд кожных покровов',
    'шелушение кожи',
    'изменение цвета кожных покровов',
    'появление новообразований',
    'выпадение волос',
    'ломкость ногтей',
    'повышенная потливость',
    'сухость кожи',
    'пигментация кожи'
        ]
    },
'Органы чувств': {
'organs': ['глаза', 'уши', 'нос', 'язык', 'вестибулярный аппарат'],
'symptoms': [
    'снижение остроты зрения',
    'боль в глазах',
    'покраснение глаз',
    'ощущение песка в глазах',
    'двоение в глазах',
    'слезотечение',
    'снижение слуха',
    'шум в ушах',
    'нарушение обоняния',
    'нарушение вкуса'
        ]
    },
'Иммунная система': {
'organs': ['лимфатические узлы', 'селезенка', 'костный мозг', 'тимус', 'миндалины'],
'symptoms': [
    'увеличение лимфатических узлов',
    'частые инфекционные заболевания',
    'аллергические реакции',
    'повышение температуры тела',
    'слабость и утомляемость',
    'ночная потливость',
    'снижение массы тела',
    'боли в костях',
    'склонность к кровотечениям',
    'длительное заживление ран'
        ]
    },
'Женская половая система': {
'organs': ['матка', 'яичники', 'влагалище', 'фаллопиевы трубы', 'молочные железы'],
'symptoms': [
    'нарушение менструального цикла',
    'боли внизу живота',
    'патологические выделения из влагалища',
    'болезненность молочных желез',
    'образование уплотнений в груди',
    'зуд в области половых органов',
    'боли при половом акте',
    'нарушение репродуктивной функции',
    'приливы жара',
    'сухость влагалища'
        ]
    },
'Мужская половая система': {
'organs': ['предстательная железа', 'яички', 'половой член', 'семенные пузырьки'],
'symptoms': [
    'нарушение мочеиспускания',
    'боли в промежности',
    'снижение либидо',
    'нарушение эрекции',
    'боли при эякуляции',
    'изменение качества спермы',
    'уплотнения в яичках',
    'боли в мошонке',
    'преждевременная эякуляция',
    'снижение фертильности'
        ]
    },
'Кровь и кроветворная система': {
'organs': ['кровь', 'костный мозг', 'селезенка', 'лимфатические узлы'],
'symptoms': [
    'бледность кожных покровов',
    'повышенная утомляемость',
    'одышка при нагрузке',
    'учащенное сердцебиение',
    'склонность к кровотечениям',
    'образование синяков',
    'увеличение лимфатических узлов',
    'ночная потливость',
    'повышение температуры тела',
    'потеря веса'
        ]
    },
'Лимфатическая система': {
'organs': ['лимфатические сосуды', 'лимфатические узлы', 'миндалины', 'аденоиды'],
'symptoms': [
    'увеличение лимфатических узлов',
    'отеки конечностей',
    'боли в области лимфоузлов',
    'повышение температуры тела',
    'слабость и недомогание',
    'ночная потливость',
    'потеря веса',
    'частые инфекции',
    'покраснение кожи над лимфоузлами',
    'ощущение тяжести в конечностях'
        ]
    },
'Психическая сфера': {
'organs': ['психика', 'эмоциональная сфера', 'когнитивные функции'],
'symptoms': [
    'снижение настроения',
    'повышенная тревожность',
    'нарушение сна',
    'апатия и безразличие',
    'раздражительность',
    'панические атаки',
    'навязчивые мысли',
    'снижение концентрации внимания',
    'нарушение памяти',
    'изменение поведения'
        ]
    },
'Стоматологическая система': {
'organs': ['зубы', 'десны', 'язык', 'слизистая полости рта', 'челюсти'],
'symptoms': [
    'зубная боль',
    'кровоточивость десен',
    'повышенная чувствительность зубов',
    'неприятный запах изо рта',
    'образование язвочек во рту',
    'подвижность зубов',
    'боль при жевании',
    'отечность десен',
    'изменение цвета зубов',
    'боль в височно-нижнечелюстном суставе'
        ]
    },
'Реабилитационная система': {
'organs': ['опорно-двигательный аппарат', 'нервная система', 'послеоперационные состояния'],
'symptoms': [
    'ограничение подвижности суставов',
    'мышечная слабость',
    'нарушение координации движений',
    'боли при движении',
    'снижение мышечной силы',
    'нарушение походки',
    'быстрая утомляемость',
    'нарушение баланса',
    'снижение выносливости',
    'послеоперационные боли'
        ]
    },
'Сомнологическая система': {
'organs': ['циркадные ритмы', 'структура сна', 'дыхание во сне'],
'symptoms': [
    'нарушение засыпания',
    'частые пробуждения ночью',
    'дневная сонливость',
    'храп во сне',
    'остановки дыхания во сне',
    'беспокойный сон',
    'кошмарные сновидения',
    'раннее пробуждение',
    'ощущение невыспанности',
    'снижение качества сна'
        ]
    },
'Профессиональные заболевания': {
'organs': ['легкие', 'кожа', 'опорно-двигательный аппарат', 'нервная система'],
'symptoms': [
    'хронический кашель',
    'одышка при нагрузке',
    'кожные высыпания',
    'боли в суставах',
    'мышечная слабость',
    'нарушение слуха',
    'головные боли',
    'повышенная утомляемость',
    'нарушение координации',
    'снижение концентрации'
        ]
    },
'Детские заболевания': {
'organs': ['растущий организм', 'иммунная система', 'нервная система'],
'symptoms': [
    'повышение температуры тела',
    'кашель и насморк',
    'сыпь на коже',
    'снижение аппетита',
    'нарушение сна',
    'повышенная возбудимость',
    'отставание в развитии',
    'частые простудные заболевания',
    'боли в животе',
    'нарушение стула'
        ]
    },
'Возрастные изменения': {
'organs': ['все системы организма', 'когнитивные функции', 'опорно-двигательный аппарат'],
'symptoms': [
    'снижение памяти',
    'ухудшение зрения',
    'нарушение слуха',
    'боли в суставах',
    'снижение мышечной силы',
    'нарушение равновесия',
    'повышенная утомляемость',
    'нарушение мочеиспускания',
    'снижение плотности костей',
    'ухудшение качества кожи'
        ]
    },
'Эстетические проблемы': {
'organs': ['кожа', 'волосы', 'ногти', 'подкожная клетчатка'],
'symptoms': [
    'морщины на коже',
    'пигментные пятна',
    'сосудистые звездочки',
    'целлюлит',
    'выпадение волос',
    'ломкость ногтей',
    'сухость кожи',
    'избыточный вес',
    'растяжки на коже',
    'возрастные изменения лица'
        ]
    },
'Нарушения питания': {
'organs': ['желудочно-кишечный тракт', 'обмен веществ', 'эндокринная система'],
'symptoms': [
    'избыточный вес',
    'недостаточный вес',
    'нарушение аппетита',
    'тяга к определенным продуктам',
    'нарушение пищевого поведения',
    'вздутие живота после еды',
    'изжога и отрыжка',
    'запоры или диарея',
    'отеки',
    'слабость и утомляемость'
        ]
    }
}

def decompose_bank_card(df: pd.DataFrame, card_column: str, element: str) -> pd.DataFrame:
    payment_systems = {
        '4': 'VISA',
        '5': 'MasterCard',
        '2': 'Mir',
    }
    banks = {
        '04': 'Sberbank',
        '16': 'Tinkoff',
        '41': 'VTB',
        '35': 'Alfa-Bank',
        '22': 'Gazprombank',
        '36': 'Raiffeisenbank',
        '45': 'Otkritie',
        '20': 'Promsvyazbank',
        '43': 'Rosbank',
    }
    df = df.copy()
    if element == "Платежная система":
        df[card_column] = df[card_column].astype(str)
        df['Платежная система'] = df[card_column].str[:1].apply(lambda x: payment_systems[str(x)])
        df = delete_columns(df, card_column)
    elif element == "Банк":
        df[card_column] = df[card_column].astype(str)
        df['Банк'] = df[card_column].str[1:3].apply(lambda x: banks[str(x)])
        df = delete_columns(df, card_column)
    return df


def generalize_doctors_strong(df: pd.DataFrame, doctor_column: str) -> pd.DataFrame:
    """
    Сильное обобщение врачей в крупные категории.
    """
    doctor_to_group = {
        'Дерматолог': 'Другое',
        'Кардиолог': 'Системные специалисты',
        'Невролог': 'Системные специалисты',
        'Гематолог': 'Другое',
        'Диетолог': 'Другое',
        'Гинеколог': 'Реабилитация и общие',
        'Реабилитолог': 'Реабилитация и общие',
        'Ортопед': 'Реабилитация и общие',
        'Гастроэнтеролог': 'Системные специалисты',
        'Отоларинголог': 'Системные специалисты',
        'Андролог': 'Реабилитация и общие',
        'Пульмонолог': 'Системные специалисты',
        'Эндокринолог': 'Системные специалисты',
        'Уролог': 'Системные специалисты',
        'Стоматолог': 'Системные специалисты',
        'Терапевт': 'Реабилитация и общие',
        'Аллерголог': 'Другое',
        'Педиатр': 'Другое',
        'Психотерапевт': 'Реабилитация и общие',
        'Иммунолог': 'Другое',
        'Нефролог': 'Другое'
    }


    df = df.copy()
    df[doctor_column] = df[doctor_column].map(doctor_to_group).fillna('Не определено')
    df['Симптомы'] = df['Врач']
    df['Анализы'] = df['Врач']
    df['Медицинская информация'] = df['Врач']
    delete_columns(df, 'Врач')
    return df


def categorize_costs_quantile(df, column_name, num_bins):
    """
    Разбивает столбец со стоимостью на диапазоны с примерно равным количеством записей,
    заменяет старый столбец на новый с подписями диапазонов.
    
    :param df: pandas DataFrame
    :param column_name: имя столбца с ценами
    :param num_bins: количество диапазонов
    :return: DataFrame с обновленным столбцом
    """
    bins = pd.qcut(df[column_name], q=num_bins)
    labels = [f"{int(interval.left)}-{int(interval.right)}" for interval in bins.cat.categories]
    df[column_name] = pd.qcut(df[column_name], q=num_bins, labels=labels)
    
    return df


def combine_fio_to_uid(df: pd.DataFrame, surname_col: str, name_col: str, patronymic_col: str, new_col: str = "UID") -> pd.DataFrame:
    """
    Объединяет три столбца ФИО в один уникальный идентификатор с помощью хеширования.
    
    :param df: DataFrame
    :param surname_col: имя столбца с фамилией
    :param name_col: имя столбца с именем
    :param patronymic_col: имя столбца с отчеством
    :param new_col: имя нового столбца с UID
    :return: DataFrame с новым столбцом и удалёнными исходными ФИО
    """
    
    def hash_fio(row):
        fio_str = f"{row[surname_col]} {row[name_col]} {row[patronymic_col]}"
        return hashlib.md5(fio_str.encode('utf-8')).hexdigest()
    
    df[new_col] = df.apply(hash_fio, axis=1)
    
    df = df.drop(columns=[surname_col, name_col, patronymic_col])
    
    return df


def generalize_snils(df: pd.DataFrame, snils_column: str) -> pd.DataFrame:
    df = df.copy()
    df[snils_column] = df[snils_column].apply(lambda x: 'Гражданин РФ' if x not in ['Гражданин РБ', 'Гражданин РК'] else x)
    return df


def mask_passport_data(df: pd.DataFrame, passport_column: str, length: int) -> pd.DataFrame:
    df = df.copy()
    df[passport_column] = df[passport_column].apply(lambda x: x[:length] + '***' if len(x) > length else x)
    return df


def decompose_dates(df: pd.DataFrame, date_column: str, element: str) -> pd.DataFrame:
    # example: '2020-02-09T12:30+03:00' -> '2020', '2020-02', '2020-02-09'
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    if element == "Год":
        df[date_column] = df[date_column].dt.to_period("Y")
    elif element == "Квартал":
        df[date_column] = df[date_column].dt.to_period("Q")
    elif element == "Месяц":
        df[date_column] = df[date_column].dt.to_period("M")
    elif element == "День":
        df[date_column] = df[date_column].dt.to_period("D")
    else:
        raise ValueError(f"Неизвестный элемент: {element}")
    df["Дата готовности анализов"] = df[date_column]
    return df

def save_current_state(data: pd.DataFrame, file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        data.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass

            adjusted_width = (max_length + 2) * 1.1
            worksheet.column_dimensions[column_letter].width = adjusted_width

def calculate_k_anonymity_with_stats(df: pd.DataFrame, quasi_identifiers: list[str]) -> dict:
    missing = [col for col in quasi_identifiers if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}") 
    group_sizes = df.groupby(quasi_identifiers, observed=True).size() 
    k = int(group_sizes.min())
    frequency_distribution = group_sizes.value_counts().sort_index()
    result = {
        "k_anonymity": k,
        "num_groups": len(group_sizes),
        "frequency_distribution": frequency_distribution.to_dict()
    }
    return result

def calculate_k_anonymity_from_df(df: pd.DataFrame, quasi_identifiers: list[str]) -> int:
    """
    Рассчитывает k-анонимность на основе уже загруженного DataFrame.
    Безопасно работает с категориальными столбцами и учитывает только реально встречающиеся группы.

    :param df: pandas DataFrame
    :param quasi_identifiers: список квази-идентификаторов
    :return: минимальный размер группы (k-анонимность)
    """
    missing = [col for col in quasi_identifiers if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")

    if df.empty:
        return 0

    for col in quasi_identifiers:
        if pd.api.types.is_categorical_dtype(df[col]):
            df[col] = df[col].astype(str)

    group_sizes = df.groupby(quasi_identifiers, observed=True).size()

    if group_sizes.empty:
        return 0

    k = group_sizes.min()
    return int(k)

def calculate_k_anonymity_from_df_debug(df: pd.DataFrame, quasi_identifiers: list[str]) -> int:
    """
    Рассчитывает k-анонимность с выводом диагностики.
    """
    missing = [col for col in quasi_identifiers if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")
    
    if df.empty:
        print("DataFrame пустой")
        return 0
    
    print("Первые 5 строк DataFrame:")
    print(df.head())
    
    group_sizes = df.groupby(quasi_identifiers, observed=True).size()
    
    print("\nРазмеры групп по квази-идентификаторам:")
    print(group_sizes)
    
    if group_sizes.empty:
        print("После группировки нет групп!")
        return 0
    
    k = group_sizes.min()
    
    print(f"\nМинимальный размер группы (k-анонимность): {k}")
    
    return int(k)


def worst_k_anonymity_groups(df: pd.DataFrame, quasi_identifiers: list[str], n: int = 5) -> pd.DataFrame:
    """
    Возвращает n групп с минимальным размером (наименее защищенные группы) для оценки k-анонимности.
    
    :param df: pandas DataFrame
    :param quasi_identifiers: список квази-идентификаторов
    :param n: количество худших групп для отображения
    :return: DataFrame с комбинациями квази-идентификаторов и размером группы
    """
    missing = [col for col in quasi_identifiers if col not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")

    if df.empty:
        return pd.DataFrame(columns=quasi_identifiers + ["group_size"])

    for col in quasi_identifiers:
        if pd.api.types.is_categorical_dtype(df[col]):
            df[col] = df[col].astype(str)

    group_sizes = df.groupby(quasi_identifiers, observed=True).size().reset_index(name="group_size")

    group_sizes_sorted = group_sizes.sort_values(by="group_size", ascending=True)

    return group_sizes_sorted.head(n)

def copy_and_save_current_state(data: pd.DataFrame) -> pd.DataFrame:
    copy = data.copy()
    save_current_state(copy, "files/dataset_5k_copy.xlsx")
    return copy


def suppress_worst_k_groups_by_rows(
    df: pd.DataFrame,
    quasi_identifiers: list[str],
    rows_to_remove: int,
    allow_overshoot: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """
    Подавляет (удаляет) записи, выбирая группы с худшим k (минимальным размером),
    пока сумма удалённых строк не достигнет rows_to_remove.
    
    Параметры:
      - rows_to_remove: целевое число строк для удаления
      - allow_overshoot: если True — разрешить перевысить rows_to_remove на размер последней выбранной группы

    Возвращает:
      (df_filtered, report)
      report = {
        'before_k': int,          # k до подавления
        'after_k': int,           # k после подавления
        'groups_removed': int,    # сколько групп удалено
        'rows_removed': int,      # сколько строк удалено
        'removed_frac': float,    # доля удалённых строк
        'removed_k_hist': pd.Series,  # распределение размеров удалённых групп (k -> кол-во групп)
      }
    """
    if rows_to_remove <= 0 or df.empty:
        # Ничего не удаляем
        k_before = int(df.groupby(quasi_identifiers, observed=True).size().min()) if len(df) else 0
        return df.copy(), {
            'before_k': k_before, 'after_k': k_before, 'groups_removed': 0,
            'rows_removed': 0, 'removed_frac': 0.0, 'removed_k_hist': pd.Series(dtype=int)
        }

    missing = [c for c in quasi_identifiers if c not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")

    # Устойчивая строковая ключ-склейка (без проблем с Period/категориями)
    sep = "\u241F"
    keys = df[quasi_identifiers].astype(str).agg(sep.join, axis=1)

    group_sizes = keys.value_counts()  # index=key, value=размер группы (k)
    if group_sizes.empty:
        return df.copy(), {
            'before_k': 0, 'after_k': 0, 'groups_removed': 0,
            'rows_removed': 0, 'removed_frac': 0.0, 'removed_k_hist': pd.Series(dtype=int)
        }

    before_k = int(group_sizes.min())

    # Идём от меньших k к большим
    gs_sorted = group_sizes.sort_values(ascending=True)

    picked = []
    removed_rows = 0

    for key, k_val in gs_sorted.items():
        k_val = int(k_val)
        # Если добавление этой группы превысит лимит — решаем по allow_overshoot
        if removed_rows + k_val > rows_to_remove and not allow_overshoot:
            break
        picked.append((key, k_val))
        removed_rows += k_val
        if removed_rows >= rows_to_remove:
            break

    if not picked:
        # Ничего не удалили (слишком маленький лимит без overshoot)
        return df.copy(), {
            'before_k': before_k, 'after_k': before_k, 'groups_removed': 0,
            'rows_removed': 0, 'removed_frac': 0.0, 'removed_k_hist': pd.Series(dtype=int)
        }

    picked_keys = {k for k, _ in picked}
    mask_keep = ~keys.isin(picked_keys)
    df_filtered = df.loc[mask_keep].copy()

    if not df_filtered.empty:
        new_group_sizes = df_filtered.groupby(quasi_identifiers, observed=True).size()
        after_k = int(new_group_sizes.min())
    else:
        after_k = 0

    removed_k_hist = pd.Series([k for _, k in picked], dtype=int).value_counts().sort_index()
    report = {
        'before_k': before_k,
        'after_k': after_k,
        'groups_removed': len(picked),
        'rows_removed': removed_rows,
        'removed_frac': removed_rows / max(len(df), 1),
        'removed_k_hist': removed_k_hist
    }
    return df_filtered, report

def delete_columns(data: pd.DataFrame, columns: list) -> pd.DataFrame:
    return data.drop(columns=columns, axis=1)


from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # рендер без окна
import matplotlib.pyplot as plt

def _sanitize_filename(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in str(name)).strip().replace(" ", "_")

def visualize_distributions(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    output_dir: str = "files/plots",
    max_categories: int = 20
) -> list[str]:
    """
    Сохраняет PNG-графики распределений по указанным колонкам.
    - Числовые: гистограмма
    - Даты/Period: столбчатая диаграмма по периодам
    - Категориальные/строки: топ-N категорий (+ 'Другое')
    Возвращает список путей к созданным файлам.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    cols = columns or list(df.columns)
    saved: list[str] = []

    for col in cols:
        if col not in df.columns:
            continue
        s = df[col].dropna()

        # Period → str, чтобы корректно строить
        if pd.api.types.is_period_dtype(s):
            s = s.astype(str)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.set_title(f"Распределение: {col}")

        if pd.api.types.is_numeric_dtype(s):
            ax.hist(s, bins=30, color="#4C78A8", edgecolor="white")
            ax.set_ylabel("Количество")
            ax.set_xlabel(col)
        elif pd.api.types.is_datetime64_any_dtype(s):
            counts = s.dt.to_period("M").astype(str).value_counts().sort_index()
            counts.plot(kind="bar", color="#72B7B2", ax=ax)
            ax.set_ylabel("Количество")
            ax.set_xlabel("Период (месяц)")
        else:
            vc = s.astype(str).value_counts()
            if len(vc) > max_categories:
                top = vc.head(max_categories)
                other = vc.iloc[max_categories:].sum()
                if other > 0:
                    top.loc["Другое"] = other
                vc = top
            vc = vc.sort_values(ascending=False)
            vc.plot(kind="bar", color="#F58518", ax=ax)
            ax.set_ylabel("Количество")
            ax.set_xlabel("Категории")
            total = float(s.shape[0])
            for p in ax.patches:
                h = p.get_height()
                if h > 0:
                    ax.annotate(f"{h/total:.1%}", (p.get_x() + p.get_width()/2, h),
                                ha="center", va="bottom", fontsize=8)

        plt.tight_layout()
        out = str(Path(output_dir) / f"dist_{_sanitize_filename(col)}.png")
        fig.savefig(out, dpi=150)
        plt.close(fig)
        saved.append(out)

    return saved


from matplotlib.ticker import MaxNLocator

def visualize_k_group_sizes(
    df: pd.DataFrame,
    quasi_identifiers: list[str],
    output_path: str = "files/plots/k_distribution.png",
    top_n: int = 25
) -> str:
    """
    Рисует читаемый график распределения размеров групп (k).
    - Горизонтальные столбцы (не накладываются подписи)
    - Показывает до top_n разных k; остальные агрегируются в «≥K»
    - Справа от каждого бара — доля строк датасета, попавших в группы данного k
    """
    Path(Path(output_path).parent).mkdir(parents=True, exist_ok=True)

    group_sizes = df.groupby(quasi_identifiers, observed=True).size()
    fig, ax = plt.subplots(figsize=(9, 4.5))

    if group_sizes.empty:
        ax.text(0.5, 0.5, "Нет данных для построения", ha="center", va="center")
        plt.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return output_path

    # index=k, value=кол-во групп размером k
    vc = group_sizes.value_counts().sort_index()
    dist = pd.DataFrame({"k": vc.index.astype(int), "groups": vc.values})
    dist["records"] = dist["k"] * dist["groups"]
    total_rows = max(len(df), 1)
    dist["share"] = dist["records"] / total_rows

    # Оставляем первые (наименьшие) k, остальное агрегируем
    dist = dist.sort_values("k")
    if len(dist) > top_n:
        head = dist.head(top_n - 1).copy()
        tail = dist.iloc[top_n - 1:]
        agg = pd.DataFrame({
            "k": [None],
            "groups": [int(tail["groups"].sum())],
            "records": [int(tail["records"].sum())],
            "share": [float(tail["share"].sum())],
        })
        head["k_label"] = head["k"].astype(str)
        agg["k_label"] = f"≥{int(tail['k'].min())}"
        plot_df = pd.concat([head, agg], ignore_index=True)
    else:
        plot_df = dist.copy()
        plot_df["k_label"] = plot_df["k"].astype(str)

    # Горизонтальная диаграмма
    fig_h = max(4.5, 0.35 * len(plot_df) + 1.0)  # динамическая высота под число категорий
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, fig_h))
    bars = ax.barh(plot_df["k_label"], plot_df["groups"], color="#E45756")

    ax.set_title("Распределение размеров групп (k)")
    ax.set_xlabel("Количество групп")
    ax.set_ylabel("Размер группы k")
    ax.invert_yaxis()  # маленькие k сверху
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", linestyle=":", alpha=0.4)

    # Подписи долей справа от столбцов
    max_groups = plot_df["groups"].max() if len(plot_df) else 1
    x_offset = max_groups * 0.02 + 0.5
    for rect, share in zip(bars, plot_df["share"].tolist()):
        y = rect.get_y() + rect.get_height() / 2
        x = rect.get_width() + x_offset
        ax.text(x, y, f"{share:.1%}", va="center", ha="left", fontsize=9)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path