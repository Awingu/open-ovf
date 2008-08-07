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
$mkovf --efile -f "$f" -i otherLamp -n otherLamp.vmdk -s 20000 --compression gzip \
		--chunksize 150000

$mkovf --disk -f "$f" \
   --info "List of the virtual disks used in the package" \
   -i lamp -c 4294967296 -s 1924967692 --fileRef lamp \
   --format "http://www.vmware.com/specifications/vmdk.html#compressed" \
   --capacity 50000000 --capacityAlloc 150000  -q true
   
$mkovf --disk -f "$f" \
   --info "List of the virtual disks used in the package" \
   -i lamp2 -c 4294967296 -s 1924967692 --fileRef lamp \
   --format "http://www.vmware.com/specifications/vmdk.html#compressed" \
   --capacity 50000000 --capacityAlloc 150000  --parentRef lamp 

$mkovf --net -f "$f" \
   --info "Logical networks used in the package" --networkName "VM Network" \
   -d "The network that the LAMP Service will be available on" --netID 1

$mkovf --deploy -f "$f" \
	--info "Deployment section of the OVF." --configID Typical --infoID 3 \
	--label "Some label to describe the config." --description "description" \
	--default True --labelID 1 --descID 1

$mkovf --vsc -f "$f" \
		--vscID "CollectionOfvVS" --info "This virtual System Collection \
		contain other Virtual Systems." --infoID 4
		
$mkovf --resAlloc -f "$f" --secID resAlloc1 \
		--info "Some resources in the VS." --infoID 5 \
		--config "no config" --bound min --id CollectionOfvVS \
		
$mkovf --resource -f "$f" --caption "1 virtual CPU" --id resAlloc1 \
   --description "Number of virtual CPUs" --address "http://www.ibm.com" \
   --resourceID 1 --resourceType 3 --virtualQuantity 1 \
   --elementName "virtual CPU" --addressOnParent "http://www.notIBM.com" \
   --allocUnits MegaBytes --automaticAllocation True --autoDealloc false \
   --connection "A CABLE?" --consVis 1 --hostResource true --limit 5 \
   --mapBehavior 2 --otherResourceType otherRes --parent VirtLamp --poolID 4 \
   --reservation 0 --resourceSubtype "subType" --virtualQuantity 14 \
   --weight 10 --required True --config "some config" --bound min 		

 $mkovf --startup -f "$f" --info "some information about the startup section." \
	--infoID 8 --entityName someEntity --order 3 --startDelay 1 \
	--waitForGuest False --startAction powerOn --stopDelay 0 \
	--stopAction powerOff --id CollectionOfvVS
	
$mkovf --vs -f "$f"  -i MyLampService \
   -m "Single-VM Virtual appliance with LAMP stack" --id CollectionOfvVS \
   --infoID 5
   
$mkovf --license -f "$f" --info "License agreement for the Virtual System." \
	--infoID 6 --agreement "License terms can go in here." --licenseID 1 \
	--id MyLampService
	
$mkovf --virthw -f "$f" --id MyLampService --type vmx-4 --secID hw1 \
   --info "Virtual Hardware Requirements: 256Mb, 1 CPU, 1 disk, 1 nic" \
   --infoID 7 --instanceID 1 --sysID MyLampService --transport iso \
   --description "Description of the virtual hardware section." --type machine
   
 
$mkovf --resource -f "$f" --caption "1 virtual CPU" --id hw1 \
   --description "Number of virtual CPUs" --address "http://www.ibm.com" \
   --resourceID 1 --resourceType 3 --virtualQuantity 1 \
   --elementName "virtual CPU" --addressOnParent "http://www.notIBM.com" \
   --allocUnits MegaBytes --automaticAllocation True --autoDealloc false \
   --connection "A CABLE?" --consVis 1 --hostResource true --limit 5 \
   --mapBehavior 2 --otherResourceType otherRes --parent VirtLamp --poolID 4 \
   --reservation 0 --resourceSubtype "subType" --virtualQuantity 14 \
   --weight 10 --required True --config "some config" --bound min  
   
$mkovf --install -f "$f" --info "This is the install section." \
	--infoID 10 --initBoot 5 --bootStopdelay 9 --id MyLampService
   
$mkovf --product -f "$f" \
   --info "Product customization for the installed Linux system" \
   --comment "Linux component configuration parameters" \
   --product "Linux Distribution X" --productVersion 2.6.3 \
   --classDesc org.linuxdistx --id MyLampService --instance 1
   
$mkovf --property -f "$f" --classDesc org.linuxdistx --instance 1 \
   --key netCoreWmemMaxMB --type string \
   --description "Specify TCP write max buffer size in mega bytes. Default is 16." 
   
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


   
$mkovf --os -f "$f" --id MyLampService --info "Guest Operating System" \
   --description "Linux 2.6.x" --secID 103
   
$mkovf --vs -f "$f" -i AnotherLamp --info "A second Virtual System."\
	 --id CollectionOfvVS
$mkovf --product -f "$f" \
   --info "Product customization for the installed Apache Web Server" \
   --comment "Apache  component configuration parameters" \
   --product "Apache Distribution Y" --productVersion 2.6.6 \
   --classDesc org.apache.httpd --vendor RedHat --fullVersion 3.4.6 \
   --prodURL "http://www.aix.com" --vendorURL "http://www.ibm.com" \
   --appURL "http://somethign"	--id AnotherLamp --instance 2
$mkovf --icon -f "$f" --fileRef someFile.png --height 34 \
	--width 15 --mimeType .png --classDesc org.apache.httpd --instance 2	
	
$mkovf --property -f "$f" --classDesc org.apache.httpd \
   --key httpPort --type int --description "Port number for HTTP requests." \
   --value 80 --userConfig True --instance 2	

$mkovf --category -f "$f" --classDesc org.apache.httpd \
	--category "some category description" --instance 2	
	
$mkovf --property -f "$f" --classDesc org.apache.httpd \
   --key httpsPort  --type int  --userConfig True \
   --description "Port number for HTTPS requests." --value 443 --instance 2	

$mkovf --property -f "$f" --classDesc org.apache.httpd \
   --key startThreads --type int --value 50 --userConfig True \
   --description "Number of threads created on startup." --instance 2	

$mkovf --property -f "$f" --classDesc org.apache.httpd \
   --key minSpareThreads --type int --value 15 --userConfig True \
   --description "Minimum number of idle threads to handle request spikes."  \
   --instance 2	

$mkovf --property -f "$f" --classDesc org.apache.httpd \
   --key maxSpareThreads --type string --value 30 --userConfig True \
   --description "Maximum number of idle threads." --instance 2	

$mkovf --property -f "$f" --classDesc org.apache.httpd \
   --key maxClients --type string --value 256 --userConfig True \
   --description "Limit the number of simultaneous requests that will be served."\
   --instance 2	

$mkovf --product -f "$f" \
   --info "Product customization for  the installed MySql Database Server" \
   --comment "MySQL  component configuration parameters" \
   --product "MySQL Distribution Z" --productVersion 5.0 \
   --classDesc org.mysql.db --id AnotherLamp --instance 3

$mkovf --property -f "$f" --classDesc org.mysql.db \
   --key queryCacheSizeMB --type int --value 32 --userConfig True \
   --description "Buffer to cache repeated queries for faster access" \
   --instance 3

$mkovf --property -f "$f" --classDesc org.mysql.db \
   --key maxConnections --type int --value 500 --userConfig True \
   --description "The number of concurrent connections that can be served." \
   --instance 3

$mkovf --property -f "$f" --classDesc org.mysql.db \
   --key waitTimeout --type int --value 100 --userConfig True \
   --description "Number of seconds to wait before timing out a connection ." \
   --instance 3

$mkovf --product -f "$f" \
   --info "Product customization for the installed PHP  component" \
   --comment "PHP component configuration parameters" \
   --product "PHP Distribution U" --productVersion 5.0 --classDesc net.php \
   --id AnotherLamp --instance 4

$mkovf --property -f "$f" \
   --classDesc net.php --key sessionTimeout --type int \
   --value 5 --userConfig True --instance 4 \
   --description "How many minutes a session has to be idle before it is timed out." 

$mkovf --property -f "$f" --classDesc net.php --key concurrentSessions \
   --type int --value 500 --userConfig True --instance 4 \
   --description "The number of concurrent sessions that can be served." 

$mkovf --property -f "$f" --classDesc net.php --key memoryLimit \
   --type int --value 32 --userConfig True --instance 4 \
   --description "How much memory in megabytes a script can consume before being killed." 

$mkovf --os -f "$f" --id AnotherLamp --info "Guest Operating System" \
   --description "Linux 2.6.x" --secID 103

$mkovf --virthw -f "$f" --id AnotherLamp --type vmx-4 --secID hw2 \
   --info "Virtual Hardware Requirements: 256Mb, 1 CPU, 1 disk, 1 nic"
 
$mkovf --resource -f "$f" --caption "1 virtual CPU" --id hw2 \
   --description "Number of virtual CPUs" \
   --resourceID 1 --resourceType 3 --virtualQuantity 1 --elementName "virtual CPU"

$mkovf --resource -f "$f" --allocUnits MegaBytes --id hw2 \
   --caption "256 MB of memory" --description "Memory Size" \
   --resourceID 2 --resourceType 4 --virtualQuantity 256 \
   --elementName 'Memory'

$mkovf --resource -f "$f" --automaticAllocation True --id hw2 \
   --caption "Ethernet adapter on 'VM Network'" \
   --connection "VM Network" --resourceID 3 --resourceType 10 \
   --elementName "Ethernet adapter" --description 'VM Network?'

$mkovf --resource -f "$f" \
   --caption "SCSI Controller 0 - LSI Logic" --resourceID 4 --id hw2 \
   --resourceSubtype LsiLogic --resourceType 6 --elementName "SCSI controller" \
   --description 'SCI Controller'

$mkovf --resource -f "$f" --caption "Harddisk 1" --id hw2 \
   --hostResource "ovf://disk/lamp" --resourceID 5 --parent 4 \
   --resourceType 17 --elementName "Hard Disk" --description 'HD'
   
$mkovf --annotate -f "$f" --info "Some information." \
	--infoID 11 --annotation "This is an annotation for the vs."\
	--id AnotherLamp
echo "wrote to ${f}"

