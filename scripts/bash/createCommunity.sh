
communityName=$1
urlPrefix=$2
templateName=$3
desc=$4

rm testingCommunityExists.txt
sfdx force:data:record:get -s Network -w "Name="$communityName > testingCommunityExists.txt

if [ -s testingCommunityExists.txt ]; then
  echo 'The '$communityName' does not exist so I will create it...'
  sfdx force:community:create --name "$communityName" --urlpathprefix $urlPrefix --templatename "$templateName" --description "$desc"
else
  echo 'The '$communityName' already exists...'
fi

rm testingCommunityExists.txt


echo 'pausing for 10 seconds while the community creates it self...'
sleep 10
