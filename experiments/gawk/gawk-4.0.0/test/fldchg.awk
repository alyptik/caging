{
#	print "0:", $0
	gsub("aa", "+")
	print "1:", $0
	$3 = "<" $3 ">"
	print "2:", $0
	print "2a:" "%" $1 "%" $2 "%" $3 "%" $4 "%" $5
}