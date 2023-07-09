# pic pods are in format pic-worker-X, where X is related to the input it should read
hostname=$(cat /etc/hostname)
delimiter="-"
IFS="$delimiter" read -ra parts <<< "$hostname"
number=${parts[-1]}
picfile="/data/gem/$number/$number.inp" 
./sputniPIC "$picfile"
