if exist "%programfiles%\check_mk\check_mk_agent.exe" goto ende
if exist "%programfiles(x86)%\check_mk\check_mk_agent.exe" goto ende

.\check-mk-agent-1.2.4p3.exe /S
rem .\install_agent-64.exe /S

net stop Check_MK_Agent

if exist "%programfiles(x86)%" goto x64
copy .\config.ini "%programfiles%\check_mk\config.ini" /y
netsh advfirewall firewall add rule name="Check_MK_Agent" dir=in action=allow program="%programfiles%\check_mk\check_mk_agent.exe" enable=yes
net start Check_MK_Agent
goto ende

:x64
copy .\config.ini "%programfiles(x86)%\check_mk\config.ini" /y
netsh advfirewall firewall add rule name="Check_MK_Agent" dir=in action=allow program="%programfiles(x86)%\check_mk\check_mk_agent.exe" enable=yes
net start Check_MK_Agent
goto ende

:ende
