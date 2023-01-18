# Strings_Attached
An online shop and community for music students 

Source code can be found [here](https://github.com/johnrearden/strings_attached)

The live project can be viewed [here](https://strings-attached-jr.herokuapp.com)

## Purpose of Project
The aim of the project is to help users on their journey to musical proficency. The website consists
of a shop where instruments and accessories can be purchased, and subscriptions to music lesson videos 
can be signed up to. There is also a community on the site, within which users can post videos, sound
clips and comment on their progess.

![responsivenes_screenshot]()

---

## Links to content

[**Features**](#Features)

[**User Experience**](#User-Experience)
- [Design](#design)
    - [Fonts](#fonts)
    - [Colour](#colour)
    - [Wireframes](#wireframes)

[**Development Process**](#Development-Process)
- [Project Planning](#project-planning-and-documentation-in-github)
- [Inline JavaScript](#inline-javascript-and-event-handlers)
- [Data Model](#data-model)

[**Testing**](#Testing)
- [Manual Testing](#manual-testing)
    - [Feature Testing](#feature-testing)
    - [Responsiveness](#responsiveness)
    - [Browser Compatibility](#browser-compatibility)
    - [Lighthouse](#lighthouse)
    - [Code Validation](#code-validation)
        - [Python](#python-code)
        - [JavaScript](#javascript-code)
        - [HTML](#html-validation)
        - [CSS](#css-validation)
    - [User Stories](#user-stories)
- [Automated Testing](#automated-testing)
    - [Django testing](#testing-django-views-models-and-forms)
    - [Selenium testing](#testing-page-functionality-with-selenium)

[**Bugs**](#Bugs)

[**Libraries and Programs Used**](#libraries-and-programs-used)

[**Deployment**](#Deployment)
- [Deploying the app on Heroku](#deploying-the-app-on-heroku)
- [Making a local clone](#making-a-local-clone)
- [Running the app in your local environment](#running-the-app-in-your-local-environment)

[**Credits**](#Credits)

[**Acknowledgements**](#acknowledgements)

---

## Features


### Future Features


[Return to top](#Strings_Attached)
# User Experience

## Design

### Fonts 

### Colour

### Wireframes
![products_display wireframe](/static/doc_images/products_display.png)
![products_detail wireframe](/static/doc_images/product_detail_screenshot.png)
![display_basket wireframe](/static/doc_images/display_basket_screenshot.png)

[Return to top](#Strings_Attached)

# Development Process

## Project planning and documentation in GitHub

GitHub Issues were used to document the development steps undertaken in the project. Two issue templates, 
for [User Epics]() and [User Stories]() were used. Various labels were employed to enable quick identification of issue type including Bugs, User Epics, User Stories and Style. MoSCoW prioritisation was employed using the labels must-have, should-have and could-have. 

To break the project into manageable sprints, GitHub Projects was used to provide a Kanban board
onto which the issues were posted, moving them from 'Todo' to 'In Progress' to 'Done' as they 
were completed in turn. The iterations are documented here - [Iteration 1]

The User Epics and their related User Stories are as follows:
- Epic : [).
    - Story : [)
    - Story : [)

## Data Model

![Entity-relationship diagram for models]()

- Data validation

# Testing
- Manual testing
- Automated testing
- In-app testing
- User story testing
- Validator testing

---

## Manual Testing

### Feature Testing

|Page|Feature|Action|Effect|
|---|---|---|---|



### Responsiveness

### Browser Compatibility

| Feature | Chrome | Firefox | Safari(mobile) |
--- | --- | --- | --- | 

### Lighthouse

![loop_rating_page](media/docs/create_review_lighthouse_report.png)

### Code Validation

#### Python code : 
- All python code is validated by both the Flake8 linter (installed in VSCode) and the external CodeInstitute validator @ https://pep8ci.herokuapp.com/. The sole exceptions are the test classes, some of which contain
JavaScript snippets which are more readable if confined to one line.

#### JavaScript code :
- All JavaScript code in the project was validated during development with the JSHint plugin for VSCode.

#### HTML Validation :
- All HTML files in the project were validated using the W3C Narkup Validation Service.
https://validator.w3.org/

#### CSS Validation :
- No errors were found when the single CSS file style.css was passed through the W3C Validation Service.
https://jigsaw.w3.org/css-validator/


### User Stories
The User Epics and Stories in this project are documented in three GitHub Projects, corresponding 
to the iterations that comprised the development work of the project. These can be found here :

- [Iteration 1]()

Alternitively, the Epics and Stories are individually linked here :

- [Epics and Stories](#development-process)

---

## Automated Testing

### Testing django views, models and forms.



[Return to top](#Strings_attached)

# Bugs

- A number of other bugs and their solution are documented in the issues tracker on GitHub, such as :
    - https://github.com/
    
## Remaining Bugs
There are (hopefully) no remaining bugs in the project.

[Return to top](#Strings_attached)

# Libraries and Programs Used
1. [Lucid](https://www.lucidchart.com/pages/)
    - Lucid charts were used to create the execution path diagrams.
2. [Heroku](https://www.heroku.com/)
    - Heroku was used to deploy the project
3. [Git](https://git-scm.com/)
    - Version control was implemented using Git through the Github terminal.
4. [Github](https://github.com/)
    - Github was used to store the projects after being pushed from Git and its cloud service [Github Pages](https://pages.github.com/) was used to serve the project on the web. GitHub Projects was used to track the User Stories, User Epics, bugs and other issues during the project.
5. [Visual Studio Code](https://code.visualstudio.com/)
    - VS Code was used locally as the main IDE environment, with the JSHint and Flake8 linters installed for JavaScript and Python code validation respectively.
6. [pytest](https://docs.pytest.org/en/7.1.x/)
    - Pytest was used for automated testing.
7. [GIMP](https://www.gimp.org/)
    - The GIMP graphic editing package was used to manipulate and export all images used in the project.
8. [tooltip-sequence](https://github.com/SoorajSNBlaze333/tooltip-sequence)
    - A handy javascript/css library for creating a sequence of modal tooltips, used in this project 
    to create instructions for the Loop Editor.
# Deployment

## Setting up a cloudinary account for static storage.

## Deploying the app on Heroku
1. Log into Heroku and navigate to the Dashboard.
2. Click on the 'New' button.
3. Choose a unique app name, and select the region closest to you.
4. Create a database on Heroku (I elected to stay on Heroku and pay the monthly fee)
    - Click on the Resources tab.
    - Click the Find more add-ons button.
    - Select Heroku Postgres, and click on Install Heroku Postgres.
    - Select a plan (default = Mini @ $5.00 a month, which I'm using), and select your app.
    - Return to Resources tab and click on the Heroku Postgres icon, then select the settings tab and click on Database Credentials. Copy the URI to your clipboard. Paste it to your env.py file using the key "DATABASE_URL". This will allow you to use the same database for development and production.
5. Click the settings tab on the Dashboard, and click the button to Reveal Config Vars. Your database url should be populated here already. Add your Django secret key and your Cloudinary URL (see 1st section above) to the config variables.
Set the PORT to 8000. I also have a GOOGLE-API-KEY config variable to enable Social-Sign-In with Google.
6. In your local repository, add a Procfile to the root directory of the project, containing the following line :<br /> `web: gunicorn JUST_BEATS.wsgi`.
7. Add the url of your Heroku project to the `ALLOWED_HOSTS` list in `settings.py`.
8. Set DEBUG to False, and commit your changes and push to GitHub.
9. In Heroku, navigate to the Settings Tab, and within this the Buildpacks section, and click on Add Buildpack. Select the python buildpack, and save changes.
10. On the Dashboard, select the Deploy tab, and under the Deployment Method heading, select the
GitHub icon to connect your Heroku project to your GitHub repo. Enter your repository name in the text input, and click Search, and then when your repo appears, click Connect.
11. Under the Manual deploy section, click Deploy Branch. You should receive this message - 'Your app was successfully deployed". Click view to see the app running in the browser.

## Making a local clone
1. Open a terminal/command prompt on your local machine.
2. Navigate to the folder on your local machine where you would like to clone the project.
3. Enter the command : `git clone 'https://github.com/johnrearden/just-beats.git'`

## Running the app in your local environment
1. Create a virtual enviroment in the new project folder using the command `python3 -m venv venv`
2. Activate the virtual environment : `source venv/bin/activate`
3. Install the project requirements : `pip3 install -r requirements.txt`
4. Create an env.py file containing the following variables (see env.example.py in the root directory of the project for a complete list of variables necessary to run the app) :
    - DATBASE_URL : This is the url generated by Heroku - see [Deploying the app](#deploying-the-app-on-heroku)
    - SECRET_KEY : This is the Django secret key. Choose your own and add it both here and to the Heroku config vars.
    - CLOUDINARY_URL : This is the Cloudinary url set up above.
    - JUST-BEATS-GOOGLE-API-KEY - You need a Google cloud account to get the API key for social sign in.
    - SELENIUM_TEST_USERNAME, SELENIUM_TEST_PASSWORD, SELENIUM_FIXTURE_USERNAME, SELENIUM_FIXTURE_PASSWORD: 
        If you are the project assessor, these settings can be accessed through Code Institute. They are required to run the Selenium tests using the fixtures included in the project. Standard Django automated tests do not require these variables to run.

## Testing the app locally
1. Open a terminal and enter the command : `python3 manage.py test`. Testing the front-end with Selenium requires (on a linux system) requires both Chromium and chromedriver to be installed, and chromedriver must be added to the PATH variable. chromedriver version should match the version of Chrome installed on the system: most recent versions can be found here - https://chromedriver.chromium.org/downloads
2. To test only the Django code, enter the command : <br/>`python3 manage.py test beats_app.test_views beats_app.test_models beats_app.test_forms`

[Return to top](#Strings_attached)
# Credits
Structure of extensible base.html page largely copied from Boutique Ado Walkthrough
https://github.com/Code-Institute-Solutions/boutique_ado_v1/blob/250e2c2b8e43cccb56b4721cd8a8bd4de6686546/templates/base.html
Hero image of guitar on guitar stand - Kelvin Franca on Pexels
https://www.pexels.com/@kelvinernandi/
Truncate text in a paragraph tag in html
https://stackoverflow.com/questions/47761085/how-can-i-set-a-character-limit-for-paragraph
Remove up and down arrows from number input
https://www.geeksforgeeks.org/how-to-disable-arrows-from-number-input/


# Acknowledgements

I'd like to acknowledge the invaluable assistance I received from my tutor, Celestine Okoro, 
and the advice and encouragement I received from my cohort coordinators Kenan Wright and Kasia Bogucka.
Thanks also to my fellow students whose help in our weekly stand-ups made a big difference.

[Return to top](#Strings_attached)
