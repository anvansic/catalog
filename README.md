# **README for the Catalog Project**

## 1.) Installing
In order to run this catalog application, a few components must be installed
first:

1. A Virtualbox environment.
2. The Vagrant virtual machine.
3. Python 3.6.1 or later.
4. All files contained in the _catalog/_ directory.
5. The sqlalchemy package.
6. The flask package.

The latter two Python packages must be installed in directories where the
application will be able to access them.

## 2.) Running
Once the above components are installed, start by activating the Vagrant
machine. Navigate into the _catalog/_ directory where the _views.py_ file is
located. Execute the file by entering the command "python views.py".

When using the application, several options are only available to users with
existing Google accounts (Google+, gmail, etc). The application uses OAuth to
automatically enable these options for logged in users. Occasionally -
especially if the user is signing in or out of their accounts on other pages -
the browser may display an error message when they attempt to log out. In this
case, simply navigating back to the home page will resolve the issue.

If the user chooses to navigate backwards to a page featuring a form, it is
strongly recommended that, when prompted, the data from the form be resubmitted.

## 3.) Dependencies
All files contained within the _catalog/_ directory are considered essential
for the proper functioning of this catalog application.

## 4.) Acknowledgments
Because of the straightforward nature of connecting and disconnecting users with
OAuth, this functionality - specifically, the '/gconnect' and '/gdisconnect'
routes - has been reappropriated from examples provided by Udacity with
minimal change or embellishment.
