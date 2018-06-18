
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
<head>
<title>test Browser Identifikation</title>
</head>
<body>

<?PHP
echo $_SERVER['HTTP_USER_AGENT'] . "\n\n";

$browser = get_browser(null, true);
print"<pre>";
print_r($browser);
print"</pre>";

?>

</body>
</html>