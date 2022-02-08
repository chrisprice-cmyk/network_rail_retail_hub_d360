
/**
 * Creates an internal user for engaging with the house keeping mobile app
 * Assumes a file called Mary has been uploaded (into a ContentVersion object)
 * which is used as the users chatter profile picture.
 * Also applies whichever specified Permission sets to the user.
 *
**/

//Make a list of permission sets you want your user to have
// multiple permsets are comma separated in new single quotes eg {'permSetName1','permSetName2'}
// If no perm sets to be applied, set permSetNames = null;
List<String> permSetNames = new List<String>();
//List<String> permSetNames = new List<String>{'tth_Hospitality_Housekeeping','tth_Hospitality_Base'};


//Create your user with the following parameters:
/*
   FirstName, LastName,
   Alias, ProfileName,
   Title,
   ContentVersion Title,
   contactId,
   externalId,
   permSetNames

// Example of creating a new user called Mary Housekeeper
CreateUser(
    'Mary',
    'Housekeeper',
    'mHouse',
    'System Administrator',
    'Housekeeper',
    'Mary',
    '',
    'tthHospUser.001',
    permSetNames
  );
  */


// ******** DO NOT TOUCH ANYTHING FROM HERE DOWN OR YOU WILL BREAK SOMETHING **********

void CreateUser(String FirstName,String LastName,String Alias,
                String ProfileName,String Title,
                String contentVersionTitle, String contactId,
                String externalId, List<String> permSetNames) {

    String fullDomainURL = System.URL.getOrgDomainUrl().toExternalForm();
    Integer HTTPS = 8;
    String emailSuffix = '@example.com';

    String domain = fullDomainURL.subString(HTTPS, fullDomainURL.indexOf('.'));
    String Profile = [SELECT Id,Name FROM Profile Where Name = :ProfileName].Id;
    String EmailAdd = (FirstName + LastName).replaceAll( '\\s+', '');
    String myAlias = Alias;
    Integer maxSize = 8;
    if(myAlias.length() > maxSize ){
        myAlias = myAlias.substring(0, maxSize);
    }
    String newUserName = EmailAdd + '@' + domain + '.demo';

    //check if the user already exists
    User existingUser;
    try {
      existingUser = [SELECT ID from USER where Username =: newUserName];
      System.debug('Mary HouseKeeper user already exists.');
    } catch (Exception ex) {
      existingUser = null;
      System.debug('Mary HouseKeeper user does not exists so she will be created');
    }

    // If a user with that username doesn't exist, then they need to be created
    if ( existingUser == null) {
          User u = new User (
            FirstName = FirstName, LastName = LastName,
            ProfileID = Profile, Title = Title,
            Email = EmailAdd + emailSuffix, Alias = myAlias, Username = newUserName,
            CommunityNickname = myAlias, External_ID__c = externalId,
            LocaleSidKey = 'en_US',
            TimeZoneSidKey = 'GMT',
            LanguageLocaleKey = 'en_US',
            EmailEncodingKey = 'UTF-8'
          );

          // If this user has an associated Contact (for Communities)
          if(!String.isEmpty(contactId)) {
            u.ContactId = contactId;
          }
          insert u;

          // Update the users chatter profile image if the ContentVersion.Title is provided
          if (!String.isEmpty(contentVersionTitle)) {
            GenerateUserImage(u.ID ,contentVersionTitle);
          }

          // Check to see whether there are permission sets that need to be applied to this user
          if (permSetNames != null || !(permSetNames.isEmpty()) ) {
              applyPermSetsToUser(u, permSetNames);
          }

        } // END - if ( existingUser == null)
  } // END - CreateUsers

  void GenerateUserImage(String UserId, String contentVersionTitle){
      ContentVersion doc = [SELECT ID, VersionData FROM ContentVersion WHERE Title = 'Mary' and IsLatest = true LIMIT 1];
      ConnectApi.UserProfiles.setPhoto(null, UserId, new ConnectApi.BinaryInput(doc.VersionData,'image/jpg','user.jpg'));
  } // END - GenerateUserImage


  void applyPermSetsToUser(User user, List<String> permSetNames) {
    List<PermissionSetAssignment> permSetAssignments = new List<PermissionSetAssignment>();
    PermissionSetAssignment psa;

    //create mapping of all permSetIds
    for (String curPermSetName : permSetNames) {
      try {
        PermissionSet permSet = [SELECT id FROM PermissionSet WHERE Name =: curPermSetName ];
          psa = new PermissionSetAssignment(PermissionSetId = permSet.ID, AssigneeId = user.ID);
          permSetAssignments.add(psa);
            //System.debug('*** Added permset ' + curPermSetName + ' to map with ID ' + permSet.ID);
      } catch (Exception ex) {
          //System.debug('ORG MISSING PERMSET: ' + curPermSetName);
      }
    }// END - for permSetNames

    System.debug('*** applyPermSets Script -- About to add ' + permSetAssignments.size() + ' permset assignments for user: ' + user.FirstName + ' ' + user.LastName);
    Database.insert(permSetAssignments,false);
  } // END applyPermSetsToUser
