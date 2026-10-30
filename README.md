# Arknights RU — независимый русификатор (рабочая база v0.58)

Любительский перевод **оригинальной Arknights, Yostar Global PC**. Это **не Endfield**.

## Что уже есть

- **Основной сюжет:** главы 0–2 — 2 377 реплик (44 файла); глава 3 — 642 реплики (9 файлов: 3-1–3-4 до/после боя и 3-5 до боя). Всего 3 019 реплик в 53 файлах, первые черновики.
- **Darknights Memoir:** 13 из 13 сценариев, 2 062 строки в завершённых первых черновиках. DM-1–DM-6 и st01 переведены; требуется литературная вычитка и проверка в клиенте. Продолжаем по хронологии Терры.
- **Интерфейс:** 2 544 переведённых ключа.
- Инструменты для сохранения команд и переменных, словари, отчёты и автоматические тесты.

## Где искать

| Путь | Содержание |
| --- | --- |
| `story/` | перевод основного сюжета |
| `events/` | перевод ивентов (Darknights Memoir) |
| `translations/` | UI и предметные черновики |
| `scripts/` | генераторы предпросмотра и тесты |
| `chronology/` | порядок перевода по хронологии |
| `docs/`, `reports/` | заметки, проверки, журнал изменений |
| `backlog/`, `drafts/`, `data/` | очереди непереведённого текста, промежуточные таблицы |

DM-3 до боя: завершённый первый черновик в `events/darknights_memoir_dm3_before_ru_v037.json`, аудит CN/EN — `reports/DM3_SOURCE_AUDIT_v037.json`. Для локального предпросмотра пяти готовых сцен доступен `BUILD_DARKNIGHTS_DM1_DM2_DM3_BEFORE_PREVIEW_v037.bat` (без установки в игру).

Архив предыдущих черновиков: `events/darknights_memoir_dm3_before_partial_ru_v036.json`, `events/darknights_memoir_dm3_before_partial_ru_v035.json`, `events/darknights_memoir_dm3_before_partial_ru_v034.json`, `events/darknights_memoir_dm3_before_partial_ru_v032.json` и `events/darknights_memoir_dm3_before_partial_ru_v033.json`. Они не являются актуальными файлами для сборки.

## Проверка

Установить Python 3 и выполнить из корня репозитория:

```bash
python -m unittest discover -s scripts -p 'test*.py' -v
```

Также есть проверка через GitHub Actions — `Translation workspace tests`.

## Предпросмотр

В Windows для Darknights Memoir доступен `BUILD_DARKNIGHTS_DM1_TO_DM5_PREVIEW_v044.bat`. Архивная версия `BUILD_DARKNIGHTS_DM1_DM2_DM3_BEFORE_PREVIEW_v037.bat` сохранена для сравнения. Для глав 0–2 — `BUILD_CHAPTERS_0_TO_2_RU_v025.bat`.

Скрипты скачивают игровые сценарии CN/EN отдельно и проверяют версии оригиналов. Перевод **не устанавливается в игру автоматически**. В рабочей базе есть исторические и потенциально небезопасные варианты XUnity: не используйте файлы с меткой `UNSAFE` как готовый патч.

**Статус:** литературные черновики, технические тесты на подготовленных данных пройдены; реальная работа перевода в игровом клиенте ещё не подтверждена.

Подробности переноса — [`MIGRATION.md`](MIGRATION.md).

DM-3 после боя завершена в первом черновике: `events/darknights_memoir_dm3_after_ru_v040.json` (160 именных + 11 безымянных реплик); аудит — `reports/DM3_AFTER_SOURCE_AUDIT_v040.json`. Предыдущие частичные версии `events/darknights_memoir_dm3_after_partial_ru_v038.json` и `events/darknights_memoir_dm3_after_partial_ru_v039.json` сохраняются как архивы. Полный локальный предпросмотр шести сцен: `BUILD_DARKNIGHTS_DM1_DM2_DM3_PREVIEW_v040.bat` (не установщик игры).

DM-4 до боя — первый полный русский черновик: `events/darknights_memoir_dm4_before_ru_v041.json` (154 именных + 16 безымянных строк). Объединённая выборка семи сцен: `events/darknights_memoir_dm1_dm2_dm3_dm4_before_ru_v041.json`. Аудит: `reports/DM4_BEFORE_SOURCE_AUDIT_v041.json`. Предпросмотр: `BUILD_DARKNIGHTS_DM1_TO_DM4_BEFORE_PREVIEW_v041.bat`. Перевод ещё не проверен в игре.

DM-4 после боя — полный первый черновик: `events/darknights_memoir_dm4_after_ru_v042.json` (76 именных + 14 безымянных реплик). Актуальная объединённая выборка восьми сцен: `events/darknights_memoir_dm1_dm2_dm3_dm4_ru_v042.json`. Сверка источников: `reports/DM4_AFTER_SOURCE_AUDIT_v042.json`. Предпросмотр: `BUILD_DARKNIGHTS_DM1_TO_DM4_PREVIEW_v042.bat`. Следующая сцена DM-5 до боя. Не проверено в игре.

DM-5 до боя — полный первый черновик: `events/darknights_memoir_dm5_before_ru_v043.json` (102 именные реплики, безымянных нет). Объединённая выборка девяти сцен: `events/darknights_memoir_dm1_dm2_dm3_dm4_dm5_before_ru_v043.json`. Аудит: `reports/DM5_BEFORE_SOURCE_AUDIT_v043.json`. Предпросмотр: `BUILD_DARKNIGHTS_DM1_TO_DM5_BEFORE_PREVIEW_v043.bat`. Следующая сцена DM-5 после боя. Не проверено в игре.

DM-5 после боя — полный первый русский черновик: `events/darknights_memoir_dm5_after_ru_v044.json` (74 именных + 10 безымянных). Объединённая выборка десяти сцен: `events/darknights_memoir_dm1_dm2_dm3_dm4_dm5_ru_v044.json`. Аудит: `reports/DM5_AFTER_SOURCE_AUDIT_v044.json`. Предпросмотр: `BUILD_DARKNIGHTS_DM1_TO_DM5_PREVIEW_v044.bat`. Следующая: DM-6 до боя. Не проверено в игре.

DM-6 до боя — полный первый русский черновик: `events/darknights_memoir_dm6_before_ru_v045.json` (219 именных + 6 безымянных). Объединённая выборка 11 сцен: `events/darknights_memoir_dm1_to_dm6_before_ru_v045.json`. Аудит: `reports/DM6_BEFORE_SOURCE_AUDIT_v045.json`. Предпросмотр: `BUILD_DARKNIGHTS_DM1_TO_DM6_BEFORE_PREVIEW_v045.bat`. Следующая: DM-6 после боя. Не проверено в игре.

DM-6 после боя — полный первый черновик: `events/darknights_memoir_dm6_after_ru_v046.json` (132 именные + 5 безымянных). Актуальная объединённая выборка двенадцати сцен: `events/darknights_memoir_dm1_to_dm6_ru_v046.json`. Аудит `reports/DM6_AFTER_SOURCE_AUDIT_v046.json`, безопасный предпросмотр `BUILD_DARKNIGHTS_DM1_TO_DM6_PREVIEW_v046.bat`. Осталась сцена st01. Игровой клиент не проверен.

Darknights Memoir завершена в первом черновике (13/13): `events/darknights_memoir_all_ru_v047.json` (2062 русские строки). Дополнительная история: `events/darknights_memoir_st01_ru_v047.json` (239 именных + 5 безымянных). Аудит: `reports/DM_ST01_SOURCE_AUDIT_v047.json`. Локальный предпросмотр: `BUILD_DARKNIGHTS_ALL_PREVIEW_v047.bat`. **Не проверено в игре.** Тестовый пакет интерфейса требует отдельного подтверждения механизма загрузки текстов клиентом.

Babel / «Вавилон» начат в v0.48: код игрового события `act33side`, первым по авторскому порядку идёт BB-ST-1 (`level_act33side_st01.txt`). В `events/babel_st01_opening_partial_ru_v048.json` сохранён **частичный** перевод исходных строк 1–114: 21 именная реплика, 15 строк повествования и 14 строк `Sticker(text)`, всего 50 текстовых элементов из 141. Сцена **не завершена**, следующий фрагмент начинается с исходной строки 115. Источники и хеши — `reports/BABEL_ST01_SOURCE_AUDIT_v048.json`; индекс — `events/BABEL_INDEX_v048.tsv`. Существующий предпросмотр Darknights не умеет применять Babel; клиент не проверен.

## BepInEx / XUnity: экспериментальное дополнение v0.48

Для готовой папки оригинальной Yostar Global PC (`Arknights_EN/BepInEx/Translation/ru/Text`) предусмотрен отдельный ZIP `ArknightsRU_BepInEx_DropIn_v048.zip`. При распаковке в корень игры он **добавляет только** `ArknightsRU_ExpandedUI_v048.txt` и не перезаписывает существующие семь пользовательских TXT-файлов. 489 уже используемых английских ключей исключаются из добавочного файла; дополнительные переводы берутся из `translations/xunity_LITERAL_SAFE_PREVIEW.txt`. Проверка в клиенте ещё не проводилась; это не внедрение 2544 keyed UI-ключей и не игровой патч сюжета. Подробнее: `release/README_BEPINEX_RU_v048.md`.

Babel BB-ST-1 продолжен в v0.49: `events/babel_st01_opening_partial_ru_v049.json` — исходные строки 1–194, 34 именные + 29 безымянных + 14 Sticker(text), всего 77/141 текстовых элементов. В этом изменении добавлены 13 именных и 14 безымянных строк (115–194). Следующая строка 195; **0/23 завершённых сцен Babel**. Аудит: `reports/BABEL_ST01_SOURCE_AUDIT_v049.json`; индекс: `events/BABEL_INDEX_v049.tsv`; хронология: `chronology/CHRONOLOGY_MANIFEST_v049.json`. Не проверено в игре.

## Единый BepInEx-пакет UI v0.52 (экспериментальный)

Для оригинальной Arknights Yostar Global PC подготовлена объединённая сборка `ArknightsRU_BepInEx_Unified_v052.zip`. Она содержит 8 распределённых по категориям TXT, проверку повторов, отчёт о покрытии интерфейса на скриншотах и безопасный скрипт переноса старых v0.48–v0.51 в резервную папку. **Исходные семь файлов пользователя не заменяются.** Инструкция `release/README_UNIFIED_BEPINEX_v052.md`. Точный перехват некоторых кнопок и графических надписей ещё не подтверждён; 2544 keyed UI-значения и полный черновик DM не являются готовыми XUnity-подстановками.

## Продолжение сюжета: Babel BB-ST-1 (v0.50)

`events/babel_st01_ru_v050.json` содержит полный первый черновик BB-ST-1: 89 именных, 38 строк повествования, 14 Sticker(text) и 17 кинематографических Subtitle(text) = 158 элементов. Аудит `reports/BABEL_ST01_SOURCE_AUDIT_v050.json`, индекс `events/BABEL_INDEX_v050.tsv`, хронология `chronology/CHRONOLOGY_MANIFEST_v050.json`. Следующая сцена BB-1 до боя `activities/act33side/level_act33side_01_beg.txt`. Не установленный патч и не проверенный в игре перевод.

## Основной сюжет: глава 3, этап 3-1 (v0.51)

Согласно выбранному порядку первого чтения, теперь переводим основной сюжет последовательно. Первый этап главы 3 (`obt/main/level_main_03-01_beg.txt`, `obt/main/level_main_03-01_end.txt`) переведён полностью, **125/125** именных реплик. Отдельный перевод: `story/story_chapter_3_stage_3-1_ru_v051.json`. Общая безопасная выборка глав 0–2 и 3-1: `story/story_main_selection_ru_v051.json` (46 файлов, 2 502 реплики). Сверка: `reports/CHAPTER_3_STAGE_3-1_AUDIT_v051.json`, индекс: `story/CHAPTER_3_INDEX_v051.tsv`, хронология: `chronology/CHRONOLOGY_MANIFEST_v051.json`. Следующий этап — 3-2 до боя. Это литературный первый черновик, **не** установленный патч Global PC. Перевод Babel не утрачен, но поставлен на паузу согласно текущему порядку пользователя.

### Глава 3, начало 3-2 (v0.52)

`story/story_chapter_3_stage_3-2_before_ru_v052.json` — все 37 именных реплик **до боя**. Объединённая выборка `story/story_main_selection_ru_v052.json` (47 файлов, 2 539 реплик). Осталась часть **после боя** `obt/main/level_main_03-02_end.txt` (120 именных реплик в источнике). Статистика: `reports/QA_MAIN_STORY_v052.json`, индекс: `story/CHAPTER_3_INDEX_v052.tsv`. Не проверено в игровом клиенте.

### Глава 3, уровень 3-2 завершён в черновике (v0.53)

Добавлены **120 реплик после боя**: `story/story_chapter_3_stage_3-2_after_ru_v053.json`. Вместе с ранее готовой частью до боя это 157 реплик уровня 3-2. Общая выборка `story/story_main_selection_ru_v053.json` — 48 файлов, 2 659 реплик. Отчёт по CN/EN: `reports/CHAPTER_3_STAGE_3-2_AFTER_SOURCE_AUDIT_v053.json`. Проверка: `reports/QA_MAIN_STORY_v053.json`. Следующий этап — 3-3 до боя. Пока не установленный русификатор клиента.

### Глава 3, уровень 3-3 до боя (v0.54)

Переведены все 51 реплика в `story/story_chapter_3_stage_3-3_before_ru_v054.json`. Общая выборка: `story/story_main_selection_ru_v054.json` (49 файлов, 2710 реплик). Аудит: `reports/QA_MAIN_STORY_v054.json`. После боя (`obt/main/level_main_03-03_end.txt`) пока не переведено 92 реплики по источникам. Рабочие JSON не являются готовым модом или установленным русификатором клиента.

### Глава 3, уровень 3-3 завершён в первом черновике (v0.55)

После боя переведены **92 именные реплики** `story/story_chapter_3_stage_3-3_after_ru_v055.json`; до боя было 51, итого **143 реплики** уровня 3-3. Сводная выборка `story/story_main_selection_ru_v055.json`: 50 файлов, 2802 именные реплики; все прежние 49 файлов сохранены без изменения. Сверка китайского и английского: `reports/CHAPTER_3_STAGE_3-3_AFTER_SOURCE_AUDIT_v055.json`; QA: `reports/QA_MAIN_STORY_v055.json`. Следующий файл — `obt/main/level_main_03-04_beg.txt`. Перевод не установлен и не проверен в клиенте Yostar Global PC.

### Глава 3, уровень 3-4 до боя (v0.56)

Первый полный черновик **сцены до боя**: `story/story_chapter_3_stage_3-4_before_ru_v056.json` (79 именных реплик). Объединённая выборка `story/story_main_selection_ru_v056.json` — 51 файл и 2 881 реплика. Сверка CN/EN и замечания: `reports/CHAPTER_3_STAGE_3-4_BEFORE_SOURCE_AUDIT_v056.json`; QA: `reports/QA_MAIN_STORY_v056.json`. Следующая сцена: `obt/main/level_main_03-04_end.txt`. Часть после боя ещё не переведена; это не проверенный игровой патч.

### Глава 3, уровень 3-4 завершён в первом черновике (v0.57)

После боя переведены **55 именных реплик** `story/story_chapter_3_stage_3-4_after_ru_v057.json`; вместе с 79 репликами до боя — **134 реплики** уровня 3-4. Объединённая выборка `story/story_main_selection_ru_v057.json`: 52 файла, 2 936 реплик; предыдущие 51 файла сохранены без изменений. Аудит CN/EN: `reports/CHAPTER_3_STAGE_3-4_AFTER_SOURCE_AUDIT_v057.json`; QA: `reports/QA_MAIN_STORY_v057.json`; следующий файл `obt/main/level_main_03-05_beg.txt`. Это литературный черновик, не проверенный в игровом клиенте.

## Основной сюжет: 3-5 до боя (v0.58)

Полный первый черновик `story/story_chapter_3_stage_3-5_before_ru_v058.json`: 83 именные реплики и 5 вариантов ответа в 3 ветвлениях. Объединённая выборка `story/story_main_selection_ru_v058.json` содержит 53 файла и 3019 реплик. CN/EN Git blob SHA и разночтения зафиксированы в `reports/CHAPTER_3_STAGE_3-5_BEFORE_SOURCE_AUDIT_v058.json`. Следующая сцена — `obt/main/level_main_03-05_end.txt`. Предпросмотр не является игровым патчем; реальная работа в клиенте не проверена.

## Тест перевода сюжетных реплик глав 0–2 через XUnity (v0.55)

Для проверки прямо в оригинальном PC-клиенте подготовлен экспериментальный `ArknightsRU_Story_Chapters_0-2_XUnity_TEST_v055.zip` с отдельными TXT по главам. Из 2377 черновых русских реплик 1732 уникальных английских ключа безопасно сопоставлены с русским текстом (1738 потенциальных попаданий); остальные 639 исключены из-за коротких общих формулировок, конфликтов и динамических вставок. Оригинальные семь пользовательских TXT, UI-пакет v0.52 и игра остаются нетронутыми. Установка: `release/README_STORY_CHAPTERS_0_2_XUNITY_v055.md`; аудит: `reports/QA_STORY_XUNITY_v055.json`. **Загрузка словаря в XUnity подтверждена сборкой, но перехват и отображение сюжетных диалогов в клиенте пока не проверены.**
