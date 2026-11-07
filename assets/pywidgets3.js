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
