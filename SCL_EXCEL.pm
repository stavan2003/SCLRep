#!"C:\Strawberry\perl\bin\perl.exe" -w
package SCL_EXCEL;
use Config::Simple;
use strict;
use Exporter;
our @ISA= qw( Exporter );
our @EXPORT_OK = qw( get_WorkSheetHeader get_ExcelSheetErrorString get_AllExcelErrors);
our @EXPORT = qw($book %worksheet);
our ($book, %worksheet);

sub get_WorkSheetHash {
	$book = shift;
	foreach my $key ( keys %{ $book->[0]{sheet} } ) {
		my $val = $book->[0]{sheet}{$key};
		$worksheet{$key} = $val;
		#print "$key -> $val\n";
	}
	return %worksheet;
}

	
sub get_WorkSheetHeader {
	my $worksheetName = $_[0];
	#print "\n--------------------------- $worksheetName -----------------------\n";
	my %worksheetHeaderHash = ();
	for (my $col=1; $col <= $book->[ $worksheet{$worksheetName} ]{maxcol} ; $col++){
		my $header = $book->[ $worksheet{$worksheetName} ]{cell}[$col][1];
		$worksheetHeaderHash{$header} = $col;
		#print "$header -> $col\n";
	}
	return %worksheetHeaderHash;
} 

sub get_ExcelSheetErrorString {
	my ($row, $error) = @_;
	my $excel_sheet_errors = '';
	if($row != '') {
		$excel_sheet_errors = "<p>Row #: $row	Error:	$error</p>";
	} else {
		$excel_sheet_errors = "<p>Error:	$error</p>";
	}
	#print "$excel_sheet_errors\n";
	return $excel_sheet_errors;
}

sub get_AllExcelErrors {
	my ($sheetname, $excel_sheet_errors) = @_;
	my $excel_errors = "<h2>$sheetname Sheet</h2><section>$excel_sheet_errors</section>";	
	#print "$excel_errors\n";
	return $excel_errors;}
1;