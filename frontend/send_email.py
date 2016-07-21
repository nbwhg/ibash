#!/usr/bin/env python
# -*- coding: utf-8 -*-

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib, sys
from ibash import settings

# if len(sys.argv) < 5:
#    print '%s to_address to_name email_content email_subject' % sys.argv[0]
#    sys.exit(1)

class Email(object):
    def __init__(self,to_name, to_addr):
        self.__from_addr = settings.EMAIL_USER
        self.__password = settings.EMAIL_PWD
        self.__smtp_server = settings.EMAIL_SER
        self.__smtp_port = int(settings.EMAIL_PORT)
        self.__to_addr = to_addr
        self.__to_name = to_name

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr(( \
            Header(name, 'utf-8').encode(), \
            addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    def Send(self, email_content, email_subject):
        msg = MIMEText(email_content, 'plain', 'utf-8')
        msg['From'] = self._format_addr(u'iBash爱运维网站 <%s>' % self.__from_addr)
        msg['To'] = self._format_addr(u'%s <%s>' % (self.__to_name, self.__to_addr))
        msg['Subject'] = Header(u'%s' % email_subject, 'utf-8').encode()
        server = smtplib.SMTP(self.__smtp_server, self.__smtp_port)
        # server.set_debuglevel(1)
        server.login(self.__from_addr, self.__password)
        server.sendmail(self.__from_addr, [self.__to_addr], msg.as_string())
        server.quit()

#if __name__ == '__main__':
#    test = email(u'张三', 'xxxx@xxxx.xxx')
#    content = u'这是一封测试邮件,请忽略,勿回复,多谢!'
#    subject = u'测试邮件'
#    test.Send(content, subject)