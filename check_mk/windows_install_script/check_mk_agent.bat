rem @author Alexander Zell <alexander.zell@hamcos.de>
rem @maintainer Robin Schneider <robin.schneider@hamcos.de>
rem @company hamcos IT Service GmbH http://www.hamcos.de
rem @license GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>

if exist "%programfiles%\check_mk\check_mk_agent.exe" goto ende
if exist "%programfiles(x86)%\check_mk\check_mk_agent.exe" goto ende

.\install_agent-64.exe /S
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
