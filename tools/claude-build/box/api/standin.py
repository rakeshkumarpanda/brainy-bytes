"""A local stand-in for the Claude Messages API, used so the SDK examples can run without a key.
Its replies are scripted from replies.json. They are not written by Claude."""
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPT = json.load(open('replies.json')) if os.path.exists('replies.json') else {}
COUNTER = {'n': 0}


def text_of(content):
    if isinstance(content, str):
        return content
    return ' '.join(b.get('text', '') if b.get('type') == 'text' else json.dumps(b.get('content', b.get('input', ''))) for b in content)


def tokens(s):
    return max(1, round(len(s) / 4))


def choose(body):
    last = body['messages'][-1]
    content = last['content']
    results = [b for b in content if isinstance(b, dict) and b.get('type') == 'tool_result'] if isinstance(content, list) else []
    if results:
        joined = '\n'.join(r['content'] if isinstance(r['content'], str) else text_of(r['content']) for r in results)
        return [{'type': 'text', 'text': SCRIPT.get('after_tool', 'Done: {result}').format(result=joined)}], 'end_turn'
    said = text_of(content).lower()
    if body.get('tools'):
        for key, call in SCRIPT.get('tool_calls', {}).items():
            if key in said:
                calls = call if isinstance(call, list) else [call]
                blocks = [{'type': 'text', 'text': SCRIPT.get('before_tool', 'Let me check.')}]
                for c in calls:
                    COUNTER['n'] += 1
                    blocks.append({'type': 'tool_use', 'id': f'toolu_standin_{COUNTER["n"]}', 'name': c['name'], 'input': c['input']})
                return blocks, 'tool_use'
    for key, reply in SCRIPT.get('replies', {}).items():
        if key in said:
            return [{'type': 'text', 'text': reply}], 'end_turn'
    return [{'type': 'text', 'text': SCRIPT.get('default', 'Hello! (stand-in reply)')}], 'end_turn'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['content-length'])))
        blocks, stop = choose(body)
        prompt = (text_of(body['system']) if body.get('system') else '') + ' '.join(text_of(m['content']) for m in body['messages'])
        prompt += json.dumps(body.get('tools', ''))
        usage = {'input_tokens': tokens(prompt), 'output_tokens': sum(tokens(json.dumps(b)) for b in blocks), 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0}
        if os.environ.get('STANDIN_LOG'):
            print(f"   [API request: {len(body['messages'])} message(s), {len(body.get('tools', []))} tool(s), stream={bool(body.get('stream'))}]", flush=True)
        msg = {'id': 'msg_standin', 'type': 'message', 'role': 'assistant', 'model': body['model'], 'content': blocks,
               'stop_reason': stop, 'stop_sequence': None, 'usage': usage}
        if not body.get('stream'):
            data = json.dumps(msg).encode()
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.send_header('content-length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(200)
        self.send_header('content-type', 'text/event-stream')
        self.end_headers()

        def ev(name, payload):
            self.wfile.write(f'event: {name}\ndata: {json.dumps({"type": name, **payload})}\n\n'.encode())
            self.wfile.flush()
        ev('message_start', {'message': {**msg, 'content': [], 'stop_reason': None, 'usage': {'input_tokens': usage['input_tokens'], 'output_tokens': 1}}})
        for i, b in enumerate(blocks):
            if b['type'] == 'text':
                ev('content_block_start', {'index': i, 'content_block': {'type': 'text', 'text': ''}})
                words = b['text'].split(' ')
                for j, w in enumerate(words):
                    ev('content_block_delta', {'index': i, 'delta': {'type': 'text_delta', 'text': w + (' ' if j < len(words) - 1 else '')}})
            else:
                ev('content_block_start', {'index': i, 'content_block': {**b, 'input': {}}})
                ev('content_block_delta', {'index': i, 'delta': {'type': 'input_json_delta', 'partial_json': json.dumps(b['input'])}})
            ev('content_block_stop', {'index': i})
        ev('message_delta', {'delta': {'stop_reason': stop, 'stop_sequence': None}, 'usage': {'output_tokens': usage['output_tokens']}})
        ev('message_stop', {})


def start():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    os.environ['ANTHROPIC_BASE_URL'] = f'http://127.0.0.1:{server.server_address[1]}'
    os.environ.setdefault('ANTHROPIC_API_KEY', 'standin-key')
    return server
