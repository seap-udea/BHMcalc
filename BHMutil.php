<?
/*
###################################################
#  ____  _    _ __  __           _      
# |  _ \| |  | |  \/  |         | |     
# | |_) | |__| | \  / | ___ __ _| | ___ 
# |  _ <|  __  | |\/| |/ __/ _` | |/ __|
# | |_) | |  | | |  | | (_| (_| | | (__ 
# |____/|_|  |_|_|  |_|\___\__,_|_|\___|
# v2.0
###################################################
# 2014 [)] Jorge I. Zuluaga, Viva la BHM!
###################################################
# UTILITARY FUNCTIONS
###################################################
*/
include_once("web/BHM.php");
?>

<?PHP
if(false){}
////////////////////////////////////////////////////
//GENERATE MASTER LINK
////////////////////////////////////////////////////
else if($ACTION=="MasterLink"){
  if(!is_dir($SESSDIR)){$source_dir=$SYSDIR."template/";}
  else{$source_dir=$SYSDIR."$SESSID/";}
  loadConfiguration("$source_dir/star1.conf","star1");
  loadConfiguration("$source_dir/star2.conf","star2");
  loadConfiguration("$source_dir/binary.conf","binary");
  loadConfiguration("$source_dir/hz.conf","hz");
  loadConfiguration("$source_dir/rotation.conf","rotation");
  loadConfiguration("$source_dir/planet.conf","planet");
  loadConfiguration("$source_dir/interaction.conf","interaction");
  $masterlink="?LOADCONFIG&$PARSE_STRING";
  echo<<<LINK
<a href="$masterlink" target="_blank">Copy this link</a>
SYS=$binary_str_sys<br/>
<div style="width:300px;overflow:auto">$masterlink</div>
LINK;
}
////////////////////////////////////////////////////
//GENERATE MASTER LINK
////////////////////////////////////////////////////
else if($ACTION=="CommandLine"){
  if(!is_dir($SESSDIR)){$source_dir=$SYSDIR."template/";}
  else{$source_dir=$SYSDIR."$SESSID/";}
  loadConfiguration("$source_dir/star1.conf","star1");
  loadConfiguration("$source_dir/star2.conf","star2");
  loadConfiguration("$source_dir/binary.conf","binary");
  loadConfiguration("$source_dir/hz.conf","hz");
  loadConfiguration("$source_dir/rotation.conf","rotation");
  loadConfiguration("$source_dir/planet.conf","planet");
  loadConfiguration("$source_dir/interaction.conf","interaction");

  $id=md5($PARSE_STRING);
  $sessdir="$TMPDIR$id";
  $cmd="$PYTHONCMD BHMrun.py BHMinteraction.py $sessdir \"CONFIG:$PARSE_STRING\"";
  echo $cmd;
}
////////////////////////////////////////////////////
//DEFAULT BEHAVIOR
////////////////////////////////////////////////////
else{
  echo "<i>Unrecognized option</i>";
}
?>
