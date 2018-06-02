<!DOCTYPE HTML>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>IO test</title>
<style>

a{
  text-decoration:none;
}
.mybutton{
  border:1px solid gray;
  border-radius:5px;
  background-color:#efefff;
  min-width:100px;
  max-width:400px;
  height:30px;
  font-size:20px;
  color:black;
  
  margin:5px;
  padding:5px;
  text-align:center;
  vertical-align:middle;
}
</style>
</head>
<body>
<header>
</header>
<div class="cont1">

</div>
<div class="cont2">
<table>
<tr>
<td>Rot</td>
<td><a href="test_io.php?a=s_on&out=29"><div class="mybutton">ON</div></a></td>
<td><a href="test_io.php?a=s_off&out=29"><div class="mybutton">OFF</div></a></td>
</tr>
<tr>
<td>Grün</td>
<td><a href="test_io.php?a=s_on&out=31"><div class="mybutton">ON</div></a></td>
<td><a href="test_io.php?a=s_off&out=31"><div class="mybutton">OFF</div></a></td>
</tr>
<tr>
<td>Blau</td>
<td><a href="test_io.php?a=s_on&out=33"><div class="mybutton">ON</div></a></td>
<td><a href="test_io.php?a=s_off&out=33"><div class="mybutton">OFF</div></a></td>
</tr>
<tr>
<td></td>
<td colspan="2"><a href="test_io.php?a=snapshot"><div class="mybutton">Kamera-snapshot</div></a></td>

</tr>
</table>

</div>

<?php
$action = $_REQUEST['a'];

if ($action == 's_on')
{
	$out = $_REQUEST['out'];
	print "$out AN";
  exec("gpio -1 mode $out out");
  exec("gpio -1 write $out 1");
}
if ($action == 's_off')
{
	$out = $_REQUEST['out'];
	print "$out AUS";
  exec("gpio -1 write $out 0");
}
if ($action == 'snapshot')
{
	$test = exec("raspistill -o /var/www/html/DCIM/temp.jpg -n -t 1 -w 800 -h 600");
	
}
print '<br/><img src="/DCIM/temp.jpg"/>'.$test;
?>

</body>
</html>