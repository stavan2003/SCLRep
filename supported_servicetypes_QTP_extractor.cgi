#!"C:\Strawberry\perl\bin\perl.exe" -w

#use strict;
use warnings;
use Config::Simple;
use File::Basename;
use Data::Printer;
use Spreadsheet::Read;
use File::Copy;



my $book  = ReadData ('C:\ServiceTypeQTP\Temp_10G.xls');
#p $book;

my %worksheet;


#print "Worksheets and Index :";
foreach my $key ( keys %{ $book->[0]{sheet} } ) {
	my $val = $book->[0]{sheet}{$key};
	$worksheet{$key} = $val;
}

sub getWorkSheetHeader {
	my $worksheetName = $_[0];
	my %worksheetHeaderHash = ();
	for (my $col=1; $col <= $book->[ $worksheet{$worksheetName} ]{maxcol} ; $col++){
		my $header = $book->[ $worksheet{$worksheetName} ]{cell}[$col][1];
		$worksheetHeaderHash{$header} = $col;
	}
	return %worksheetHeaderHash;
} 
sub  trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

my %networksheetheader = getWorkSheetHeader('Global');
for (my $row=2; $row <= $book->[ $worksheet{'Global'} ]{maxrow} ; $row++){
	my $txpType = '';
	$txpType = $book->[ $worksheet{'Global'} ]{cell}[$networksheetheader{'Header'}][$row];
	next if $book->[ $worksheet{'Global'} ]{cell}[$networksheetheader{'Header'}][$row] eq '';
	my $servicetypeDetail = $book->[ $worksheet{'Global'} ]{cell}[$networksheetheader{'ServiceType'}][$row];
	my $cardTypeDetail = $book->[ $worksheet{'Global'} ]{cell}[$networksheetheader{'CardType'}][$row];
	if (my ($traffictype, $protection, $inteface, $hierarcy) = $servicetypeDetail =~ /Traffic type :(.*)\nProtections :(.*)\nInterfaces :(.*)\nHierarchy:(.*)/m){
		#print "Matched\n";
		#print "$1 , $2, $3, $4";
		#print "$txpType, $traffictype, $protection, $inteface, $hierarcy\n";
		my @interfaces = ();
		my @protections = ();
		my @internal_name = ();
		if(! $inteface eq '') {
			@interfaces = split(/ /, $inteface);
		} 
		if(! $protection eq '') {
			@protections = split(/ /, $protection);
		}
		if(! $hierarcy eq '') {
			@internal_name = split(/:/,$hierarcy);
			$internal_name[0] = trim($internal_name[0]);
		}
		
		foreach my $prots (@protections){
			if(scalar @interfaces == 0){
				print "$traffictype,$cardTypeDetail,$txpType,$prots,,$internal_name[0]\n"; 
			} else {
				foreach my $int (@interfaces) {
					next if $int =~ /BackPane/i;
					print "$traffictype,$cardTypeDetail,$txpType,$prots,$int,$internal_name[0]\n";
				}
			}
			
		}
	}

}