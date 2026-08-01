import re
def chek (format, s):
    return len(re.findall(format, s))
format = "=</"
s1 = 'setklga=</w;rogjn.la awoi=</65494ed4'#2
s2 = '=</se=</;/lknserrpm=</34p98y8th=</'#4
s3 = 'dryjn=</strm"==</</=</""=</"rymjsr=</ynb'#5
s4 = '=</dryj=</nstrm"=</""=</"rymjsrynb'#4
s5 = 'dryjns==</</trm"=</"asbbbfb"=</"rymjsrynb'#3
print(chek("=</", s5))