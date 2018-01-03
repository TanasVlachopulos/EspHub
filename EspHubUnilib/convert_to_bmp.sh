#!/bin/bash

if [[ -z $1 ]]; then
	echo "Missing path to folder with images"
	exit 1
fi

((counter=0))

for file in $(ls $1)
do
	#echo $1$file
	((counter=counter+1))
	printf -v out "%05d" $counter
	convert $1$file -colors 2 +dither -type bilevel $1$out.bmp
	rm $1$file
done

echo "Successfully converted $counter images."

