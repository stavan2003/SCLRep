#!"C:\Strawberry\perl\bin\perl.exe" -w
package SideValidator_CTP;
use strict;
use Exporter;
use SCL_EXCEL;
use Validator_CTP;
use SiteValidator_CTP;
our @ISA= qw( Exporter );


sub validateSideDetails {
	my %sidesheader = %{$_[0]};
	my $excel_sheet_errors = '';
	for (my $row=2; $row <= $book->[ $worksheet{'Sides'} ]{maxrow} ; $row++){
		my $siteName = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{SiteName}][$row];
		$siteName =~ s/^\s+|\s+$//g;
		if ( ! grep( /^$siteName$/, @sites ) ) {
			$excel_sheet_errors .= SCL_EXCEL::get_ExcelSheetErrorString($row,"Site $siteName is not defined in 'Sites' Sheet");
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
						if(exists($sidesheader{ColorlessPorts}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ColorlessPorts}][$row] and $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{ColorlessPorts}][$row] ne ''){
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
				if(exists($sidesheader{LineSides}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{LineSides}][$row]){
					my @lineSides = split /,/,$book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{LineSides}][$row];
					print "Line Sides : @lineSides";
					foreach (@lineSides) {
						my %side;
						$side{Name} = $_;
						if(exists($sidesheader{InterleaverType}) and defined $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{InterleaverType}][$row]){
							$side{InterleaverType} = $book->[ $worksheet{'Sides'} ]{cell}[$sidesheader{InterleaverType}][$row];
						}
						push @{$sitesXML[$count]{Sides}{Side}}, \%side;
					}
				}
			}
		} # End XML Side Creation
	
	}
	return $excel_sheet_errors;
}
1;