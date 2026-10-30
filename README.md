# Arknights RU — независимый русификатор (рабочая база v0.40)

Любительский перевод **оригинальной Arknights, Yostar Global PC**. Это **не Endfield**.

## Что уже есть

- **Главы 0–2:** 2 377 сюжетных реплик, первый русский черновик (44 файла).
- **Darknights Memoir:** 6 из 13 основных сцен, 1 010 строк в завершённых первых черновиках. DM-3 до и после боя завершены; далее DM-4 до боя. Продолжаем по хронологии Терры.
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

В Windows для Darknights Memoir доступен `BUILD_DARKNIGHTS_DM1_DM2_DM3_BEFORE_PREVIEW_v037.bat`. Для глав 0–2 — `BUILD_CHAPTERS_0_TO_2_RU_v025.bat`.

Скрипты скачивают игровые сценарии CN/EN отдельно и проверяют версии оригиналов. Перевод **не устанавливается в игру автоматически**. В рабочей базе есть исторические и потенциально небезопасные варианты XUnity: не используйте файлы с меткой `UNSAFE` как готовый патч.

**Статус:** литературные черновики, технические тесты на подготовленных данных пройдены; реальная работа перевода в игровом клиенте ещё не подтверждена.

Подробности переноса — [`MIGRATION.md`](MIGRATION.md).

DM-3 после боя завершена в первом черновике: `events/darknights_memoir_dm3_after_ru_v040.json` (160 именных + 11 безымянных реплик); аудит — `reports/DM3_AFTER_SOURCE_AUDIT_v040.json`. Предыдущие частичные версии `events/darknights_memoir_dm3_after_partial_ru_v038.json` и `events/darknights_memoir_dm3_after_partial_ru_v039.json` сохраняются как архивы. Полный локальный предпросмотр шести сцен: `BUILD_DARKNIGHTS_DM1_DM2_DM3_PREVIEW_v040.bat` (не установщик игры).
