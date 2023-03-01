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
### Products App
![Entity-relationship diagram for models](docs/products_app_db_schema.png)

### Checkout App
![Entity-relationship diagram for models](docs/checkout_app_db_schema.png)

- Data validation

# Payments Integration

In thinking about the payment integration, I decided to try to decouple the Django backend from Stripe
as much as possible, to make it easier to switch to a different payment processor without having to rewrite the app. To this end, the payment flow is as follows.
    
    - When the user clicks the Pay Now button, the order is posted to the backend and saved, with the payment_confirmed flag set to False. The The newly generated order number is returned to the page in
    the ensuing response.
    - The event handler then 

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
## Stripe Webhook Testing


### Stripe Payment Flow
The payment flow handling differs from the Boutique Ado project. I decided that the application would be more robust if orders were saved to the database _before_ the Stripe payment process was initiated, with a flag, 
payment_confirmed set to false. This ensures that any order made is recorded before the network back and forth begins. It also allows the application to send the order_number field from the order instance to Stripe as metadata for later retrieval, so that the order does not need to be built from the basket contents. When the Stripe confirmPayment method (called from stripe_payments.js) promise is fulfilled, the front-end then sends a POST request back to the endpoint, which sets the payment_confirmed flag to True. 

In the event that the promise is rejected, or the POST request fails, the Stripe webhook event (stripe.payment_intent.succeeded) will pass the metadata back to the webhook handler. If the order is present in the database, the handler ensures that the payment_confirmed flag is set to True. If it is not present, the handler will construct a new order from the basket information encoded in the metadata as an insurance policy.

Another advantage of this approach is that orders whose payments are not processed remain on the system, and can be retrieved by staff and users if necessary at a later point (although this is not implemented in the project).

### Webhook Tests
The application listens for 5 Stripe webhook events, and takes appropriate action based on each. The events
were tested by adding a local listener on the dashboard webhook page, which forwards the webhook events
to the development server on localhost:8000. The webhook for the deployed project on Heroku was disabled for these tests, as the deployed and development versions of the project both use the production database. Tests for each webhook are manual rather than automated.

- stripe.payment_intent.succeeded:
    - The handler retrieves the order_number from the event metadata and checks that the order exists. If
    so, it ensures that the payment confirmed flag is set to True. This was tested by commenting out the code in checkout.views.PaymentConfirmedView that sets the flag to True and then, after the payment has been processed and the webhook event received, checking the flag in the admin panel. Results as follows :
        - With webhook forwarding disabled : payment_confirmed flag is False
        - With webhook forwarding enabled : payment_confirmed flag is True.
    So, the handler is working correctly when an order is already on the system. Next the code in the handler is altered by setting the value of the result_set returned by the search to None, creating an order on the site and then initiating a payment. This should result in a duplicate order being created, the same in all respects as the original except for its order_number. The results were as follows : 
        - With webhook forwarding disabled : Only one order exists in the database.
        - With webhook forwarding enabled : A duplicate order also exists in the database.
    So, we can conclude that this webhook handler is working as intended.

- stripe.payment_intent.payment_failed
    - This handler just returns a HTTP 200 response code to Stripe. The stripe webhook dashboard confirmed that
    the event had been fired and that the 200 response had been received.

- stripe.checkout.session.completed
    - Unlike the payment_intent.succeeded webhook, this hook plays a crucial role in confirming a subscription payment has been processed by Stripe, as it is the only means by which notice of a successful payment will be sent. We need to confirm that subscriber flag is set to True, and that the stripe_customer_id and stripe_subscription_id fields are set correctly on the UserOrderProfile record. The test consists of examining the UserOrderProfile record created when the user chooses a subscription plan, and comparing it with the same record after the payment has been processed. Results as follows (with invoice_paid webhook disabled in order to isolate this webhook) :
        - With webhook forwarding disabled : subscriber flag set to False, stripe_subscription_id and stripe_customer_id fields unfilled.
        - With webhook forwarding enabled : subscriber flag set to True, stripe_subscription_id and stripe_customer_id filled correctly (compared to stripe webhook event detailed on dashboard).
    So, we can conclude that this handler is working correctly.

- stripe.invoice_paid
    - This handlers task is simply to set the UserOrderProfile's subscription_paid flag to True, so
    that the subscription is live and all video content is available to the user. The test consists of checking the UserOrderProfile record before proceeding to process payment for a subscription, and confirming that the flag is set afterwards. Results as follows :
        - With webhook forwarding disabled : subscription_paid flag set to False following payment.
        - With webhook forwarding enabled : subscription_paid flag set to True following payment.

- stripe.invoice.payment_failed
    - This handler sets the subscription_paid flag to false when it is received. Unfortunatly it is not possible to trigger this webhook either from the Stripe dashboard or from the CLI, so the only way to test it is to supply stripe with a test card with a short expiration date, and wait for the subscription period to end and the test to fail! A bit of research uncovered [this project](https://github.com/stripe/stripe-mock), released by Stripe, but the time required to get the mock HTTP server up and running and the fact that it is stateless anyway(the responses to mock API calls are hardcoded) means that I'll reluctantly have to leave this handler untested. In a production situation, I would set up a fake product on the backend and a corresponding product on the Stripe dashboard with a subscription period of 1 day (the shortest option Stripe currently offers) and show up punctually to observe the handler fire 24 hours later.
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

Combining querysets in Django
https://stackoverflow.com/questions/431628/how-to-combine-multiple-querysets-in-django

Testing in Django
https://realpython.com/testing-in-django-part-1-best-practices-and-examples/

Email send test not working because of missing User email field
https://stackoverflow.com/questions/39493749/django-tests-for-sending-email

Generate database schema diagram from project models
https://django-extensions.readthedocs.io/en/latest/graph_models.html

Make a Django class based view CSRF exempt
https://www.programmersought.com/article/2914850608/

Testing a DoesNotExist exception on a query
https://stackoverflow.com/questions/11109468/how-do-i-import-the-django-doesnotexist-exception

Mocking stripe methods in a view to enable testing
https://stackoverflow.com/questions/31284622/mock-stripe-methods-in-python-for-testing


# Acknowledgements

I'd like to acknowledge the invaluable assistance I received from my tutor, Celestine Okoro, 
and the advice and encouragement I received from my cohort facilitators Kenan Wright, Kasia Bogucka, and Paul O'Donnell.
Thanks also to my fellow students whose help in our weekly stand-ups made a big difference.

[Return to top](#Strings_attached)
