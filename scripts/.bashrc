
function dxlogout() {
   sfdx force:auth:logout -p -u $1
}

function dxpush() {
   sfdx force:source:push $@
}

function dxpull() {
   sfdx force:source:pull $@
}

function dxopen() {
   sfdx force:org:open $@
}

function dxstatus() {
   sfdx force:source:status $@
}

function packlist() {
   sfdx force:package:version:list $@
}

function orglist() {
   sfdx force:org:list --all
}

function packlist() {
  sfdx force:package:version:list $@
}

function orglist() {
   sfdx force:org:list --all
}

function cscratch() {
   sfdx force:org:create --wait 120 -d 25 -s -f config/project-scratch-def.json -a $@
   sfdx shane:user:password:set -p Demo1234 -g User -l User
   sfdx force:org:display --verbose -u $@
}

function dscratch() {
   sfdx force:org:delete --noprompt -u $@
}

function defscratch() {
   sfdx force:config:set defaultusername=$@
}

function dxclass() {
   sfdx force:apex:class:create -n $@
}

function dxaura() {
    sfdx force:lightning:component:create --type aura -n $@
}

function dxlwc() {
   sfdx force:lightning:component:create --type lwc -n $@
}

function dxapp() {
   sfdx force:lightning:app:create -n $@
}

function dxtrigger() {
   sfdx force:apex:trigger:create -n $1 -s $2 -e 'before insert,before update,before delete, after insert, after updatae, after delete'
}

function dxinstallpack() {
   sfdx force:package:install -w 1000 --package $@
}

function dxauthorg() {
   sfdx force:auth:web:login -a $@
}

function dxsand() {
   read -p 'Sandbox Alias: ' orgAlias
   read -p 'Prod Alias: ' prodAlias
   sfdx force:org:create -t sandbox sandboxName=$orgAlias licenseType=Developer -u $prodAlias -a $orgAlias -w 1000

}

function dxdeforg() {
   read -p 'Default Alias: ' orgAlias
   sfdx force:config:set defaultusername=$orgAlias
}

function dxMakeCert(){
  # Taken from https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_key_and_cert.htm
  # on how to make a Private Key and Self-signed Digital Certificate

  read -p 'Enter a password for the certs: ' certPass
  read -p 'Enter certificate Name (no spaces): ' certName

  openssl genrsa -des3 -passout pass:$certPass -out server.pass.key 2048
  openssl rsa -passin pass:$certPass -in server.pass.key -out $certName.key

  rm server.pass.key

  openssl req -new -key $certName.key -out $certName.csr
  openssl x509 -req -sha256 -days 365 -in $certName.csr -signkey $certName.key -out $certName.crt
}
