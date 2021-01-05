function dxpush() {
if [$# -eq 0 ];
   then
      sfdx force:source:push
   else
      sfdx force:source:push -u $@
fi
}

function dxpull() {
if [ $# -eq 0 ];
then
    sfdx force:source:pull
else
    sfdx force:source:pull -u $@
fi
}

function dxopen() {
if [ $# -eq 0 ];
then
   sfdx force:org:open
else
   sfdx force:org:open -u $@
fi
}

function dxstatus() {
if [ $# -eq 0 ];
then
   sfdx force:source:status
else
   sfdx force:source:status -u $@
fi
}

function packlist() {
  sfdx force:package:version:list $@
}

function orglist() {
   sfdx force:org:list --all
}

function cscratch() {
   sfdx force:org:create -s -f config/project-scratch-def.json -a $@
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
