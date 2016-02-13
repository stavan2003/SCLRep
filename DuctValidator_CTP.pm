#!"C:\Strawberry\perl\bin\perl.exe" -w
package DuctValidator_CTP;
use strict;
use Exporter;
use SCL_EXCEL;
use Validator_CTP;
use SiteValidator_CTP;
our @ISA= qw( Exporter );
our @EXPORT = qw(@ductsXML);

our (@ductsXML);

sub validateDuctDetails {
	my %ductheader = %{$_[0]};
	my $excel_sheet_errors = '';
	my $ductCount = 0;
	
	my @fiberTypes = Validator_CTP::get_fiberType();
	my @sideNames = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z");
	
	
	for (my $row=2; $row <= $book->[ $worksheet{'Duct-details'} ]{maxrow} ; $row++){
		my $sourceSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcsite}][$row];
		$sourceSite =~ s/^\s+|\s+$//g;
		$ductsXML[$ductCount]{Source}{Site} = $sourceSite;
		if ( ! grep( /^$sourceSite$/, @sites ) ) {
			$excel_sheet_errors .= SCL_EXCEL::get_ExcelSheetErrorString($row,"Source site $sourceSite is not defined in 'Sites' Sheet");
		}
		$sideTracker{$sourceSite} ++;
			
		my $destSite = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destsite}][$row];
		$destSite =~ s/^\s+|\s+$//g;
		$ductsXML[$ductCount]{Destination}{Site} = $destSite;
		if ( ! grep( /^$destSite$/, @sites ) ) {
			$excel_sheet_errors .= SCL_EXCEL::get_ExcelSheetErrorString($row,"Destination site $destSite is not defined in 'Sites' Sheet");
		}
		
		$sideTracker{$destSite} ++;
		
		#-------------------------------------------------- Ducts XML----------------------------------------------------------------------------
		  
		my $ductNameCount = $ductCount + 1;
		
		if(exists($ductheader{DuctName}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{DuctName}][$row] ne ''){
			$ductsXML[$ductCount]{Name} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{DuctName}][$row];
		} else {
			$ductsXML[$ductCount]{Name} = "Duct - ".$ductNameCount;
		}

		if(exists($ductheader{srcSide}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcSide}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Side} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcSide}][$row];
		} else {
			$ductsXML[$ductCount]{Source}{Side} = $sideNames[$sideTracker{$sourceSite}-1];
			#print "$sourceSite : ".$sideNames[$sideTracker{$sourceSite}-1];
		}	

		if(exists($ductheader{srcPreAmp}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcPreAmp}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Pre} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcPreAmp}][$row];
		} 
		if(exists($ductheader{srcBstAmp}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcBstAmp}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Bst} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcBstAmp}][$row];
		} 
		if(exists($ductheader{srcRaman}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcRaman}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Raman} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{srcRaman}][$row];
		} 

		if(exists($ductheader{destSide}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destSide}][$row] ne ''){
			$ductsXML[$ductCount]{Destination}{Side} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destSide}][$row];
		} else {
			$ductsXML[$ductCount]{Destination}{Side} = $sideNames[$sideTracker{$destSite}-1];
			#print "  $destSite : ". $sideNames[$sideTracker{$destSite}-1]."\n";
		}
		
		if(exists($ductheader{destPreAmp}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destPreAmp}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Pre} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destPreAmp}][$row];
		} 
		if(exists($ductheader{destBstAmp}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destBstAmp}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Bst} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destBstAmp}][$row];
		} 
		if(exists($ductheader{destRaman}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destRaman}][$row] ne ''){
			$ductsXML[$ductCount]{Source}{Raman} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{destRaman}][$row];
		} 
		
		if(exists($ductheader{FiberType}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{FiberType}][$row] ne ''){
			my $fibertype = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{FiberType}][$row];
			if ( ! grep( /^$fibertype$/, @fiberTypes ) ) {
				$excel_sheet_errors .= SCL_EXCEL::get_ExcelSheetErrorString($row,"Fiber Type site $fibertype is not defined");
			}
			$ductsXML[$ductCount]{Type} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{FiberType}][$row];
		}

		if(exists($ductheader{SpanLength}) and $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{SpanLength}][$row] ne ''){
			$ductsXML[$ductCount]{Length} = $book->[ $worksheet{'Duct-details'} ]{cell}[$ductheader{SpanLength}][$row];
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
	return $excel_sheet_errors;
}
1;	