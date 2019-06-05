#!/bin/sh
# Supports all linux (includs vrops)

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
    --no-cache \
    -t vropscli:linux-${VERSION} .

docker create -ti --name artifacts vropscli:linux-${VERSION} bash && \
    docker cp artifacts:/vropscli/dist/vropscli artifacts/vropscli_linux_v${VERSION}

# cleanup
docker rm -fv artifacts &> /dev/null
docker rmi vropscli:linux-${VERSION}
