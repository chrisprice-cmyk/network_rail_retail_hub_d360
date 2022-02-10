/*
* Brute force script to apply all listed permission sets to all users
* who are part of the listed profiles
* Called from sfdx command line - eg: sfdx force:apex:execute -f scripts/applyPermSets.apex -u SDO
*/
List<String> permSetNames = new List<String>();
List<String> permSetGroupNames = new List<String>();
List<String> profileNames = new List<String>();
List<ID>permSetIDs = new List<ID>();
List<ID>permSetGroupIDs = new List<ID>();
List<ID>profileIDs = new List<ID>();

Map<String, List<ID>> usersPerProfile = new Map<String, List<ID>>();
List<PermissionSetAssignment> permSetAssignments = new List<PermissionSetAssignment>();

/*
 * MAKE YOUR CHANGES BELOW - PUT IN YOUR DESIRED PERM SETS AND PROFILES
*/
//List of permission sets to apply
permSetNames.add('SDO_Tool_Salesforce_Rewind');
permSetNames.add('force__ContactCenterAdmin');
permSetNames.add('SDO_Service_LiveMessage_PSL_Permissions');

//List of permission set groups to apply
permSetGroupNames.add('SDO_Service_All_Permissions');

//List of Profiles to apply all above perm sets to
profileNames.add('System Administrator');
/*
 * ----- DON'T TOUCH ANYTHING BELOW THIS OR YOU'LL BREAK SOMETHING -----
*/


//create mapping of all permSetIds
for (String curPermSetName : permSetNames) {
  try {
    PermissionSet permSet = [SELECT id FROM PermissionSet WHERE Name =: curPermSetName ];
      permSetIDs.add(permSet.ID);
        System.debug('*** Added permset ' + curPermSetName + ' to map with ID ' + permSet.ID);
  } catch (Exception ex) {
      System.debug('ORG MISSING PERMSET: ' + curPermSetName);
  }
}

//create mapping of all permSetGroupIds
for (String curPermSetGroupName : permSetGroupNames) {
  try {
    PermissionSetGroup permSetGroup = [SELECT id FROM PermissionSetGroup WHERE DeveloperName =: curPermSetGroupName ];
      permSetGroupIDs.add(permSetGroup.ID);
        System.debug('*** Added permset group' + curPermSetGroupName + ' to map with ID ' + permSetGroup.ID);
  } catch (Exception ex) {
      System.debug('ORG MISSING PERMSETGROUP: ' + curPermSetGroupName);
  }
}

//create mapping of all Profile IDs
for(String curProfileName : profileNames) {
  try {
    Profile curProfile = [SELECT id FROM Profile WHERE name =: curProfileName];
    profileIDs.add(curProfile.id);
    //System.debug('*** Added Profile ' + curProfileName + ' to profile map with ID ' + curProfile.id);
  } catch (Exception ex){
    System.debug('ORG MISSING PROFILE: ' + curProfileName);
  }
}

// Get all users who are part of a Profile
//Apply each permset to each of them - loop to next profile
for(ID curProfileID : profileIDs) {
  List<User> users = [SELECT id FROM User WHERE ProfileId =: curProfileID AND IsActive = true];

  //Create a perm set assignment for each of the people for each of the perm sets
  PermissionSetAssignment psa;
  PermissionSetAssignment psga;
  for(User curUser : users){
    for(ID curPermSetID : permSetIDs) {
        psa = new PermissionSetAssignment
        (PermissionSetId = curPermSetID, AssigneeId = curUser.ID);
        permSetAssignments.add(psa);
        System.debug('Permset ID ' + curPermSetID + ' to user: ' + curUser.ID);
    }
    for(ID curPermSetGroupID : permSetGroupIDs) {
        psga = new PermissionSetAssignment
        (PermissionSetGroupId = curPermSetGroupID, AssigneeId = curUser.ID);
        permSetAssignments.add(psga);
        System.debug('Permset Group ID ' + curPermSetGroupID + ' to user: ' + curUser.ID);
    }
  }
}

System.debug('*** applyPermSets Script -- About to add ' + permSetAssignments.size() + ' permset/permsetgroup assignments');
try {
  Database.insert(permSetAssignments,false);
} catch (Exception ex) {
  System.debug('Issue inserting permSet Assignments: ' + ex.getMessage());
}
