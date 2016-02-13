#!"C:\Strawberry\perl\bin\perl.exe" -w
use strict;
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

use Garuda_DB;
use Validator_CTP;
use SCL_EXCEL;
use NetworkValidator_CTP;
use SiteValidator_CTP;
use SideValidator_CTP;
use DemandValidator_CTP;
use DuctValidator_CTP;

use Exporter;
our @ISA = 'Exporter';
our @EXPORT = qw($book %worksheet);

my $standalone = 1;

my %Config;
Config::Simple->import_from('Config.ini', \%Config);
my $excel_errors ='';
my $filename = '';
my $designMethod = 'xml';
my $fileLink = '';
my $upload_dir = '';

if (! $standalone) {
	my $query    = new CGI;
	print $query->header('text/html;charset=UTF-8');
	$filename = $query->param("excelInput");
	$designMethod = $query->param("designmethod");

	#Setting Safety Limits
	$CGI::POST_MAX = 1024 * $Config{'FILE.MAX_FILE_SIZE'};
	my $safe_filename_characters = "a-zA-Z0-9_.-";
	$upload_dir = $Config{'DIRECTORIES.UPLOAD_DIR'};

	$fileLink = '<a href="/SCL/uploadedFiles/'.$filename.'">'.$filename.'</a>';
	if ( !$filename ) {
		print $query->header();
		print "There was a problem uploading your file (try a smaller file) or contact ctp-india-test\@cisco.com.";
		my $id = Garuda_DB::insert_record($ENV{'REMOTE_USER'},$filename, $fileLink, 'InvalidFile');
		exit;
	}

	# Making the Filename Safe
	my ( $name, $path, $extension ) = fileparse( $filename, '..*' );
	$filename = time().'-'.$name . $extension;
	$filename =~ tr/ /_/;
	$filename =~ s/[^$safe_filename_characters]//g;
	
	if ( $filename =~ /^([$safe_filename_characters]+)$/ ){
		$filename = $1;
	} else {
		print "Filename contains invalid characters. Valid characters are : a-zA-Z0-9_.-";
		my $id = Garuda_DB::insert_record($ENV{'REMOTE_USER'},$filename, $fileLink, 'InvalidFile');
		exit;
	}

	# Getting the File Handle
	my $upload_filehandle = $query->upload("excelInput");

	# Saving the File
	open ( UPLOADFILE, ">$upload_dir/$filename" ) or die "$!";
	binmode UPLOADFILE;
	while ( <$upload_filehandle> ){
		print UPLOADFILE;
	}
	close UPLOADFILE;
	$fileLink = '<a href="/SCL/uploadedFiles/'.$filename.'"download>'.$filename.'</a>';
	print "<p><b>File Uploaded $fileLink</b></p>";

}

#-------------------------------------------------- Storing CTP Allowed Values ----------------------------------------------------------
our ($functionality_ref, $structure_ref, $type_ref, $structure_functionality_type_ref) = Validator_CTP::get_SFT();


#-------------------------------------------------- Reading the Input Excel -------------------------------------------------------------
my $book  = ReadData ("$upload_dir/$filename");
#$book  = ReadData ('C:/Users/stshah/Desktop/Verizon/Trials/CTP_Input_Excel_v3.xlsx');
$book  = ReadData ('C:/Users/stshah/Desktop/Verizon/CTP_Input_Excel_v2 NYC YI20160210-v1.xlsx');

#-------------------------------------------------- Creating Worksheet Hash and check of mandatory Worksheets ----------------------------
my %worksheet = SCL_EXCEL::get_WorkSheetHash($book);

if(! exists $worksheet{'Sites'} or ! exists $worksheet{'Duct-details'} or ! exists $worksheet{'NetworkSheet'} ){
	print "<p>Worksheets : NetworkSheet, Sites and Duct-details are mandatory </p>";
	#my $id = Garuda_DB::insert_record($ENV{'REMOTE_USER'},$filename, $fileLink, 'InvalidFile');
	exit;
}

#-------------------------------------------------- Creating Worksheet Headers--------------------------------------------------
my %networksheetheader = SCL_EXCEL::get_WorkSheetHeader('NetworkSheet');
my %siteheader =  SCL_EXCEL::get_WorkSheetHeader('Sites');
my %sidesheader = SCL_EXCEL::get_WorkSheetHeader('Sides');
my %demandsheader = SCL_EXCEL::get_WorkSheetHeader('Demands');
my %ductheader = SCL_EXCEL::get_WorkSheetHeader('Duct-details');


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating NetworkSheet ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n";
my $network_excel_sheet_errors = NetworkValidator_CTP::validateNetworkDetails(\%networksheetheader);
if($network_excel_sheet_errors ne ''){ $excel_errors .= SCL_EXCEL::get_AllExcelErrors('Network', $network_excel_sheet_errors);}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sites ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
my $site_excel_sheet_errors = SiteValidator_CTP::validateSiteDetails(\%siteheader);
if($site_excel_sheet_errors ne ''){ $excel_errors .= SCL_EXCEL::get_AllExcelErrors('Site', $site_excel_sheet_errors);}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Sides ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

my $side_excel_sheet_errors = SideValidator_CTP::validateSideDetails(\%sidesheader);
if($side_excel_sheet_errors ne ''){ $excel_errors .= SCL_EXCEL::get_AllExcelErrors('Sides', $side_excel_sheet_errors);}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Demands ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

my $demand_excel_sheet_errors = DemandValidator_CTP::validateDemandDetails(\%demandsheader);
if($demand_excel_sheet_errors ne ''){ $excel_errors .= SCL_EXCEL::get_AllExcelErrors('Demands', $demand_excel_sheet_errors);}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validating Duct Details ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

my $duct_excel_sheet_errors = DuctValidator_CTP::validateDuctDetails(\%ductheader);
if($duct_excel_sheet_errors ne ''){ $excel_errors .= SCL_EXCEL::get_AllExcelErrors('Duct-Details', $duct_excel_sheet_errors);}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validation Complete ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if($excel_errors eq ''){

	my $id = Garuda_DB::insert_record($ENV{'REMOTE_USER'},$filename, $fileLink, 'XMLGenerationStarted');
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
			'C-Band-Rule' => $cBandRules,
			'L-Band-Rule' => "None",
			NodeType => $nodeType,
			Sites => { Site => \@sitesXML,},
			Fibres => { Duct => \@ductsXML,},
			Demands => { PointToPoint => \@p2pXML,}, 
		}, 
	  };
	my $doc = XML::LibXML::Document->new('1.0', 'UTF-8');
	my $xsd = $Config{'XSD.XSDFILE'};
	my $schema = XML::Compile::Schema->new($xsd);
	
	my %option;
	$option{validation} = 0;
	my $write  = $schema->compile(WRITER => 'Project', %option );
	
	my $xml    = $write->($doc, $data);
	$doc->setDocumentElement($xml);
	#print $doc->toString(1); 
		
	my $xmlschema = XML::LibXML::Schema->new(location => $xsd);
	eval { $xmlschema->validate( $doc ); };

	if ( my $ex = $@ ) {
		print "XML Generation Failed due to Below Errors :\n";
		my @arr = split /\n/, $ex;
		foreach(@arr) {
			print "<p>$_</p>";
		}
		Garuda_DB::update_record($id, 'InvalidFile');	
	} else {
		print "<p>SUCCESS for $filename  --> XML Generation Started</p>";
		my $arg_filename = "$upload_dir/$filename";
		my ($name, $ext) = split(/\./, $filename);
		my $arg_resultXML = "$upload_dir/$name.xml";
		
		$arg_resultXML = 'C:\Users\stshah\Desktop\Verizon\SCL-Result.xml';
		
		open(my $fh, '>', $arg_resultXML) or die "Could not open file '$arg_resultXML' $!";
		print $fh $doc->toString(1);
		close $fh;
		
		print "XML Generation Complete : $filename \n";
		
		if($designMethod eq 'mpz') {
			print "<br>Moving the design to Queue : $filename \n";
			my $uploadctpxml = 'C:\Temp\ctp\\'.$name.".xml";
			copy($arg_resultXML,$uploadctpxml);
		} elsif ($designMethod eq 'xml') {
			my $fileLink = '<a href="/SCL/uploadedFiles/'.$name.'.xml">'.$name.'.xml</a>';
			print "<p><b>XML File --> $fileLink</b></p>";

		}
		Garuda_DB::update_record($id, 'XMLGenerationComplete');
	}
} else {
	my $id = Garuda_DB::insert_record($ENV{'REMOTE_USER'},$filename, $fileLink, 'InvalidFile');
	my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\excelError.tmpl');
	print $template->fill_in(HASH=> {excelError => $excel_errors}, DELIMITERS => [ '<<@@', '@@>>' ]);
}
