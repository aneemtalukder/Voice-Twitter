#!/usr/bin/perl

use strict;
use POSIX qw(strftime);

my $sentence_dir = "/tmp/";

#input data format is light weight JSON. Some examples provided below
my $json1 = <<END;
{
	type: "read",
	tweets: [
		{
			text: "This is a Tweet!",
			id: 1324123,
			timestamp: 1331000834,
			user: "yufeiliu",
			user_id: 3123,
			original_user: "yufeiliu",
			original_user_id: 1234
		},
		{
			text: "This is another Tweet!",
			id: 1324415,
			timestamp: 1239890713,
			user: "yufeiliu",
			user_id: 3123,
			original_user: "yufeiliu",
			original_user_id: 1234
		},
		{
			text: "This is another Tweet!",
			id: 1324415,
			timestamp: 1239890713,
			user: "yufeiliu",
			user_id: 3123,
			original_user: "yufeiliu",
			original_user_id: 1234
		}
	]
}
END

my $json1_flat = <<END;
{type: "read",tweets: [{text: "This is a Tweet!",id: 1324123,timestamp: 1331000834,user: "yufeiliu",user_id: 3123,original_user: "yufeiliu",original_user_id: 1234},{text: "This is another Tweet!",id: 1324415,timestamp: 1239890713,user: "yufeiliu",user_id: 3123,original_user: "yufeiliu",original_user_id: 1234}]}
END

my $json2 = <<END;
{type: "action",action: "retweet"}
END

my $json3 = <<END;
{type: "question",id: 1}
END

# *** update these variables with your own info ***
my $USERNAME = "yl2515";
my $TOPIC    = "timeline";

# arguments
my $input = shift;    # input string
my $wav_file = shift; # absolute path and name of the output wav file

# checks the parameters, printing an error message if anything is wrong.
if (!$input || !$wav_file) {
	die  "This script transforms an input string into an English sentence, \n"
		."synthesizes it and saves the\n"
		."results as a wav file. \n"

		." ***COMPLETE THE DESCRIPTION OF WHAT THIS SCRIPT DOES*** \n"

		."Usage: tts.pl INPUT WAVFILE \n"
		."Where: \n"
		." INPUT:   ***COMPLETE: INPUT DESCRIPTION AND FORMAT***\n"
		." WAVFILE: absolute path and name of the output wav file.\n";
}

# transforms the string $input into an English sentence
my $sentence = generate_sentence($input);

# full path to the TTS: partc
# (update if necessary)
my $BASEDIR = "/proj/speech/users/cs4706/".$USERNAME."/partc";


# creates a Festival script
my $filename = "/tmp/temp_".time().".scm";
open OUTPUT, ">$filename" or die "Can't open '$filename' for writing.\n";

print OUTPUT '(load "'.$BASEDIR.'/festvox/SLP_'.$TOPIC.'_xyz_ldom.scm")' . "\n";
print OUTPUT '(voice_SLP_'.$TOPIC.'_xyz_ldom)' . "\n";
print OUTPUT '(Parameter.set \'Audio_Method \'Audio_Command)' . "\n";
print OUTPUT '(Parameter.set \'Audio_Required_Rate 16000)' . "\n";
print OUTPUT '(Parameter.set \'Audio_Required_Format \'wav)' . "\n";
print OUTPUT '(Parameter.set \'Audio_Command "cp $FILE '.$wav_file.'")' . "\n";
print OUTPUT '(SayText "'. $sentence .'")' . "\n";

close OUTPUT;


# tells Festival to execute the script we just created
system "cd $BASEDIR; festival --batch $filename";

open (S_FILE, '>' . $sentence_dir . 'temp.txt');
print S_FILE "$sentence";
close S_FILE;

print "======== finished writing to file $sentence_dir" . 'temp.txt';

print "======== from perl script: finished generating file at $wav_file\n";

# deletes the temporary script
unlink $filename;


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# transforms the input ($string) into an English sentence and
# returns it.
sub generate_sentence {
	my $string = shift;

	# todo: some error checking; right now it assumes very rigid data format

	# get rid of enclosing {}
	$string = trim(substr(trim($string), 1, length($string) - 2));
	my @temp = split(/,/, $string);
	my $type = trim((split(/:/, shift(@temp)))[-1]);
	#gets rid of surrounding quotes
	$type = substr($type,1,length($type)-2);
	my $rest = trim(join(',', @temp));

	#read tweets
	if ($type eq 'read' || $type eq "search") {
		@temp = split(/:/, $rest);
		shift(@temp);
		$rest = trim(join(':',@temp));
		# strip []
		$rest = trim(substr($rest, 1, length($rest)-2));

		my $copy = $rest;
		$copy =~ s/}//g;

		my $num = length($rest) - length($copy);
		my $time = -1;

		if ($rest =~ m/timestamp:[ ]*([0-9]+),/ ) {
			$time = $1 + 0;
		}

		my $now = (strftime "%s", localtime) + 0;

		return "There " . ($num==1 ? "is " : "are ") . numToText($num) . ($type eq 'read' ? " new" : "") .
			" tweet" . ($num==1 ? "" : "s") . ($type eq 'read' ? " since you last checked, " : " in your search result, ") .
			"the most recent is from " . secondsToAgo($now - $time);
	}

	# confirm action
	if ($type eq 'action') {
		my $action = "";
		if ($rest =~ m/action:[ ]*"([a-zA-Z]+)"/) {
			$action = $1;
		}

		return ucfirst($action) . "ed successfully";
	}

	my $id = -1;
	my $tweet_text = "";

	if ($rest =~ m/id:[ ]*([0-9]+)/) {
		$id = $1;
	}

	if ($rest =~ m/text:[ ]*"([^"]+)"/) {
		$id = 0;
		$tweet_text = $1;
	}



	if ($type eq 'help') {
		return help($id);
	}

	if ($type eq 'tweet') {
		return $tweet_text;
	}

	if ($type eq 'question') {
		return question($id);
	}

	if ($type eq 'prompt') {
		return prompt($id);
	}

	return prompt(1);
}

# *** Define any auxiliary functions here ***

sub numToText {
	my $input = shift;
	if ($input == 0) {
		return "zero";
	} elsif ($input == 1) {
		return "one";
	} elsif ($input == 2) {
		return "two";
	} elsif ($input == 3) {
		return "three";
	} elsif ($input == 4) {
		return "four";
	} elsif ($input == 5) {
		return "five";
	} elsif ($input == 6) {
		return "six";
	} elsif ($input == 7) {
		return "seven";
	} elsif ($input == 8) {
		return "eight";
	} elsif ($input == 9) {
		return "nine";
	} elsif ($input == 10) {
		return "ten";
	} elsif ($input > 40) {
		return "many";
	} elsif ($input > 30) {
		return "more than thirty";
	} elsif ($input > 20) {
		return "more than twenty";
	} elsif ($input > 10) {
		return "more than ten";
	}

	return "";
}

sub secondsToAgo {
	my $sec = shift;
	if ($sec < 30) {
		return "a few seconds ago";
	} elsif ($sec < 90) {
		return "about a minute ago";
	} elsif ($sec < 450) {
		return "about five minutes ago";
	} elsif ($sec < 900) {
		return "about ten minutes ago";
	} elsif ($sec < 1500) {
		return "about twenty minutes ago";
	} elsif ($sec < 45 * 60) {
		return "about half an hour ago";
	} elsif ($sec < 90 * 60) {
		return "about an hour ago";
	} elsif ($sec < 60 * 60 * 10) {
		return "about a few hours ago";
	} elsif ($sec < 60 * 60 * 18) {
		return "about twelve hours ago";
	} elsif ($sec < 60 * 60 * 36) {
		return "about a day ago";
	} elsif ($sec < 60 * 60 * 24 * 5) {
		return "about a few days ago";
	} elsif ($sec < 60 * 60 * 24 * 10) {
		return "about a week ago";
	} else {
		return "a long time ago";
	}
}

sub help {
	my $id = shift;
	if ($id == 0) {
		return "You can say read, search, write, or exit";
	} elsif ($id == 1) {
		return "At any time, say restart to go to main menu";
	} elsif ($id == 2) {
		return "Say retweet, favorite, follow user, unfollow user, or say nothing to skip";
	} elsif ($id == 3) {
		return "You can say politics, sports, entertainment, or trending";
	} elsif ($id == 4) {
		return "You can say I'm happy, I'm sad, I'm angry, I'm excited, talk about today's weather, or tweet a random fact";
	}
}

sub question {
	my $id = shift;
	if ($id == 0) {
		return "What would you like to do?";
	} elsif ($id == 1) {
		return "What would you like to do to this tweet?";
	} elsif ($id == 2) {
		return "Which keywords would you like to search?";
	} elsif ($id == 3) {
		return "What would you like to tweet?";
	}
}

sub prompt {
	my $id = shift;
	if ($id == 0) {
		return "Welcome to Voice Twitter!";
	} elsif ($id == 1) {
		return "Sorry I didn't quite get that, try again";
	} elsif ($id == 2) {
		return "Thanks, goodbye!";
	}
}

sub trim {
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}
