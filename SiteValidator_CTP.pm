#!"C:\Strawberry\perl\bin\perl.exe" -w
package SiteValidator_CTP;
use strict;
use Exporter;
use SCL_EXCEL;
use Validator_CTP;our @ISA= qw( Exporter );
our @EXPORT = qw(@sites @sitesXML %sideTracker);

our (@sites, @sitesXML, %sideTracker); # { SiteName --> SidesUsed }

our ($functionality_ref, $structure_ref, $type_ref, $structure_functionality_type_ref);

sub test {
	
	print "Book in SiteValidator : ".$book->[ 2 ]{maxrow}."\n";
	return 1;}

sub validateSiteDetails {
	
	my %siteheader = %{$_[0]};
	my %seen;
	my $siteCount = 0;
	
	my $excel_sheet_errors = '';
	for (my $row=2; $row <= $book->[ $worksheet{Sites} ]{maxrow} ; $row++){
		#------------------------------------- Verifying no Duplicate Site exists ---------------------------------------------
		
		my $site = $book->[ $worksheet{Sites} ]{cell}[$siteheader{site}][$row];
		if ( !$seen{$site} ) {
			$site =~ s/^\s+|\s+$//g;
			push( @sites, $site );
			$seen{$site}++;
		} else {
			$excel_sheet_errors .=  SCL_EXCEL::get_ExcelSheetErrorString($row,"Site $site is duplicated");
		}
		
		#------------------------------------- Verifying Site Structure is defined ----------------------------------------------------
		my $structure = $book->[ $worksheet{Sites} ]{cell}[$siteheader{Structure}][$row];
		if ( ! grep( /^$structure$/, @site_structure ) ) {
			$excel_sheet_errors .=  SCL_EXCEL::get_ExcelSheetErrorString($row,"Structure Type $structure is not defined");
		}
		
		#------------------------------------- Verifying Site Functionality is defined ------------------------------------------------
		my $functionality = $book->[ $worksheet{Sites} ]{cell}[$siteheader{Functionality}][$row];
		if ( ! grep( /^$functionality$/, @site_functionality ) ) {
			$excel_sheet_errors .=  SCL_EXCEL::get_ExcelSheetErrorString($row,"Fuctionality $functionality is not defined");
		}
		
		#------------------------------------- Verifying Site Type is defined ---------------------------------------------------------
		my $type = $book->[ $worksheet{Sites} ]{cell}[$siteheader{Type}][$row];
		if ( ! grep( /^$type$/, @site_type ) ) {
			$excel_sheet_errors .=  SCL_EXCEL::get_ExcelSheetErrorString($row,"Site Type $type is not defined");
		}
		
		#------------------------------------- Verifying Site Structure-Functionality-Type is defined ---------------------------------
		my $str_funct_type = "$structure:$functionality:$type";
		if ( ! grep( /^$str_funct_type$/, @structure_functionality_type ) ) {
			$excel_sheet_errors .=  SCL_EXCEL::get_ExcelSheetErrorString($row,"Structure_functionality_type $str_funct_type is not defined");
		}
		
		#------------------------------------------------------ Site Creation XML -----------------------------------------------------
		$sitesXML[$siteCount]{Name} =  $site;
		$sitesXML[$siteCount]{Structure} = $structure;
		$sitesXML[$siteCount]{Functionality} = $functionality;
		if($type ne "Auto") {
			$sitesXML[$siteCount]{Type} = $type;
		}
		if(exists($siteheader{Chassis}) and defined $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Chassis}][$row]){
			if ( $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Chassis}][$row] =~ m/M15|M6|M2|M12 Chassis/i) {
				$sitesXML[$siteCount]{Chassis} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{Chassis}][$row];
			}
		}
		if(exists($siteheader{ScalableUptoDegree}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{ScalableUptoDegree}][$row] ne ''){
			$sitesXML[$siteCount]{ScalableUptoDegree} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{ScalableUptoDegree}][$row];
		}
		if(exists($siteheader{EvolvedMesh}) and defined $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{EvolvedMesh}][$row]){
			# if( $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{EvolvedMesh}][$row] =~ /Yes|No/i) {
				# $sitesXML[$siteCount]{EvolvedMesh} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{EvolvedMesh}][$row];
			# }
			if( $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{EvolvedMesh}][$row] =~ /Yes/i) {
				$sitesXML[$siteCount]{EvolvedMesh} = 'true';
			} else {
				$sitesXML[$siteCount]{EvolvedMesh} = 'false';
			}	
		}
		if(exists($siteheader{'Position-X'}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{'Position-X'}][$row] ne ''){
			$sitesXML[$siteCount]{Position}{X} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{'Position-X'}][$row];
		}
		if(exists($siteheader{'Position-Y'}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{'Position-Y'}][$row] ne ''){
			$sitesXML[$siteCount]{Position}{Y} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{'Position-Y'}][$row];
		}
		if(exists($siteheader{'NodeProtection'}) and $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{'NodeProtection'}][$row] ne ''){
			$sitesXML[$siteCount]{NodeProtection} = $book->[ $worksheet{'Sites'} ]{cell}[$siteheader{'NodeProtection'}][$row];
		}
		$sideTracker{$site} = 0;
		$siteCount++;
	}
	#return (\@sites, \@sitesXML, \%sideTracker, $excel_sheet_errors);
	return $excel_sheet_errors;}
1;