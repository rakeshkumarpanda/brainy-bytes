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
