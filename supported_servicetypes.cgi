#!"C:\Strawberry\perl\bin\perl.exe" -w
use CGI;
use Text::Template;

sub  trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };
my $query    = new CGI;
print $query->header('text/html;charset=UTF-8');
open my $handle, '<', 'C:\xampp\htdocs\SCL\SupportedConfigs\servicetype-cardtype.csv';
chomp(my @service_card_type = <$handle>);
close $handle;

my $databody = '';
foreach(@service_card_type){
	next if $_ =~ /^#/;
	my ($service, $cardtype, $card, $protection, $interface, $internal_name) = split(/,/);

	$databody .= "<tr><td>$service</td><td>$cardtype</td><td>$card</td><td>$protection</td><td>$interface</td><td>$internal_name</td></tr>\n";
}

#my $filename = 'C:\xampp\htdocs\SCL\SFT.html';
#open my $fh, '<', $filename or die "error opening $filename: $!";
#my $data = do { local $/; <$fh> };
#$data =~ s/TBODY/$databody/g;
#print $data;


# my $template = HTML::Template->new(filename => 'C:\xampp\cgi-bin\SCL\templates\SFT.tmpl');   
# $template->param('tablecontents', $databody);   
# print $template->output; 

 
my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\DataTable.tmpl');
my $navTemplate = 'C:\xampp\cgi-bin\SCL\templates\navbar.tmpl';
my $pageheader = 'Supported <b>Service Type - Card Type </b> in CTP';
my $tableheader = '<th>Service Rate</th><th>Card Type</th><th>Card Name</th><th>Protection</th><th>Client Interface</th><th>Internal Name</th>';

my $template_nav = Text::Template->new(TYPE => "FILE", SOURCE => $navTemplate);
my $navbar = $template_nav->fill_in(HASH=> {name => $ENV{'REMOTE_USER'}}, DELIMITERS => [ '<<@@', '@@>>' ]);

print $template->fill_in( HASH=> {databody => $databody, 
				pageheader => $pageheader, 
				navbar => $navbar, 
				tableheader => $tableheader}, 
			   DELIMITERS => [ '<<@@', '@@>>' ]);