#!/usr/bin/env python3
"""Build a Portuguese->Chinese searchable lexicon from CC BY-SA Chinese Wiktionary data.

No AI, no secret API, no paid infrastructure. Stream local JSONL or download from Kaikki.
Outputs only entries with non-empty Chinese glosses; excludes inflections, proper nouns and junk.

Example:
  python scripts/import_kaikki.py --download --out data/open_lexicon.json --report data/build_report.json
  python scripts/import_kaikki.py --input ./simplified.jsonl ./traditional.jsonl --out data/open_lexicon.json
"""
import argparse, collections, datetime, gzip, json, re, sys, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import quote

SOURCES = [
 ('traditional','https://kaikki.org/zhwiktionary/%E8%91%A1%E8%90%84%E7%89%99%E8%AA%9E/kaikki.org-dictionary-%E8%91%A1%E8%90%84%E7%89%99%E8%AA%9E.jsonl'),
 ('simplified','https://kaikki.org/zhwiktionary/%E8%91%A1%E8%90%84%E7%89%99%E8%AF%AD/kaikki.org-dictionary-%E8%91%A1%E8%90%84%E7%89%99%E8%AF%AD.jsonl'),
]
POS={'noun':'名词','verb':'动词','adj':'形容词','adv':'副词','prep':'介词','pron':'代词','conj':'连词','det':'限定词','num':'数词','phrase':'固定表达','intj':'感叹词','name':'专名'}
ALLOWED=set(POS)-{'name'}
SKIP_WORDFORM=re.compile(r'^(?:[\d\-\W]+)$',re.U)
INFLECTION=re.compile(r'(?:[的之]\s*(?:复数|複數|阴性|陰性|阳性|陽性|单数|單數|变位|變位|比较级|比較級|最高级|最高級|屈折形式|非限定形式|過去分詞|过去分词|现在分词|現在分詞|動名詞|动名词)|(?:第一|第二|第三)[一二三]?人称|(?:first|second|third)[ -]person|\b(?:plural|singular|inflection|form of)\b)',re.I)
CJK=re.compile(r'[\u3400-\u9fff]')
TRASH_GLOSS=re.compile(r'^(?:參見|参见|同|见|見|的|\.|\(|\)|\-)[^\u3400-\u9fff]{0,10}$')


def download_if_needed(url,path):
    if path.exists() and path.stat().st_size>10240:
        print('Cache:',path,flush=True);return
    path.parent.mkdir(parents=True,exist_ok=True)
    print('Downloading:',url,flush=True)
    r=urllib.request.Request(url,headers={'User-Agent':'VascarioDictionaryBuilder/1.5 (open educational project; wiktextract)'})
    with urllib.request.urlopen(r,timeout=180) as resp, path.open('wb') as output:
        from shutil import copyfileobj
        copyfileobj(resp,output,1024*1024)
    print('Downloaded',path.stat().st_size,'bytes',flush=True)


def iter_rows(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:yield json.loads(line)
                except json.JSONDecodeError: continue


def extract(row,converter=None):
    if row.get('lang_code')!='pt':return None
    word=row.get('word') or ''
    word=re.sub(r'\s+',' ',str(word)).strip()
    if not (2<=len(word)<=85) or not re.search(r'[A-Za-zÀ-ÿ]',word) or SKIP_WORDFORM.fullmatch(word):return None
    pos=row.get('pos','')
    if pos not in ALLOWED:return None
    senses=row.get('senses') or []
    glosses=[];form_senses=0;seen=set()
    for sense in senses:
        if not isinstance(sense,dict):continue
        if sense.get('form_of') or 'form-of' in (sense.get('tags') or []) or 'inflection' in (sense.get('tags') or []):
            form_senses+=1;continue
        for gloss in sense.get('glosses') or sense.get('raw_glosses') or []:
            gloss=re.sub(r'\s+',' ',str(gloss)).strip(' ;；。. ')
            if not (CJK.search(gloss)) or len(gloss)>240 or not gloss:continue
            if TRASH_GLOSS.match(gloss):continue
            if INFLECTION.search(gloss) and len(gloss)<105:continue
            if gloss not in seen:glosses.append(gloss);seen.add(gloss)
    if not glosses:return None
    glosses=glosses[:4]
    if converter:glosses=[converter.convert(v) for v in glosses]
    clean='；'.join(glosses)
    if len(clean)>360:clean=clean[:360].rstrip('；')
    if not clean:return None
    tags=set(row.get('tags') or []); sense_tags=set(t for s in senses if isinstance(s,dict) for t in (s.get('tags') or []))
    all_tags=tags|sense_tags
    reg='巴葡常见' if {'Brazil','Brazilian','Brazilian Portuguese'}&all_tags else '欧葡常见' if {'Portugal','European Portuguese'}&all_tags else '两地可能通用'
    return word,{'pos':POS[pos],'level':'开放词库','def':clean,'ipa':'开放词库自动提取；释义及用法需核对','region':reg,
       'senses':[{'title':glosses[0],'scene':'开放词典 / 基础释义','desc':'中文 Wiktionary 提取数据；部分词条可能存在语义、地域或词性差异。','pt':'','br':'','zh':'','tip':'暂未配置经人工审核的例句。'}],
       'phrases':[],'compare':'该条为自动整理的开放词典释义，尚未经过逐条人工审核。正式工程文书请结合技术规范核对。',
       'forms':[],'origin':'open','source': 'zh.wiktionary.org',
       'sourceUrl':'https://zh.wiktionary.org/wiki/'+quote(word,safe=''),'license':'CC BY-SA 4.0'}


def rank(item):
    word,entry=item
    gloss=entry['def']
    # Prioritise concise lemmas with multiple useful glosses; don't mistake variation for coverage.
    fav={'名词':5,'动词':5,'形容词':4,'副词':4,'介词':4,'代词':4,'连词':4,'固定表达':4,'数词':3,'感叹词':3}
    return (fav.get(entry['pos'],0),2 if len(word)<=15 else 0,2 if not re.search(r'\d',word) else 0,
      2 if len(gloss)<=100 else 0,1 if '；' in gloss else 0,-len(word))


def run(inputs,output,report,target=10000,limit=15000,curated_keys_file=None):
    try:
        from opencc import OpenCC
        converter=OpenCC('t2s')
        print('Traditional Chinese conversion active.')
    except ImportError:converter=None
    entries={};counts=collections.Counter();per_file={}
    for path in inputs:
        counts_here=collections.Counter()
        for row in iter_rows(path):
            counts_here['rows']+=1
            pair=extract(row,converter)
            if not pair:continue
            word,entry=pair
            counts_here['valid_rows']+=1
            if word not in entries:entries[word]=entry
            else:
                existing=entries[word]
                if len(existing['def'])<len(entry['def']) and len(entry['def'])<280:entries[word]=entry
                counts_here['duplicate_words']+=1
        per_file[path.name]=dict(counts_here);counts.update(counts_here)
        print(path.name,'rows',counts_here['rows'],'valid',counts_here['valid_rows'],'unique_total',len(entries),flush=True)
    ranked=sorted(entries.items(),key=lambda e:(rank(e),e[0]),reverse=True)
    selected=dict(ranked[:limit])
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(selected,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    curated_keys=set(json.loads(Path(curated_keys_file).read_text(encoding='utf-8'))) if curated_keys_file and Path(curated_keys_file).exists() else set()
    curated_overlap=len(set(selected)&curated_keys)
    overall_total=len(set(selected)|curated_keys)
    data={'curated_entry_count':len(curated_keys),'overlap_with_curated':curated_overlap,'total_distinct_app_headwords':overall_total,'target_met':overall_total>=target,
      'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_urls':[u for _,u in SOURCES],
      'input_files':[str(p) for p in inputs],'valid_distinct_entries':len(entries),
      'selected_entries':len(selected),'target':target,'target_met_by_open_words':len(selected)>=target,
      'notices':['排除词形变化、空白或非中文释义；词义由 Wiktionary 提供且未经逐条审校。','词数仅统计独立检索词目，不含变位枚举。','开放词库受 CC BY-SA 许可约束，需署名并提供许可说明。'],
      'part_of_speech_counts':dict(collections.Counter(v['pos'] for v in selected.values())), 'input_stats':per_file,'output_sha256':__import__('hashlib').sha256(output.read_bytes()).hexdigest()}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Generated:',output,'selected:',len(selected),'goal:',target, 'overall:',overall_total,'achieved?',data['target_met'],flush=True)
    return data

if __name__=='__main__':
    pa=argparse.ArgumentParser()
    pa.add_argument('--download',action='store_true')
    pa.add_argument('--input',nargs='*',type=Path,default=[])
    pa.add_argument('--out',type=Path,default=Path('data/open_lexicon.json'))
    pa.add_argument('--report',type=Path,default=Path('data/build_report.json'))
    pa.add_argument('--target',type=int,default=10000)
    pa.add_argument('--curated-keys',type=Path,default=Path('data/curated_keys.json'))
    pa.add_argument('--limit',type=int,default=15000)
    args=pa.parse_args()
    inputs=args.input
    if args.download:
        for label,url in SOURCES:
            p=Path('data/sources')/(label+'.jsonl')
            try:download_if_needed(url,p);inputs.append(p)
            except Exception as e:print('Source unavailable:',label,str(e),file=sys.stderr)
    if not inputs:pa.error('Provide --input path or --download')
    report=run(inputs,args.out,args.report,args.target,args.limit,args.curated_keys)
    if not report['target_met']:
        print('WARNING: Open word count below goal. Quality filters retained. Do not pad records.',file=sys.stderr)
