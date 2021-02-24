import os


fd=open('identcode.normal.exp0.box')
i=0
f1=open('identcode.normal.exp0.box2', 'w')
for line in fd:
    line=line[:-1]
    fes=line.split()
    fes[5]=str(i//4)
    line=' '.join(fes)
    f1.write(line+'\n')
    i+=1


fd.close()
f1.close()

os.system('mv identcode.normal.exp0.box2 identcode.normal.exp0.box')
