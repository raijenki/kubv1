hostname=$(cat /etc/hostname)
delimiter="-"
IFS="$delimiter" read -ra parts <<< "$hostname"
number=${parts[-1]}

picfile="/data/gem/" $number "/" $number ".inp" 
./sputniPIC $picfile
