#!"C:\Strawberry\perl\bin\perl.exe" -w
package DemandValidator_CTP;
use strict;
use Exporter;
use SCL_EXCEL;
use Validator_CTP;
use SiteValidator_CTP;
our @ISA= qw( Exporter );
our @EXPORT = qw(@p2pXML);

our (@p2pXML);

sub validateDemandDetails {
	my %demandsheader = %{$_[0]};
	my $excel_sheet_errors = '';
	my $p2pCount = 0;
	for (my $row=2; $row <= $book->[ $worksheet{'Demands'} ]{maxrow} ; $row++){
		my $sourceSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Source}][$row];
		$sourceSite =~ s/^\s+|\s+$//g;
		$p2pXML[$p2pCount]{Source} = $sourceSite;
		if ( ! grep( /^$sourceSite$/, @sites ) ) {
			$excel_sheet_errors .= "<p>Row #: $row	Error:	Source site $sourceSite is not defined in 'Sites' Sheet\n</p>";
		}	
		
		my $destSite = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Destination}][$row];
		$destSite =~ s/^\s+|\s+$//g;
		$p2pXML[$p2pCount]{Destination} = $destSite;
		if ( ! grep( /^$destSite$/, @sites ) ) {
			$excel_sheet_errors .= "<p>Row #: $row	Error:	Destination site $destSite is not defined in 'Sites' Sheet\n</p>";
		}
		
		#-------------------------------------------------- Demands XML----------------------------------------------------------------------------
		my $scount = $p2pCount+1;
		$p2pXML[$p2pCount]{Name} = "Service - $scount - $sourceSite - $destSite";
		 if(exists($demandsheader{Encryption}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Encryption}][$row] =~ /Yes|No/i){
			 $p2pXML[$p2pCount]{Encryption} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Encryption}][$row];
		 }
		# if(exists($demandsheader{Bypass}) and defined $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Bypass}][$row]){
			# $p2pXML[$p2pCount]{Bypass} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Bypass}][$row];
		# }
		if(exists($demandsheader{ServiceRate}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ServiceRate}][$row] ne ''){
			$p2pXML[$p2pCount]{Service} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ServiceRate}][$row];
		}
		if(exists($demandsheader{CardForcing}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{CardForcing}][$row] ne ''){
			$p2pXML[$p2pCount]{CardForcing} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{CardForcing}][$row];
		}
		if(exists($demandsheader{Protection}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Protection}][$row] ne ''){
			$p2pXML[$p2pCount]{Protection} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Protection}][$row];
		}
		if(exists($demandsheader{HierarchyType}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{HierarchyType}][$row] ne ''){
			$p2pXML[$p2pCount]{Hierarchy} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{HierarchyType}][$row];
		}
		if(exists($demandsheader{PresentChannels}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row] ne ''){
			$p2pXML[$p2pCount]{PresentChannels} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row];
			$p2pXML[$p2pCount]{ForecastChannels} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row];
		}
		if(exists($demandsheader{ForecastChannels}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ForecastChannels}][$row] ne ''){
			$p2pXML[$p2pCount]{ForecastChannels} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{ForecastChannels}][$row] + $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PresentChannels}][$row];
		}
		if(exists($demandsheader{colorless_src}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_src}][$row] ne ''){
			$p2pXML[$p2pCount]{SrcColorless} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_src}][$row];
		}
		if(exists($demandsheader{colorless_dest}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_dest}][$row] ne ''){
			$p2pXML[$p2pCount]{DstColorless} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{colorless_dest}][$row];
		}
		if(exists($demandsheader{Omnidirectional_src}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_src}][$row] ne ''){
			$p2pXML[$p2pCount]{SrcOmniSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_src}][$row];
		}
		if(exists($demandsheader{Omnidirectional_dest}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_dest}][$row] ne ''){
			$p2pXML[$p2pCount]{DstOmniSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Omnidirectional_dest}][$row];
		}
		if(exists($demandsheader{Contentionless_src}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_src}][$row] ne ''){
			$p2pXML[$p2pCount]{SrcContentionlessSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_src}][$row];
		}
		if(exists($demandsheader{Contentionless_dest}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_dest}][$row] ne ''){
			$p2pXML[$p2pCount]{DstContentionlessSide} = $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{Contentionless_dest}][$row];
		}
		if(exists($demandsheader{PathConstraints}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PathConstraints}][$row] ne ''){
			my @ductConstraints = split /,/,$book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{PathConstraints}][$row];
			$p2pXML[$p2pCount]{PathConstraints}{DuctName} = \@ductConstraints;
		}
		if(exists($demandsheader{SiteConstraints}) and $book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{SiteConstraints}][$row] ne ''){
			my @siteConstraints = split /,/,$book->[ $worksheet{'Demands'} ]{cell}[$demandsheader{SiteConstraints}][$row];
			$p2pXML[$p2pCount]{PathConstraints}{SiteName} = \@siteConstraints;
		}
		
		$p2pCount++;
		
	   
	}
	return $excel_sheet_errors;
}
1;