@echo off

rem @author Robin Schneider <robin.schneider@hamcos.de>
rem @company hamcos IT Service GmbH http://www.hamcos.de
rem @license GPLv3 <https://www.gnu.org/licenses/gpl-3.0.html>

rem needed because cmd is incapable of executing the install script from an UNC path.

xcopy "\\source\mon" C:\_service_it\mon /D /E /C /R /H /I /K /Y
cd C:\_service_it\mon
.\check_mk_agent.bat
