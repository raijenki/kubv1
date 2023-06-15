#!/bin/bash

values=(8 16 32 48 64 128)

for val in "${values[@]}"
do
	sed -i "s/#define NLOOP [0-9]\+/#define NLOOP $val/" stream_mpi.c 
	git add .
	git commit -m "update nloop"
	git push
	docker build . --tag=raijenki/mpik8s:smpi --no-cache
	docker push raijenki/mpik8s:smpi
	for i in 1 2 3
	do
		echo "STARTING $val - Trial $i" >> parint.txt 
		kubectl create -f smpi-vanilla.yaml
		sleep 900
		kubectl describe job.batch.volcano.sh >> parint.txt 
		kubectl delete -f smpi-vanilla.yaml
		sleep 15
		echo "FINISHED" >> parint.txt
	done
done
