#!/usr/bin/env python3
# coding: utf-8
"""Version-verified LOCAL PREVIEW of a selected event scene.

Unlike main-story V0.25 patcher, supports both [name="..."] lines and
unnamed dialogue/narration (non-command non-comment lines).  All other lines
including scene control, music and backgrounds stay byte-for-byte the same.
"""
import argparse, hashlib, json, pathlib, re
from apply_ru_story import SPEAKER, INLINE, git_blob_sha1, quoted_tokens, read_validated

ALLOWED_EVENT_PATH=re.compile(r'activities/act9d0/level_act9d0_(?:0[1-6]_(?:beg|end)|st01)\.txt\Z')
SPEAKER_EVENT_RU={'Ines':'Инес', 'Hoederer':'Хёдерер',
    'Disheveled Sarkaz Woman':'Оборванная девушка-сарказ',
    'W':'W',
    'Sarkaz Warrior':'Воин-сарказ',
    'Sarkaz Warrior?':'Воин-сарказ?', 'Mercenary':'Наёмник'}

def plain_line(s):
    t=s.strip()
    return bool(t) and not t.startswith('[') and not t.startswith('//')

def extract(raw):
    named,plain=[],[]
    for line in raw.decode('utf-8-sig').splitlines():
        m=SPEAKER.search(line)
        if m:
            spoken=line[m.end():].strip()
            if spoken and not spoken.startswith('//'):named.append((m.group(3),spoken))
        elif plain_line(line):
            plain.append(line.strip())
    return named,plain

def patch(en_raw,spec):
    if len(spec['dialogues'])!=spec['dialogue_count'] or len(spec['plain_dialogues'])!=spec['plain_dialogue_count']:
        raise ValueError('Translation spec count mismatch')
    orig=en_raw.decode('utf-8-sig')
    bom=en_raw.startswith(b'\xef\xbb\xbf')
    lines=orig.splitlines(keepends=True)
    count_n=count_p=0
    for n,rawline in enumerate(lines):
        body=rawline.rstrip('\r\n');eol=rawline[len(body):]
        m=SPEAKER.search(body)
        if m:
            spoken=body[m.end():].strip()
            if not spoken or spoken.startswith('//'):continue
            count_n+=1
            key=str(count_n)
            if key not in spec['dialogues']:raise ValueError('Missing named RU '+key)
            ru=spec['dialogues'][key]
            if m.group(3) not in SPEAKER_EVENT_RU:raise ValueError('Unmapped event speaker: '+m.group(3))
            pref=body[:m.start(3)]+SPEAKER_EVENT_RU[m.group(3)]+body[m.end(3):m.end()]
            suffix=body[m.end():];ws=suffix[:len(suffix)-len(suffix.lstrip())]
            after=pref+ws+ru
        elif plain_line(body):
            count_p+=1
            key=str(count_p)
            if key not in spec['plain_dialogues']:raise ValueError('Missing plain RU '+key)
            ru=spec['plain_dialogues'][key]
            ws=body[:len(body)-len(body.lstrip())]
            after=ws+ru
            spoken=body.strip()
        else:
            continue
        if not isinstance(ru,str) or not ru.strip() or re.search(r'[\r\n\t]',ru):raise ValueError('Bad RU text at '+str(n+1))
        if quoted_tokens(spoken)!=quoted_tokens(ru):raise ValueError('Markup mismatch at '+str(n+1))
        lines[n]=after+eol
    if (count_n,count_p)!=(spec['dialogue_count'],spec['plain_dialogue_count']):raise ValueError('File dialogue count mismatch')
    new=''.join(lines)
    if len(orig.splitlines())!=len(new.splitlines()):raise ValueError('Line count changed')
    return (b'\xef\xbb\xbf' if bom else b'')+new.encode('utf-8')

def build(source_root,out_root,translations):
    src=pathlib.Path(source_root).resolve();dest=pathlib.Path(out_root).resolve()
    if src==dest or src in dest.parents:raise ValueError('Output cannot be inside source folder')
    specdoc=json.loads(pathlib.Path(translations).read_text('utf8'))
    pending=[]
    for rel,spec in specdoc['files'].items():
        if not ALLOWED_EVENT_PATH.fullmatch(rel):raise ValueError('Disallowed event file path '+rel)
        en=read_validated(src/'en'/rel,spec['en_git_blob_sha1'])
        cn=read_validated(src/'cn'/rel,spec['cn_git_blob_sha1'])
        en_n,en_p=extract(en);cn_n,cn_p=extract(cn)
        if (len(en_n),len(en_p))!=(len(cn_n),len(cn_p)) or (len(en_n),len(en_p))!=(spec['dialogue_count'],spec['plain_dialogue_count']):
            raise ValueError('CN EN RU dialogue count mismatch '+rel)
        transformed=patch(en,spec)
        old=en.decode('utf-8-sig').splitlines();new=transformed.decode('utf-8-sig').splitlines()
        for a,b in zip(old,new):
            if not SPEAKER.search(a) and not plain_line(a) and a!=b:
                raise ValueError('Story control command changed')
        pending.append((rel,transformed,spec))
    report={'version':specdoc.get('version'),'event':specdoc.get('event'),
            'files':len(pending),'named_ru_lines':sum(x[2]['dialogue_count'] for x in pending),
            'plain_ru_lines':sum(x[2]['plain_dialogue_count'] for x in pending),
            'status':'preview_only; no game files modified','outputs':[]}
    for rel,data,spec in pending:
        p=dest/'ru'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        report['outputs'].append({'file':rel,'sha256':hashlib.sha256(data).hexdigest()})
    (dest/'event_preview_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',default='source/story');p.add_argument('--output',default='output/darknights_preview')
    p.add_argument('--translations',default='events/darknights_memoir_dm1_before_ru_v026.json')
    a=p.parse_args()
    print(json.dumps(build(a.source,a.output,a.translations),ensure_ascii=False,indent=2))
