#!"C:\Strawberry\perl\bin\perl.exe" -w
package Garuda_DB;
use CGI;
use DBI;
use Config::Simple;
use strict;

my %Config;
Config::Simple->import_from('Config.ini', \%Config);
my $userid =  $Config{'MYSQL.USERID'};
my $password = $Config{'MYSQL.PASSWORD'};
my $database = $Config{'MYSQL.DATABASE'};
my $driver = $Config{'MYSQL.DRIVER'};


sub db_connect {
	my $dsn = "DBI:$driver:database=$database";
	my $dbh = DBI->connect($dsn, $userid, $password ) or die $DBI::errstr;
	return $dbh;
}


sub retrieve_record {
	my $dbh = db_connect();
	my $sth = $dbh->prepare("SELECT id, userid FROM garuda_archives");
	$sth->execute() or die $DBI::errstr;
	print "Number of rows found :".$sth->rows;
	while (my @row = $sth->fetchrow_array()) {
		my ($id, $userid ) = @row;
		print "ID = $id, USER = $userid\n";
	}
  	$sth->finish();
}


sub insert_record {
   
}
	
sub delete_record {
}