#!/usr/bin/perl
use Data::Printer;
use Spreadsheet::Read;

open my $handle, '<', "Structure-Functionality-Type.txt";
chomp(my @structure_functionality_type = <$handle>);
close $handle;

my @site_functionality =();
my @site_structure = () ;
my @site_type = ();

foreach(@structure_functionality_type){
	my ($structure, $functionality, $type) = split(/:/);
	if ( ! grep( /^$functionality$/, @site_functionality ) ) {
		push(@site_functionality, $functionality);
	}
	if ( ! grep( /^$structure$/, @site_structure ) ) {
		push(@site_structure, $structure);
	}
	if ( ! grep( /^$type$/, @site_type ) ) {
		push(@site_type, $type);
	}
}

print "Site Structure : @site_structure\n";
print "Site Types : @site_type\n";
print "Site Functionalities : @site_functionality\n";
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";

print "Entering Main Code..";

my $book  = ReadData ('C:\Temp_learnings\SCL_10_51_v1.xlsx');
#my $book = ReadData('C:\Temp\Sample.xlsx');

#p $book;
#exit;

my %worksheet;


print "Worksheets and Index :";
foreach $key ( keys %{ $book->[0]{sheet} } ) {
	my $val = $book->[0]{sheet}{$key};
	$worksheet{$key} = $val;
	print "$key ---> $book->[0]{sheet}{$key}\n";
}




sub getWorkSheetHeader {
	my $worksheetName = $_[0];
	print "Creating headers for $worksheetName\n";
	my %worksheetHeaderHash = ();
	for (my $col=1; $col <= $book->[ $worksheet{$worksheetName} ]{maxcol} ; $col++){
		my $header = $book->[ $worksheet{$worksheetName} ]{cell}[$col][1];
		$worksheetHeaderHash{$header} = $col;
		print "$header ";
	}
	print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
	return %worksheetHeaderHash;
} 


print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sites ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %siteheader = getWorkSheetHeader('Sites');
my %seen ;
my @sites;
for (my $row=2; $row <= $book->[ $worksheet{'Sites'} ]{maxrow} ; $row++){
	
	#------------------------------------- Verifying no Duplicate Site exists ---------------------------------------------
	my $site = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{site}][$row];
	if ( !$seen{$site} ) {
		push( @sites, $site );
		$seen{$site}++;
	} else {
		print "Sheet : Sites 	Row #: $row	Error:	Site $site is duplicated\n";
	}
	
	#------------------------------------- Verifying Site Structure is defined ---------------------------------------------
	my $structure = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Structure}][$row];
	if ( ! grep( /^$structure$/, @site_structure ) ) {
		print "Sheet : Sites 	Row #: $row	Error:	Structure Type $structure is not defined\n";
	}
	
	#------------------------------------- Verifying Site Functionality is defined ---------------------------------------------
	my $functionality = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Functionality}][$row];
	if ( ! grep( /^$functionality$/, @site_functionality ) ) {
		print "Sheet : Sites 	Row #: $row	Error:	Fuctionality $functionality is not defined\n";
	}
	
	#------------------------------------- Verifying Site Type is defined ---------------------------------------------
	my $type = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Type}][$row];
	if ( ! grep( /^$type$/, @site_type ) ) {
		print "Sheet : Sites 	Row #: $row	Error:	Site Type $type is not defined\n";
	}
	
	#------------------------------------- Verifying Site Structure-Functionality-Type is defined ---------------------------------------------
	my $str_funct_type = "$structure:$functionality:$type";
	if ( ! grep( /^$str_funct_type$/, @structure_functionality_type ) ) {
		print "Sheet : Sites 	Row #: $row	Error:	Structure_functionality_type $str_funct_type is not defined\n";
	}
	
}

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sides ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %sidesheader = getWorkSheetHeader('Sides');
for (my $row=2; $row <= $book->[ $worksheet{'Sides'} ]{maxrow} ; $row++){
	my $siteName = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{SiteName}][$row];
	if ( ! grep( /^$siteName$/, @sites ) ) {
		print "Sheet : Sides 	Row #: $row	Error:	Site $siteName is not defined in 'Sites' Sheet\n";
	}	
}

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Demands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %demandsheader = getWorkSheetHeader('Demands');
for (my $row=2; $row <= $book->[ $worksheet{'Demands'} ]{maxrow} ; $row++){
	my $sourceSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Source}][$row];
	if ( ! grep( /^$sourceSite$/, @sites ) ) {
		print "Sheet : Sides 	Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n";
	}	
	my $destSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Destination}][$row];
	if ( ! grep( /^$destSite$/, @sites ) ) {
		print "Sheet : Sides 	Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n";
	}
}

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Duct Details ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %ductheader = getWorkSheetHeader('Duct-details');
for (my $row=2; $row <= $book->[ $worksheet{'Duct-details'} ]{maxrow} ; $row++){
	my $sourceSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcsite}][$row];
	if ( ! grep( /^$sourceSite$/, @sites ) ) {
		print "Sheet : Sides 	Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n";
	}	
	my $destSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destsite}][$row];
	if ( ! grep( /^$destSite$/, @sites ) ) {
		print "Sheet : Sides 	Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n";
	}

}

#my %ductheader = getWorkSheetHeader('Duct-details');

