import smtplib, json, os, logging
from datetime import datetime
from configparser import ConfigParser

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

os.chdir('/home/pi/Documents/PythonProjects/')

config = ConfigParser()
config.read("EKS/settings.ini")
logging.basicConfig(filename='EKS/eks.log', level=logging.DEBUG)

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.


def read_data():

    file = min(os.listdir('EKS/Data'))
    f = open('EKS/Data/' + file)

    x = json.load(f)[file]['details']
    ID_zakazky = x['ID_zakazky']
    url = x['url']
    nazov = x['nazov']
    CPV= x['CPV']
    vyska_zdrojov = x['vyska zdrojov']+'€'
    termin_ponuky = x['termin ponuky']

    return [ID_zakazky, nazov, CPV, vyska_zdrojov, termin_ponuky, url]


# Create the body of the message (a plain-text and an HTML version).


def send_mail():
    to = config['DEFAULT']['recipients'].split(',')
    login_user = config['DEFAULT']['login_user']
    login_user_pwd = config['DEFAULT']['login_user_pwd']
    smtpserver = smtplib.SMTP(config['DEFAULT']['smtp_server'])
    logging.info(str(datetime.now()) + '  {} {} {} : smtp. login data\n'.format(login_user, login_user_pwd, smtpserver))

    smtpserver.login(login_user, login_user_pwd)
    logging.info(str(datetime.now()) + ' : smtp. login successful\n')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = read_data()[0] + ', ponuka do: ' + read_data()[4][:10]
    msg['From'] = login_user
    msg['To'] = to[0]

    text = str(read_data())
    part1 = MIMEText(text, 'plain')

    html = """\
    <html>
      <head></head>
      <body>
        <table border="1" cellpadding="2" cellspacing="2">
          <tbody>
            <tr>
              <td valign="top" align="center">ID zákazky<br></a></td>
              <td valign="top" align="center">názov<br></td>
              <td valign="top" align="center">CPV<br></td>
              <td valign="top" align="center">Výška zdrojov<br></td>
              <td valign="top" align="center">Termín ponuky</td>
            </tr>
              <tr>
              <td valign="top" align="left"><a href={url}>{ID_zakazky}<br></a></td>
              <td valign="top" align="left">{nazov}<br></td>
              <td valign="top" align="left">{CPV}<br></td>
              <td valign="top" align="left">{vyska_zdrojov}<br></td>
              <td valign="top" align="left">{termin_ponuky}</td>
              </tr>
      </body>
    </html>
    """.format(url=read_data()[5],
               ID_zakazky=read_data()[0],
               nazov=read_data()[1],
               CPV=read_data()[2],
               vyska_zdrojov=read_data()[3],
               termin_ponuky=read_data()[4])
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    smtpserver.sendmail(login_user, to, msg.as_string())
    item = min(os.listdir('EKS/Data'))
    logging.info(str(datetime.now()) + ' : ' + item + ' sent to:'+str(to)+'\n')
    smtpserver.quit()
    logging.info(str(datetime.now()) + ' : connection to the server closed\n')

