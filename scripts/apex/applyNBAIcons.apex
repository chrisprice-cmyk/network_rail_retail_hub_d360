//Work around to line up Recommendation images with ContentAsset metadata of related names
//Required since recommendations are record data whilst the Recommendation image is metadata and is stored via ID
//
//How this Annon APEX works
//Select all the Recommendations ID and Names that do not have an image linked
//Take the Recommendation names, remove all special characters and whitespace and look for a ContentAsset file that has that same name
//Update the Recommendation record to make use of that image
//e.g. if Recommendation name was "Select Super-Sized Meal" this script would look for a content asset with the name SelectSuperSizedMeal

// WHERE ImageID = null
List<Recommendation> recommendations = [SELECT ID, Name, ImageID from Recommendation WHERE ImageID = null];
Map<String,Recommendation> recommendationMap = new Map<String,Recommendation>();
List<String> fileNames = new List<String>();
List<ContentAsset> assetFiles;
List<Recommendation> recsToUpdate = new List<Recommendation>();

for(Recommendation curRec : recommendations) {
  String fileName;
  fileName = curRec.name.replaceAll('[^a-zA-Z0-9\\s+]', '').deleteWhitespace();
  System.debug('******* Recommendation ' + curRec.name + ' is missing an icon. Guessing at ContentAsset name of: ' + fileName);
  recommendationMap.put(fileName, curRec);
  fileNames.add(fileName);
}

if (!fileNames.isEmpty()) {
  System.debug('******* Searching for the following ContentAssets: ' + fileNames);
  assetFiles = [SELECT ID, DeveloperName FROM ContentAsset where DeveloperName in :fileNames];

  for(ContentAsset curContent : assetFiles) {
    Recommendation curRec = recommendationMap.get(curContent.DeveloperName);

    if(curRec != null) {
      curRec.imageId = curContent.ID;
      recsToUpdate.add(curRec);
    }
  }
}

if (!recsToUpdate.isEmpty()) {
  System.debug('Going to update ' + recsToUpdate.size() + ' Recommendations');
  Database.update(recsToUpdate);
}
