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
# DATA INSTALL
###################################################
TMPDIR="/tmp"
if [ ! -d BHM/data/Stars ]
then
    echo "Reconstructing data tarball..."
    cat BHM/.data/data_* > /tmp/BHMdata.tgz
    echo "Unpacking data into data directory..."
    tar zxf /tmp/BHMdata.tgz -C BHM/
else
    echo "Data already unpacked."
fi

if [ ! -e "web/BHMprotect.php" ]
then echo "<?php define('USE_USERNAME',false); define('LOGOUT_URL', 'http://www.example.com/'); define('TIMEOUT_MINUTES', 0); define('TIMEOUT_CHECK_ACTIVITY', true); shell_exec(\"hostname > $TMPDIR/host\");  shell_exec(\"md5sum $TMPDIR/host | cut -f 1 -d ' ' > $TMPDIR/md5\");  \$md5=substr(rtrim(shell_exec(\"cat $TMPDIR/md5\")),0,7); shell_exec(\"echo 'BHM\$md5' > $TMPDIR/\$md5\"); shell_exec(\"rm $TMPDIR/host $TMPDIR/md5\");  \$LOGIN_INFORMATION = array(\$md5);  \$timeout = (TIMEOUT_MINUTES == 0 ? 0 : time() + TIMEOUT_MINUTES * 60); if(isset(\$_GET['logout'])) {   setcookie(\"verify\", '', \$timeout, '/');    header('Location: ' . LOGOUT_URL);   exit(); } if(!function_exists('showLoginPasswordProtect')) { function showLoginPasswordProtect(\$error_msg) { ?> <html> <head>   <title>Please enter password to access this page</title>   <META HTTP-EQUIV=\"CACHE-CONTROL\" CONTENT=\"NO-CACHE\">   <META HTTP-EQUIV=\"PRAGMA\" CONTENT=\"NO-CACHE\"> </head> <body>   <style>     input { border: 1px solid black; }   </style>   <div style=\"width:500px; margin-left:auto; margin-right:auto; text-align:center\">   <form method=\"post\">     <h3>Please enter password to access this page</h3>     <font color=\"red\"><?php echo \$error_msg; ?></font><br /> <?php if (USE_USERNAME) echo 'Login:<br /><input type=\"input\" name=\"access_login\" /><br />Password:<br />'; ?>     <input type=\"password\" name=\"access_password\" /><p></p><input type=\"submit\" name=\"Submit\" value=\"Submit\" />   </form>   <br />   <a style=\"font-size:9px; color: #B0B0B0; font-family: Verdana, Arial;\" href=\"http://www.zubrag.com/scripts/password-protect.php\" title=\"Download Password Protector\">Powered by Password Protect</a>   </div> </body> </html> <?php   die(); } } if (isset(\$_POST['access_password'])) {   \$login = isset(\$_POST['access_login']) ? \$_POST['access_login'] : '';   \$pass = \$_POST['access_password'];   if (!USE_USERNAME && !in_array(\$pass, \$LOGIN_INFORMATION)   || (USE_USERNAME && ( !array_key_exists(\$login, \$LOGIN_INFORMATION) || \$LOGIN_INFORMATION[\$login] != \$pass ) )    ) {     showLoginPasswordProtect(\"Incorrect password.\");   }   else {     setcookie(\"verify\", md5(\$login.'%'.\$pass), \$timeout, '/');     unset(\$_POST['access_login']);     unset(\$_POST['access_password']);     unset(\$_POST['Submit']);   } } else {   if (!isset(\$_COOKIE['verify'])) {     showLoginPasswordProtect(\"\");   }   \$found = false;   foreach(\$LOGIN_INFORMATION as \$key=>\$val) {     \$lp = (USE_USERNAME ? \$key : '') .'%'.\$val;     if (\$_COOKIE['verify'] == md5(\$lp)) {       \$found = true;       if (TIMEOUT_CHECK_ACTIVITY) {         setcookie(\"verify\", md5(\$lp), \$timeout, '/');       }       break;     }   }   if (!\$found) {     showLoginPasswordProtect(\"\");   } } ?> " > web/BHMprotect.php 
fi 