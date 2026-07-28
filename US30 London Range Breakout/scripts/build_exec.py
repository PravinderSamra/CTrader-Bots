"""Inject analysis/dollar/consolidated.json into the exec-summary template."""
import os, re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl=open(os.path.join(ROOT,'scripts','exec_summary_template.html')).read()
data=open(os.path.join(ROOT,'analysis','dollar','consolidated.json')).read()
out=re.sub(r'/\*INJECT\*/.*?/\*END\*/','__D__',tpl,flags=re.S).replace('__D__',data)
open(os.path.join(ROOT,'exec_summary.html'),'w').write(out)
print('built exec_summary.html', len(out),'bytes; DATA embeds:', out.count('const DATA ='))
