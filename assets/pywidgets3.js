/* ===== Complete Python animations, part 3: Web and APIs. See assets/pywidgets.js for the framework. ===== */

/* =====================================================================================================
   Web 1.1  one HTTP request and response, line by line: a GET, a POST that creates, a 404 and a cached 304
   ===================================================================================================== */
(() => {
  const { trace, head, D, box } = PYZ;
  const { rr } = AIZ;
  /* each step: [request lines so far, response lines so far, arrow ('', 'right', 'left', 'both', 'server'), arrow label, say] */
  const G = (req, res, arrow, label, say, hot) => ({ req, res, arrow, label, say, hot });
  const CASES = {
    get: () => {
      const R = ['GET /api/books/1 HTTP/1.1', 'Host: api.example.com', 'Accept: application/json', 'User-Agent: python-requests/2.32', ''];
      const S = ['HTTP/1.1 200 OK', 'Content-Type: application/json', 'Content-Length: 26', '', '{"id": 1, "title": "Dune"}'];
      return [
        G([], [], '', 'https://api.example.com/api/books/1', 'The program asks for <b>https://api.example.com/api/books/1</b>. The URL has a scheme (https), a host (api.example.com) and a path (/api/books/1).'),
        G([], [], 'right', 'DNS: api.example.com is 203.0.113.10', 'First the computer asks DNS, the phone book of the internet, for the IP address of the host.'),
        G([], [], 'both', 'TCP and TLS handshake on port 443', 'It opens a TCP connection to port 443 and does a TLS handshake, so everything after this is encrypted. This costs one or two round trips before any data moves.'),
        G(R.slice(0, 1), [], 'right', 'request line', 'The request starts with the <b>request line</b>: the method GET (read), the path, and the HTTP version.', 'req'),
        G(R.slice(0, 4), [], 'right', 'headers', '<b>Headers</b> add details, one "Name: value" per line. Host says which site, Accept says "please answer in JSON".', 'req'),
        G(R, [], 'right', 'blank line: end of headers', 'An empty line ends the headers. A GET has no body, so the request is complete.', 'req'),
        G(R, [], 'server', 'route /api/books/<id> to a function', 'The server matches the path to a function (a <b>route</b>), which finds book 1 in its database.'),
        G(R, S.slice(0, 1), 'left', 'status line', 'The answer starts with the <b>status line</b>. 200 OK means success. The number is for programs, the words are for people.', 'res'),
        G(R, S.slice(0, 3), 'left', 'response headers', 'Content-Type says the body is JSON. Content-Length says the body is 26 bytes, so the client knows where it ends.', 'res'),
        G(R, S, 'left', 'body', 'After a blank line comes the <b>body</b>. In Python, response.json() turns it into the dict {"id": 1, "title": "Dune"}.', 'res')
      ];
    },
    post: () => {
      const R = ['POST /api/books HTTP/1.1', 'Host: api.example.com', 'Content-Type: application/json', 'Content-Length: 17', '', '{"title": "Emma"}'];
      const S = ['HTTP/1.1 201 Created', 'Location: /api/books/3', 'Content-Type: application/json', '', '{"id": 3, "title": "Emma"}'];
      return [
        G(R.slice(0, 1), [], 'right', 'request line', '<b>POST</b> sends new data to the server. The path is the collection /api/books, not one book.', 'req'),
        G(R.slice(0, 4), [], 'right', 'headers', 'This time the request has a body, so it says what it is (Content-Type: application/json) and how long (17 bytes).', 'req'),
        G(R, [], 'right', 'body', 'The body is the JSON of the new book. requests writes all of this for you with requests.post(url, json={"title": "Emma"}).', 'req'),
        G(R, [], 'server', 'check the JSON, save, new id 3', 'The server checks that the body is valid JSON with a title, saves it and gives it the next free id, 3.'),
        G(R, S.slice(0, 1), 'left', 'status line', '<b>201 Created</b> is more exact than 200: something new now exists.', 'res'),
        G(R, S.slice(0, 2), 'left', 'Location header', 'The <b>Location</b> header tells the client the address of the new book.', 'res'),
        G(R, S, 'left', 'body', 'The body shows the saved book with its id. Sending the same POST again would make a SECOND book: POST is not <b>idempotent</b>.', 'res')
      ];
    },
    notfound: () => {
      const R = ['GET /api/books/99 HTTP/1.1', 'Host: api.example.com', 'Accept: application/json', ''];
      const S = ['HTTP/1.1 404 Not Found', 'Content-Type: application/json', 'Content-Length: 30', '', '{"error": "book 99 not found"}'];
      return [
        G(R, [], 'right', 'request', 'The client asks for book 99.', 'req'),
        G(R, [], 'server', 'no book 99 in the database', 'The route works, but there is no book with id 99.'),
        G(R, S.slice(0, 1), 'left', 'status line', '<b>404 Not Found</b>. Codes from 400 to 499 mean the CLIENT asked for something wrong. From 500 to 599 the SERVER failed.', 'res', true),
        G(R, S, 'left', 'error body', 'A good API also sends a JSON error message. Note: HTTP itself worked fine. The request did not raise any Python error, so your code must check the status.', 'res', true),
        G(R, S, '', 'requests: response.raise_for_status()', 'With requests, response.raise_for_status() turns a 4xx or 5xx status into an HTTPError exception, so errors cannot be missed by accident.', 'res', true)
      ];
    },
    cache: () => {
      const R1 = ['GET /logo.png HTTP/1.1', 'Host: example.com', ''];
      const S1 = ['HTTP/1.1 200 OK', 'Cache-Control: max-age=60', 'ETag: "v7"', '', '(12,000 bytes of picture)'];
      const R2 = ['GET /logo.png HTTP/1.1', 'Host: example.com', 'If-None-Match: "v7"', ''];
      const S2 = ['HTTP/1.1 304 Not Modified', 'ETag: "v7"', '', '(no body)'];
      return [
        G(R1, S1, 'both', 'first visit: full answer', 'The first time, the server sends the picture with two caching headers. <b>Cache-Control: max-age=60</b> means "you may keep this for 60 seconds". The <b>ETag</b> is a version label.', 'res'),
        G([], [], '', 'within 60 s: no request at all', 'For the next 60 seconds the browser uses its own copy. No request is sent, which is the fastest request of all.'),
        G(R2, [], 'right', 'after 60 s: ask "still version v7?"', 'After 60 seconds the copy is old, but maybe still right. The browser asks with <b>If-None-Match: "v7"</b>.', 'req'),
        G(R2, S2, 'left', '304: keep using your copy', 'The picture has not changed, so the server answers <b>304 Not Modified</b> with no body. Only a few hundred bytes travel instead of 12,000.', 'res')
      ];
    }
  };
  trace('pyhttp', {
    title: 'One HTTP request and its response',
    sub: 'Pick a case. Each step adds one line of the real text that travels between the program and the server.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Case', type: 'select', v: 'get', opts: [['get', 'GET a book (200 OK)'], ['post', 'POST a new book (201 Created)'], ['notfound', 'A missing book (404)'], ['cache', 'Caching with ETag (304)']] }],
    tips: [
      { t: 'GET: DNS, handshake, request line, headers, then the answer.', set: { case: 'get' }, play: true },
      { t: 'POST: a request with a body creates something new.', set: { case: 'post' }, play: true },
      { t: '404: HTTP worked, but the status says it went wrong.', set: { case: 'notfound' }, play: true },
      { t: '304: the cheapest answer is "you already have it".', set: { case: 'cache' }, play: true }
    ],
    frames(p) { return CASES[p.case](); },
    paint(z, f) {
      const c = z.col, g = z.g;
      box(z, 16, 22, 150, 54, 'Python program', { s: 13, b: true, stroke: f.hot === 'req' || f.arrow === 'right' ? c.cv : c.line });
      box(z, 434, 22, 150, 54, 'Server', { s: 13, b: true, stroke: f.arrow === 'server' || f.arrow === 'left' ? c.orange : c.line });
      const y = 49;
      if (f.arrow === 'right' || f.arrow === 'both') D.arrow(g, 172, y - 6, 428, y - 6, c.cv, 2.5, 8);
      if (f.arrow === 'left' || f.arrow === 'both') D.arrow(g, 428, y + 6, 172, y + 6, c.orange, 2.5, 8);
      if (f.arrow === 'server') rr(g, 430, 18, 158, 62, 10, { stroke: c.orange, w: 3 });
      if (f.label) D.text(g, f.label, 300, 96, { a: 'center', s: 12, b: true, c: f.arrow === 'left' ? c.orange : c.cv });
      const panel = (x, title, lines, col, bad) => {
        head(z, title, x, 124);
        rr(g, x, 132, 278, 256, 8, { fill: c.dark ? '#0b1220' : '#111827', stroke: bad ? c.red : c.line, w: bad ? 2 : 1 });
        lines.forEach((ln, i) => {
          const s = ln === '' ? '(blank line)' : ln;
          D.text(g, s, x + 10, 156 + i * 21, { s: PYZ.fit ? PYZ.fit(g, s, 258, 11.5, { mono: true }) : 11, mono: true, c: ln === '' ? '#6b7280' : (i === lines.length - 1 ? col : '#e5e7eb') });
        });
      };
      panel(16, 'Request (program to server)', f.req, '#93c5fd');
      panel(306, 'Response (server to program)', f.res, '#fdba74', f.hot === 'res' && f.res.length && /^HTTP\/1.1 4/.test(f.res[0]));
    }
  });
})();

/* =====================================================================================================
   Web 1.2  sockets as a timeline: the TCP handshake and close, a byte stream with no message borders,
   a lost TCP segment that is sent again, and UDP datagrams with no handshake and no resend
   ===================================================================================================== */
(() => {
  const { trace, D, box } = PYZ;
  /* a row: dir ('cs' client to server, 'sc' server to client, '' no arrow), label on the arrow,
     left = what the client program calls, right = what the server program calls, lost = the packet never arrives */
  const R = (dir, label, left, right, say, lost) => ({ dir, label, left, right, say, lost });
  const CASES = {
    tcp: [
      R('', '', '', 'socket(), bind(), listen()', 'The server makes a socket, <b>binds</b> it to a port (here 8000) and calls <b>listen()</b>. Now it waits in <b>accept()</b> for clients.'),
      R('cs', 'SYN  seq=100', 'create_connection()', '', 'The client calls <b>socket.create_connection(("server", 8000))</b>. TCP sends a <b>SYN</b> packet: "I want to talk, my numbers start at 100".'),
      R('sc', 'SYN-ACK  seq=300 ack=101', '', '', 'The server answers <b>SYN-ACK</b>: "OK, my numbers start at 300, and I got your byte 100, so send 101 next".'),
      R('cs', 'ACK  ack=301', 'connect() returns', 'accept() returns', 'The client sends <b>ACK</b>. This is the <b>three way handshake</b>. It costs one round trip, and only now does accept() give the server a NEW socket for this one client.'),
      R('cs', 'data "hello" (5 bytes)', 'sendall(b"hello")', '', 'The client sends 5 bytes with <b>sendall()</b>. Sockets send <b>bytes</b>, so text must be encoded first.'),
      R('sc', 'ACK  ack=106', '', 'recv(1024) gives b"hello"', 'The server TCP confirms it got bytes 101 to 105. The server program calls <b>recv(1024)</b> and gets b"hello".'),
      R('sc', 'data "HELLO" (5 bytes)', 'recv(1024) gives b"HELLO"', 'sendall(b"HELLO")', 'The server answers on the same connection. TCP is <b>two way</b>: both sides can send at any time.'),
      R('cs', 'FIN', 'close()', '', 'The client is done and calls <b>close()</b>. TCP sends <b>FIN</b>: "I will send nothing more".'),
      R('sc', 'ACK + FIN', '', 'recv() gives b""', 'On the server, recv() now returns <b>b""</b> (empty bytes). That is how a program learns the other side closed. The server closes too.'),
      R('cs', 'ACK', 'closed', 'closed', 'A last ACK and the connection is gone. A with block (with socket ... as s) calls close() for you even when an error happens.')
    ],
    stream: [
      R('', '', '', 'connection is open', 'A TCP connection is already open. Watch what happens to two separate sendall() calls.'),
      R('cs', '"hi"', 'sendall(b"hi")', '', 'The client sends the message b"hi".'),
      R('cs', '"there"', 'sendall(b"there")', '', 'Right after, it sends a second message, b"there".'),
      R('', '', '', 'recv(1024) gives b"hithere"', 'The server calls recv(1024) once and gets <b>b"hithere"</b>. The two messages are glued together. TCP is a <b>stream of bytes</b>, it does not keep message borders.'),
      R('', '', '', 'or: b"hit", then b"here"', 'Another time the same sends can arrive as b"hit" and then b"here". recv() returns <b>whatever bytes have arrived</b>, from 1 byte up to the size you asked for.'),
      R('cs', '00 00 00 02 "hi"', 'send length + data', '', 'The fix is <b>framing</b>. Put the length in front of every message: 4 bytes made with struct.pack("!I", 2), then the 2 bytes of data.'),
      R('cs', '00 00 00 05 "there"', 'send length + data', '', 'Same for the second message: length 5, then 5 bytes.'),
      R('', '', '', 'read 4 bytes: size 2, read 2: "hi"', 'The server reads exactly 4 bytes to learn the size, then exactly that many bytes. It loops on recv() until it has them all.'),
      R('', '', '', 'read 4 bytes: size 5, read 5: "there"', 'Now each message comes out whole, however TCP cut the stream. HTTP does the same job with Content-Length, and other protocols end each message with a new line.')
    ],
    lost: [
      R('', '', 'connection is open', 'connection is open', 'A TCP connection is open. The network between the two computers is busy and sometimes drops a packet.'),
      R('cs', 'data seq=101 "hello"', 'sendall(b"hello")', '', 'The client sends 5 bytes. On the way a router is full and <b>drops</b> the packet.', true),
      R('', '', 'timer runs out, no ACK', 'recv() is still waiting', 'The client TCP started a timer when it sent the data. No ACK came back before the timer ran out.'),
      R('cs', 'data seq=101 "hello" (again)', 'TCP sends it again', '', 'So TCP <b>sends the same bytes again</b>. The Python program did nothing: this all happens inside the operating system.'),
      R('sc', 'ACK  ack=106', '', 'recv(1024) gives b"hello"', 'This time it arrives. The server program gets b"hello" as if nothing went wrong.'),
      R('', '', 'it was only slower', '', 'This is why TCP is <b>reliable</b>: no loss, no duplicates, the right order. The price is delay: bytes after a lost packet wait until it is sent again.')
    ],
    udp: [
      R('', '', '', 'socket(SOCK_DGRAM), bind()', 'With UDP the receiver makes a SOCK_DGRAM socket and binds a port. There is <b>no listen() and no accept()</b>.'),
      R('cs', '"ping 0"', 'sendto(b"ping 0", addr)', '', 'The sender calls <b>sendto()</b> with the address. No handshake: the first packet already carries data.'),
      R('cs', '"ping 1"', 'sendto(b"ping 1", addr)', '', 'The second datagram is lost on the way.', true),
      R('cs', '"ping 2"', 'sendto(b"ping 2", addr)', '', 'The third one arrives.'),
      R('', '', '', 'recvfrom(): b"ping 0", b"ping 2"', 'The receiver calls <b>recvfrom()</b> and gets each datagram whole, with the address of the sender. Message borders are kept.'),
      R('', '', 'nobody tells the sender', 'ping 1 is just missing', 'Nobody sends the lost one again and nobody tells the sender. If the program cares, it must notice and resend by itself.'),
      R('', '', 'fast and simple', '', 'UDP is used where speed matters more than every packet: DNS questions, video calls, online games. HTTP/3 (QUIC) builds its own reliability on top of UDP.')
    ]
  };
  trace('pysock', {
    title: 'Sockets on a timeline',
    sub: 'Time runs down the page. Each step adds one packet between the client and the server, with the Python call that caused it.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Case', type: 'select', v: 'tcp', opts: [['tcp', 'TCP: connect, talk, close'], ['stream', 'TCP is a stream: framing'], ['lost', 'A lost TCP packet is sent again'], ['udp', 'UDP: datagrams, no handshake']] }],
    tips: [
      { t: 'TCP: the three way handshake, data and ACKs, then FIN.', set: { case: 'tcp' }, play: true },
      { t: 'Two sends can arrive as one recv. Framing fixes it.', set: { case: 'stream' }, play: true },
      { t: 'TCP hides a lost packet by sending it again.', set: { case: 'lost' }, play: true },
      { t: 'UDP keeps message borders but never resends.', set: { case: 'udp' }, play: true }
    ],
    frames(p) {
      const rows = CASES[p.case];
      return rows.map((r, i) => ({ rows: rows.slice(0, i + 1), say: r.say }));
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const CX = 185, SX = 355;
      box(z, CX - 60, 8, 120, 32, 'Client', { s: 13, b: true, stroke: c.cv });
      box(z, SX - 60, 8, 120, 32, 'Server', { s: 13, b: true, stroke: c.orange });
      for (let y = 44; y < 392; y += 10) {
        D.line(g, CX, y, CX, y + 5, c.line, 1.5);
        D.line(g, SX, y, SX, y + 5, c.line, 1.5);
      }
      const n = f.rows.length, gap = n > 9 ? 33 : 36;
      f.rows.forEach((r, i) => {
        const y = 62 + i * gap, now = i === n - 1;
        const ink = now ? c.ink : c.ink2;
        if (r.dir) {
          const x1 = r.dir === 'cs' ? CX : SX, x2 = r.dir === 'cs' ? SX : CX, col = r.dir === 'cs' ? c.cv : c.orange;
          const drop = 16;
          if (r.lost) {
            const mx = (x1 + x2) / 2, my = y + drop / 2;
            D.line(g, x1, y, mx, my, c.red, now ? 2.5 : 1.5);
            D.line(g, mx - 6, my - 6, mx + 6, my + 6, c.red, 2.5);
            D.line(g, mx - 6, my + 6, mx + 6, my - 6, c.red, 2.5);
            D.text(g, 'lost', mx + 10, my + 4, { s: 10.5, b: true, c: c.red });
          } else D.arrow(g, x1, y, x2, y + drop, now ? col : c.ink2, now ? 2.5 : 1.5, 7);
          const s = r.label;
          D.text(g, s, (CX + SX) / 2, y - 4, { a: 'center', s: PYZ.fit ? PYZ.fit(g, s, 160, 11.5, { mono: true }) : 11, mono: true, b: now, c: r.lost ? c.red : ink });
        }
        const sz = (s, w) => PYZ.fit ? PYZ.fit(g, s, w, 11, { mono: true }) : 10;
        if (r.left) D.text(g, r.left, CX - 8, y + 10, { a: 'right', s: sz(r.left, 170), mono: true, b: now, c: now ? c.cv : c.ink2 });
        if (r.right) D.text(g, r.right, SX + 8, y + 10, { s: sz(r.right, 236), mono: true, b: now, c: now ? c.orange : c.ink2 });
      });
    }
  });
})();

/* =====================================================================================================
   Web 2.1  what one requests call does: the Python lines, the HTTP text it makes, and the Response object
   ===================================================================================================== */
(() => {
  const { trace, head, D, codeView } = PYZ;
  const { rr } = AIZ;
  /* a step: cur = highlighted code line, wire = HTTP lines so far, resp = [name, value] rows of the Response object */
  const S = (cur, wire, resp, say, bad) => ({ cur, wire, resp, say, bad });
  const HDR = ['Host: api.example.com', 'User-Agent: python-requests/2.34', 'Accept-Encoding: gzip, deflate', 'Accept: */*', 'Connection: keep-alive'];
  const CASES = {
    get: {
      code: ['import requests', 'r = requests.get(URL + "/books",', '        params={"q": "dune", "page": 2},', '        timeout=5)', 'r.raise_for_status()', 'books = r.json()'],
      steps: () => {
        const L1 = ['GET /books?q=dune&page=2 HTTP/1.1'], L2 = L1.concat(HDR), L3 = L2.concat(['', 'HTTP/1.1 200 OK', 'Content-Type: application/json', '[{"id": 1, "title": "Dune"}]']);
        const R1 = [['r.status_code', '200'], ['r.ok', 'True'], ['r.url', '...books?q=dune&page=2'], ['r.headers["Content-Type"]', 'application/json']];
        return [
          S(0, [], [], '<b>requests</b> is not part of Python itself. Install it once with <b>pip install requests</b>, then import it.'),
          S(1, [], [], '<b>requests.get</b> will send a GET request, which reads data. Nothing has been sent yet.'),
          S(2, L1, [], '<b>params</b> is a normal dict. requests turns it into the query string <b>?q=dune&page=2</b> and encodes spaces and special letters for you.'),
          S(3, L2, [], '<b>timeout=5</b> means: wait at most 5 seconds. Without a timeout, requests can wait for ever. requests also adds headers such as User-Agent and asks for gzip.'),
          S(3, L3, R1, 'The answer arrives. requests puts it into a <b>Response</b> object: status_code is 200, ok is True, and the headers work like a dict that ignores upper and lower case.'),
          S(4, L3, R1, '<b>raise_for_status()</b> does nothing for a 2xx answer. For 4xx or 5xx it raises an error, so a failed call can not go unnoticed.'),
          S(5, L3, R1.concat([['r.text', '\'[{"id": 1, "title": "Dune"}]\''], ['r.json()', '[{\'id\': 1, \'title\': \'Dune\'}]']]), '<b>r.text</b> is the body as a string. <b>r.json()</b> turns the JSON text into Python lists and dicts that you can use at once.')
        ];
      }
    },
    post: {
      code: ['payload = {"title": "Emma", "year": 1815}', 'r = requests.post(URL + "/books",', '        json=payload, timeout=5)', 'print(r.status_code, r.headers["Location"])', 'new_book = r.json()'],
      steps: () => {
        const L1 = ['POST /books HTTP/1.1', 'Host: api.example.com', 'Content-Type: application/json', 'Content-Length: 31', '', '{"title": "Emma", "year": 1815}'];
        const L2 = L1.concat(['', 'HTTP/1.1 201 Created', 'Location: /books/3']);
        const R1 = [['r.status_code', '201'], ['r.ok', 'True'], ['r.headers["Location"]', '/books/3']];
        return [
          S(0, [], [], 'The new book is a normal Python dict.'),
          S(1, [], [], '<b>requests.post</b> sends data to create something new.'),
          S(2, L1, [], '<b>json=payload</b> does two jobs: it turns the dict into JSON text (31 bytes) and sets <b>Content-Type: application/json</b>. Using data= instead would send a web form.'),
          S(2, L2, R1, 'The server saved the book and answers <b>201 Created</b> with a <b>Location</b> header that holds the address of the new book.'),
          S(3, L2, R1, 'print shows <b>201 /books/3</b>.'),
          S(4, L2, R1.concat([['r.json()', '{\'id\': 3, \'title\': \'Emma\', ...}']]), 'r.json() gives the saved book back, now with the id that the server chose.')
        ];
      }
    },
    error: {
      code: ['r = requests.get(URL + "/books/99", timeout=5)', 'print(r.status_code, r.ok)', 'r.raise_for_status()'],
      steps: () => {
        const L1 = ['GET /books/99 HTTP/1.1'].concat(HDR.slice(0, 2)), L2 = L1.concat(['', 'HTTP/1.1 404 Not Found', 'Content-Type: application/json', '{"error": "book 99 not found"}']);
        const R1 = [['r.status_code', '404'], ['r.ok', 'False'], ['r.json()', '{\'error\': \'book 99 not found\'}']];
        return [
          S(0, L1, [], 'The program asks for book 99, which does not exist.'),
          S(0, L2, R1, 'The server answers <b>404 Not Found</b>. requests still returns a normal Response object.'),
          S(1, L2, R1, 'print shows <b>404 False</b>. Important: <b>no exception</b> happened. requests does not raise for 4xx or 5xx by itself.', 1),
          S(2, L2, R1.concat([['raises', 'requests.HTTPError']]), '<b>raise_for_status()</b> raises <b>requests.HTTPError: 404 Client Error: Not Found</b>. Call it right after each request, or check r.ok yourself.', 2),
          S(2, L2, R1.concat([['raises', 'requests.HTTPError']]), 'Catch it with <b>except requests.HTTPError as err</b>. err.response is the Response, so you can still read the error message from the server.', 2)
        ];
      }
    },
    timeout: {
      code: ['try:', '    r = requests.get(URL + "/slow", timeout=(3, 2))', 'except requests.Timeout:', '    print("too slow, try again later")', 'except requests.ConnectionError:', '    print("cannot reach the server")'],
      steps: () => {
        const L1 = ['GET /slow HTTP/1.1'].concat(HDR.slice(0, 2)), L2 = L1.concat(['', '(1 s ... no answer)']), L3 = L1.concat(['', '(2 s ... still no answer)']);
        return [
          S(1, [], [], '<b>timeout=(3, 2)</b> is a pair: wait at most 3 s to <b>connect</b>, and at most 2 s for <b>each read</b> of the answer.'),
          S(1, L1, [], 'The connection works quickly and the request is sent.'),
          S(1, L2, [], 'The server is busy. One second passes and no byte of the answer has come.'),
          S(1, L3, [['raises', 'requests.ReadTimeout']], 'After 2 seconds requests stops waiting and raises <b>ReadTimeout</b>, which is a kind of <b>requests.Timeout</b>.', 1),
          S(3, L3, [['raises', 'requests.ReadTimeout']], 'The except block catches it and the program goes on. Without a timeout this program could hang for ever.'),
          S(5, ['(no connection, nothing is sent)'], [['raises', 'requests.ConnectionError']], 'If the server is down or the name is wrong, no connection is made and requests raises <b>ConnectionError</b> instead. Both are kinds of <b>requests.RequestException</b>.')
        ];
      }
    }
  };
  trace('pyreq', {
    title: 'What one requests call does',
    sub: 'Pick a case. Each step runs one line and shows the HTTP text it makes and what you get back in Python.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Case', type: 'select', v: 'get', opts: [['get', 'GET with params'], ['post', 'POST with json='], ['error', 'A 404 and raise_for_status'], ['timeout', 'Timeouts and connection errors']] }],
    tips: [
      { t: 'GET: params, timeout, the Response object and r.json().', set: { case: 'get' }, play: true },
      { t: 'POST: json= writes the body and the Content-Type for you.', set: { case: 'post' }, play: true },
      { t: 'A 404 is not an exception until raise_for_status().', set: { case: 'error' }, play: true },
      { t: 'Always pass a timeout, and catch Timeout and ConnectionError.', set: { case: 'timeout' }, play: true }
    ],
    frames(p) { return CASES[p.case].steps(); },
    paint(z, f) {
      const c = z.col, g = z.g, P = CASES[z.p.case];
      head(z, 'Your Python code', 16, 18);
      const yEnd = codeView(z, P.code, f.cur, 16, 24, 568, { s: 12, lh: 19, bad: f.bad === undefined ? undefined : f.cur });
      const top = yEnd + 24, hgt = 392 - top;
      head(z, 'On the wire (HTTP text)', 16, top - 6);
      rr(g, 16, top, 300, hgt, 8, { fill: c.dark ? '#0b1220' : '#111827', stroke: c.line });
      const lh = Math.min(16, (hgt - 12) / Math.max(f.wire.length, 1));
      const firstRes = f.wire.findIndex(x => /^HTTP\//.test(x));
      f.wire.forEach((ln, i) => {
        const s = ln === '' ? '(blank line)' : ln;
        const isRes = firstRes >= 0 && i >= firstRes;
        D.text(g, s, 24, top + 16 + i * lh, { s: PYZ.fit(g, s, 284, 10.5, { mono: true }), mono: true, c: ln === '' || /^\(/.test(ln) ? '#6b7280' : isRes ? '#fdba74' : '#93c5fd' });
      });
      head(z, 'The Response object', 328, top - 6);
      rr(g, 326, top, 258, hgt, 8, { fill: c.surf, stroke: f.resp.some(r => r[0] === 'raises') ? c.red : c.line, w: f.resp.some(r => r[0] === 'raises') ? 2 : 1 });
      const rh = Math.min(32, (hgt - 10) / Math.max(f.resp.length, 1));
      f.resp.forEach(([k, v], i) => {
        const y = top + 17 + i * rh, bad = k === 'raises';
        D.text(g, k, 336, y, { s: PYZ.fit(g, k, 238, 11, { mono: true }), mono: true, b: true, c: bad ? c.red : c.cv });
        D.text(g, v, 348, y + 14, { s: PYZ.fit(g, v, 228, 11.5, { mono: true }), mono: true, c: bad ? c.red : c.ink });
      });
      if (!f.resp.length) D.text(g, 'nothing yet', 455, top + hgt / 2, { a: 'center', s: 12, c: c.ink2 });
    }
  });
})();

/* =====================================================================================================
   Web 2.2  retries on a time line: fixed waits, exponential backoff, backoff with jitter, and Retry-After.
   The server can take 2 requests at the same moment. A third one at the same moment makes all of them fail.
   ===================================================================================================== */
(() => {
  const { trace, D, head } = PYZ;
  const { rr } = AIZ;
  /* an attempt: lane 0..2 (client A, B, C), t in seconds, ok, code, and the wait that follows it */
  const A = (lane, t, ok, code, wait) => ({ lane, t, ok, code, wait });
  const ROUND = (t, wait) => [A(0, t, false, '503', wait), A(1, t, false, '503', wait), A(2, t, false, '503', wait)];
  const CASES = {
    fixed: [
      [ROUND(0, 1), 'Three clients call the API at <b>t = 0</b>. The server can handle 2 at once, so the third one overloads it and all three get <b>503 Service Unavailable</b>.'],
      [ROUND(1, 1), 'Each client waits a fixed 1 second and tries again. They all started together, so they all come back together at t = 1. All fail again.'],
      [ROUND(2, 1), 't = 2: the same thing. Fixed waits keep the clients in step.'],
      [ROUND(3, 1), 't = 3: they still hit the server at the same moment. This is called a <b>thundering herd</b>: the retries themselves keep the server overloaded.'],
      [[], 'Fixed waits are simple, but when many clients fail together they also retry together. They never get out of step.']
    ],
    backoff: [
      [ROUND(0, 1), 'The same start: three calls at t = 0, all fail.'],
      [ROUND(1, 2), '<b>Exponential backoff</b>: wait 1 s, then 2 s, then 4 s, doubling each time. So the second try is at t = 1.'],
      [ROUND(3, 4), 'Third try at t = 1 + 2 = 3. Fewer tries per second means less load on the server.'],
      [ROUND(7, 0), 'Fourth try at t = 3 + 4 = 7. But all three clients use the same waits, so they still arrive together and still fail.'],
      [[], 'Backoff alone lowers the load but does not spread the clients out. The formula is wait = base &times; 2<sup>attempt</sup>, usually with a maximum such as 30 s.']
    ],
    jitter: [
      [ROUND(0, 0), 'Again three calls at t = 0, all fail.'],
      [[A(0, 0, false, '', 0.6, true), A(1, 0, false, '', 1.7, true), A(2, 0, false, '', 1.1, true)], '<b>Jitter</b>: each client picks a RANDOM wait between 0 and base &times; 2<sup>attempt</sup>, here between 0 and 2 s. Python: random.uniform(0, 2).'],
      [[A(0, 0.6, true, '200')], 'Client A happened to pick 0.6 s. It is alone at that moment, so it gets <b>200 OK</b>.'],
      [[A(2, 1.1, true, '200')], 'Client C picked 1.1 s. A is already done, so C is served too.'],
      [[A(1, 1.7, true, '200')], 'Client B picked 1.7 s and also works. Every client got its answer before t = 2.'],
      [[], 'Random waits spread the clients over time, so the server sees a few requests at a time instead of a crowd. AWS calls this <b>full jitter</b> and recommends it.']
    ],
    after: [
      [[A(0, 0, false, '429', 3)], 'Client A calls an API with a rate limit. It has used its allowance, so the server answers <b>429 Too Many Requests</b> with the header <b>Retry-After: 3</b>.'],
      [[], 'Retry-After tells the client exactly how many seconds to wait. A polite client waits that long instead of using its own backoff.'],
      [[A(0, 3, true, '200')], 'At t = 3 the client tries again and gets <b>200 OK</b>. Calling earlier would only have added more 429 answers.'],
      [[A(1, 0.5, true, '200'), A(1, 2, true, '200')], 'Client B was never over its limit, so its calls work at once. Rate limits are usually counted per API key or per user.'],
      [[], 'Read Retry-After (seconds, or a date) and the X-RateLimit-Remaining and X-RateLimit-Reset headers when an API sends them.']
    ]
  };
  trace('pyretry', {
    title: 'Retrying a failed call',
    sub: 'Time runs left to right. Each step shows the next tries of three clients. The server can take 2 requests at the same moment.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'How to retry', type: 'select', v: 'fixed', opts: [['fixed', 'Fixed wait (1 s)'], ['backoff', 'Exponential backoff'], ['jitter', 'Backoff with jitter'], ['after', 'A 429 with Retry-After']] }],
    tips: [
      { t: 'Fixed waits: all clients retry together and keep failing.', set: { case: 'fixed' }, play: true },
      { t: 'Backoff: 1, 2, 4 s. Less load, but still together.', set: { case: 'backoff' }, play: true },
      { t: 'Jitter: random waits spread the clients out.', set: { case: 'jitter' }, play: true },
      { t: 'Retry-After: the server says how long to wait.', set: { case: 'after' }, play: true }
    ],
    frames(p) {
      const st = CASES[p.case];
      let done = [];
      return st.map(([add, say]) => { done = done.concat(add); return { at: done.slice(), fresh: add, say }; });
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      const X = t => 90 + t * 62, LANES = ['Client A', 'Client B', 'Client C'], Y = i => 80 + i * 80;
      LANES.forEach((name, i) => {
        D.text(g, name, 16, Y(i) + 4, { s: 12, b: true, c: c.ink });
        D.line(g, X(0), Y(i), X(8), Y(i), c.line, 1.2);
      });
      D.line(g, X(0), 330, X(8), 330, c.ink2, 1.5);
      for (let t = 0; t <= 8; t++) {
        D.line(g, X(t), 326, X(t), 334, c.ink2, 1.5);
        D.text(g, t + ' s', X(t), 350, { a: 'center', s: 11, c: c.ink2 });
      }
      head(z, 'time', X(8), 372, { a: 'right' });
      f.at.forEach(a => {
        const x = X(a.t), y = Y(a.lane), now = f.fresh.includes(a);
        if (a.wait) {
          const x2 = X(a.t + a.wait);
          for (let xx = x + 14; xx < x2 - 14; xx += 8) D.line(g, xx, y - 22, Math.min(xx + 4, x2 - 14), y - 22, c.ink2, 1.2);
          D.text(g, 'wait ' + a.wait + ' s', (x + x2) / 2, y - 28, { a: 'center', s: 10.5, c: c.ink2 });
        }
        if (a.ghost) return;
        D.circle(g, x, y, now ? 13 : 11, { fill: a.ok ? c.green : c.red, stroke: now ? c.ink : c.surf, w: now ? 2 : 1.5 });
        D.text(g, a.ok ? '✓' : '✗', x, y + 5, { a: 'center', s: 13, b: true, c: '#fff' });
        D.text(g, a.code, x, y + 30, { a: 'center', s: 11, b: true, mono: true, c: a.ok ? c.green : c.red });
      });
      rr(g, 400, 14, 184, 26, 6, { fill: c.surf, stroke: c.line });
      D.text(g, 'Server: at most 2 at once', 492, 31, { a: 'center', s: 11.5, b: true, c: c.orange });
    }
  });
})();

/* =====================================================================================================
   Web 3.1  the journey of one request through Flask: server, URL matching, hooks, the view, the response
   ===================================================================================================== */
(() => {
  const { trace, D, box, head } = PYZ;
  const { rr } = AIZ;
  const STAGES = ['Browser', 'WSGI server (Werkzeug, Gunicorn)', 'Match the URL to a route', 'before_request hooks', 'Your view function', 'Turn the result into a Response', 'after_request hooks'];
  /* a step: stage index, new facts [name, value] added to the panel, say, bad = an error path */
  const S = (stage, facts, say, bad) => ({ stage, facts, say, bad });
  const CASES = {
    get: [
      S(0, [['request', 'GET /hello/ann?lang=fr']], 'The browser asks for <b>/hello/ann?lang=fr</b>.'),
      S(1, [['environ["PATH_INFO"]', '/hello/ann'], ['environ["QUERY_STRING"]', 'lang=fr']], 'A <b>WSGI server</b> reads the HTTP text and calls the Flask app with a dict called environ. In development this is Werkzeug (flask run), in production often Gunicorn.'),
      S(2, [['matched rule', '/hello/<name>'], ['endpoint', 'hello'], ['view_args', '{"name": "ann"}']], 'Flask compares the path with every <b>@app.route</b>. The rule /hello/&lt;name&gt; matches and takes "ann" out of the URL.'),
      S(3, [['g.user', 'None (not logged in)']], 'Functions marked <b>@app.before_request</b> run first, for example to load the logged in user into <b>g</b>, a place for data that lives for one request.'),
      S(4, [['call', 'hello(name="ann")'], ['request.args["lang"]', 'fr']], 'Flask calls your <b>view function</b> with the URL parts as arguments. Inside it, <b>request</b> holds everything else: args, form, JSON, headers, cookies.'),
      S(4, [['returns', 'render_template("hello.html", ...)']], 'The view returns a string made from a <b>Jinja template</b>: "Bonjour, ann!".'),
      S(5, [['response', '200 OK, text/html; charset=utf-8']], 'Flask turns a string into a <b>Response</b> with status 200 and Content-Type text/html. A dict or list would become JSON, a (body, status) pair sets the status.'),
      S(6, [['header added', 'X-Time: 3 ms']], '<b>@app.after_request</b> functions can change the response, for example to add a header. Then the server sends it back.'),
      S(0, [['page shown', 'Bonjour, ann!']], 'The browser shows the page. All of this took a few milliseconds.')
    ],
    post: [
      S(0, [['request', 'POST /login'], ['form body', 'user=ann&pw=secret']], 'The user sends the login form. The browser makes a <b>POST</b> with the form fields in the body.'),
      S(2, [['matched rule', '/login, methods GET and POST'], ['endpoint', 'login']], 'The rule allows POST because it says methods=["GET", "POST"]. Without that Flask would answer 405 Method Not Allowed.'),
      S(4, [['request.form["user"]', 'ann'], ['password check', 'ok']], 'The view reads <b>request.form</b> and checks the password (in real apps against a hash, never plain text).'),
      S(4, [['session["user"]', 'ann']], 'It stores the user in the <b>session</b>. Flask keeps the session in a cookie that is signed with app.secret_key, so the user cannot change it.'),
      S(5, [['response', '302 Found'], ['Location', '/'], ['Set-Cookie', 'session=eyJ1c2Vy...']], 'The view returns <b>redirect(url_for("home"))</b>: status 302 with a Location header, plus the new session cookie.'),
      S(0, [['next request', 'GET / with Cookie: session=...']], 'The browser follows the redirect with a GET. This is the <b>Post, Redirect, Get</b> pattern: pressing refresh now repeats the GET, not the login.')
    ],
    missing: [
      S(0, [['request', 'GET /nope']], 'The browser asks for a page that does not exist.'),
      S(1, [['environ["PATH_INFO"]', '/nope']], 'The server passes it to Flask as usual.'),
      S(2, [['matched rule', 'none'], ['raised', 'werkzeug NotFound (404)']], 'No rule matches, so Flask raises a <b>NotFound</b> error instead of calling a view.', true),
      S(4, [['error handler', 'not_found(error)']], 'If you wrote <b>@app.errorhandler(404)</b>, Flask calls that function. It can return a nice page or a JSON error.', true),
      S(5, [['response', '404 Not Found'], ['body', '{"error": "not found"}']], 'The handler&#39;s result becomes the response with status 404. Without a handler Flask sends a short default HTML page.', true),
      S(0, [['shown', 'the 404 page or JSON']], 'The same happens for abort(403) in a view, or for an exception in your code, which becomes a 500 error.', true)
    ],
    api: [
      S(0, [['request', 'GET /api/books/2'], ['Accept', 'application/json']], 'A program, not a person, calls the JSON API.'),
      S(2, [['matched rule', '/api/books/<int:book_id>'], ['view_args', '{"book_id": 2}']], 'The <b>int:</b> converter only matches whole numbers and turns "2" into the int 2. /api/books/two would be a 404.'),
      S(4, [['call', 'get_book(book_id=2)'], ['returns', '{"id": 2, "title": "Emma"}']], 'The view finds the book and simply returns a <b>dict</b>.'),
      S(5, [['response', '200 OK, application/json'], ['body', '{"id": 2, "title": "Emma"}']], 'Flask sees a dict and makes JSON with the right Content-Type, the same as jsonify(). For a missing book the view would return ({"error": ...}, 404).'),
      S(0, [['client', 'r.json() gives the dict back']], 'The calling program reads it with requests or httpx, as in step 2.')
    ]
  };
  trace('pyflask', {
    title: 'One request through Flask',
    sub: 'Pick a request. Each step moves it one stage further and shows what Flask knows at that point.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Request', type: 'select', v: 'get', opts: [['get', 'GET a page with a template'], ['post', 'POST a login form'], ['missing', 'A page that does not exist'], ['api', 'GET from a JSON API']] }],
    tips: [
      { t: 'A page: route, view, template, response.', set: { case: 'get' }, play: true },
      { t: 'A form: session cookie and redirect.', set: { case: 'post' }, play: true },
      { t: '404: no route matches, an error handler answers.', set: { case: 'missing' }, play: true },
      { t: 'An API: int converter and a dict that becomes JSON.', set: { case: 'api' }, play: true }
    ],
    frames(p) {
      let facts = [];
      return CASES[p.case].map(st => { facts = facts.concat(st.facts.map(x => x.concat([st]))); return { stage: st.stage, facts: facts.slice(-11), fresh: st, say: st.say, bad: st.bad }; });
    },
    paint(z, f) {
      const c = z.col, g = z.g;
      STAGES.forEach((name, i) => {
        const y = 14 + i * 54, on = i === f.stage;
        box(z, 16, y, 236, 38, name, { s: 12, b: on, stroke: on ? (f.bad ? c.red : c.cv) : c.line, w: on ? 2.5 : 1.2, fill: on ? (c.dark ? '#1e3a5f' : '#dbeafe') : c.surf });
        if (i < STAGES.length - 1) D.arrow(g, 134, y + 39, 134, y + 53, c.ink2, 1.2, 5);
      });
      head(z, 'What Flask knows now', 272, 22);
      rr(g, 268, 30, 316, 360, 8, { fill: c.surf, stroke: c.line });
      f.facts.forEach(([k, v, st], i) => {
        const y = 50 + i * 31, now = st === f.fresh;
        D.text(g, k, 278, y, { s: PYZ.fit(g, k, 296, 11, { mono: true }), mono: true, b: true, c: now ? (f.bad ? c.red : c.cv) : c.ink2 });
        D.text(g, v, 290, y + 14, { s: PYZ.fit(g, v, 286, 11.5, { mono: true }), mono: true, c: now ? c.ink : c.ink2 });
      });
    }
  });
})();

/* =====================================================================================================
   Web 3.2  a real Flask app: the factory builds it, a request uses the database and the login, a test runs it
   ===================================================================================================== */
(() => {
  const { trace, D, box, head } = PYZ;
  const { rr } = AIZ;
  const S = (stage, facts, say, bad) => ({ stage, facts, say, bad });
  const CASES = {
    build: {
      stages: ['create_app(settings) is called', 'app = Flask(__name__)', 'Load the config', 'Set up the database helpers', 'Register the blueprints', 'The app is ready'],
      steps: [
        S(0, [['call', 'create_app()']], 'Nothing is made when Python imports the package. The app is built only when someone calls the <b>application factory</b> create_app().'),
        S(1, [['app', 'Flask("shop")']], 'The factory makes a new Flask object. Calling it twice gives two separate apps, which is exactly what tests need.'),
        S(2, [['SECRET_KEY', 'dev (default)'], ['DATABASE', 'instance/shop.sqlite'], ['from settings', 'TESTING=True (in tests)'], ['from environment', 'FLASK_SECRET_KEY=...']], 'Config comes in layers: safe defaults first, then the settings passed in, then environment variables. Later layers win, so production secrets never live in the code.'),
        S(3, [['teardown_appcontext', 'close_db'], ['CLI command', 'flask init-db']], 'The database module registers <b>close_db</b> to run after every request and adds an <b>init-db</b> command for the terminal.'),
        S(4, [['blueprint auth', '/auth/register, /auth/login'], ['blueprint books', '/, /create, /<id>/update'], ['blueprint api', '/api/books ...']], 'Each part of the site is a <b>Blueprint</b> in its own file. register_blueprint adds its routes, and url_prefix puts them under a path such as /api.'),
        S(5, [['return', 'app']], 'The factory returns the app. Gunicorn calls it with gunicorn "shop:create_app()", and tests call it with their own settings.')
      ]
    },
    request: {
      stages: ['Request arrives', 'before_app_request: load the user', 'login_required check', 'View: get_db()', 'Run SQL with ? placeholders', 'Return the response', 'teardown_appcontext: close_db'],
      steps: [
        S(0, [['request', 'GET /books with a session cookie']], 'A logged in user opens the list of books.'),
        S(1, [['session["user_id"]', '1'], ['g.user', 'row of user 1']], 'A function marked <b>@bp.before_app_request</b> reads the user id from the session and loads the user into <b>g.user</b>, for every request of the app.'),
        S(2, [['@login_required', 'g.user is set, go on']], 'The <b>login_required</b> decorator checks g.user. Here it is set, so the view runs.'),
        S(3, [['g.db', 'new sqlite3 connection']], 'The view calls <b>get_db()</b>. The first call in a request opens a connection and keeps it on g, later calls in the same request reuse it.'),
        S(4, [['SQL', 'SELECT ... WHERE author_id = ?'], ['params', '(1,)']], 'Values always go in as <b>? placeholders</b>, never glued into the SQL text, so a title that contains SQL code is stored as plain text and never runs.'),
        S(5, [['response', '200, rendered books.html']], 'The view renders the template with the rows and returns it.'),
        S(6, [['g.db', 'closed']], 'After the response, Flask calls <b>close_db</b>, even if the view raised an error. Every request gets a fresh connection and nothing is left open.')
      ]
    },
    login: {
      stages: ['GET /orders, not logged in', 'login_required redirects', 'POST /auth/login', 'check_password_hash', 'Store the user in the session', 'Redirect back to /orders'],
      steps: [
        S(0, [['g.user', 'None']], 'Someone who is not logged in opens /orders.'),
        S(1, [['response', '302, Location: /auth/login']], 'login_required sees g.user is None and returns a <b>redirect</b> to the login page instead of running the view.', true),
        S(2, [['form', 'name=ann, password=...']], 'The user sends the login form.'),
        S(3, [['stored', 'pbkdf2:sha256:1000000$salt$hash'], ['check', 'True']], 'The app NEVER stores passwords. It stores a slow, salted <b>hash</b> made by generate_password_hash, and check_password_hash hashes the typed password the same way and compares.'),
        S(4, [['session', 'cleared, then user_id = 1']], 'session.clear() first, so no old data survives the login. Then the user id goes into the signed session cookie.'),
        S(5, [['response', '302, Location: /orders'], ['next request', 'g.user = ann, view runs']], 'Back at /orders, before_app_request loads ann into g.user and the view runs.')
      ]
    },
    test: {
      stages: ['pytest finds test_ functions', 'Fixture app: create_app(TESTING)', 'Fixture: a fresh database', 'Fixture client: app.test_client()', 'The test sends requests', 'assert the answers', 'Clean up'],
      steps: [
        S(0, [['found', 'tests/test_notes.py::test_add_note']], 'pytest looks in the tests folder for files and functions whose names start with test_.'),
        S(1, [['app', 'create_app({"TESTING": True, ...})']], 'The test asks for a <b>client</b> argument. pytest sees a <b>fixture</b> with that name in conftest.py and runs it first. It calls the factory with test settings.'),
        S(2, [['DATABASE', '/tmp/pytest-.../test.sqlite'], ['init-db', 'done']], 'Each test gets its own empty database in a temporary file (or :memory:), so tests never depend on each other.'),
        S(3, [['client', 'FlaskClient']], 'The fixture returns app.test_client(). It sends requests straight into the app, with no network and no server.'),
        S(4, [['request', 'client.post("/api/notes", json=...)'], ['status', '201']], 'The test body uses the client like a browser or an API caller would.'),
        S(5, [['assert', 'r.status_code == 201 passed'], ['assert', 'r.get_json()["text"] == "milk" passed']], 'Plain assert statements check the answers. When one fails, pytest shows both values.'),
        S(6, [['cleanup', 'temporary database removed'], ['result', '1 passed']], 'After the test pytest finishes the fixture (code after yield), so the temporary database is deleted.')
      ]
    }
  };
  trace('pyflaskapp', {
    title: 'Inside a real Flask app',
    sub: 'Pick a view of the app. Each step moves one stage further and shows what the app knows at that point.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Show', type: 'select', v: 'build', opts: [['build', 'The factory builds the app'], ['request', 'A request with the database'], ['login', 'Logging in'], ['test', 'A pytest test']] }],
    tips: [
      { t: 'create_app: config layers, database helpers, blueprints.', set: { case: 'build' }, play: true },
      { t: 'A request: g.user, login_required, g.db, teardown.', set: { case: 'request' }, play: true },
      { t: 'Login: redirect, password hash, session.', set: { case: 'login' }, play: true },
      { t: 'A test: fixtures, a fresh app and database, the test client.', set: { case: 'test' }, play: true }
    ],
    frames(p) {
      let facts = [];
      return CASES[p.case].steps.map(st => { facts = facts.concat(st.facts.map(x => x.concat([st]))); return { stage: st.stage, facts: facts.slice(-11), fresh: st, say: st.say, bad: st.bad }; });
    },
    paint(z, f) {
      const c = z.col, g = z.g, stages = CASES[z.p.case].stages;
      const gap = Math.min(54, 376 / stages.length);
      stages.forEach((name, i) => {
        const y = 14 + i * gap, on = i === f.stage;
        box(z, 16, y, 236, gap - 16, name, { s: 12, b: on, stroke: on ? (f.bad ? c.red : c.cv) : c.line, w: on ? 2.5 : 1.2, fill: on ? (c.dark ? '#1e3a5f' : '#dbeafe') : c.surf });
        if (i < stages.length - 1) D.arrow(g, 134, y + gap - 15, 134, y + gap - 1, c.ink2, 1.2, 5);
      });
      head(z, 'What the app knows now', 272, 22);
      rr(g, 268, 30, 316, 360, 8, { fill: c.surf, stroke: c.line });
      f.facts.forEach(([k, v, st], i) => {
        const y = 50 + i * 31, now = st === f.fresh;
        D.text(g, k, 278, y, { s: PYZ.fit(g, k, 296, 11, { mono: true }), mono: true, b: true, c: now ? (f.bad ? c.red : c.cv) : c.ink2 });
        D.text(g, v, 290, y + 14, { s: PYZ.fit(g, v, 286, 11.5, { mono: true }), mono: true, c: now ? c.ink : c.ink2 });
      });
    }
  });
})();

/* =====================================================================================================
   Web 4.1  Django: a new project step by step, and one request through middleware, URLconf, view, ORM, template
   ===================================================================================================== */
(() => {
  const { trace, D, box, head } = PYZ;
  const { rr } = AIZ;
  const S = (stage, facts, say, bad) => ({ stage, facts, say, bad });
  const FLOW = ['Browser', 'WSGI or ASGI handler', 'Middleware, on the way in', 'URLconf: urlpatterns', 'The view', 'Models and the ORM', 'The template', 'Middleware, on the way out'];
  const CASES = {
    project: {
      stages: ['django-admin startproject mysite', 'python manage.py startapp books', 'Add "books" to INSTALLED_APPS', 'Write a model in books/models.py', 'python manage.py makemigrations', 'python manage.py migrate', 'python manage.py runserver'],
      steps: [
        S(0, [['created', 'manage.py'], ['created', 'mysite/settings.py, urls.py'], ['created', 'mysite/wsgi.py, asgi.py']], '<b>startproject</b> makes the project: manage.py to run commands, settings.py for all settings, urls.py for the first URL list, and wsgi.py and asgi.py for the web server.'),
        S(1, [['created', 'books/models.py, views.py'], ['created', 'books/admin.py, apps.py, tests.py'], ['created', 'books/migrations/']], 'A project holds one or more <b>apps</b>. Each app is one feature, such as books or accounts, with its own models, views and tests. startapp makes the files.'),
        S(2, [['INSTALLED_APPS', '[..., "books"]']], 'Django only looks at apps listed in <b>INSTALLED_APPS</b>. Forgetting this step is the most common reason why makemigrations says "No changes detected".'),
        S(3, [['class Book', 'title = CharField(max_length=200)'], ['', 'year = PositiveIntegerField()']], 'A <b>model</b> is a Python class. Each class becomes a table and each field becomes a column. You never write CREATE TABLE yourself.'),
        S(4, [['migration file', 'books/migrations/0001_initial.py'], ['operation', '+ Create model Book']], '<b>makemigrations</b> compares the models with the last migration and writes the difference into a new Python file. You commit this file to git.'),
        S(5, [['SQL run', 'CREATE TABLE "books_book" (...)'], ['applied', 'contenttypes, auth, admin, sessions, books']], '<b>migrate</b> runs every migration that is not applied yet, also those of the built in apps. The table name is the app label plus the model name: books_book.'),
        S(6, [['server', 'http://127.0.0.1:8000/'], ['reloads', 'on every saved file']], '<b>runserver</b> starts the development server. It is for your computer only. In production Gunicorn or Uvicorn runs the project through wsgi.py or asgi.py.')
      ]
    },
    page: {
      stages: FLOW,
      steps: [
        S(0, [['request', 'GET /books/2/']], 'The browser asks for the page of book 2.'),
        S(1, [['HttpRequest', 'method GET, path /books/2/']], 'The <b>handler</b> (from wsgi.py or asgi.py) turns the HTTP text into an <b>HttpRequest</b> object.'),
        S(2, [['SessionMiddleware', 'request.session loaded'], ['AuthenticationMiddleware', 'request.user = ann']], 'Each <b>middleware</b> in settings.MIDDLEWARE sees the request in order. Here they load the session and the logged in user.'),
        S(3, [['pattern', 'books/<int:book_id>/'], ['view', 'book_detail'], ['kwargs', '{"book_id": 2}']], 'Django tries the <b>urlpatterns</b> from top to bottom and stops at the first match. The int converter turns "2" into the number 2.'),
        S(4, [['call', 'book_detail(request, book_id=2)']], 'Django calls the <b>view</b>. A view is any function (or class) that takes a request and returns an HttpResponse.'),
        S(5, [['ORM', 'Book.objects.get(pk=2)'], ['SQL', 'SELECT ... FROM books_book WHERE id = 2']], 'The view asks the <b>ORM</b> for the book. Django writes the SQL, sends the values safely and gives back a Book object.'),
        S(6, [['render', 'books/detail.html'], ['context', '{"book": <Book: Emma>}']], '<b>render()</b> fills the template with the context. Every value is HTML escaped, so a title with &lt;script&gt; is shown as text.'),
        S(7, [['response', '200 OK, text/html'], ['added', 'Set-Cookie, security headers']], 'The response goes back through the middleware in <b>reverse order</b>, which can add headers or cookies, and then to the browser.')
      ]
    },
    slash: {
      stages: FLOW,
      steps: [
        S(0, [['request', 'GET /books']], 'Someone types the address without the slash at the end.'),
        S(2, [['CommonMiddleware', 'APPEND_SLASH = True'], ['test', '/books does not match, /books/ does']], '<b>CommonMiddleware</b> checks: no pattern matches /books, but /books/ would match, and APPEND_SLASH is on (the default).'),
        S(7, [['response', '301 Moved Permanently'], ['Location', '/books/']], 'It answers with a redirect at once. The URLconf, the view and the template never run.', true),
        S(0, [['next request', 'GET /books/'], ['result', '200, the list of books']], 'The browser follows the redirect. This is why Django URLs end with a slash. A POST to the address without the slash cannot be redirected and gives an error in DEBUG mode.')
      ]
    },
    csrf: {
      stages: FLOW,
      steps: [
        S(0, [['request', 'POST /books/add/'], ['form', 'title=Hamlet, no csrfmiddlewaretoken']], 'A form is sent without the hidden CSRF token, for example from another website that tries to act for a logged in user.'),
        S(2, [['CsrfViewMiddleware', 'cookie csrftoken = abc...'], ['form token', 'missing']], '<b>CsrfViewMiddleware</b> compares the token in the form with the one in the csrftoken cookie. Another site can make the browser send the cookie, but it cannot read it to copy it into the form.'),
        S(7, [['response', '403 Forbidden'], ['reason', 'CSRF token missing']], 'The tokens do not match, so Django stops here with <b>403</b>. The view never runs, so no book is added.', true),
        S(0, [['fix', '{% csrf_token %} inside every POST form']], 'In your own templates, put <b>{% csrf_token %}</b> inside each POST form and the check passes. JSON APIs send the token in the X-CSRFToken header instead.')
      ]
    },
    admin: {
      stages: FLOW,
      steps: [
        S(0, [['request', 'GET /admin/books/book/'], ['logged in', 'no']], 'Someone who is not logged in opens the admin list of books.'),
        S(2, [['AuthenticationMiddleware', 'request.user = AnonymousUser']], 'The middleware finds no user in the session, so request.user is an <b>AnonymousUser</b>.'),
        S(3, [['pattern', 'admin/ (admin.site.urls)'], ['view', 'ModelAdmin changelist']], 'The admin is just one entry in urlpatterns, path("admin/", admin.site.urls), with many views inside.'),
        S(4, [['check', 'user.is_staff is False'], ['response', '302 to /admin/login/?next=...']], 'The admin view checks that the user is <b>staff</b>. It is not, so the answer is a redirect to the login page.', true),
        S(0, [['login', 'boss (created by createsuperuser)'], ['request', 'GET /admin/books/book/?q=dune']], 'After logging in as the superuser the user searches for "dune".'),
        S(5, [['search_fields', '["title"]'], ['SQL', 'WHERE title LIKE %dune% ...']], 'The ModelAdmin settings drive the page: <b>search_fields</b> becomes a WHERE clause, <b>list_display</b> chooses the columns, <b>list_filter</b> adds the filter box.'),
        S(6, [['template', 'admin/change_list.html'], ['rows', 'Dune Messiah, Dune']], 'Django renders its own admin templates. You wrote three lines in admin.py and got a full page to search, add, change and delete books.'),
        S(7, [['response', '200 OK']], 'The page goes back through the middleware to the browser.')
      ]
    }
  };
  trace('pydjango', {
    title: 'Inside Django',
    sub: 'Pick what to follow. Each step moves one stage further and shows what Django knows at that point.',
    W: 600, H: 400,
    params: [{ k: 'case', label: 'Show', type: 'select', v: 'project', opts: [['project', 'A new project, command by command'], ['page', 'GET a page: URL, view, ORM, template'], ['slash', 'An address without the last slash'], ['csrf', 'A form without a CSRF token'], ['admin', 'The admin site']] }],
    tips: [
      { t: 'startproject, startapp, makemigrations, migrate, runserver.', set: { case: 'project' }, play: true },
      { t: 'One page: middleware, urlpatterns, view, ORM, template.', set: { case: 'page' }, play: true },
      { t: 'APPEND_SLASH: CommonMiddleware answers with 301.', set: { case: 'slash' }, play: true },
      { t: 'CSRF: the middleware stops a forged form with 403.', set: { case: 'csrf' }, play: true },
      { t: 'The admin: staff check, search_fields, list_display.', set: { case: 'admin' }, play: true }
    ],
    frames(p) {
      let facts = [];
      return CASES[p.case].steps.map(st => { facts = facts.concat(st.facts.map(x => x.concat([st]))); return { stage: st.stage, facts: facts.slice(-11), fresh: st, say: st.say, bad: st.bad }; });
    },
    paint(z, f) {
      const c = z.col, g = z.g, stages = CASES[z.p.case].stages;
      const gap = Math.min(54, 376 / stages.length);
      stages.forEach((name, i) => {
        const y = 14 + i * gap, on = i === f.stage;
        box(z, 16, y, 236, gap - 14, name, { s: 12, b: on, stroke: on ? (f.bad ? c.red : c.cv) : c.line, w: on ? 2.5 : 1.2, fill: on ? (c.dark ? '#1e3a5f' : '#dbeafe') : c.surf });
        if (i < stages.length - 1) D.arrow(g, 134, y + gap - 13, 134, y + gap - 1, c.ink2, 1.2, 4);
      });
      head(z, 'What Django knows now', 272, 22);
      rr(g, 268, 30, 316, 360, 8, { fill: c.surf, stroke: c.line });
      f.facts.forEach(([k, v, st], i) => {
        const y = 50 + i * 31, now = st === f.fresh;
        D.text(g, k, 278, y, { s: PYZ.fit(g, k, 296, 11, { mono: true }), mono: true, b: true, c: now ? (f.bad ? c.red : c.cv) : c.ink2 });
        D.text(g, v, 290, y + 14, { s: PYZ.fit(g, v, 286, 11.5, { mono: true }), mono: true, c: now ? c.ink : c.ink2 });
      });
    }
  });
})();
