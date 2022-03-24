from flask_celery import make_celery
from smtplib import SMTPAuthenticationError, SMTPServerDisconnected, SMTPException
from decouple import config
from flask_mail import Mail, Message
# from temp.t_configs import createapp
import time

'''
If using SSL/TLS directly with MAIL_USE_SSL = True, then use MAIL_PORT = 465
If using STARTTLS with MAIL_USE_TLS = True, then use MAIL_PORT = 587
'''

from flask import Flask
app = Flask(__name__)



app.config['MAIL'] = 1
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'joseph.reymond@tatacommunications.com'
app.config['MAIL_PASSWORD'] = config('KEY')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379',
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
app.config['SENDER_1'] = 'joseph.reymond@tatacommunications.com'


celery = make_celery(app)
mail = Mail(app)


@celery.task()
def mailtask():
    return send_mail_to_user()


@celery.task()
def createmail():
    return send_mail_to_user()


def send_mail_to_user():
   msg = Message(subject='msg from joseph', sender = app.config['SENDER_1'], recipients = ['joseph.reymond'])
   msg.body = "Hello Flask message sent from Flask-Mail"
   retcode = 0
   # mail.send(msg)
   if app.config['MAIL']:
      try:
         mail.send(msg)
         print(app.import_name)
         print(app.name)
      except SMTPAuthenticationError as e:
         print(e)
         retcode = 2
      except SMTPServerDisconnected as e:
         print(e)
         retcode = 3
      except SMTPException as  e:
         print(e)
         retcode = 1
   else:
      print(msg.html)

   if retcode:
      app.logger.error(retcode)

   print(mail.state)
   return 'mail sent' if retcode == 0 else 'mail not sent'


@app.route("/")
def index():
   start_time = time.time()
   status = send_mail_to_user()                    #blocking method
   # status = mailtask().delay()          # celery call calls this method in another process
   print('time taken {} seconds'.format(round(time.time() - start_time, 3)))
   return status



if __name__ == '__main__':
   # start redis server
   # start celery worker  celery -A appname.celery worker
   app.run(debug = True)


