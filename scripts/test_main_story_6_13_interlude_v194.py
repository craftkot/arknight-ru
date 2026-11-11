# -*- coding: utf-8 -*-
import json, re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
T=load("story/story_chapter_6_stage_6-13_interlude_partial_ru_v194.json")
A=load("reports/MAIN_6-13_INTERLUDE_SOURCE_AUDIT_v194.json")
Q=load("reports/QA_MAIN_STORY_v194.json")
M=load("chronology/CHRONOLOGY_MANIFEST_v354.json")
S=load("story/story_main_selection_ru_v189.json")
I=(ROOT/"story/CHAPTER_6_INDEX_v194.tsv").read_text(encoding="utf-8")
R=(ROOT/"README.md").read_text(encoding="utf-8")
NEW_LINES=[313, 314, 315, 316, 317, 318, 319, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 336, 337, 338, 339, 342, 343, 344, 345, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360]
COUNTS={"HEADER":1,"stopmusic":1,"delay":3,"Decision":30,"Predicate":41,"Dialog":11,"Character":23,"Blocker":10,"Background":3,"PlayMusic":1,"Image":2,"ImageTween":1,"hideitem":1}
class TestMainStory613InterludeV194(unittest.TestCase):
 def test_progress(self):
  p,rows=T["progress"],T["dialogues"]
  self.assertEqual(T["version"],"v1.94")
  self.assertEqual((p["translated"],p["total"],p["remaining"],p["complete"]),(232,269,37,False))
  self.assertEqual((p["named_translated"],p["unnamed_translated"]),(220,12))
  self.assertEqual((p["next_ordinal"],p["next_source_line"]),(233,361))
  self.assertEqual([x["ordinal"] for x in rows],list(range(1,233)))
  self.assertEqual([x["source_line"] for x in rows[-40:]],NEW_LINES)
  self.assertTrue(all(x["speaker_cn"]=="霜星" for x in rows[-40:]))
 def test_payload(self):
  payload="\n".join(x["text_ru"] for x in T["dialogues"])
  options="\n".join(s for d in T["decision_options_ru"] for s in d["options_ru"])
  self.assertIsNone(re.search(r"[\u3400-\u9fff]",payload+options))
  self.assertEqual(payload.count("{@nickname}"),4)
  self.assertEqual(T["source_alignment"]["placeholder_count_ru"],4)
  self.assertEqual((len(T["decision_options_ru"]),sum(len(x["options_ru"]) for x in T["decision_options_ru"])),(30,45))
 def test_source_and_commands(self):
  s,a=T["source"],T["source_alignment"]
  self.assertEqual(s["cn_git_blob_sha1"],"ffa8947a78abc196f2ebfcb90ae2283ee136c953")
  self.assertEqual(s["en_git_blob_sha1"],"79204a97fedbc6e1950440f86a618c8d6efa37ba")
  self.assertEqual((a["cn_text_positions"],a["en_text_positions"]),(269,269))
  self.assertEqual((a["command_lines_cn"],a["command_lines_en"]),(141,141))
  self.assertTrue(a["command_line_numbers_match"])
  tr=a["translated_range"]
  self.assertEqual((tr["ordinal_start"],tr["ordinal_end"]),(1,232))
  self.assertEqual(tr["command_lines_in_range"],128)
  self.assertEqual(tr["command_counts"],COUNTS)
  self.assertEqual((tr["decision_commands"],tr["decision_option_strings"],tr["predicate_branches"]),(30,45,41))
  self.assertEqual(a["untranslated_positions"],37)
  self.assertEqual(A["integrity"]["next_source_line"],361)
 def test_indexes_and_manifest(self):
  row=[x for x in I.splitlines() if x.startswith("level_st_06-02.txt")]
  self.assertEqual(len(row),1)
  f=row[0].split("\t")
  self.assertEqual(f[:5],["level_st_06-02.txt","partial_first_draft","220","12","232"])
  self.assertEqual(f[5:],["ffa8947a78abc196f2ebfcb90ae2283ee136c953","79204a97fedbc6e1950440f86a618c8d6efa37ba"])
  self.assertEqual(M["version"],"v3.54")
  self.assertEqual((M["next_text_ordinal"],M["next_text_source_line"]),(233,361))
  self.assertEqual((M["translation_integrity"]["main_story_partial_text_entries"],M["translation_integrity"]["main_story_partial_named_ru_lines"]),(232,220))
  self.assertNotIn("obt/main/level_st_06-02.txt",S["files"])
  self.assertEqual((Q["partial_scene_text_entries"],Q["partial_scene_named_ru"],Q["partial_scene_unnamed_ru"]),(232,220,12))
  self.assertEqual((Q["next_scene"]["translated"],Q["next_scene"]["next_ordinal"],Q["next_scene"]["next_source_line"]),(232,233,361))
  self.assertFalse(Q["editorial_review"])
  self.assertFalse(Q["in_game_test"])
  self.assertIn("232/269",R)
  self.assertIn("Следующая позиция — №233",R)
if __name__=="__main__": unittest.main()
