#!/bin/sh -e

[ "$1" = "-h" -o "$1" = "--help" ] && {
   echo "Usage: ${0##*/} [file]"
   echo "   writes sample ovf to file. file defaults to 'out.ovf'"
   exit 0
}
if [ -z "${MKOVF}" ]; then
   { MKOVF=$(which mkovf.py) || MKOVF=$(which mkovf); } 2>/dev/null || {
      echo "cannot find mkovf. export MKOVF or add 'mkovf.py' to PATH" >&2
      exit 1;
   }
fi
mkovf=${MKOVF}

f=${1:-out.ovf}
rm -f "${f}"

$mkovf --efile -f "$f" -i lamp -n lamp.vmdk  -s 180114671

$mkovf --disk -f "$f" \
   --info "List of the virtual disks used in the package" \
   -i lamp -c 4294967296 -s 1924967692 --fileRef lamp \
   --format "http://www.vmware.com/specifications/vmdk.html#compressed"

$mkovf --net -f "$f" \
   --info "Logical networks used in the package" --networkName "VM Network" \
   -d "The network that the LAMP Service will be available on" -i 1

$mkovf --vs -f "$f"  -i MyLampService \
   -m "Single-VM Virtual appliance with LAMP stack" 

$mkovf --product -f "$f" \
   --info "Product information for the service" \
   --comment " Overall information about the product" \
   --product "My Lamp Service" --productVersion 1.0 --fullVersion 1.0.0 \
   --appURL 'http://{org.linux.ip}:{org.apache.httpd.httpdPort}/' \
   --id MyLampService

$mkovf --product -f "$f" \
   --info "Product customization for the installed Linux system" \
   --comment "Linux component configuration parameters" \
   --product "Linux Distribution X" --productVersion 2.6.3 \
   --classDesc org.linuxdistx --instance 1 --id MyLampService

$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key hostname --type string \
   --description "Specifies the hostname for the appliance" 


$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key ip --type string \
   --description "Specifies the IP address for the appliance" 

$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key subnet --type string \
   --description "Specifies the subnet to use on the deployed network" 

$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key gateway --type string \
   --description "Specifies the gateway on the deployed network" 

$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key dns --type string \
   --description "A comma separated list of DNS servers on the deployed network" 

$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key netCoreRmemMaxMB --type string \
   --description "Specify TCP read max buffer size in mega bytes. Default is 16." 

$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key netCoreWmemMaxMB --type string \
   --description "Specify TCP write max buffer size in mega bytes. Default is 16." 

$mkovf --product -f "$f" \
   --info "Product customization for the installed Apache Web Server" \
   --comment "Apache  component configuration parameters" \
   --product "Apache Distribution Y" --productVersion 2.6.6 \
   --classDesc org.apache.httpd --instance 2 --id MyLampService

$mkovf --property -f "$f" --classDesc org.apache.httpd --instance 2 \
   --key httpPort --type int --description "Port number for HTTP requests." \
   --value 80 --userConfig True

$mkovf --property -f "$f" --classDesc org.apache.httpd --instance 2 \
   --key httpsPort  --type int  --userConfig True \
   --description "Port number for HTTPS requests." --value 443

$mkovf --property -f "$f" --classDesc org.apache.httpd --instance 2 \
   --key startThreads --type int --value 50 --userConfig True \
   --description "Number of threads created on startup." 

$mkovf --property -f "$f" --classDesc org.apache.httpd --instance 2 \
   --key minSpareThreads --type int --value 15 --userConfig True \
   --description "Minimum number of idle threads to handle request spikes." 

$mkovf --property -f "$f" --classDesc org.apache.httpd --instance 2 \
   --key maxSpareThreads --type string --value 30 --userConfig True \
   --description "Maximum number of idle threads."

$mkovf --property -f "$f" --classDesc org.apache.httpd --instance 2 \
   --key maxClients --type string --value 256 --userConfig True \
   --description "Limit the number of simultaneous requests that will be served." 

$mkovf --product -f "$f" \
   --info "Product customization for  the installed MySql Database Server" \
   --comment "MySQL  component configuration parameters" \
   --product "MySQL Distribution Z" --productVersion 5.0 \
   --classDesc org.mysql.db --instance 3 --id MyLampService

$mkovf --property -f "$f" --classDesc org.mysql.db --instance 3 \
   --key queryCacheSizeMB --type int --value 32 --userConfig True \
   --description "Buffer to cache repeated queries for faster access"

$mkovf --property -f "$f" --classDesc org.mysql.db --instance 3 \
   --key maxConnections --type int --value 500 --userConfig True \
   --description "The number of concurrent connections that can be served." 

$mkovf --property -f "$f" --classDesc org.mysql.db --instance 3 \
   --key waitTimeout --type int --value 100 --userConfig True \
   --description "Number of seconds to wait before timing out a connection ." 

$mkovf --product -f "$f" \
   --info "Product customization for the installed PHP  component" \
   --comment "PHP component configuration parameters" \
   --product "PHP Distribution U" --productVersion 5.0 --classDesc net.php \
   --id MyLampService --instance 3

$mkovf --property -f "$f" \
   --classDesc org.mysql.db --key sessionTimeout --type int \
   --value 5 --userConfig True --instance 3 \
   --description "How many minutes a session has to be idle before it is timed out." 

$mkovf --property -f "$f" --classDesc org.mysql.db --key concurrentSessions \
   --type int --value 500 --userConfig True --instance 3 \
   --description "The number of concurrent sessions that can be served." 

$mkovf --property -f "$f" --classDesc org.mysql.db --key memoryLimit \
   --type int --value 32 --userConfig True --instance 3 \
   --description "How much memory in megabytes a script can consume before being killed." 

$mkovf --os -f "$f" --id MyLampService --info "Guest Operating System" \
   --description "Linux 2.6.x" --secID 103

$mkovf --virthw -f "$f" --id MyLampService --type vmx-4 \
   --info "Virtual Hardware Requirements: 256Mb, 1 CPU, 1 disk, 1 nic"
 
$mkovf --resource -f "$f" --id MyLampService --caption "1 virtual CPU" \
   --description "Number of virtual CPUs" \
   --resourceID 1 --resourceType 3 --virtualQuantity 1 --elementName "virtual CPU"

$mkovf --resource -f "$f" --id MyLampService --allocUnits MegaBytes \
   --caption "256 MB of memory" --description "Memory Size" \
   --resourceID 2 --resourceType 4 --virtualQuantity 256

$mkovf --resource -f "$f" --id MyLampService --automaticAllocation True \
   --caption "Ethernet adapter on 'VM Network'" --description "Ethernet" \
   --connection "VM Network" --resourceID 3 --resourceType 10 \
   --elementName "Ethernet adapter"

$mkovf --resource -f "$f" --id MyLampService \
   --caption "SCSI Controller 0 - LSI Logic" --description "SCSI" --resourceID 4 \
   --resourceSubtype LsiLogic --resourceType 6 --elementName "SCSI controller"

$mkovf --resource -f "$f" --id MyLampService --caption "Harddisk 1" \
   --description "Harddisk" --hostResource "ovf://disk/lamp" --resourceID 5 \
   --parent 4 --resourceType 17 --elementName "Hard Disk"

echo "wrote to ${f}"

