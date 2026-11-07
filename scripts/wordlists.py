#!/usr/bin/env python3
"""Validate the reviewable Markdown banks and build their native Hoon library."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
BANKS={'default':('default.md',2000),'easy':('easy.md',500),'hard':('hard.md',500),'urbit':('Urbit.md',500)}
def read_bank(name):
    path=ROOT/'wordlists'/BANKS[name][0]
    words=re.findall(r'^- (.+)$',path.read_text(),re.M)
    assert len(words)==BANKS[name][1],(name,len(words))
    assert len(set(w.lower().replace(' ','') for w in words))==len(words),f'Duplicate normalized answers in {name}'
    assert all(w==w.lower() and 0<len(w)<=64 and all(32<=ord(c)<127 for c in w) for w in words),name
    if name=='default':assert not {'delivery van','fire engine'}&set(words)
    return words

def build():
    banks={name:read_bank(name) for name in BANKS}
    def cord(word):return "'"+''.join('\\%02x'%ord(c) if c in "'\\" else c for c in word)+"'"
    text='::  Generated from wordlists/*.md by scripts/wordlists.py.\n|%\n'
    for name,words in banks.items():
        text+='++  '+name+'\n  ^-  (list @t)\n  :~  '+'\n      '.join(cord(w) for w in words)+'\n  ==\n'
    text+='--\n';(ROOT/'desk/lib/ursketch-words.hoon').write_text(text)
    report={name:{'count':len(words),'sha256':hashlib.sha256((ROOT/'wordlists'/BANKS[name][0]).read_bytes()).hexdigest()} for name,words in banks.items()}
    (ROOT/'artifacts/wordlists-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Validated word banks:',', '.join(name+'='+str(len(words)) for name,words in banks.items()))
    return banks
if __name__=='__main__':build()
