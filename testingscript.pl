#!"C:\Strawberry\perl\bin\perl.exe" -w
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


	my $doc = XML::LibXML::Document->new('1.0', 'UTF-8');
	my $xsd = 'C:/xampp/cgi-bin/SCL/schema/ctp.xsd';
	my $schema = XML::Compile::Schema->new($xsd);
	print $schema->template('XML','Project', show_comments=>NONE);
	exit;
	
