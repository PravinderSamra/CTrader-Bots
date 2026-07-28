"""Inject trail_consolidated.json into the stop-loss dashboard template."""
import os, re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl=open(os.path.join(ROOT,'scripts','trail_template.html')).read()
data=open(os.path.join(ROOT,'analysis','trail','trail_consolidated.json')).read()
out=re.sub(r'/\*INJECT\*/.*?/\*END\*/','__D__',tpl,flags=re.S).replace('__D__',data)
open(os.path.join(ROOT,'stop_loss_management.html'),'w').write(out)
print('built stop_loss_management.html', len(out), 'bytes')
