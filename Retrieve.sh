#! /bin/perl

if (@ARGV < 1)
{	
	printf("Usage Retrieve.sh [filename] [RecNumber] \n"); 
	exit -1;
}
$i=0;

#文件名
$FileName=$ARGV[0];

$NewFileName="$FileName.Rand";

#文件行数 
$CommdResult=qx{wc -l $FileName};
chomp($CommdResult);
@Tmp=split(/\s+/, $CommdResult);
$FileLine=$Tmp[1];

open(FILEHANDLE, ">$NewFileName") or die "fail to open $NewFileName";

#需要的记录个数
$i=0;
$RecNum=$ARGV[1];
print "REc is $RecNum \n";

my $numbers = GenRandomNumber($FileLine, $RecNum);

open HANDLE, "<$FileName" or die "can't read [$FileName]";
my $lineno = 0;
while (<HANDLE>)
{
	++$lineno;
	print FILEHANDLE $_ if (defined $numbers->{$lineno});
}
close HANDLE;
close FILEHANDLE;




sub GenRandomNumber
{
	my ($max, $cnt) = @_;
	my %numbers = ();
	while (scalar keys %numbers < $cnt)
	{
		my $RandLineNO=int(rand($FileLine)) + 1;
		$numbers{$RandLineNO}++;
	}
	return {%numbers};
}









