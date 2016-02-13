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
use File::Copy;
use XML::Compile::Schema;
use XML::LibXML::Reader;

sub getDucts(){
   my @ducts = ();
   my $ductCount = 4;
   
   for (my $count = 0; $count < $ductCount; $count++) {
     $ducts[$count]{Name} = "Duct - ".$count;
     $ducts[$count]{Type} = 'G652-SMF - 28E';
     $ducts[$count]{Source}{Site} = 'SourceSite';
     $ducts[$count]{Source}{Side} = 'A';
     $ducts[$count]{Destination}{Site} = 'SourceSite';
     $ducts[$count]{Destination}{Side} = 'A';
     $ducts[$count]{Length} = '10';
     $ducts[$count]{Loss} = '3.23';
     $ducts[$count]{Pmd} = '3.24';
     $ducts[$count]{CdCBand} = '3.25';
   }
   return \@ducts;
}


my %Config;
Config::Simple->import_from('Config.ini', \%Config);
my $excel_errors ='';

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


my $book  = ReadData ('C:\Users\stshah\Desktop\Verizon\Trials\CTP_Input_Excel_Test2.xlsx');
my %worksheet;


#print "Worksheets and Index :";
foreach my $key ( keys %{ $book->[0]{sheet} } ) {
	my $val = $book->[0]{sheet}{$key};
	$worksheet{$key} = $val;
	#print "$worksheet{$key} = $val\n";
}

sub getWorkSheetHeader {
	my $worksheetName = $_[0];
	my %worksheetHeaderHash = ();
	for (my $col=1; $col <= $book->[ $worksheet{$worksheetName} ]{maxcol} ; $col++){
		my $header = $book->[ $worksheet{$worksheetName} ]{cell}[$col][1];
		$worksheetHeaderHash{$header} = $col;
		#print  "$worksheetHeaderHash{$header} -> $col";
	}
	return %worksheetHeaderHash;
} 

if(! exists $worksheet{'Sites'} or ! exists $worksheet{'Duct-details'} or ! exists $worksheet{'NetworkSheet'} ){
	print "<p>Worksheets : NetworkSheet, Sites and Duct-details are mandatory </p>";
	exit;
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating NetworkSheet ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %networksheetheader = getWorkSheetHeader('NetworkSheet');
my @bandrules = ('C 72Chs 50 GHz(-2dBm/Ch)','C 80Chs 50 GHz(+1dBm/Ch)','C 80Chs 50 GHz(-2dBm/Ch)','C 96Chs 50 GHz(+1dBm/Ch)');
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
	$excel_errors = "<h2>Network Sheet</h2><section>$excel_sheet_errors</section>";
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sites ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %siteheader = getWorkSheetHeader('Sites');
my %seen ;
my @sites = ();
my @sitesXML = ();
my $siteCount = 0;
my %sideTracker; # SiteName --> SidesUsed
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
	
	#------------------------------------------------------ Site Creation XML ---------------------------------------------------------------------
	$sitesXML[$siteCount]{Name} =  $site;
	$sitesXML[$siteCount]{Structure} = $structure;
	$sitesXML[$siteCount]{Functionality} = $functionality;
	if($type ne "Auto") {
		$sitesXML[$siteCount]{Type} = $type;
	}
	if(exists($siteheader{Chassis}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Chassis}][$row] =~ /M15|M6|M2|M12 Chassis/i){
		$sitesXML[$siteCount]{Chassis} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Chassis}][$row];
	}
	if(exists($siteheader{ScalableUptoDegree}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{ScalableUptoDegree}][$row] ne ''){
		$sitesXML[$siteCount]{ScalableUptoDegree} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{ScalableUptoDegree}][$row];
	}
	if(exists($siteheader{EvolvedMesh}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{EvolvedMesh}][$row] =~ /Yes|No/i){
		$sitesXML[$siteCount]{EvolvedMesh} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{EvolvedMesh}][$row];
	}
	$sideTracker{$site} = 0;
	$siteCount++;
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
	#------------------------------------------------------ Side Creation XML ---------------------------------------------------------------------
	
	for (my $count= 0; $count< scalar @sitesXML; $count++) {
		if($sitesXML[$count]{Name} eq $siteName) {
			if(exists($sidesheader{ContentionlessSides}) and defined $book->[ $worksheet{'Sides'}]{cell}[$sidesheader{ContentionlessSides}][$row]){
				my @contSides = split /,/,$book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ContentionlessSides}][$row];
				foreach (@contSides) {
					my %side;
					$side{Name} = $_;
					$side{ContentionlessSide} = "Yes";
					if(exists($sidesheader{ColorlessPorts}) and $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ColorlessPorts}][$row] ne ''){
						$side{ColorlessPorts} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ColorlessPorts}][$row];
					}
					if(exists($sidesheader{Colorless100GPorts}) and $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{Colorless100GPorts}][$row] ne ''){
						$side{Colorless100GPorts} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{Colorless100GPorts}][$row];
					}
					if(exists($sidesheader{ContentionlessSideType}) and $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ContentionlessSideType}][$row] ne ''){
						$side{ContentionlessSideType} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ContentionlessSideType}][$row];
					}
					push @{$sitesXML[$count]{Sides}{Side}}, \%side;
				}
			}
			if(exists($sidesheader{OmniDirectionalSides}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{OmniDirectionalSides}][$row]){
				my @omniSides = split /,/,$book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{OmniDirectionalSides}][$row];
				foreach (@omniSides) {
					my %side;
					$side{Name} = $_;
					$side{OmnidirectionalSide} = "Yes";
					if(exists($sidesheader{ColorlessPorts}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ColorlessPorts}][$row]){
						$side{ColorlessPorts} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ColorlessPorts}][$row];
					}
					if(exists($sidesheader{Colorless100GPorts}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{Colorless100GPorts}][$row]){
						$side{Colorless100GPorts} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{Colorless100GPorts}][$row];
					}
					if(exists($sidesheader{OmniSideType}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{OmniSideType}][$row]){
						$side{OmniSideType} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{OmniSideType}][$row];
					}
					push @{$sitesXML[$count]{Sides}{Side}}, \%side;
				}
			}
		}
	} # End XML Side Creation
	
}
if($error){
	$excel_errors .= "<h2>Sides Sheet</h2><section>$excel_sheet_errors</section>";
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Demands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %demandsheader = getWorkSheetHeader('Demands');
$error = 0;
$excel_sheet_errors = '';
my $p2pCount = 0;
my @p2p = ();
for (my $row=2; $row <= $book->[ $worksheet{'Demands'} ]{maxrow} ; $row++){
	my $sourceSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Source}][$row];
	$p2p[$p2pCount]{Source} = $sourceSite;
	if ( ! grep( /^$sourceSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}	
	
	my $destSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Destination}][$row];
	$p2p[$p2pCount]{Destination} = $destSite;
	if ( ! grep( /^$destSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}
	
	#-------------------------------------------------- Demands XML----------------------------------------------------------------------------
	my $scount = $p2pCount+1;
	$p2p[$p2pCount]{Name} = "Service - $scount - $sourceSite - $destSite";
	 if(exists($demandsheader{Encryption}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Encryption}][$row] =~ /Yes|No/i){
		 $p2p[$p2pCount]{Encryption} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Encryption}][$row];
	 }
	# if(exists($demandsheader{Bypass}) and defined $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Bypass}][$row]){
		# $p2p[$p2pCount]{Bypass} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Bypass}][$row];
	# }
	if(exists($demandsheader{ServiceRate}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ServiceRate}][$row] ne ''){
		$p2p[$p2pCount]{Service} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ServiceRate}][$row];
	}
	if(exists($demandsheader{CardForcing}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{CardForcing}][$row] ne ''){
		$p2p[$p2pCount]{CardForcing} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{CardForcing}][$row];
	}
	if(exists($demandsheader{Protection}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Protection}][$row] ne ''){
		$p2p[$p2pCount]{Protection} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Protection}][$row];
	}
	if(exists($demandsheader{HierarchyType}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{HierarchyType}][$row] ne ''){
		$p2p[$p2pCount]{Hierarchy} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{HierarchyType}][$row];
	}
	if(exists($demandsheader{PresentChannels}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row] ne ''){
		$p2p[$p2pCount]{PresentChannels} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row];
		$p2p[$p2pCount]{ForecastChannels} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row];
	}
	if(exists($demandsheader{ForecastChannels}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ForecastChannels}][$row] ne ''){
		$p2p[$p2pCount]{ForecastChannels} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ForecastChannels}][$row] + $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row];
	}
	if(exists($demandsheader{colorless_src}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_src}][$row] ne ''){
		$p2p[$p2pCount]{SrcColorless} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_src}][$row];
	}
	if(exists($demandsheader{colorless_dest}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_dest}][$row] ne ''){
		$p2p[$p2pCount]{DstColorless} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_dest}][$row];
	}
	if(exists($demandsheader{Omnidirectional_src}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_src}][$row] ne ''){
		$p2p[$p2pCount]{SrcOmniSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_src}][$row];
	}
	if(exists($demandsheader{Omnidirectional_dest}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_dest}][$row] ne ''){
		$p2p[$p2pCount]{DstOmniSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_dest}][$row];
	}
	if(exists($demandsheader{Contentionless_src}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_src}][$row] ne ''){
		$p2p[$p2pCount]{SrcContentionlessSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_src}][$row];
	}
	if(exists($demandsheader{Contentionless_dest}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_dest}][$row] ne ''){
		$p2p[$p2pCount]{DstContentionlessSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_dest}][$row];
	}
	if(exists($demandsheader{PathConstraints}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PathConstraints}][$row] ne ''){
		my @ductConstraints = split /,/,$book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PathConstraints}][$row];
		$p2p[$p2pCount]{PathConstraints}{DuctName} = \@ductConstraints;
	}
	if(exists($demandsheader{SiteConstraints}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{SiteConstraints}][$row] ne ''){
		my @siteConstraints = split /,/,$book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{SiteConstraints}][$row];
		$p2p[$p2pCount]{PathConstraints}{SiteName} = \@siteConstraints;
	}
	
	$p2pCount++;
	
   
}
if($error){
	$excel_errors .= "<h2>Demands Sheet</h2><section>$excel_sheet_errors</section>";
}


#print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Duct Details ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my %ductheader = getWorkSheetHeader('Duct-details');
$error = 0;
$excel_sheet_errors = '';
my @ductsXML = ();
my $ductCount = 0;

my @sideNames = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z");


for (my $row=2; $row <= $book->[ $worksheet{'Duct-details'} ]{maxrow} ; $row++){
	my $sourceSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcsite}][$row];
	$ductsXML[$ductCount]{Source}{Site} = $sourceSite;
	if ( ! grep( /^$sourceSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}
	$sideTracker{$sourceSite} ++;
		
	my $destSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destsite}][$row];
	$ductsXML[$ductCount]{Destination}{Site} = $destSite;
	if ( ! grep( /^$destSite$/, @sites ) ) {
		#print "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$excel_sheet_errors .= "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		$error = 1;
	}
	$sideTracker{$destSite} ++;
	
	#-------------------------------------------------- Ducts XML----------------------------------------------------------------------------
	  
	my $ductNameCount = $ductCount + 1;
	
	if(exists($ductheader{DuctName}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{DuctName}][$row] ne ''){
		$ductsXML[$ductCount]{Name} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{DuctName}][$row];
	} else {
		$ductsXML[$ductCount]{Name} = "Duct - ".$ductNameCount;
	}

	if(exists($ductheader{Type}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Type}][$row] ne ''){
		$ductsXML[$ductCount]{Type} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Type}][$row];
	}
	
	if(exists($ductheader{srcSide}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcSide}][$row] ne ''){
		$ductsXML[$ductCount]{Source}{Side} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Type}][$row];
	} else {
		$ductsXML[$ductCount]{Source}{Side} = $sideNames[$sideTracker{$sourceSite}-1];
		print "$sourceSite : ".$sideNames[$sideTracker{$sourceSite}-1];
	}	
	
	
	if(exists($ductheader{destSide}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destSide}][$row] ne ''){
		$ductsXML[$ductCount]{Destination}{Side} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destSide}][$row];
	} else {
		$ductsXML[$ductCount]{Destination}{Side} = $sideNames[$sideTracker{$destSite}-1];
		print "  $destSite : ". $sideNames[$sideTracker{$destSite}-1]."\n";
	}

	if(exists($ductheader{SpanLength}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{SpanLength}][$row] ne ''){
		$ductsXML[$ductCount]{Length} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{SpanLength}][$row];
	}
	if(exists($ductheader{FiberType}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{FiberType}][$row] ne ''){
		$ductsXML[$ductCount]{Type} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{FiberType}][$row];
	}
	if(exists($ductheader{Loss}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Loss}][$row] ne ''){
		$ductsXML[$ductCount]{Loss} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Loss}][$row];
	}
	if(exists($ductheader{Pmd}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Pmd}][$row] ne ''){
		$ductsXML[$ductCount]{Pmd} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{Pmd}][$row];
	}
	if(exists($ductheader{CdCBand}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{CdCBand}][$row] ne ''){
		$ductsXML[$ductCount]{CdCBand} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{CdCBand}][$row];
	}
	
       $ductCount++;
	

}
if($error){
	$excel_errors .= "<h2>Duct-details Sheet</h2><section>$excel_sheet_errors</section>";
}

if($excel_errors eq ''){
	my $row = 2;
	my $data = { 
		CreatedBy => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'CreatedBy'}][$row],
		Customer => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'CustomerName'}][$row],
		'E-mail' => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'Email'}][$row],
		ProjectName => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'ProjectName'}][$row],
		Platform => "ONS15454",
		MeasurementUnit => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'MeasurementsUnits'}][$row],
		Release => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'MSTPRelease'}][$row],
		Layout => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'NetworkPlatformLayout'}][$row],
		Network => {
			'C-Band-Rule' => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'CBandRules'}][$row],
			'L-Band-Rule' => "None",
			NodeType => $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'NodeType'}][$row],
			Sites => { Site => \@sitesXML,},
			Fibres => { Duct => \@ductsXML,},
			Demands => { PointToPoint => \@p2p,}, 
		}, 
	  };
	my $doc    = XML::LibXML::Document->new('1.0', 'UTF-8');
	my $xsd = 'C:\Users\stshah\Desktop\Verizon\ctp.xsd';
	my $schema = XML::Compile::Schema->new($xsd);
	my %option;
	$option{validation} = 0;
	
	my $write  = $schema->compile(WRITER => 'Project', %option );
	my $xml    = $write->($doc, $data);
	$doc->setDocumentElement($xml);
	
	my $xmlschema = XML::LibXML::Schema->new(location => $xsd);
	eval { $xmlschema->validate( $doc ); };

	if ( my $ex = $@ ) {
		print "XML Generation Failed due to Below Errors :\n";
		print $ex;
	} else {
	 
		print "Printing....document\n";
		#print $doc->toString(1); # 1 indicates "pretty print"
		print "\nEnd print";
		
		my $filename = 'SCL-Result.xml';
		open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
		print $fh $doc->toString(1);
		close $fh;
		print "\nXML Generation Complete : C:\\CTP\\SCL-Result.xml\n";
	}

} else {
	print "ERRORS : $excel_errors\n";

}
