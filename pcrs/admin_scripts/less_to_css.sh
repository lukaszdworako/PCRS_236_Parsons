#!/bin/bash

FILES="edit_challenge
challenge_page
quest_list
quest_page
submission
base"

cd ../resources/less

if hash lessc 2>/dev/null; then
        echo "lessc detected"

	for file in $FILES
	do
		if [ -f $file.less ]; then
			if lessc -x $file.less > $file.css ; then
				echo "Created $file.css"
			else
				echo "ERROR: Could not create $file.css"			
			fi
		else
			echo "ERROR: File $file.less does not exist"
		fi	
	done

else
    echo "You need to install lessc"
    echo "To install lessx run: sudo npm install -g less"
    echo "Stopping script"
    exit 1
fi

