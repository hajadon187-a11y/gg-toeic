#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V=ROOT/"app/src/main/assets/vocabulary.json"; P=ROOT/"app/src/main/assets/vocabulary_phrase_translations.json"
EN={"subside":"The noise should subside after the construction ends.","corrupted":"The IT team restored the corrupted database from a backup.","portability":"The portability of the device makes it useful for field staff.","constituted":"The committee was constituted to review the merger.","formulated":"The researchers formulated a plan to reduce waste.","suitability":"The engineer assessed the suitability of the site.","clustered":"The stores are clustered around the central station.","accumulated":"The company accumulated enough data to identify the trend.","fairness":"The committee emphasized fairness in the promotion process.","intervening":"During the intervening period, the supplier changed its policy."}
JA={"subside":"工事が終われば騒音は収まるはずだ。","corrupted":"ITチームはバックアップから破損したデータベースを復元した。","portability":"機器は持ち運びやすく現場職員に便利だ。","constituted":"合併を検討する委員会が設置された。","formulated":"研究者は廃棄物削減計画を策定した。","suitability":"技術者はその場所が適切か評価した。","clustered":"店舗は中央駅周辺に集中している。","accumulated":"会社は傾向を特定できる十分なデータを蓄積した。","fairness":"委員会は昇進手続きの公平性を強調した。","intervening":"その間に、仕入先は方針を変更した。"}
def main():
    v=json.loads(V.read_text(encoding='utf-8')); p=json.loads(P.read_text(encoding='utf-8')); t=p.setdefault('translations',{}); rows=[x for x in v if int(x.get('level',0))==4][140:150]; assert {x['word'] for x in rows}==set(EN)==set(JA)
    for x in rows:
        w=x['word']; x['example']=EN[w]; t.setdefault(f"builtin:{x['id']}",{}).setdefault('example',{}).update(source=EN[w],en=EN[w],ja=JA[w])
    V.write_text(json.dumps(v,ensure_ascii=False,indent=1)+'\n',encoding='utf-8'); P.write_text(json.dumps(p,ensure_ascii=False,indent=1)+'\n',encoding='utf-8'); print('reviewed 800+ English/Japanese examples batch 1e: 10 terms')
if __name__=='__main__': main()
