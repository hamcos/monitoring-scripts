rem @author Alexander Zell <alexander.zell@hamcos.de>
rem @maintainer Robin Schneider <robin.schneider@hamcos.de>
rem @company hamcos IT Service GmbH http://www.hamcos.de
rem @license GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>
rem To download the setup file, run https://github.com/hamcos/monitoring-scripts/blob/master/check_mk/Makefile

rem This script is only needed if you do not use configuration management (which you should use).

if exist "%programfiles%\check_mk\check_mk_agent.exe" goto ende
if exist "%programfiles(x86)%\check_mk\check_mk_agent.exe" goto ende

.\install_agent-64.exe install
rem .\install_agent-64.exe /S

net stop Check_MK_Agent

if exist "%programfiles(x86)%" goto x64
mkdir "%programfiles%\check_mk"
copy .\check_mk.ini "%programfiles%\check_mk\check_mk.ini" /y
netsh advfirewall firewall add rule name="Check_MK_Agent" dir=in action=allow protocol=TCP localport=6556 enable=yes
net start Check_MK_Agent
goto ende

:x64
mkdir "%programfiles(x86)%\check_mk"
copy .\check_mk.ini "%programfiles(x86)%\check_mk\check_mk.ini" /y
netsh advfirewall firewall add rule name="Check_MK_Agent" dir=in action=allow protocol=TCP localport=6556 enable=yes
net start Check_MK_Agent
goto ende

:ende
