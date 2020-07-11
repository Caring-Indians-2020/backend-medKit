#!/bin/bash

SIM=0
BUILD=0
while getopts "sb" OPTION
do
	case $OPTION in
		s)
			echo "Running Simulation"
			SIM=1
			;;
		b)
			echo "Building images"
			BUILD=1
			;;
	esac
done

cd backend-medKit
if [ $BUILD == 0 ]; then
	if [ $SIM == 0 ]; then
		docker-compose up -d
	else
		docker-compose -f docker-compose.simulator.yml up -d
	fi
	cd ..
	cd ivms-mobile-app
	docker-compose up
else
	if [ $SIM == 0 ]; then
		docker-compose up --build -d
	else
            docker-compose -f docker-compose.simulator.yml up --build -d
	fi
	cd ..
	cd ivms-mobile-app
	docker-compose up --build
fi