use Config::Simple;
use Text::Template;
use File::Copy;
# my %Config;
# Config::Simple->import_from('Config.ini', \%Config);


# foreach my $key ( keys %Config){
	# print "$key ---> $Config{$key}";
# }



# my $template = HTML::Template->new(filename => 'C:\xampp\cgi-bin\SCL\greeting1.tmpl');   

# $template->param('email', 'bill@nowhere.com');   

# $template->param('person', 'William');   

# print "Content-Type: text/htmlnn";   

# print $template->output; 


 my $template = Text::Template->new(TYPE => "FILE", SOURCE => 'C:\xampp\cgi-bin\SCL\templates\SFT.tmpl');
 $filename = 'C:\xampp\cgi-bin\SCL\templates\navbar.tmpl';
 $navbar = 'C:\xampp\cgi-bin\SCL\templates\navbar.tmpl';
 $tablebody = '121212';
 print $template->fill_in(DELIMITERS => [ '<<<', '>>>' ]);