#!/bin/sh

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
    -t vropscli:vrops-${VERSION} .

docker create -ti --name artifacts vropscli:vrops-${VERSION} bash && \
    docker cp artifacts:/vropscli/dist/vropscli artifacts/vropscli_vrops_v${VERSION}

# cleanup
docker rm -fv artifacts &> /dev/null
docker rmi vropscli:vrops-${VERSION}
