#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V=ROOT/"app/src/main/assets/vocabulary.json"; P=ROOT/"app/src/main/assets/vocabulary_phrase_translations.json"
EN={"responsiveness":"The support team's responsiveness improved after the new system launched.","inconsistency":"The audit found an inconsistency in the two invoices.","deterioration":"The inspection revealed deterioration in the building's roof.","sociological":"The report presents a sociological analysis of workplace culture.","heroism":"The company honored the driver's heroism during the rescue.","collaborator":"Each collaborator received a copy of the project plan.","fictional":"The advertisement uses a fictional customer to illustrate the service.","theoretically":"Theoretically, the new process could double output.","uselessness":"The test demonstrated the uselessness of the outdated tool.","hierarchical":"The hierarchical structure slows communication between departments."}
JA={"responsiveness":"新システム導入後、サポートチームの対応力が向上した。","inconsistency":"監査で2つの請求書の不一致が見つかった。","deterioration":"検査で建物の屋根の劣化が明らかになった。","sociological":"報告書は職場文化を社会学的に分析している。","heroism":"会社は救助中の運転手の勇気をたたえた。","collaborator":"共同作業者全員が計画書のコピーを受け取った。","fictional":"広告はサービスを説明する架空の顧客を使っている。","theoretically":"理論上、新工程で生産量を倍増できる。","uselessness":"試験で旧式の道具が役に立たないことが示された。","hierarchical":"階層的な構造が部署間の意思疎通を遅らせている。"}
def main():
    v=json.loads(V.read_text(encoding='utf-8')); p=json.loads(P.read_text(encoding='utf-8')); t=p.setdefault('translations',{}); rows=[x for x in v if int(x.get('level',0))==4][130:140]; assert {x['word'] for x in rows}==set(EN)==set(JA)
    for x in rows:
        w=x['word']; x['example']=EN[w]; t.setdefault(f"builtin:{x['id']}",{}).setdefault('example',{}).update(source=EN[w],en=EN[w],ja=JA[w])
    V.write_text(json.dumps(v,ensure_ascii=False,indent=1)+'\n',encoding='utf-8'); P.write_text(json.dumps(p,ensure_ascii=False,indent=1)+'\n',encoding='utf-8'); print('reviewed 800+ English/Japanese examples batch 1d: 10 terms')
if __name__=='__main__': main()
