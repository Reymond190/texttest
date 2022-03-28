import os
import random
import time
from smtplib import SMTPAuthenticationError, SMTPServerDisconnected, SMTPException

from decouple import config
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from flask_mail import Mail, Message
from celery import Celery


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL'] = 1
# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'edwardsteve2011@gmail.com'
app.config['MAIL_PASSWORD'] = config('KEY')
app.config['MAIL_DEFAULT_SENDER'] = 'edwardsteve2011@gmail.com'
app.config['SENDER_1'] = 'edwardsteve2011@gmail.com'
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
celery.send_task('test_server', queue='queue3')

celery.conf.beat_schedule = {
    "run_every_10_secs": {
        "task": "run_every_10_secs",
        "schedule": 10.0,
        'options': {'queue' : 'queue1'}
    },
}

@celery.task(name='run_every_10_secs')
def run_every_10_secs():
    with app.app_context():
        print('hi hellow how are you')





def send_mail_to_user():
   msg = Message(subject='msg from joseph', sender = app.config['SENDER_1'], recipients = ['josephreymond2011@gmail.com'])
   msg.body = "Hello Flask message sent from Flask-Mail"
   retcode = 0
   # mail.send(msg)

   with app.app_context():
       mail.send(msg)

   if retcode:
      app.logger.error(retcode)

   print(mail.state)
   return 'mail sent' if retcode == 0 else 'mail not sent'

@celery.task(queue='queue1')
def mailtask():
    return send_async_email()


@app.route("/")
def index():
   start_time = time.time()
   status = ""
   # status = send_mail_to_user()                    #blocking method
   mailtask.delay()       # celery call calls this method in another process
   print('time taken {} seconds'.format(round(time.time() - start_time, 3)))
   return "sent" if status else "not sent"


# ------------
@celery.task(queue='queue1')
def send_async_email():
    """Background task to send an email with Flask-Mail."""
    msg = Message('sub',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=['josephreymond2011@gmail.com'])
    msg.body = 'hello'
    with app.app_context():
        mail.send(msg)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'GET':
#         return render_template('index.html', email=session.get('email', ''))
#     email = request.form['email']
#     session['email'] = email
#
#     # send the email
#     email_data = {
#         'subject': 'Hello from Flask',
#         'to': email,
#         'body': 'This is a test email sent from a background Celery task.'
#     }
#     if request.form['submit'] == 'Send':
#         # send right away
#         send_async_email.delay(email_data)
#         flash('Sending email to {0}'.format(email))
#     else:
#         # send in one minute
#         send_async_email.apply_async(args=[email_data], countdown=60)
#         flash('An email will be sent to {0} in one minute'.format(email))
#
#     return redirect(url_for('index'))


@app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}



if __name__ == '__main__':
    app.run(debug=True)


'''
send_async_email.apply_async(args=[email_data], countdown=60)
'''

'''

app.conf.beat_schedule = {
    "calc-ten-seconds-task": {
        "task": "calc_task",
        "schedule": 10.0,
        'options': {'queue' : 'queue2'}
    },

    "geofence": {
        "task": "geofence_checker",
        "schedule": 360.0,
        'options': {'queue' : 'queue4'}
    },
    #  default value for everyday-store:  crontab(minute=10,hour=0)
    'everyday-store': {
        'task': 'store_task',
        'schedule': crontab(minute=10,hour=0),
        'options': {'queue' : 'queue4'}
    },

    # CHANGE  invoicer FROM 0 - crontab(0, 0, day_of_month='1')
    'invoicer': {
        'task': 'invoicer',
        'schedule': crontab(0, 0, day_of_month='1'),
        'options': {'queue' : 'queue4'}
    },

    # CHANGE  invoice_warning FROM 0 - crontab(0, 0, day_of_month='1')
    'invoice_warning': {
            'task': 'invoice_warning',
            'schedule': crontab(0, 0, day_of_month='20'),
            'options': {'queue' : 'queue4'}
        },

    # CHANGE  invoice_warning FROM 0 - crontab(0, hour=3, day_of_month='1')
    'invoice_remove_access': {
            'task': 'invoice_remove_access',
            'schedule': crontab(0, 0, day_of_month='28'),
            'options': {'queue' : 'queue4'}
        },

    'change_lat_lon_to_address': {
        'task': 'change_lat_lon_to_address',
        "schedule": 360.0,
        'options': {'queue': 'queue5'}
    },

    'upload_fixtures_daily': {
            'task': 'upload_fixtures_daily',
            "schedule": crontab(minute=12,hour=0),
            'options': {'queue' : 'queue4'}
        },

# 'calc_task_mark1': {
#             'task': 'calc_task_mark1',
#             "schedule": 10,
#             'options': {'queue' : 'queue4'}
#         },

'process_and_store_reports': {
            'task': 'process_and_store_reports',
            "schedule": 500,
            'options': {'queue' : 'queue4'}
        },

}
'''
