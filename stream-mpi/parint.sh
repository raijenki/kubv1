#!/bin/bash

#values=(8 16 32 48 64)
values=(16 64)
scenarios=(90 150 210 320 530 740) 

for val in "${values[@]}"
do
	sed -i "s/#define NLOOP [0-9]\+/#define NLOOP $val/" stream_mpi.c 
	git add .
	git commit -m "auto update nloop"
	git push
	docker build . --tag=raijenki/mpik8s:smpi --no-cache
	docker push raijenki/mpik8s:smpi
	for scen in "${scenarios[@]}"
	do
	if [ $scen -lt 300 ]
	then
		for i in 1 2 3
		do
		echo "STARTING $val - Trial $i - Base $scen" >> parint_2to6ranks_16.txt 
		kubectl create -f smpi.yaml
		sleep $scenarios
		kubectl create -f scheduler.yaml
		sleep 900
		kubectl describe job.batch.volcano.sh >> parint_2to6ranks_16.txt 
		kubectl delete -f smpi.yaml -f scheduler.yaml
		sleep 10
		echo "FINISHED" >> parint_2to6ranks_16.txt
		done
	fi
	if [ $scen -gt 300 ]
	then
		for i in 1 2 3
		do
		echo "STARTING $val - Trial $i - Base $scen" >> parint_2to6ranks_64.txt 
		kubectl create -f smpi.yaml
		sleep $scenarios
		kubectl create -f scheduler.yaml
		sleep 900
		kubectl describe job.batch.volcano.sh >> parint_2to6ranks_64.txt 
		kubectl delete -f smpi.yaml -f scheduler.yaml
		sleep 10
		echo "FINISHED" >> parint_2to6ranks_64.txt
		done
	fi
	done
done
