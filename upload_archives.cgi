#!"C:\Strawberry\perl\bin\perl.exe" -w
use CGI;
use Text::Template;
use Garuda_DB;


my $query    = new CGI;
print $query->header('text/html;charset=UTF-8');
my $list;

if($ENV{'REMOTE_USER'} eq 'stshah') {
	$list = Garuda_DB::retrieve_record($ENV{'REMOTE_USER'});
} else {
	$list = Garuda_DB::retrieve_selected_record($ENV{'REMOTE_USER'});
}


opendir my $dir, 'C:\Temp\ctp' or die "Cannot open directory: $!";
my @files = readdir $dir;
my @sorted_files = sort(@files);
closedir $dir;

my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\DataTable.tmpl');
my $navTemplate = 'C:\xampp\cgi-bin\SCL\templates\navbar.tmpl';
my $pageheader = 'Garuda v2.0 - Archived Designs';
my $tableheader = '<th>ID</th><th>User ID<th>File</th><th>Upload Time</th><th>Status</th>';

my $databody = '';

foreach my $db_rows ( @{$list} ) {
	$databody .= '<tr>';
	foreach my $field (@$db_rows) {
		$databody .= "<td>$field</td>";
	}
	$databody .= '</tr>';
}

my $template_nav = Text::Template->new(TYPE => "FILE", SOURCE => $navTemplate);
my $navbar = $template_nav->fill_in(HASH=> {name => $ENV{'REMOTE_USER'}}, DELIMITERS => [ '<<@@', '@@>>' ]);

print $template->fill_in( HASH=> {databody => $databody, 
				pageheader => $pageheader, 
				navbar => $navbar, 
				tableheader => $tableheader}, 
			   DELIMITERS => [ '<<@@', '@@>>' ]);