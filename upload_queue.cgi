#!"C:\Strawberry\perl\bin\perl.exe" -w
use CGI;
use Text::Template;

my $query    = new CGI;
print $query->header('text/html;charset=UTF-8');
opendir my $dir, 'C:\Temp\ctp' or die "Cannot open directory: $!";
my @files = readdir $dir;
my @sorted_files = sort(@files);
closedir $dir;

my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\DataTable.tmpl');
my $navTemplate = 'C:\xampp\cgi-bin\SCL\templates\navbar.tmpl';
my $pageheader = 'Garuda v2.0 - Design File Queue';
my $tableheader = '<th>Priority</th><th>Submit Time<th>File Name</th>';

my $databody = '';
my $count = 1;
my @months = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");

foreach(@sorted_files) {
	my ($time, $name) = split(/-/,$_,2);
	next unless $name =~ m/.*.xml/;
	my ($sec, $min, $hour, $day,$month,$year) = (localtime($time))[0,1,2,3,4,5]; 
	#print "Unix time ".$time." converts to ".$months[$month]." ".$day.", ".($year+1900);
	#print " ".$hour.":".$min.":".$sec."\n";
	my $table_time = $months[$month]." ".$day.", ".($year+1900)." ".$hour.":".$min.":".$sec;
	$databody .= "<tr><td>$count</td><td>$table_time</td><td>$name</td></tr>\n";
	$count++;
}



my $template_nav = Text::Template->new(TYPE => "FILE", SOURCE => $navTemplate);
my $navbar = $template_nav->fill_in(HASH=> {name => $ENV{'REMOTE_USER'}}, DELIMITERS => [ '<<@@', '@@>>' ]);

print $template->fill_in( HASH=> {databody => $databody, 
				pageheader => $pageheader, 
				navbar => $navbar, 
				tableheader => $tableheader}, 
			   DELIMITERS => [ '<<@@', '@@>>' ]);