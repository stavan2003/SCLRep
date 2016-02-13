#!"C:\Strawberry\perl\bin\perl.exe" -w

#use strict;
use warnings;
use Config::Simple;
use CGI;
use CGI::Carp qw ( fatalsToBrowser );
use File::Basename;
use Data::Printer;
use Spreadsheet::Read;
use Text::Template;

my $excel_errors ='';
my $query    = new CGI;
print $query->header('text/html;charset=UTF-8');
open my $handle, '<', 'C:\xampp\cgi-bin\SCL\Structure-Functionality-Type.txt';
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


#print "Entering Main Code..Upload DIR : $upload_dir : @site_functionality :  @site_structure : @site_type\n";

my $book  = ReadData ('C:\Temp_learnings\SCL_10_51_v1.xlsx');
#p $book;
#exit;

my %worksheet;


#print "Worksheets and Index :";
foreach my $key ( keys %{ $book->[0]{sheet} } ) {
	my $val = $book->[0]{sheet}{$key};
	$worksheet{$key} = $val;
	#print "$key ---> $book->[0]{sheet}{$key}\n";
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

if(! exists $worksheet{'Sites'} or ! exists $worksheet{'Duct-details'} or ! exists $worksheet{'NetworkSheet'} ){
	print "<p>Worksheets : NetworkSheet, Sites and Duct-deails are mandatory </p>";
	exit;
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating NetworkSheet ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %networksheetheader = getWorkSheetHeader('NetworkSheet');
my @bandrules = ('C 72Chs 50 GHz(-2dBm/Ch)','C 80Chs 50 GHz(+1dBm/Ch)','C 80Chs 50 GHz(-2dBm/Ch)','Ch 96Chs 50 GHz(+1dBm/Ch)');
my $error = 0;
my $excel_sheet_errors = '';
for (my $row=2; $row <= $book->[ $worksheet{'NetworkSheet'} ]{maxrow} ; $row++){
	my $cBandRules = $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'CBandRules'}][$row];
	my $found = 0;
	foreach(@bandrules) {
		if($cBandRules eq $_){
			$found = 1;			
		}
	}
	if ( ! $found ) {
		#print "<p>Row #: $row	Error:	Band Rules $cBandRules is not defined\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Band Rules  $cBandRules is not defined</p>";
		$error = 1;
	}	
}
if($error){
	$excel_errors = "<section><h2>Network Sheet</h2><section>$excel_sheet_errors</section>";
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sites ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %siteheader = getWorkSheetHeader('Sites');
my %seen ;
my @sites;
$error = 0;
$excel_sheet_errors = '';
for (my $row=2; $row <= $book->[ $worksheet{'Sites'} ]{maxrow} ; $row++){
	#------------------------------------- Verifying no Duplicate Site exists ---------------------------------------------
	my $site = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{site}][$row];
	if ( !$seen{$site} ) {
		push( @sites, $site );
		$seen{$site}++;
	} else {
		#print "<p>Row #: $row	Error:	Site $site is duplicated\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Site $site is duplicated\n</p>";
		$error = 1;
	}
	
	#------------------------------------- Verifying Site Structure is defined ---------------------------------------------
	my $structure = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Structure}][$row];
	if ( ! grep( /^$structure$/, @site_structure ) ) {
		#print "<p>Row #: $row	Error:	Structure Type $structure is not defined\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Structure Type $structure is not defined\n</p>";
		$error = 1;
	}
	
	#------------------------------------- Verifying Site Functionality is defined ---------------------------------------------
	my $functionality = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Functionality}][$row];
	if ( ! grep( /^$functionality$/, @site_functionality ) ) {
		#print "<p>Row #: $row	Error:	Fuctionality $functionality is not defined\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Fuctionality $functionality is not defined\n</p>";
		$error = 1;
	}
	
	#------------------------------------- Verifying Site Type is defined ---------------------------------------------
	my $type = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Type}][$row];
	if ( ! grep( /^$type$/, @site_type ) ) {
		#print "<p>Row #: $row	Error:	Site Type $type is not defined\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Site Type $type is not defined\n</p>";
		$error = 1;
	}
	
	#------------------------------------- Verifying Site Structure-Functionality-Type is defined ---------------------------------------------
	my $str_funct_type = "$structure:$functionality:$type";
	if ( ! grep( /^$str_funct_type$/, @structure_functionality_type ) ) {
		#print "<p>Row #: $row	Error:	Structure_functionality_type $str_funct_type is not defined\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Structure_functionality_type $str_funct_type is not defined\n</p>";
		$error = 1;
	}
	
}

if($error){
	$excel_errors .= "<h2>Site Sheet</h2><section>$excel_sheet_errors</section>";
}

#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sides ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %sidesheader = getWorkSheetHeader('Sides');
$error = 0;
$excel_sheet_errors = '';
for (my $row=2; $row <= $book->[ $worksheet{'Sides'} ]{maxrow} ; $row++){
	my $siteName = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{SiteName}][$row];
	if ( ! grep( /^$siteName$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Site $siteName is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Site $siteName is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}	
}
if($error){
	$excel_errors .= "<h2>Sides Sheet</h2><section>$excel_sheet_errors</section>";
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Demands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %demandsheader = getWorkSheetHeader('Demands');
$error = 0;
$excel_sheet_errors = '';
for (my $row=2; $row <= $book->[ $worksheet{'Demands'} ]{maxrow} ; $row++){
	my $sourceSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Source}][$row];
	if ( ! grep( /^$sourceSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}	
	my $destSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Destination}][$row];
	if ( ! grep( /^$destSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}
}
if($error){
	$excel_errors .= "<h2>Demands Sheet</h2><section>$excel_sheet_errors</section>";
}

#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Duct Details ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %ductheader = getWorkSheetHeader('Duct-details');
$error = 0;
$excel_sheet_errors = '';
for (my $row=2; $row <= $book->[ $worksheet{'Duct-details'} ]{maxrow} ; $row++){
	my $sourceSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcsite}][$row];
	if ( ! grep( /^$sourceSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}	
	my $destSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destsite}][$row];
	if ( ! grep( /^$destSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}

}
if($error){
	$excel_errors .= "<h2>Duct-details Sheet</h2><section>$excel_sheet_errors</section>";
}

#my $errorfiletemplate = 'C:\xampp\htdocs\SCL\Excel-Error.html';
#open my $fh, '<', $errorfiletemplate or die "error opening $filename: $!";
#my $dataerror = do { local $/; <$fh> };
#$dataerror =~ s/EXCEL_ERROR_FILLER/$excel_errors/g;
#print $dataerror;

my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\excelError.tmpl');
print $query->header('text/html;charset=UTF-8');
print $template->fill_in(HASH=> {excelError => $excel_errors}, DELIMITERS => [ '<<@@', '@@>>' ]);

