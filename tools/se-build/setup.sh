#!/bin/sh
# One time set up for the Selenium chapter builder. Everything lands in tools/se-build/box/, which Git ignores.
# Needs Python 3.10+, Node.js 22+, JDK 21 with Maven, Chromium (default /opt/pw-browsers/chromium), Xvfb and openssl.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
BOX="$HERE/box"
CHROMIUM=${CHROMIUM:-/opt/pw-browsers/chromium}
SE=4.51.0
mkdir -p "$BOX/java" "$BOX/node"

# Python: the Selenium bindings, pytest and a ChromeDriver that matches the Chromium build
python3 -m venv "$BOX/.venv"
"$BOX/.venv/bin/pip" -q install "selenium==$SE" pytest "chromedriver-py==$("$CHROMIUM" --version | grep -oE '[0-9]+\.[0-9.]+')b0" 2>/dev/null \
  || "$BOX/.venv/bin/pip" -q install "selenium==$SE" pytest "chromedriver-py==$("$CHROMIUM" --version | grep -oE '[0-9]+\.[0-9.]+')"
cp "$("$BOX/.venv/bin/python" -c 'import chromedriver_py, os; print(os.path.dirname(chromedriver_py.__file__))')/chromedriver_linux64" "$BOX/chromedriver"

# JavaScript: the bindings, Mocha, and local copies of the CDN files the Selenium test pages load
cd "$BOX/node" && [ -f package.json ] || npm init -y >/dev/null
npm i -s "selenium-webdriver@$SE" mocha@10 bootstrap@5.1.0 bootstrap-datepicker@1.9.0 jquery@3.6.0

# Java: every jar of selenium-java, the Grid server and JUnit 5 in box/java/lib
cat > "$BOX/java/pom.xml" <<POM
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion>
<groupId>bb</groupId><artifactId>se</artifactId><version>1</version>
<dependencies>
<dependency><groupId>org.seleniumhq.selenium</groupId><artifactId>selenium-java</artifactId><version>$SE</version></dependency>
<dependency><groupId>org.seleniumhq.selenium</groupId><artifactId>selenium-grid</artifactId><version>$SE</version></dependency>
<dependency><groupId>org.junit.platform</groupId><artifactId>junit-platform-console-standalone</artifactId><version>1.11.4</version></dependency>
<dependency><groupId>org.slf4j</groupId><artifactId>slf4j-nop</artifactId><version>2.0.16</version></dependency>
</dependencies></project>
POM
cd "$BOX/java" && mvn -q -B dependency:copy-dependencies -DoutputDirectory=lib

# A self signed certificate for the local copy of https://www.selenium.dev/selenium/web/
openssl req -x509 -newkey rsa:2048 -nodes -days 3650 -subj "/CN=www.selenium.dev" -keyout "$BOX/key.pem" -out "$BOX/cert.pem" 2>/dev/null

# ChromeDriver looks for /opt/google/chrome/chrome. The wrapper starts Chromium and sends selenium.dev and the
# CDN hosts to the local server (siteserver.py), so examples keep the real URLs a reader would use.
mkdir -p /opt/google/chrome
cat > /opt/google/chrome/chrome <<SH
#!/bin/sh
exec "$CHROMIUM" --no-sandbox --no-proxy-server --ignore-certificate-errors --host-resolver-rules="MAP www.selenium.dev:443 127.0.0.1:8443, MAP cdn.jsdelivr.net:443 127.0.0.1:8443, MAP unpkg.com:443 127.0.0.1:8443, MAP code.jquery.com:443 127.0.0.1:8443" "\$@"
SH
chmod +x /opt/google/chrome/chrome
echo "Set up done in $BOX"
