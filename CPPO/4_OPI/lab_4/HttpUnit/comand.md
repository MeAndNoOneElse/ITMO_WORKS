компиляция
$env:JAVA_HOME = 'C:\Program Files\Java\jdk1.8.0_251'; $env:Path = "$env:JAVA_HOME\bin;$env:Path"; Set-Location 'C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit'; ant clean jar

запуск
& 'C:\Program Files\Java\jdk1.8.0_251\bin\java.exe' -Xmx30m -cp 'C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\httpunit.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\js.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\junit.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\nekohtml.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\servlet.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\Tidy.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\xerces-2.4.0.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\xercesImpl.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\lib\xmlParserAPIs.jar;C:\Users\Eternal_Core\OneDrive - ITMO UNIVERSITY\github_file\ITMO\CPPO\4 OPI\lab_4\HttpUnit\dist\HttpUnit.jar' Main 1000 true

jconsole
visualmv
static _errorMessages in class com.meterware.httpunit.javascript.JavaScript : JavaScript		64 B (0%)	2 565 448 B (34,6%)