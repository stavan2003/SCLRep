#!"C:\Strawberry\perl\bin\perl.exe" -w
package NetworkValidator_CTP;
use strict;
use Exporter;
use SCL_EXCEL;
use Validator_CTP;
use SiteValidator_CTP;
our @ISA= qw( Exporter );
our @EXPORT = qw($cBandRules $nodeType);

our ($cBandRules,$nodeType);

sub validateNetworkDetails {
	my %networksheetheader = %{$_[0]};
	my @bandrules = Validator_CTP::get_bandRules();
	my @nodeTypes = Validator_CTP::get_NodeTypes();
	my $excel_sheet_errors = '';
	
	for (my $row=2; $row <= $book->[ $worksheet{'NetworkSheet'} ]{maxrow} ; $row++){
		$cBandRules = $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'CBandRules'}][$row];
		if ( ! grep( /^\Q$cBandRules\E$/, @bandrules ) ) {
			$excel_sheet_errors .= SCL_EXCEL::get_ExcelSheetErrorString($row, "Band Rules  $cBandRules is not defined");
		}
		$nodeType = $book->[ $worksheet{'NetworkSheet'} ]{cell}[$networksheetheader{'NodeType'}][$row];
		if ( ! grep( /^\Q$nodeType\E$/, @nodeTypes ) ) {
			$excel_sheet_errors .= SCL_EXCEL::get_ExcelSheetErrorString($row, "Node Type  $nodeType is not defined");
		}	
	}

	return $excel_sheet_errors;
}
1;