TAG_NAME=$(git describe --tags --abbrev=0)
TAG_HASH=$(git show-ref -s $TAG_NAME)
echo 'Using Tag: ' $TAG_NAME ' with Hash: ' $TAG_HASH
echo
