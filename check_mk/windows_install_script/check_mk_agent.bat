@echo off

rem @author Alexander Zell <alexander.zell@hamcos.de>
rem @maintainer Robin Schneider <robin.schneider@hamcos.de>
rem @company hamcos IT Service GmbH http://www.hamcos.de
rem @license GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>
rem To download the setup file, run https://github.com/hamcos/monitoring-scripts/blob/master/check_mk/Makefile

rem This script is only needed if you do not use configuration management (which you should use).

if exist "%programfiles%\check_mk\check_mk_agent.exe" goto installed
if exist "%programfiles(x86)%\check_mk\check_mk_agent.exe" goto installed

rem Check for root permissions {{{
rem http://stackoverflow.com/a/11995662
echo Administrative permissions required. Detecting permissions ...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Success: Administrative permissions confirmed.
) else (
    echo Failure: Current permissions inadequate.
    echo Please execute with administrative permissions.
    pause
    exit
)
rem }}}

rem Switch to `dirname $0` {{{
rem Windows hack to execute all following instruction in context of the directory form where the script is located.
rem https://social.technet.microsoft.com/Forums/scriptcenter/en-US/360ff40b-6a2b-4651-9a3e-360e803d8ffb/executing-batch-file-as-administrator-changes-working-directory?forum=ITCG
@setlocal enableextensions
@cd /d "%~dp0"
echo Executing script in context of %cd%
rem }}}

echo Install agent without user interaction.
.\check_mk_agent.msi /passive

echo Ensure that the agent is stopped.
net stop Check_MK_Agent

echo Add firewall rule to allow external access to the agent. Note that this will add a new rule each time it is executed.
netsh advfirewall firewall add rule name="Check_MK_Agent" dir=in action=allow protocol=TCP localport=6556 enable=yes

if exist "%programfiles(x86)%" goto x64
echo Install on x86-32 architecture.
mkdir "%programfiles%\check_mk"
copy .\check_mk.ini "%programfiles%\check_mk\check_mk.ini" /y
net start Check_MK_Agent
goto ende

:x64
echo Install on x86-64 architecture.
mkdir "%programfiles(x86)%\check_mk"
copy .\check_mk.ini "%programfiles(x86)%\check_mk\check_mk.ini" /y
net start Check_MK_Agent
goto ende

:installed
echo Agent was already installed.

:ende
pause
