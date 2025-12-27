from urllib.parse import parse_qs

def app(environ, start_response):
    query_string = environ.get('QUERY_STRING', '')
    get_params = parse_qs(query_string)

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    
    request_body = environ['wsgi.input'].read(request_body_size)
    post_params = parse_qs(request_body.decode('utf-8'))

    status = '200 OK'
    headers = [
        ('Content-Type', 'text/plain; charset=utf-8')
    ]
    
    start_response(status, headers)

    output = [b"Hello form Gunicorn!\n\n"]
    
    output.append(b"--- GET parameters ---\n")
    for k, v in get_params.items():
        line = f"{k} = {v}\n"
        output.append(line.encode('utf-8'))
        
    output.append(b"\n--- POST parameters ---\n")
    for k, v in post_params.items():
        line = f"{k} = {v}\n"
        output.append(line.encode('utf-8'))

    return output