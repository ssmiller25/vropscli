#!/bin/sh
# Supports vrops and linux(ubuntu)

if [ $1 == "vrops" ]
then
    PLATFORM="vrops"
elif [ $1 == "linux" ]
then
    PLATFORM="linux"
else
    echo "Failed to get operating system"
    exit 1
fi

VERSION=`cat vropscli.py | grep 'VERSION=' | cut -b 9- | tr -d '"'`
if [ -z "$VERSION" ]
then
      echo "Failed to get version from vropscli.py"
      exit 1
else
      echo "Building vropscli ${VERSION}"
fi

mkdir -p artifacts

docker build \
    -f Dockerfile.${PLATFORM} \
    --no-cache \
    -t vropscli:vrops-${VERSION} .

docker create -ti --name artifacts vropscli:vrops-${VERSION} bash && \
    docker cp artifacts:/vropscli/dist/vropscli artifacts/vropscli_${PLATFORM}_v${VERSION}

# cleanup
docker rm -fv artifacts &> /dev/null
docker rmi vropscli:vrops-${VERSION}

