# Arknights RU — независимый русификатор (рабочая база v0.47)

Любительский перевод **оригинальной Arknights, Yostar Global PC**. Это **не Endfield**.

## Что уже есть

- **Главы 0–2:** 2 377 сюжетных реплик, первый русский черновик (44 файла).
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
