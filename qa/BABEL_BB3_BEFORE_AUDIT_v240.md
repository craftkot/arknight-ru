# Babel BB-3 before battle — CN coverage audit (v2.40)

Date: 2026-11-07. Scope: `activities/act33side/level_act33side_03_beg.txt`.

- Source CN: `Kengxxiao/ArknightsGameData`, Git blob `3551ec9987dc3d93a0a4dc789f26a80e3a8ce240`.
- Source EN: `Kengxxiao/ArknightsGameData_YoStar`, Git blob `7e041d79ba2e7bee22e6cf8b389f91e74a7fcc45`.
- Both hashes match those already recorded in the v2.29 partial draft; source versions have not changed.
- CN text-bearing positions: **211** = 148 ordinary named dialogues + 2 named multiline dialogues + 39 unnamed narration lines + 20 subtitles + 2 stickers with text. Sticker-clear commands with no text are excluded.
- Every position matches the v2.29 Russian overlay in ordinal (1–211), exact CN source line, and position kind. No duplicate or missing position found.
- Last text is at CN line 589; remaining CN lines 590–593 contain only commands. CN file has 593 content lines plus a terminal newline; EN has 594 content lines plus a terminal newline.
- Result: **first draft complete** for BB-3 before battle. This is a coverage audit, **not** a literary edit or a game-client test. No new Russian lines were translated in this audit.
- Original v2.29 file remains intact; audited complete overlay is `events/babel_bb3_before_ru_v240.json`.

## Outstanding

1. The historical `events/BABEL_INDEX_v050.tsv` and `chronology/CHRONOLOGY_MANIFEST_v140.json` are stale for the Babel branch; do not interpret their `not_started` entries as evidence that the corresponding scene has no translation. Rebuild from actual newest scene JSON files before publishing a new canonical index.
2. Compare CN/EN command differences and rendering of subtitles and stickers against the Yostar Global PC client before declaring patch compatibility.
3. Continue Babel in the original in-event scene order after verifying the status of the next scene (BB-3 after battle v2.39, then st02).
