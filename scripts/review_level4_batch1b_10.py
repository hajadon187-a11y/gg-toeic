#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VOCAB=ROOT/"app/src/main/assets/vocabulary.json"; PHRASE=ROOT/"app/src/main/assets/vocabulary_phrase_translations.json"
EN={"diversified":"The company has a diversified portfolio of services.","grandeur":"The hotel restored the grandeur of its historic entrance.","dependability":"Dependability is essential for staff on the delivery team.","mediocre":"The review found the supplier's service mediocre.","appropriateness":"The manager questioned the appropriateness of the wording.","fluctuation":"The finance team monitors fluctuation in exchange rates.","concession":"The supplier offered a concession on the final price.","orderliness":"The warehouse improved orderliness by labeling every shelf.","compassion":"The nurse showed compassion to the injured employee.","curfew":"The resort introduced a curfew during the emergency."}
JA={"diversified":"会社は多様化したサービスのポートフォリオを持っている。","grandeur":"ホテルは歴史ある入口の壮麗さを取り戻した。","dependability":"配送チームで働く職員には信頼性が欠かせない。","mediocre":"評価では仕入先のサービスは平凡だとされた。","appropriateness":"マネージャーはその表現が適切か疑問視した。","fluctuation":"財務チームは為替レートの変動を監視している。","concession":"仕入先は最終価格を譲歩した。","orderliness":"倉庫は全ての棚にラベルを付け、整然さを改善した。","compassion":"看護師は負傷した従業員に思いやりを示した。","curfew":"リゾートは緊急時に夜間外出禁止令を導入した。"}
def main():
    v=json.loads(VOCAB.read_text(encoding='utf-8')); p=json.loads(PHRASE.read_text(encoding='utf-8')); t=p.setdefault('translations',{}); rows=[x for x in v if int(x.get('level',0))==4][100:110]; assert {x['word'] for x in rows}==set(EN)==set(JA)
    for x in rows:
        w=x['word']; x['example']=EN[w]; t.setdefault(f"builtin:{x['id']}",{}).setdefault('example',{}).update(source=EN[w],en=EN[w],ja=JA[w])
    VOCAB.write_text(json.dumps(v,ensure_ascii=False,indent=1)+'\n',encoding='utf-8'); PHRASE.write_text(json.dumps(p,ensure_ascii=False,indent=1)+'\n',encoding='utf-8'); print('reviewed 800+ English/Japanese examples batch 1b: 10 terms')
if __name__=='__main__': main()
