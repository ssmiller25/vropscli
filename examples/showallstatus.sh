#!/bin/sh
./vropscli getAdapters | grep -v "id," | while read line; do 
    UUID=$(echo $line | cut -f1 -d,)
    NAME=$(echo $line | cut -f2 -d,)
    echo ${NAME}
    ./vropscli getAdapterCollectionStatus $UUID
    echo ""
done
