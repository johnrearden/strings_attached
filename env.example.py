
import os

os.environ["DATABASE_URL"] = ""
os.environ["SECRET_KEY"] = ""
os.environ["DEBUG"] = 'True'
os.environ["EMAIL_APP_PASSWORD"] = ""
os.environ["EMAIL_APP_USER"] = ""
os.environ["STRIPE_PUBLIC_KEY"] = ""
os.environ["STRIPE_PRIVATE_KEY"] = ""
os.environ['STRIPE_WEBHOOK_SECRET'] = ""
os.environ['BASE_URL'] = 'http://localhost:8000'
os.environ['AWS_ACCESS_KEY_ID'] = ""
os.environ['AWS_SECRET_ACCESS_KEY'] = ""
