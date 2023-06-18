#!/bin/bash

#values=(8 16 32 48 64)
values=(16 64)

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
	if [ $val -eq 16 ]
	then
		for i in 1 2 3
		do
		echo "STARTING $val - Trial $i" >> parint_6ranks.txt 
		kubectl create -f smpi.yaml
		kubectl create -f scheduler.yaml
		sleep 200
		kubectl describe job.batch.volcano.sh >> parint_6ranks.txt 
		kubectl delete -f smpi.yaml
		sleep 10
		echo "FINISHED" >> parint_6ranks.txt
		done
	fi
	if [ $val -eq 64 ]
	then
		for i in 1 2 3
		do
		echo "STARTING $val - Trial $i" >> parint_6ranks.txt 
		kubectl create -f smpi.yaml
		sleep 400
		kubectl describe job.batch.volcano.sh >> parint_6ranks.txt 
		kubectl delete -f smpi.yaml
		sleep 10
		echo "FINISHED" >> parint_6ranks.txt
		done
	fi
	done
done
