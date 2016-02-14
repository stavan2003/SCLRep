#!"C:\Strawberry\perl\bin\perl.exe" -w
package Validator_CTP;
use Config::Simple;
use strict;
use Exporter;

our @ISA= qw( Exporter );
our @EXPORT = qw(@structure_functionality_type @site_functionality @site_structure @site_type);
our (@structure_functionality_type, @site_functionality, @site_structure, @site_type);

my %Config;
Config::Simple->import_from('Config.ini', \%Config);



sub get_SFT {
	open my $handle, '<', $Config{'CTP_ALLOWED.SFT'};
	chomp(@structure_functionality_type = <$handle>);
	close $handle;

	@site_functionality =();
	@site_structure = () ;
	@site_type = ();

	foreach(@structure_functionality_type){
		my ($structure, $functionality, $type) = split(/:/);
		if ( ! grep( /^$functionality$/, @site_functionality ) ) {
			push(@site_functionality, $functionality);
		}	
		if ( ! grep( /^$structure$/, @site_structure ) ) {
			push(@site_structure, $structure);
		}
		if ( ! grep( /^$type$/, @site_type ) ) {
			push(@site_type, $type);
		}
	}
	#print "SFT Set : @site_functionality \n  @site_structure \n @site_type\n";
	return (\@site_functionality,\@site_structure,\@site_type,\@structure_functionality_type);
}

sub get_bandRules {
	my @bandrules = ('C 72Chs 50 GHz(-2dBm/Ch)','C 80Chs 50 GHz(+1dBm/Ch)','C 80Chs 50 GHz(-2dBm/Ch)','C 96Chs 50 GHz(+1dBm/Ch)');
	return @bandrules;
	
}

sub get_LineCards {
	my @linecards = ();
	return @linecards;
}

sub get_fiberType {
	my @fiberTypes = ('G652-SMF - 28E','True Wave Reach','Dispersion Shifted','Metro-Core','True-Wave Plus','True-Wave Minus','True-Wave Classic','Free-Light','LS','Tera-Light','G652-SMF','ELEAF','True Wave RS');
	return @fiberTypes;
}

sub get_NodeTypes {
	my @nodeTypes = ('LEGACY MSTP 15454 ONS','HYBRID 15454 ONS','FLEX NG-DWDM');
	return @nodeTypes;

}

sub get_PreAmps {
	my @preAmps = ('OPT-EDFA-17','OPT-EDFA-24','OPT-AMP-C','OPT-AMP-17','OPT-BST-E','OPT-PRE','OPT-BST','EDRA1-26C-PRE','EDRA1-35C-PRE','EDRA2-26C-PRE','EDRA2-35C-PRE','SMR9-FS-EDFA17-PRE','SMR9-FS-EDFA24-Pre','SMR9-FS-EDFA34-Pre','SMR20-FS-EDFA17-Pre','SMR20-FS-EDFA24-PRE');
	return @preAmps;
}

sub get_BstAmps {
	my @bstAmps = ('OPT-EDFA-17','OPT-EDFA-24','OPT-AMP-C','OPT-AMP-17','OPT-BST-E','OPT-BST');
	return @bstAmps;
}

sub get_RamanAmps {
	my @ramanAmps = ('RAMAN-CTP','RAMAN-COP-CTP','OPT-RAMP-CE','OPT-RAMP-C');
	return @ramanAmps;
}

1;