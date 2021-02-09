#!/bin/bash


sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'Bathroom1'" > Bathroom1Image.txt
if grep -q "no results" Bathroom1Image.txt
then
  echo 'uploading Bathroom1 image'
  sfdx shane:data:file:upload -f data/prod/images/Bathroom1.jpg
fi
rm Bathroom1Image.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'BusinessSeat1'" > BusinessSeat1.txt
if grep -q "no results" BusinessSeat1.txt
then
  echo 'uploading BusinessSeat1 image'
  sfdx shane:data:file:upload -f data/prod/images/BusinessSeat1.jpg
fi
rm BusinessSeat1.txt


sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'BusinessSeat2'" > BusinessSeat2.txt
if grep -q "no results" BusinessSeat2.txt
then
  echo 'uploading BusinessSeat2 image'
  sfdx shane:data:file:upload -f data/prod/images/BusinessSeat2.jpg
fi
rm BusinessSeat2.txt


sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'BusinessSeat3'" > BusinessSeat3.txt
if grep -q "no results" BusinessSeat3.txt
then
  echo 'uploading BusinessSeat1 image'
  sfdx shane:data:file:upload -f data/prod/images/BusinessSeat3.jpg
fi
rm BusinessSeat3.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'EconomySeat1'" > EconomySeat1.txt
if grep -q "no results" EconomySeat1.txt
then
  echo 'uploading BusinessSeat1 image'
  sfdx shane:data:file:upload -f data/prod/images/EconomySeat1.jpg
fi
rm EconomySeat1.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'EconomySeat2'" > EconomySeat2.txt
if grep -q "no results" EconomySeat2.txt
then
  echo 'uploading EconomySeat2 image'
  sfdx shane:data:file:upload -f data/prod/images/EconomySeat2.jpg
fi
rm EconomySeat2.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'EconomySeat3'" > EconomySeat3.txt
if grep -q "no results" EconomySeat3.txt
then
  echo 'uploading EconomySeat3 image'
  sfdx shane:data:file:upload -f data/prod/images/EconomySeat3.jpg
fi
rm EconomySeat3.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'EconomySeat4'" > EconomySeat4.txt
if grep -q "no results" EconomySeat4.txt
then
  echo 'uploading EconomySeat4 image'
  sfdx shane:data:file:upload -f data/prod/images/EconomySeat4.jpg
fi
rm EconomySeat4.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'Gym1'" > Gym1.txt
if grep -q "no results" Gym1.txt
then
  echo 'uploading Gym1 image'
  sfdx shane:data:file:upload -f data/prod/images/Gym1.jpgdxopen
fi
rm Gym1.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'Pool1'" > Pool1.txt
if grep -q "no results" Pool1.txt
then
  echo 'uploading Pool1 image'
  sfdx shane:data:file:upload -f data/prod/images/Pool1.jpg
fi
rm Pool1.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'Room1'" > Room1.txt
if grep -q "no results" Room1.txt
then
  echo 'uploading Room1 image'
  sfdx shane:data:file:upload -f data/prod/images/Room1.jpg
fi
rm Room1.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'Room2'" > Room2.txt
if grep -q "no results" Room2.txt
then
  echo 'uploading Room2 image'
  sfdx shane:data:file:upload -f data/prod/images/Room2.jpg
fi
rm Room2.txt

sfdx force:data:soql:query -q "select ID from ContentVersion where title = 'Room3'" > Room3.txt
if grep -q "no results" Room3.txt
then
  echo 'uploading Room3 image'
  sfdx shane:data:file:upload -f data/prod/images/Room3.jpg
fi
rm Room3.txt
