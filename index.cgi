#!"C:\Strawberry\perl\bin\perl.exe" -w
use CGI;
use Text::Template;

my $query    = new CGI;
print $query->header('text/html;charset=UTF-8');

my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\index.tmpl');
my $navTemplate = 'C:\xampp\cgi-bin\SCL\templates\navbar.tmpl';

my $template_nav = Text::Template->new(TYPE => "FILE", SOURCE => $navTemplate);
my $navbar = $template_nav->fill_in(HASH=> {name => $ENV{'REMOTE_USER'}}, DELIMITERS => [ '<<@@', '@@>>' ]);

print $template->fill_in(HASH=> {navbar => $navbar, userid => $ENV{'REMOTE_USER'}}, DELIMITERS => [ '<<@@', '@@>>' ]);