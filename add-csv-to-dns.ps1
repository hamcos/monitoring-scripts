## @author Robin Schneider <robin.schneider@hamcos.de>
## @company hamcos IT Service GmbH http://www.hamcos.de
## @license GPL-2.0 <https://www.gnu.org/licenses/gpl-2.0.html>

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
