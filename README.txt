to install must have python 3.6.*

try running all this is as admin

'cd to where you have this file/folder'

'pip install virtualenv'

'virtualenv venv'

'venv/scripts/activate'

'cd backend'


#this might give you errors i had to use: pip install --user pybuilder
#another error might be it tells you its missing a PATH variable it should tell you which one and you can add it to your system

'pip install pybuilder'

#then

'python -m pip install -r requirements.txt'

#if all is succesfull you should be able to run the build file with 


'pyb'

#or 

'python build.py'


######################

basic tasks

'pyb' or 'python build.py' will run unit tests and run the code through flake8 to warn about any code quality issues

'pyb run' or 'python build.py run' will run the flask app

########################

Note:

on windows the coverage module does not read the import\def statements and as such reports them as missing coverage. however on linux all works fine
running on windows gives you a warning that references this issue on pybuilder's issue #184
other than that all should work well