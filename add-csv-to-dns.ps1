## @author Robin Schneider <robin.schneider@hamcos.de>
## @company hamcos IT Service GmbH http://www.hamcos.de
## @license AGPL-3.0 <https://www.gnu.org/licenses/agpl-3.0.html>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, version 3 of the
## License.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <https://www.gnu.org/licenses/>.

if(!($args[0]) -or !($args[1]) -or !($args[2]))
{
	write-host -Fore Red "** Argument missing! ***"
	write-host -Fore Red "Usage: .\add-csv-to-dns.ps1 hostname_ip.csv localhost example.com"
	exit
}

$dns_server = $args[1]
$domain = $args[2]

Import-Csv $args[0] | ForEach-Object {

    ## Example call:
    # dnscmd 192.0.2.1 /recordadd example.com. hostname A 192.0.2.23
    dnscmd $dns_server /RecordAdd $domain $_.hostname /createPTR A $_.IP

}
