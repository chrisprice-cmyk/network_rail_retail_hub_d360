
communityName=$1
urlPrefix=$2
templateName=$3
desc=$4
communityCreated=false

sfdx force:data:record:get -s Network -w "Name='$communityName'" > testingCommunityExists.txt

if [ -s testingCommunityExists.txt ]; then
  echo 'The '$communityName' already exists...'
else
  echo 'The '$communityName' does not exist so I will create it...'
  sfdx force:community:create --name "$communityName" --urlpathprefix $urlPrefix --templatename "$templateName" --description "$desc"

  while [ "$communityCreated" = false ]; do
    echo 'pausing for 10 seconds while the community creates it self...'
    sleep 10

    sfdx force:data:record:get -s Network -w "Name='$communityName'" > communityCreated.txt
    if [ -s communityCreated.txt ]; then
      communityCreated=true
      rm communityCreated.txt
      echo 'Community has been created...'
    fi
  done
fi

rm testingCommunityExists.txt
