#!"C:\Strawberry\perl\bin\perl.exe" -w
package Garuda_DB;
use CGI;
use DBI;
use Config::Simple;
use strict;
use Exporter;

our @ISA= qw( Exporter );
our @EXPORT_OK = qw( retrieve_record insert_record delete_record update_record);

my %Config;
Config::Simple->import_from('Config.ini', \%Config);
my $userid =  $Config{'MYSQL.USERID'};
my $password = $Config{'MYSQL.PASSWORD'};
my $database = $Config{'MYSQL.DATABASE'};
my $driver = $Config{'MYSQL.DRIVER'};


#insert_record('stshah','SC1','C:\xxx\xxx\xxx.xml', 'uploaded');
#update_record(10, "New Status");
#retrieve_selected_record('stshah');
sub db_connect {
	my $dsn = "DBI:$driver:database=$database";
	my $dbh = DBI->connect($dsn, $userid, $password ) or die $DBI::errstr;
	return $dbh;
}


sub retrieve_record {
	my $dbh = db_connect();
	my $sth = $dbh->prepare("SELECT id, userid, location, uploadtime, status FROM garuda_archives");
	$sth->execute() or die $DBI::errstr;
	#print "Number of rows found :".$sth->rows;
	my $list = $sth->fetchall_arrayref;
	$sth->finish();
	return $list;
}

sub retrieve_selected_record {
	my $user = $_[0];
	my $dbh = db_connect();
	my $sth = $dbh->prepare("SELECT id, userid, location, uploadtime, status FROM garuda_archives where userid = ?");
	$sth->execute($user) or die $DBI::errstr;
	#print "Number of rows found :".$sth->rows;
	my $list = $sth->fetchall_arrayref;
	$sth->finish();
	return $list;
}

sub insert_record {
	my ($uid, $filename, $link, $status) = @_;
	my $dbh = db_connect();
	my $query = "insert into garuda_archives (userid, filename, location, status) values (?, ?, ?, ?) ";
	my $sth = $dbh->prepare($query);
	$sth->execute($uid, $filename, $link, $status);
	$sth->finish();
	#print "Record Inserted : $dbh->{mysql_insertid}\n";
	return $dbh->{mysql_insertid};
   
}
	
sub delete_record {
}

sub update_record {
	my ($id, $status) = @_;
	my $dbh = db_connect();
	my $query = "update garuda_archives SET status = ? where id = ?";
	my $sth = $dbh->prepare($query);
	$sth->execute($status, $id);
	$sth->finish();
	#print "Record Updated";
	
}
