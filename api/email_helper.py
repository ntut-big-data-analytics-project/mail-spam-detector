# coding=utf-8

import email
import re
from email.header import decode_header

import chardet
import jieba
import zhconv
from bs4 import BeautifulSoup

EMAIL_CONTENT_DELIMITER = "/ "

NOT_ALLOW_CHAR = re.compile(u"[^\u4e00-\u9fffa-zA-Z0-9,.\s]")
SYMBOL_RE = re.compile(u"[.,\[\]@\s:()\r\n\-]+")
SPACE_RE = re.compile("^\s+$")
ENCODING_RE = re.compile(r"content-type(.*?);(\s+)?charset(\s+)?=(\s+)?['\"]?([a-zA-Z0-9\-]+)['\"]?(\s|$)",
                         re.IGNORECASE | re.MULTILINE)

ENCODING_RE2 = re.compile(r"Subject:(\s+)?=\?([a-zA-Z0-9\-]+)\?", re.IGNORECASE | re.MULTILINE)

UNICODE_ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}", re.IGNORECASE | re.MULTILINE)

_SHOULD_DECODED_ENCODING = {'quoted-printable', 'base64', 'x-uuencode', 'uuencode', 'uue', 'x-uue'}


def split_words(txt: str):
    txt = txt.replace("\ufffd", "").replace("\\ufffd", "")
    txt = re.sub(UNICODE_ESCAPE_RE, "", txt)
    txt = re.sub(SYMBOL_RE, " ", txt)
    txt = re.sub(NOT_ALLOW_CHAR, "", txt)
    txt = txt.strip()
    iterator = jieba.cut(txt)
    return list(filter(lambda s: SYMBOL_RE.match(s) is None, iterator))


def get_mail_content(msg):
    if isinstance(msg, list):
        return ' '.join(map(get_mail_content, msg))
    else:
        content_charset = msg.get_content_charset()
        content_type = msg.get_content_type()
        content_text = ''

        if (not content_type.startswith("multipart/")) and (not content_type.startswith("text/")):
            return ""

        try:
            if msg.get('content-transfer-encoding') in _SHOULD_DECODED_ENCODING:
                content_text = msg.get_payload(decode=True).decode(content_charset)
            else:
                content_text = msg.get_payload(decode=False)
        except:
            content_text = msg.get_payload(decode=False)

        if content_type == 'text/plain':
            return content_text
        elif content_type == 'text/html':
            html_instance = BeautifulSoup(content_text, 'html5lib')
            [s.decompose() for s in html_instance(['script', 'style'])]
            return str(html_instance.getText())
        else:
            payload = msg.get_payload(decode=False)
            if isinstance(payload, list):
                return get_mail_content(payload)
            return payload


def read_email(file_path, raw=False):
    if raw:
        return email.message_from_string(file_path)

    fp = open(file_path, 'rb')
    try:
        eml_content_bytes = fp.read()
        fp.close()
        guessed_encoding = chardet.detect(eml_content_bytes)
        used_encoding = guessed_encoding['encoding']
        if guessed_encoding['confidence'] < 0.87:
            email_content_ascii = str(eml_content_bytes, 'ascii', errors='ignore')
            m = ENCODING_RE.search(email_content_ascii)
            if m is not None:
                m_list = m.groups()
                if len(m_list) >= 5:
                    used_encoding = m_list[4]
            else:
                m = ENCODING_RE2.search(email_content_ascii)
                if m is not None:
                    m_list = m.groups()
                    if len(m_list) >= 2:
                        used_encoding = m_list[1]

            if used_encoding is None:
                used_encoding = 'utf-8'

        eml_content = str(eml_content_bytes, encoding=used_encoding, errors='ignore')
        return email.message_from_string(eml_content)
    except Exception as e:
        print(file_path, e)
        return None


def get_recipients(to_txt):
    recipients = []
    if to_txt is None:
        return recipients

    for recipient in to_txt.split(", "):
        i = recipient.find("<")
        if i == -1:
            recipients.append(recipient)
        else:
            i += 1
            j = recipient.find(">", i)
            recipients.append(recipient[i:j])
    return recipients


def extract_email_content_as_list(file_path, raw=False):
    try:
        text_list = []
        msg = read_email(file_path, raw)
        recipients = get_recipients(msg['To'])
        text_list.extend(recipients)

        subject, charset = decode_header(msg['SUBJECT'])[0]

        if charset:
            subject = subject.decode(charset, errors='ignore')
        else:
            if isinstance(subject, bytes):
                subject = str(subject, errors='ignore')

        subject = split_words(subject)
        # print(subject)
        text_list.extend(subject)
        content = ""
        if msg.is_multipart():
            content = get_mail_content(msg.get_payload())
        else:
            content = get_mail_content(msg)

        # print(content)
        results = split_words(content)
        # print(results)
        text_list.extend(results)
        return text_list
    except Exception as e:
        print(file_path, e)
        return []


def convert_all_text_to_zh_cn(str_list):
    return list(map(lambda txt: zhconv.convert(txt, 'zh-cn'), str_list))


def process_email(file_path):
    data = extract_email_content_as_list(file_path)
    return convert_all_text_to_zh_cn(data)


def process_email_content(eml_content):
    data = extract_email_content_as_list(eml_content, raw=True)
    return convert_all_text_to_zh_cn(data)
