
communityName=$1
urlPrefix=$2
templateName=$3
desc=$4

sfdx force:data:record:get -s Network -w "Name='$communityName'" > testingCommunityExists.txt

if [ -s testingCommunityExists.txt ]; then
  echo 'The '$communityName' already exists...'
else
  echo 'The '$communityName' does not exist so I will create it...'
  sfdx force:community:create --name "$communityName" --urlpathprefix $urlPrefix --templatename "$templateName" --description "$desc"

  echo 'pausing for 10 seconds while the community creates it self...'
  sleep 10
fi

rm testingCommunityExists.txt
