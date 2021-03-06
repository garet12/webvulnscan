from ..utils import attack


@attack()
def utf7_check(client, log, page):
    if 'Content-Type' not in page.headers:
        return

    content_type = page.headers['Content-Type']

    if ';' not in content_type:
        return

    # Use Content-Type to get the charset
    charset = content_type.split(';')[1].split('=')[1]
    # If charset is not UTF-7 there is nothing to do
    if charset != 'utf-7' and charset != 'UTF-7':
        return
    else:
        # If charset is UTF-7 give warning
        log('vuln', page.url, 'UTF-7',
            'Website uses UTF-7')
