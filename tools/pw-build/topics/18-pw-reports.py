import importlib.util
import os
import subprocess

from pkit import part, say, quiz, calc, panel, four, one, js, ts, py, jv, table, tip, figure, by

# the framework chapter reads the four real projects, the labs add report code to them
_spec = importlib.util.spec_from_file_location('fw16', os.path.join(os.path.dirname(os.path.abspath(__file__)), '16-pw-framework.py'))
fw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fw)

MODULE = fw.MODULE
TREE, run_files, JM, JT = fw.TREE, fw.run_files, fw.JM, fw.JT
JAVA_NOISE = fw.JAVA_NOISE
PW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = os.path.join(PW, 'screens', 'report_shot.py')
VPY = os.path.join(PW, 'box', '.venv', 'bin', 'python')

JAVA_TRIM = JAVA_NOISE + [(r'(?m)^\tat .*\n', ''), (r'(?ms)^Call log:\n.*?(?=^\[|\Z)', '')]
PY_TRIM = [(r'(?m)^(=+ test session starts =+|platform .*|rootdir: .*|configfile: .*|plugins: .*|cachedir: .*)\n', '')]
TS_TRIM = [(r'(?ms)^\s+Call log:\n.*?(?=^\s+\d+ \||^\s+at |\Z)', ''), (r'(?ms)^\s+\d+ \|.*?(?=^\s+at |\Z)', ''),
           (r'(?m)^\s+Error Context: .*\n', '')]


def shot(folder, page, kind, name, failed=''):
    """A build hook: screenshot the report a run just wrote, before its folder is deleted."""
    def after(d, port, res):
        env = {**os.environ}
        if os.path.exists('/root/.ccr/ca-bundle.crt'):
            env['SSL_CERT_FILE'] = '/root/.ccr/ca-bundle.crt'
        subprocess.run([VPY, SHOT, os.path.join(d, folder), page, kind, name, failed], check=True, env=env)
    return after


def hook(spec, fn):
    spec['after'] = fn
    return spec


# ---------- the test that fails on purpose, so every report has a failure to show ----------
PRICE_TS = '''import { test, expect } from '../../src/fixtures/index';
import { products } from '../../src/data/products';

// Out of date on purpose: the lamp now costs ₹1,299, so the reports have a failure to show
test('the desk lamp costs ₹1,199', async ({ productsPage }) => {
  await productsPage.open();
  await expect(productsPage.card(products.deskLamp.name).price).toHaveText('₹1,199');
});'''

PRICE_TS_ALLURE = '''import * as allure from 'allure-js-commons';
import { test, expect } from '../../src/fixtures/index';
import { products } from '../../src/data/products';

// Out of date on purpose: the lamp now costs ₹1,299, so the reports have a failure to show
test('the desk lamp costs ₹1,199', async ({ productsPage }) => {
  await allure.feature('Prices');
  await allure.severity('critical');
  await test.step('open the products page', async () => {
    await productsPage.open();
  });
  await test.step('check the lamp price', async () => {
    await expect(productsPage.card(products.deskLamp.name).price).toHaveText('₹1,199');
  });
});'''

PRICE_PY = '''from playwright.sync_api import expect

from framework.data.products import DESK_LAMP
from framework.pages.products_page import ProductsPage


# Out of date on purpose: the lamp now costs ₹1,299, so the reports have a failure to show
def test_the_desk_lamp_costs_1199(products_page: ProductsPage):
    products_page.open()
    expect(products_page.card(DESK_LAMP.name).price).to_have_text("₹1,199")'''

PRICE_PY_ALLURE = '''import allure
from playwright.sync_api import expect

from framework.data.products import DESK_LAMP
from framework.pages.products_page import ProductsPage


# Out of date on purpose: the lamp now costs ₹1,299, so the reports have a failure to show
@allure.feature("Prices")
@allure.severity(allure.severity_level.CRITICAL)
def test_the_desk_lamp_costs_1199(products_page: ProductsPage):
    with allure.step("open the products page"):
        products_page.open()
    with allure.step("check the lamp price"):
        expect(products_page.card(DESK_LAMP.name).price).to_have_text("₹1,199")'''

PRICE_JAVA = '''package com.brainy.shop.tests.products;

import com.brainy.shop.base.BaseTest;
import com.brainy.shop.data.Product;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class PriceTest extends BaseTest {
  // Out of date on purpose: the lamp now costs ₹1,299, so the reports have a failure to show
  @Test
  public void theDeskLampCosts1199() {
    productsPage.open();
    assertThat(productsPage.card(Product.DESK_LAMP.label).price).hasText("₹1,199");
  }
}'''

PRICE_JAVA_ALLURE = '''package com.brainy.shop.tests.products;

import com.brainy.shop.base.BaseTest;
import com.brainy.shop.data.Product;
import io.qameta.allure.Allure;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class PriceTest extends BaseTest {
  // Out of date on purpose: the lamp now costs ₹1,299, so the reports have a failure to show
  @Test
  @Feature("Prices")
  @Severity(SeverityLevel.CRITICAL)
  public void theDeskLampCosts1199() {
    Allure.step("open the products page", () -> productsPage.open());
    Allure.step("check the lamp price",
        () -> assertThat(productsPage.card(Product.DESK_LAMP.label).price).hasText("₹1,199"));
  }
}'''

TS_PRICE = 'tests/products/price.spec.ts'
JS_PRICE = 'tests/products/price.spec.js'
PY_PRICE = 'tests/products/test_price.py'
JAVA_PRICE = JT + 'tests/products/PriceTest.java'
REP = 'src/test/java/com/brainy/shop/reporting/'


def to_js(src):
    """The JavaScript version of a lab test file: the same code, with .js on local imports as ES modules need."""
    import re
    return re.sub(r"(from '\.\.?/[\w./-]+?)(?<!\.js)'", r"\1.js'", src)


def node_files(lang, extra):
    out = dict(run_files(lang))
    for k, v in extra.items():
        if lang == 'js':
            out[k.replace('.ts', '.js')] = SUMMARY_JS if k.endswith('summary-reporter.ts') else to_js(v)
        else:
            out[k] = v
    return out


def java_files(extra, pom_deps='', listeners=()):
    files = dict(run_files('java'))
    if pom_deps:
        files['pom.xml'] = files['pom.xml'].replace('  </dependencies>', pom_deps + '  </dependencies>')
    if listeners:
        tags = ''.join(f'\n    <listener class-name="com.brainy.shop.reporting.{n}"/>' for n in listeners)
        files['testng.xml'] = files['testng.xml'].replace('<suite name="Brainy Shop" parallel="classes" thread-count="2">',
                                                          f'<suite name="Brainy Shop" parallel="classes" thread-count="2">\n  <listeners>{tags}\n  </listeners>')
    files.update(extra)
    return files


EXTENT_DEP = '''    <dependency>
      <groupId>com.aventstack</groupId>
      <artifactId>extentreports</artifactId>
      <version>5.1.2</version>
      <scope>test</scope>
    </dependency>
'''
ALLURE_DEP = '''    <dependency>
      <groupId>io.qameta.allure</groupId>
      <artifactId>allure-testng</artifactId>
      <version>3.0.1</version>
      <scope>test</scope>
    </dependency>
'''

EVIDENCE_EXTENT = '''package com.brainy.shop.reporting;

import com.brainy.shop.base.BaseTest;
import org.testng.ITestListener;
import org.testng.ITestResult;

// TestNG calls onTestFailure while the page is still open, so the screenshot shows the failure
public class EvidenceListener implements ITestListener {
  @Override
  public void onTestFailure(ITestResult result) {
    if (result.getInstance() instanceof BaseTest test) {
      result.setAttribute("screenshot", test.screenshot());   // ExtentReporter reads it at the end
    }
  }
}'''

EVIDENCE_ALLURE = '''package com.brainy.shop.reporting;

import com.brainy.shop.base.BaseTest;
import io.qameta.allure.Allure;
import io.qameta.allure.AttachmentOptions;
import org.testng.ITestListener;
import org.testng.ITestResult;

import java.io.ByteArrayInputStream;

// TestNG calls onTestFailure while the page is still open, so the screenshot shows the failure
public class EvidenceListener implements ITestListener {
  @Override
  public void onTestFailure(ITestResult result) {
    if (result.getInstance() instanceof BaseTest test) {
      byte[] png = test.screenshot();
      Allure.attachment("screenshot at failure", "image/png", new ByteArrayInputStream(png),
          AttachmentOptions.withFileExtension(".png"));
    }
  }
}'''

EXTENT_REPORTER = '''package com.brainy.shop.reporting;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.ExtentTest;
import com.aventstack.extentreports.MediaEntityBuilder;
import com.aventstack.extentreports.reporter.ExtentSparkReporter;
import org.testng.IReporter;
import org.testng.ISuite;
import org.testng.ITestResult;
import org.testng.xml.XmlSuite;

import java.util.ArrayList;
import java.util.Base64;
import java.util.Comparator;
import java.util.Date;
import java.util.List;

// TestNG calls generateReport once, after the whole suite. It writes target/extent/index.html
public class ExtentReporter implements IReporter {
  @Override
  public void generateReport(List<XmlSuite> xmlSuites, List<ISuite> suites, String outputDirectory) {
    ExtentSparkReporter spark = new ExtentSparkReporter("target/extent/index.html");
    spark.config().setDocumentTitle("Brainy Shop tests");
    spark.config().setReportName("Brainy Shop, nightly run");
    ExtentReports extent = new ExtentReports();
    extent.attachReporter(spark);
    extent.setSystemInfo("Browser", "Chromium");

    List<ITestResult> all = new ArrayList<>();
    for (ISuite suite : suites) {
      suite.getResults().values().forEach(r -> {
        all.addAll(r.getTestContext().getPassedTests().getAllResults());
        all.addAll(r.getTestContext().getFailedTests().getAllResults());
        all.addAll(r.getTestContext().getSkippedTests().getAllResults());
      });
    }
    all.sort(Comparator.comparingLong(ITestResult::getStartMillis));
    for (ITestResult result : all) add(extent, result);
    extent.flush();
  }

  private void add(ExtentReports extent, ITestResult result) {
    ExtentTest test = extent.createTest(result.getMethod().getMethodName())
        .assignCategory(result.getTestClass().getRealClass().getSimpleName());
    for (String group : result.getMethod().getGroups()) test.assignCategory(group);
    test.getModel().setStartTime(new Date(result.getStartMillis()));   // the real times, not the report time
    test.getModel().setEndTime(new Date(result.getEndMillis()));
    switch (result.getStatus()) {
      case ITestResult.SUCCESS -> test.pass("Passed");
      case ITestResult.SKIP -> test.skip("Skipped");
      default -> {
        test.fail(result.getThrowable());
        if (result.getAttribute("screenshot") instanceof byte[] png) {
          String base64 = Base64.getEncoder().encodeToString(png);
          test.fail("Screenshot at failure", MediaEntityBuilder.createScreenCaptureFromBase64String(base64).build());
        }
      }
    }
  }
}'''

ALLURE_PROPS = 'allure.results.directory=target/allure-results'

PY_ALLURE_HOOK = '''import allure
import pytest


# After each test: when it failed, attach a screenshot of the page to the Allure results.
# pytest-playwright already puts its own screenshot and trace into pytest-html.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    page = item.funcargs.get("page")
    if report.when == "call" and report.failed and page:
        allure.attach(page.screenshot(), name="screenshot at failure", attachment_type=allure.attachment_type.PNG)'''

SUMMARY_TS = '''import type { FullConfig, FullResult, Reporter, Suite, TestCase, TestResult } from '@playwright/test/reporter';

// One line per test, then a short summary that a team could also send to chat or a dashboard
export default class SummaryReporter implements Reporter {
  private passed = 0;
  private failed: string[] = [];

  onBegin(config: FullConfig, suite: Suite) {
    console.log(`Starting ${suite.allTests().length} tests on ${config.workers} workers`);
  }

  onTestEnd(test: TestCase, result: TestResult) {
    const seconds = (result.duration / 1000).toFixed(1);
    if (result.status === 'passed') {
      this.passed++;
      console.log(`PASS  ${test.title} (${seconds} s)`);
    } else {
      this.failed.push(test.title);
      console.log(`FAIL  ${test.title} (${seconds} s)`);
    }
  }

  onEnd(result: FullResult) {
    console.log(`${this.passed} passed, ${this.failed.length} failed, run ${result.status}`);
    for (const title of this.failed) console.log(`  to look at: ${title}`);
  }
}'''

SUMMARY_JS = '''// One line per test, then a short summary that a team could also send to chat or a dashboard
export default class SummaryReporter {
  passed = 0;
  failed = [];

  onBegin(config, suite) {
    console.log(`Starting ${suite.allTests().length} tests on ${config.workers} workers`);
  }

  onTestEnd(test, result) {
    const seconds = (result.duration / 1000).toFixed(1);
    if (result.status === 'passed') {
      this.passed++;
      console.log(`PASS  ${test.title} (${seconds} s)`);
    } else {
      this.failed.push(test.title);
      console.log(`FAIL  ${test.title} (${seconds} s)`);
    }
  }

  onEnd(result) {
    console.log(`${this.passed} passed, ${this.failed.length} failed, run ${result.status}`);
    for (const title of this.failed) console.log(`  to look at: ${title}`);
  }
}'''

SUMMARY_PY = '''import pytest

results = []


# pytest reports each test three times: setup, call and teardown. The call holds the result,
# and a failure while setting up is reported in the setup instead.
def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and not report.passed):
        results.append(report)


def pytest_terminal_summary(terminalreporter):
    tr = terminalreporter
    tr.section("shop summary")
    for r in results:
        name = r.nodeid.split("::")[-1]
        tr.write_line(f"{'PASS' if r.passed else 'FAIL'}  {name} ({r.duration:.1f} s)")
    failed = [r.nodeid.split("::")[-1] for r in results if r.failed]
    tr.write_line(f"{len(results) - len(failed)} passed, {len(failed)} failed")
    for name in failed:
        tr.write_line(f"  to look at: {name}")'''

SUMMARY_JAVA = '''package com.brainy.shop.reporting;

import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

// One line per test, then a short summary when the run ends
public class SummaryListener implements ITestListener {
  @Override
  public void onTestSuccess(ITestResult result) { line("PASS", result); }

  @Override
  public void onTestFailure(ITestResult result) { line("FAIL", result); }

  @Override
  public void onTestSkipped(ITestResult result) { line("SKIP", result); }

  @Override
  public void onFinish(ITestContext context) {
    System.out.printf("%d passed, %d failed, %d skipped%n", context.getPassedTests().size(),
        context.getFailedTests().size(), context.getSkippedTests().size());
    context.getFailedTests().getAllResults()
        .forEach(r -> System.out.println("  to look at: " + r.getMethod().getMethodName()));
  }

  private void line(String status, ITestResult r) {
    double seconds = (r.getEndMillis() - r.getStartMillis()) / 1000.0;
    System.out.printf("%s  %s (%.1f s)%n", status, r.getMethod().getMethodName(), seconds);
  }
}'''

ALLURE_TS_CMD = 'npx playwright test --reporter=line,allure-playwright; npx allure generate allure-results && ls allure-report/index.html'
MERGE_CMD = ('for i in 1 2; do npx playwright test --shard=$i/2 --reporter=blob; mkdir -p all-blob-reports; mv blob-report/*.zip all-blob-reports/; done; '
             'npx playwright merge-reports --reporter=html ./all-blob-reports; ls playwright-report')

CODES = {
    'builtin': four('Lab 1: the reports a machine reads',
                    java=jv(java_files({JAVA_PRICE: PRICE_JAVA}), kind='testng',
                            cmd="mvn test; grep -o '<testsuite [^>]*>' target/surefire-reports/TEST-TestSuite.xml",
                            show=[JAVA_PRICE], replace=JAVA_TRIM),
                    py=py({**run_files('python'), PY_PRICE: PRICE_PY}, ini=None,
                          cmd="pytest -q --tb=line --junitxml=results/junit.xml; grep -o '<testsuite [^>]*>' results/junit.xml",
                          show=[PY_PRICE], replace=PY_TRIM),
                    js=js(node_files('js', {TS_PRICE: PRICE_TS}), config=None,
                          cmd="PLAYWRIGHT_JSON_OUTPUT_NAME=results/results.json PLAYWRIGHT_JUNIT_OUTPUT_NAME=results/junit.xml npx playwright test --reporter=dot,json,junit; "
                              "grep -o '<testsuites [^>]*>' results/junit.xml; node -p \"JSON.stringify(require('./results/results.json').stats)\"",
                          show=[JS_PRICE], replace=TS_TRIM),
                    ts=ts(node_files('ts', {TS_PRICE: PRICE_TS}),
                          cmd="PLAYWRIGHT_JSON_OUTPUT_NAME=results/results.json PLAYWRIGHT_JUNIT_OUTPUT_NAME=results/junit.xml npx playwright test --reporter=dot,json,junit; "
                              "grep -o '<testsuites [^>]*>' results/junit.xml; node -p \"JSON.stringify(require('./results/results.json').stats)\"",
                          show=[TS_PRICE], replace=TS_TRIM),
                    result='One test now fails on purpose: the lamp costs ₹1,299, not ₹1,199. Every runner printed a short result for people and wrote JUnit XML for machines. The XML line is what Jenkins, GitLab and Azure DevOps read to count passed and failed tests: eight tests, one failure. Playwright Test also wrote JSON, whose stats say 7 expected and 1 unexpected. Several reporters can run at once, here dot, json and junit.'),
    'html': four('Lab 2: an HTML report for people',
                 java=hook(jv(java_files({JAVA_PRICE: PRICE_JAVA, REP + 'EvidenceListener.java': EVIDENCE_EXTENT, REP + 'ExtentReporter.java': EXTENT_REPORTER},
                                         pom_deps=EXTENT_DEP, listeners=('EvidenceListener', 'ExtentReporter')), kind='testng',
                              cmd='mvn test; ls target/extent',
                              show=[REP + 'ExtentReporter.java', REP + 'EvidenceListener.java', 'testng.xml', 'pom.xml'], replace=JAVA_TRIM),
                           shot('target/extent', 'index.html', 'extent', 'report-extent')),
                 py=hook(py({**run_files('python'), PY_PRICE: PRICE_PY}, ini=None,
                            cmd='pytest -q --tb=line --html=reports/report.html --self-contained-html; ls reports',
                            show=[PY_PRICE, 'pytest.ini'], replace=PY_TRIM),
                         shot('reports', 'report.html', 'pytest-html', 'report-pytest-html')),
                 js=js(node_files('js', {TS_PRICE: PRICE_TS}), config=None, cmd='npx playwright test --reporter=line,html; ls playwright-report',
                       show=['playwright.config.js'], replace=TS_TRIM),
                 ts=hook(ts(node_files('ts', {TS_PRICE: PRICE_TS}), cmd='npx playwright test --reporter=line,html; ls playwright-report',
                            show=['playwright.config.ts'], replace=TS_TRIM),
                         shot('playwright-report', 'index.html', 'playwright', 'report-pw-html', 'the desk lamp costs')),
                 result='Each language now has a report a person can open in a browser. Playwright Test has one built in: playwright-report/index.html, with the screenshot, video and trace of the failed test, because the config keeps them on failure. pytest-html wrote one self-contained file, and pytest-playwright added its screenshot and trace link to it by itself. In Java, a TestNG listener grabs a screenshot when a test fails, and an IReporter builds an ExtentReports page from all the results when the suite ends.'),
    'allure': four('Lab 3: Allure Report, the same report for every language',
                   java=hook(jv(java_files({JAVA_PRICE: PRICE_JAVA_ALLURE, REP + 'EvidenceListener.java': EVIDENCE_ALLURE,
                                            'src/test/resources/allure.properties': ALLURE_PROPS},
                                           pom_deps=ALLURE_DEP, listeners=('EvidenceListener',)), kind='testng',
                                cmd='mvn test; npx allure generate target/allure-results && ls allure-report/index.html',
                                show=[JAVA_PRICE, REP + 'EvidenceListener.java', 'src/test/resources/allure.properties', 'pom.xml'], replace=JAVA_TRIM),
                             shot('allure-report', 'index.html', 'allure', 'report-allure-java', 'theDeskLampCosts1199')),
                   py=hook(py({**run_files('python'), PY_PRICE: PRICE_PY_ALLURE, 'tests/conftest.py': PY_ALLURE_HOOK}, ini=None,
                              cmd='pytest -q --tb=line --alluredir=allure-results; npx allure generate allure-results && ls allure-report/index.html',
                              show=[PY_PRICE, 'tests/conftest.py'], replace=PY_TRIM),
                           shot('allure-report', 'index.html', 'allure', 'report-allure-py', 'desk_lamp_costs')),
                   js=js(node_files('js', {TS_PRICE: PRICE_TS_ALLURE}), config=None, cmd=ALLURE_TS_CMD, show=[JS_PRICE], replace=TS_TRIM),
                   ts=hook(ts(node_files('ts', {TS_PRICE: PRICE_TS_ALLURE}), cmd=ALLURE_TS_CMD, show=[TS_PRICE], replace=TS_TRIM),
                           shot('allure-report', 'index.html', 'allure', 'report-allure-ts', 'desk lamp costs')),
                   result='Each language wrote raw results into an allure-results folder: allure-playwright for Playwright Test, allure-pytest for pytest and allure-testng for TestNG. The same Allure command line then built the same kind of report from them. The labels and steps in the test show up as severity, feature and a step list, and the failure carries its screenshot.'),
    'custom': four('Lab 4: write your own reporter',
                   java=jv(java_files({JAVA_PRICE: PRICE_JAVA, REP + 'SummaryListener.java': SUMMARY_JAVA}, listeners=('SummaryListener',)),
                           kind='testng', cmd='mvn test; echo "exit code $?"', show=[REP + 'SummaryListener.java', 'testng.xml'], replace=JAVA_TRIM),
                   py=py({**run_files('python'), PY_PRICE: PRICE_PY, 'framework/reporting/summary.py': SUMMARY_PY}, ini=None,
                         cmd='pytest -q --tb=no -p framework.reporting.summary; echo "exit code $?"', show=['framework/reporting/summary.py'], replace=PY_TRIM),
                   js=js(node_files('js', {TS_PRICE: PRICE_TS, 'reporters/summary-reporter.ts': SUMMARY_TS}), config=None,
                         cmd='npx playwright test --reporter=./reporters/summary-reporter.js; echo "exit code $?"', show=['reporters/summary-reporter.js']),
                   ts=ts(node_files('ts', {TS_PRICE: PRICE_TS, 'reporters/summary-reporter.ts': SUMMARY_TS}),
                         cmd='npx playwright test --reporter=./reporters/summary-reporter.ts; echo "exit code $?"', show=['reporters/summary-reporter.ts']),
                   result='A reporter is a class or a set of hooks that the runner calls as the run goes: once at the start, once per finished test and once at the end. Playwright Test calls onBegin, onTestEnd and onEnd. pytest calls pytest_runtest_logreport for every phase and pytest_terminal_summary at the end. TestNG calls ITestListener methods. The run still fails with exit code 1, so CI marks it red whatever the reporter prints.'),
    'merge': one('Lab 5: one HTML report from several shards',
                 ts(node_files('ts', {TS_PRICE: PRICE_TS}), cmd=MERGE_CMD, show=[TS_PRICE], replace=TS_TRIM),
                 result='Two shards each wrote a blob report, and merge-reports built one HTML report from both: the same playwright-report folder a single run makes, with all eight tests and the failure from shard 1. This is the last job of the sharded workflow in the CI/CD chapter.'),
}

DG = {
    'flow': {'t': 'From a test run to a report someone reads', 'w': 900, 'h': 240,
             'n': [['run', 20, 92, 120, 56, 'test run', {'c': 2, 'sub': 'any runner', 'i': 'Playwright Test, pytest or TestNG runs the tests.'}],
                   ['con', 190, 20, 150, 56, 'terminal', {'c': 5, 'sub': 'list, dot, -v', 'i': 'A short result for the person watching.'}],
                   ['raw', 190, 165, 150, 56, 'raw results', {'c': 1, 'sub': 'XML, JSON, blob', 'i': 'Files that other tools read: JUnit XML, JSON, blob reports, allure-results.'}],
                   ['html', 400, 92, 150, 56, 'HTML report', {'c': 3, 'sub': 'built in or Allure', 'i': 'A page with every test, its steps, screenshots and traces.'}],
                   ['ci', 610, 30, 140, 56, 'CI server', {'c': 0, 'sub': 'reads JUnit XML', 'i': 'Counts passed and failed tests and keeps the history.'}],
                   ['ppl', 610, 155, 140, 56, 'people', {'c': 4, 'sub': 'testers, managers', 'i': 'Open the report to see what failed and why.'}]],
             'e': [['run', 'con'], ['run', 'raw'], ['raw', 'html'], ['raw', 'ci'], ['html', 'ppl']],
             'st': [[['run'], 'The runner runs the tests.'],
                    [['con', 'run>con'], 'Reporters print a short result in the terminal.'],
                    [['raw', 'run>raw'], 'Other reporters write raw results to files.'],
                    [['html', 'raw>html'], 'A report generator turns the raw results into a page.'],
                    [['ci', 'raw>ci'], 'The CI server reads the JUnit XML.'],
                    [['ppl', 'html>ppl'], 'People open the HTML report to find out why a test failed.']]},
}


def figs(items):
    """Screenshots per language: items is [(lang, file, alt, caption)]."""
    out = []
    for lang, src, alt, cap in items:
        out.append(f'<div class="only-{lang}">' + figure(src, alt, cap) + '</div>')
    return ''.join(out)


PARTS = [
    part('what', '📊', 'What a test report is for', f'''
<p>A <b>report</b> tells people and machines what happened in a test run: which tests ran, which failed, why, and how long it took. Different readers want different things, so a run usually writes several reports at once.</p>
<div class="viz" data-viz="flow" data-k="flow"></div>
{table(['Reader', 'Wants', 'Report'], [
    ['you, at the terminal', 'pass or fail, right now', 'list, line or dot in Playwright Test, -v or -q in pytest, the Surefire summary in Maven'],
    ['the CI server', 'counts and history', 'JUnit XML, which every CI server reads'],
    ['a tester fixing a failure', 'the error, the screenshot, the trace', 'the Playwright HTML report, pytest-html, Allure, ExtentReports'],
    ['a manager', 'a dashboard: how many passed, trends, which features', 'Allure, ExtentReports'],
    ['your own tools', 'data in a known shape', 'JSON, or a custom reporter'],
])}
{tip('The labs in this chapter all use the framework from the framework chapter, plus one test that fails on purpose: it still expects the lamp to cost ₹1,199 after a price change to ₹1,299. A report is only interesting when something fails.', 'tip')}
''', easy=True, kw=['report', 'reporter', 'JUnit XML', 'HTML report', 'dashboard', 'who reads']),

    part('lab1', '1️⃣', 'Lab 1: built-in reporters and JUnit XML', f'''
<p>Every runner has reporters built in. Start with the ones that need nothing installed.</p>
{table(['Playwright Test reporter', 'What it gives'], [
    ['list', 'one line per test, the default on a laptop'],
    ['line', 'one line that updates, and failures in full'],
    ['dot', 'one character per test, for long runs on CI'],
    ['html', 'a web page with every test, its steps, screenshots, videos and traces'],
    ['json', 'all results as JSON, for your own tools'],
    ['junit', 'JUnit XML for CI servers'],
    ['blob', 'raw results of one shard, merged later with merge-reports'],
    ['github', 'error notes on the right lines of a GitHub pull request'],
])}
<p>{by(py='In pytest the terminal output is set with <code>-v</code>, <code>-q</code> and <code>-rA</code>, and <code>--junitxml</code> writes JUnit XML.', java='Maven Surefire prints a summary and always writes XML files to target/surefire-reports. TestNG adds its own testng-results.xml.', js='Choose reporters with <code>--reporter</code> or in the config. Output files are set with options or environment variables such as PLAYWRIGHT_JUNIT_OUTPUT_NAME.')}</p>
[[builtin]]
''', kw=['list', 'line', 'dot', 'json', 'junit', 'blob', 'github', 'junitxml', 'surefire-reports']),

    part('lab2', '2️⃣', 'Lab 2: HTML reports with evidence', f'''
<p>An HTML report is what a tester opens first. A good one shows the error, a screenshot taken at the moment of failure, and a link to the trace.</p>
[[html]]
{figs([
    ('ts', 'report-pw-html-list.jpg', 'The Playwright HTML report from this run, listing eight tests with one failed', 'The Playwright HTML report from this run: filters at the top, one row per test file and test, the failed price test marked with a cross.'),
    ('js', 'report-pw-html-list.jpg', 'The Playwright HTML report from this run, listing eight tests with one failed', 'The Playwright HTML report from this run: filters at the top, one row per test file and test, the failed price test marked with a cross.'),
    ('ts', 'report-pw-html-failed.jpg', 'The failed price test in the Playwright HTML report, with expected and received prices', 'The failed test opened: the error with expected and received prices and the source line. The screenshot, video and trace are further down the same page.'),
    ('js', 'report-pw-html-failed.jpg', 'The failed price test in the Playwright HTML report, with expected and received prices', 'The failed test opened: the error with expected and received prices and the source line. The screenshot, video and trace are further down the same page.'),
    ('py', 'report-pytest-html.jpg', 'The pytest-html report with the failed price test opened, showing the error and a screenshot', 'The pytest-html report from this run: the environment, the summary with filters, and the failed test opened with its error, the screenshot and a Trace link.'),
    ('java', 'report-extent-tests.jpg', 'The ExtentReports page listing every test, with the failed price test opened', 'The ExtentReports page from this run: every test with its time, and the failed one with its error and the screenshot.'),
    ('java', 'report-extent-dashboard.jpg', 'The ExtentReports dashboard with pass and fail charts and a timeline', 'The ExtentReports dashboard: passed and failed counts, charts and a timeline of the run.'),
])}
{table(['Evidence', 'Playwright Test', 'pytest', 'Java with TestNG'], [
    ['screenshot at failure', "use: { screenshot: 'only-on-failure' }", '--screenshot only-on-failure', 'page.screenshot() in a listener'],
    ['video', "video: 'retain-on-failure'", '--video retain-on-failure', 'setRecordVideoDir in the context options'],
    ['trace', "trace: 'on-first-retry'", '--tracing retain-on-failure', 'context.tracing() in BaseTest'],
    ['your own file', 'testInfo.attach()', 'allure.attach or a pytest-html extra', 'Allure.attachment or an Extent media entity'],
])}
{tip('The report is only as good as its evidence. A failure with a screenshot and a trace can often be understood in a minute, without running anything again.', 'pro')}
''', kw=['html report', 'pytest-html', 'ExtentReports', 'Extent', 'screenshot', 'evidence', 'IReporter', 'ITestListener']),

    part('lab3', '3️⃣', 'Lab 3: Allure Report in all four languages', f'''
<p><b>Allure Report</b> is a free, open source report that many companies use, because it looks the same for every language and test runner. Each runner writes raw results with a small adapter, and the Allure command line turns them into a report.</p>
{table(['Language', 'Adapter', 'Writes results with'], [
    ['TypeScript and JavaScript', 'allure-playwright (npm)', '--reporter=allure-playwright'],
    ['Python', 'allure-pytest (pip)', '--alluredir=allure-results'],
    ['Java with TestNG', 'io.qameta.allure:allure-testng (Maven)', 'nothing: it registers itself as a TestNG listener'],
])}
[[allure]]
{figs([
    ('ts', 'report-allure-ts-overview.jpg', 'The Allure report overview for the TypeScript run', 'The Allure overview from the TypeScript run: totals, the pass rate and the tests grouped by folder.'),
    ('js', 'report-allure-ts-overview.jpg', 'The Allure report overview for the Playwright Test run', 'The Allure overview from the Playwright Test run: totals, the pass rate and the tests grouped by folder.'),
    ('ts', 'report-allure-ts-failed.jpg', 'The failed price test in Allure with its error, severity and feature', 'The failed test in Allure: expected and received side by side, the Critical severity, and three attachments kept by Playwright Test, among them the screenshot and the video.'),
    ('js', 'report-allure-ts-failed.jpg', 'The failed price test in Allure with its error, severity and feature', 'The failed test in Allure: expected and received side by side, the Critical severity, and three attachments kept by Playwright Test, among them the screenshot and the video.'),
    ('py', 'report-allure-py-overview.jpg', 'The Allure report overview for the Python run', 'The Allure overview from the pytest run.'),
    ('py', 'report-allure-py-failed.jpg', 'The failed price test in Allure from the Python run', 'The failed test in Allure: the error, the Critical severity from the decorator, and the screenshot from the conftest hook under Attachments.'),
    ('java', 'report-allure-java-overview.jpg', 'The Allure report overview for the Java run', 'The Allure overview from the TestNG run.'),
    ('java', 'report-allure-java-failed.jpg', 'The failed price test in Allure from the Java run', 'The failed test in Allure: the error, the Prices feature and Critical severity from the annotations, and the screenshot from the listener under Attachments.'),
])}
{tip('This page uses Allure Report 3, which installs from npm and needs Node.js, even for Python and Java projects: <code>npx allure generate allure-results</code>. Allure Report 2 is a Java program installed separately, with the command <code>allure generate</code>. Both read the same allure-results folder.', 'new')}
{tip('Keep the allure-results of earlier runs, or the history folder of the last report, and Allure shows trends and flaky tests across runs.', 'pro')}
''', kw=['Allure', 'allure-playwright', 'allure-pytest', 'allure-testng', 'allure-results', 'severity', 'feature', 'steps']),

    part('lab4', '4️⃣', 'Lab 4: a custom reporter', f'''
<p>Sometimes a team wants something no reporter gives: a message in a chat channel, a row in a dashboard, or a list of failed tests in a fixed format. Every runner lets you write your own reporter.</p>
[[custom]]
{table(['', 'Playwright Test', 'pytest', 'TestNG'], [
    ['at the start', 'onBegin(config, suite)', 'pytest_sessionstart', 'onStart(context)'],
    ['after each test', 'onTestEnd(test, result)', 'pytest_runtest_logreport(report)', 'onTestSuccess, onTestFailure, onTestSkipped'],
    ['at the end', 'onEnd(result)', 'pytest_terminal_summary', 'onFinish(context), or IReporter.generateReport'],
    ['turn it on', '--reporter=./my-reporter.ts or the config', '-p module, or code in conftest.py', 'a listener in testng.xml'],
])}
{tip('A reporter must not change whether the run passed. It only describes the run, so CI still sees exit code 1 when a test failed.', 'warn')}
''', kw=['custom reporter', 'Reporter interface', 'onTestEnd', 'pytest hooks', 'ITestListener', 'listener']),

    part('lab5', '5️⃣', 'Lab 5: merging and publishing reports in CI', f'''
<p>With shards, each machine has only part of the results. Merge them into one report, then publish it where the team looks.</p>
[[merge]]
{table(['Where', 'How'], [
    ['GitHub Actions', 'upload the report folder as an artifact, or publish it to GitHub Pages'],
    ['Jenkins', 'the junit step for counts and history, and the HTML Publisher or Allure plugin for the page'],
    ['GitLab CI', 'artifacts: reports: junit, and the report folder as an artifact or GitLab Pages'],
    ['Azure DevOps', 'PublishTestResults for JUnit XML, and PublishPipelineArtifact for the HTML'],
])}
{tip('Python and Java shards each write their own JUnit XML file. CI servers read many files at once, for example target/surefire-reports/*.xml in Jenkins, so they do not need merging first. Allure also reads several allure-results folders in one command.', 'tip')}
''', kw=['merge-reports', 'blob', 'publish', 'GitHub Pages', 'artifact', 'Jenkins junit', 'HTML Publisher']),

    part('choose', '🧭', 'Which report should a team use?', f'''
<p>Most teams combine a few. Here is a starting point that suits most projects.</p>
{table(['Need', 'TypeScript and JavaScript', 'Python', 'Java'], [
    ['CI counts', 'junit reporter', '--junitxml', 'Surefire XML, already there'],
    ['debugging a failure', 'the built-in HTML report with traces', 'pytest-html with traces from pytest-playwright', 'traces from BaseTest, plus Extent or Allure'],
    ['one report for many languages and teams', 'Allure', 'Allure', 'Allure'],
    ['a report managers know from older Java projects', '', '', 'ExtentReports'],
    ['something special', 'a custom reporter', 'hooks in a plugin', 'a listener'],
])}
{tip('Start with the built-in reports and JUnit XML. Add Allure or Extent when someone outside the test team needs to read the results, not before.', 'pro')}
''', kw=['choose', 'compare', 'Allure vs Extent', 'recommendation']),
]

INFO = {'title': 'Reports in four ideas', 'panels': [
    panel([['e', '🖥️'], ['t', 'terminal', {'b': 1}]], 'For you', 'list, dot, -v.', 'Right now.'),
    panel([['e', '🧾'], ['t', 'JUnit XML', {'b': 1}]], 'For CI', 'Counts and history.', 'Every server reads it.'),
    panel([['e', '📸'], ['t', 'HTML', {'b': 1}]], 'For testers', 'Error, screenshot, trace.', 'Why it failed.'),
    panel([['e', '📈'], ['t', 'Allure', {'b': 1}]], 'For everyone', 'Same report, any language.', 'Trends and labels.')],
    'remember': 'Write several reports from one run: a short one for the terminal, JUnit XML for CI, and an HTML report with evidence for people.'}

REAL = [
    ['🧾', 'The report that saved a release meeting', 'A release manager asks whether checkout is safe to ship. The Allure report filtered by the Checkout feature shows all tests green for the last ten nightly runs, and the meeting takes two minutes.'],
    ['📸', 'A failure understood without a rerun', 'A test fails only on CI. The HTML report has the screenshot at failure: a cookie banner covers the button. The fix is one line in the fixture, found without running anything again.'],
    ['💬', 'Failures in the team chat', 'A team writes a twenty line custom reporter that posts the failed test names to their chat channel when the nightly run ends. People see failures at the start of the day instead of finding them later.'],
]

SAY = [
    say('top', 'Welcome', 'This chapter is a set of reporting labs: built-in reporters and JUnit XML, HTML reports with evidence, Allure in all four languages, ExtentReports for Java, your own reporter, and merging reports in CI.',
        'यह अध्याय reporting labs का एक सेट है: built-in reporters और JUnit XML, सबूत के साथ HTML reports, चारों भाषाओं में Allure, Java के लिए ExtentReports, आपका अपना reporter, और CI में reports जोड़ना।',
        'ಈ ಅಧ್ಯಾಯ reporting labs ಗುಂಪು: built-in reporters ಮತ್ತು JUnit XML, ಸಾಕ್ಷ್ಯದೊಂದಿಗೆ HTML reports, ನಾಲ್ಕೂ ಭಾಷೆಗಳಲ್ಲಿ Allure, Java ಗೆ ExtentReports, ನಿಮ್ಮದೇ reporter, ಮತ್ತು CI ನಲ್ಲಿ reports ಸೇರಿಸುವುದು.',
        'ଏହି ଅଧ୍ୟାୟ reporting labs ର ଏକ ସେଟ୍: built-in reporters ଓ JUnit XML, ପ୍ରମାଣ ସହ HTML reports, ଚାରି ଭାଷାରେ Allure, Java ପାଇଁ ExtentReports, ଆପଣଙ୍କ ନିଜ reporter, ଏବଂ CI ରେ reports ଯୋଡିବା।',
        'هذا الفصل مجموعة مختبرات للتقارير: المراسلون المدمجون وJUnit XML، وتقارير HTML مع الأدلة، وAllure في اللغات الأربع، وExtentReports لـ Java، ومراسلك الخاص، ودمج التقارير في CI.',
        'Dieses Kapitel ist eine Reihe von Berichts-Labs: eingebaute Reporter und JUnit XML, HTML-Berichte mit Belegen, Allure in allen vier Sprachen, ExtentReports für Java, ein eigener Reporter und das Zusammenführen von Berichten in CI.'),
    say('what', 'What a report is for', 'A report tells people and machines what happened in a run. The terminal is for you, JUnit XML is for the CI server, and an HTML report with screenshots and traces is for whoever fixes a failure.',
        'Report लोगों और machines को बताता है कि run में क्या हुआ। Terminal आपके लिए है, JUnit XML CI server के लिए, और screenshots व traces वाली HTML report failure ठीक करने वाले के लिए।',
        'Report ಜನರಿಗೂ machines ಗೂ run ನಲ್ಲಿ ಏನಾಯಿತು ಎಂದು ಹೇಳುತ್ತದೆ. Terminal ನಿಮಗಾಗಿ, JUnit XML CI server ಗಾಗಿ, screenshots ಮತ್ತು traces ಇರುವ HTML report failure ಸರಿಪಡಿಸುವವರಿಗಾಗಿ.',
        'Report ଲୋକ ଓ machines କୁ କହେ run ରେ କଣ ହେଲା। Terminal ଆପଣଙ୍କ ପାଇଁ, JUnit XML CI server ପାଇଁ, ଏବଂ screenshots ଓ traces ଥିବା HTML report failure ଠିକ୍ କରୁଥିବା ଲୋକ ପାଇଁ।',
        'يخبر التقرير الناس والآلات بما حدث في التشغيل. الطرفية لك، وJUnit XML لخادم CI، وتقرير HTML مع اللقطات والآثار لمن يصلح الفشل.',
        'Ein Bericht sagt Menschen und Maschinen, was in einem Lauf passiert ist. Das Terminal ist für dich, JUnit XML für den CI-Server und ein HTML-Bericht mit Screenshots und Traces für den, der einen Fehler behebt.'),
    say('lab1', 'Lab 1', 'Every runner has built-in reporters. Several can run at once: a short one for the terminal and JUnit XML for the CI server. Playwright Test can also write JSON.',
        'हर runner में built-in reporters होते हैं। कई एक साथ चल सकते हैं: terminal के लिए छोटा और CI server के लिए JUnit XML। Playwright Test JSON भी लिख सकता है।',
        'ಪ್ರತಿ runner ನಲ್ಲಿ built-in reporters ಇವೆ. ಹಲವು ಒಟ್ಟಿಗೆ ನಡೆಯಬಹುದು: terminal ಗೆ ಚಿಕ್ಕದು, CI server ಗೆ JUnit XML. Playwright Test JSON ಕೂಡ ಬರೆಯಬಲ್ಲದು.',
        'ପ୍ରତି runner ରେ built-in reporters ଅଛି। ଅନେକ ଏକାସାଙ୍ଗରେ ଚାଲିପାରେ: terminal ପାଇଁ ଛୋଟ ଓ CI server ପାଇଁ JUnit XML। Playwright Test JSON ମଧ୍ୟ ଲେଖିପାରେ।',
        'لكل مشغّل مراسلون مدمجون، ويمكن تشغيل عدة منهم معًا: واحد مختصر للطرفية وJUnit XML لخادم CI. ويمكن لـ Playwright Test كتابة JSON أيضًا.',
        'Jeder Runner hat eingebaute Reporter. Mehrere können gleichzeitig laufen: ein kurzer für das Terminal und JUnit XML für den CI-Server. Playwright Test kann auch JSON schreiben.'),
    say('lab2', 'Lab 2', 'An HTML report shows the error, a screenshot at failure and the trace. Playwright Test has one built in, pytest uses pytest-html, and Java teams often use ExtentReports with a TestNG listener.',
        'HTML report error, failure के समय का screenshot और trace दिखाती है। Playwright Test में यह built-in है, pytest pytest-html इस्तेमाल करता है, और Java teams अक्सर TestNG listener के साथ ExtentReports इस्तेमाल करती हैं।',
        'HTML report error, failure ಸಮಯದ screenshot ಮತ್ತು trace ತೋರಿಸುತ್ತದೆ. Playwright Test ನಲ್ಲಿ built-in, pytest pytest-html ಬಳಸುತ್ತದೆ, Java teams ಹೆಚ್ಚಾಗಿ TestNG listener ಜೊತೆ ExtentReports ಬಳಸುತ್ತವೆ.',
        'HTML report error, failure ସମୟର screenshot ଓ trace ଦେଖାଏ। Playwright Test ରେ ଏହା built-in, pytest pytest-html ବ୍ୟବହାର କରେ, ଏବଂ Java teams ପ୍ରାୟ TestNG listener ସହ ExtentReports ବ୍ୟବହାର କରନ୍ତି।',
        'يعرض تقرير HTML الخطأ ولقطة عند الفشل والأثر. لدى Playwright Test واحد مدمج، ويستخدم pytest الإضافة pytest-html، وتستخدم فرق Java غالبًا ExtentReports مع مستمع TestNG.',
        'Ein HTML-Bericht zeigt den Fehler, einen Screenshot beim Fehlschlag und den Trace. Playwright Test hat einen eingebaut, pytest nutzt pytest-html, und Java-Teams nutzen oft ExtentReports mit einem TestNG-Listener.'),
    say('lab3', 'Lab 3', 'Allure Report looks the same for every language. An adapter writes raw results, and the Allure command line builds the report, with labels, steps and screenshots.',
        'Allure Report हर भाषा के लिए एक जैसी दिखती है। Adapter raw results लिखता है, और Allure command line labels, steps और screenshots के साथ report बनाती है।',
        'Allure Report ಪ್ರತಿ ಭಾಷೆಗೂ ಒಂದೇ ರೀತಿ ಕಾಣುತ್ತದೆ. Adapter raw results ಬರೆಯುತ್ತದೆ, Allure command line labels, steps ಮತ್ತು screenshots ಜೊತೆ report ಕಟ್ಟುತ್ತದೆ.',
        'Allure Report ପ୍ରତି ଭାଷା ପାଇଁ ସମାନ ଦେଖାଯାଏ। Adapter raw results ଲେଖେ, ଏବଂ Allure command line labels, steps ଓ screenshots ସହ report ତିଆରି କରେ।',
        'يبدو Allure Report متماثلًا في كل لغة. يكتب المحوّل النتائج الخام، ويبني سطر أوامر Allure التقرير مع الوسوم والخطوات واللقطات.',
        'Allure Report sieht in jeder Sprache gleich aus. Ein Adapter schreibt Rohergebnisse, und die Allure-Kommandozeile baut daraus den Bericht mit Labels, Schritten und Screenshots.'),
    say('lab4', 'Lab 4', 'A custom reporter is a class or a set of hooks that the runner calls at the start, after each test and at the end. It describes the run but never changes whether it passed.',
        'Custom reporter एक class या hooks का सेट है जिसे runner शुरू में, हर test के बाद और आख़िर में बुलाता है। यह run का वर्णन करता है पर उसके pass होने को कभी नहीं बदलता।',
        'Custom reporter ಒಂದು class ಅಥವಾ hooks ಗುಂಪು, runner ಆರಂಭದಲ್ಲಿ, ಪ್ರತಿ test ನಂತರ ಮತ್ತು ಕೊನೆಯಲ್ಲಿ ಕರೆಯುತ್ತದೆ. ಇದು run ವಿವರಿಸುತ್ತದೆ, pass ಆಗಿದೆಯೇ ಎಂಬುದನ್ನು ಬದಲಿಸುವುದಿಲ್ಲ.',
        'Custom reporter ଏକ class ବା hooks ର ସେଟ୍, ଯାହାକୁ runner ଆରମ୍ଭରେ, ପ୍ରତି test ପରେ ଓ ଶେଷରେ ଡାକେ। ଏହା run ବର୍ଣ୍ଣନା କରେ କିନ୍ତୁ pass ହେବା କେବେ ବଦଳାଏ ନାହିଁ।',
        'المراسل المخصص صنف أو مجموعة خطافات يستدعيها المشغّل في البداية وبعد كل اختبار وفي النهاية. يصف التشغيل ولا يغيّر أبدًا نجاحه أو فشله.',
        'Ein eigener Reporter ist eine Klasse oder eine Reihe von Hooks, die der Runner am Anfang, nach jedem Test und am Ende aufruft. Er beschreibt den Lauf, ändert aber nie, ob er bestanden hat.'),
    say('lab5', 'Lab 5', 'Shards each write a blob report, and merge-reports turns them into one HTML report. CI servers read many JUnit XML files at once, so Python and Java results need no merging.',
        'हर shard blob report लिखता है, और merge-reports उन्हें एक HTML report बनाता है। CI servers कई JUnit XML files एक साथ पढ़ते हैं, इसलिए Python और Java results को जोड़ना नहीं पड़ता।',
        'ಪ್ರತಿ shard blob report ಬರೆಯುತ್ತದೆ, merge-reports ಅವನ್ನು ಒಂದು HTML report ಮಾಡುತ್ತದೆ. CI servers ಹಲವು JUnit XML files ಒಟ್ಟಿಗೆ ಓದುತ್ತವೆ, ಆದ್ದರಿಂದ Python ಮತ್ತು Java results ಸೇರಿಸಬೇಕಿಲ್ಲ.',
        'ପ୍ରତି shard blob report ଲେଖେ, ଏବଂ merge-reports ସେଗୁଡିକୁ ଗୋଟିଏ HTML report କରେ। CI servers ଅନେକ JUnit XML files ଏକାସାଙ୍ଗରେ ପଢନ୍ତି, ତେଣୁ Python ଓ Java results ଯୋଡିବା ଦରକାର ନାହିଁ।',
        'يكتب كل جزء تقرير blob، ويحوّلها merge-reports إلى تقرير HTML واحد. وتقرأ خوادم CI ملفات JUnit XML كثيرة معًا، فلا تحتاج نتائج Python وJava إلى دمج.',
        'Jeder Shard schreibt einen Blob-Bericht, und merge-reports macht daraus einen HTML-Bericht. CI-Server lesen viele JUnit-XML-Dateien auf einmal, daher müssen Python- und Java-Ergebnisse nicht zusammengeführt werden.'),
    say('choose', 'Choosing', 'Start with the built-in reports and JUnit XML. Add Allure or ExtentReports when people outside the test team need to read the results.',
        'Built-in reports और JUnit XML से शुरू करें। जब test team के बाहर के लोगों को results पढ़ने हों, तब Allure या ExtentReports जोड़ें।',
        'Built-in reports ಮತ್ತು JUnit XML ನಿಂದ ಆರಂಭಿಸಿ. Test team ಹೊರಗಿನವರು results ಓದಬೇಕಾದಾಗ Allure ಅಥವಾ ExtentReports ಸೇರಿಸಿ.',
        'Built-in reports ଓ JUnit XML ରୁ ଆରମ୍ଭ କରନ୍ତୁ। Test team ବାହାରର ଲୋକଙ୍କୁ results ପଢିବାକୁ ପଡିଲେ Allure ବା ExtentReports ଯୋଡନ୍ତୁ।',
        'ابدأ بالتقارير المدمجة وJUnit XML. وأضف Allure أو ExtentReports حين يحتاج أشخاص من خارج فريق الاختبار إلى قراءة النتائج.',
        'Beginne mit den eingebauten Berichten und JUnit XML. Füge Allure oder ExtentReports hinzu, wenn Menschen außerhalb des Testteams die Ergebnisse lesen müssen.'),
    say('practice', 'Playground labs', 'In the labs you fix the test the reports flagged, and make a weak check precise so that a failure in the report says exactly what was wrong.',
        'Labs में आप reports में दिखे test को ठीक करते हैं, और एक कमज़ोर check को सटीक बनाते हैं ताकि report में failure ठीक-ठीक बताए कि क्या गलत था।',
        'Labs ನಲ್ಲಿ reports ತೋರಿಸಿದ test ಸರಿಪಡಿಸುತ್ತೀರಿ, ಮತ್ತು ದುರ್ಬಲ check ಅನ್ನು ನಿಖರ ಮಾಡುತ್ತೀರಿ, ಆಗ report ನಲ್ಲಿ failure ಏನು ತಪ್ಪಾಯಿತು ಎಂದು ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳುತ್ತದೆ.',
        'Labs ରେ ଆପଣ reports ଦେଖାଇଥିବା test ଠିକ୍ କରନ୍ତି, ଏବଂ ଏକ ଦୁର୍ବଳ check କୁ ସଠିକ କରନ୍ତି ଯେପରି report ରେ failure କଣ ଭୁଲ ଥିଲା ଠିକ୍ କହେ।',
        'في المختبرات تصلح الاختبار الذي أشارت إليه التقارير، وتجعل فحصًا ضعيفًا دقيقًا كي يقول الفشل في التقرير ما الخطأ بالضبط.',
        'In den Labs reparierst du den Test, den die Berichte gemeldet haben, und machst eine schwache Prüfung genau, damit ein Fehler im Bericht genau sagt, was falsch war.'),
]

QUIZ = [
    quiz(1, 'Which report format do almost all CI servers read?', ['PDF', 'JUnit XML', 'Markdown', 'CSV'], 1,
         'An XML format.', 'JUnit XML is read by Jenkins, GitLab, Azure DevOps, GitHub actions and more.'),
    quiz(1, 'Which Playwright Test reporter prints one character per test?', ['list', 'dot', 'html', 'json'], 1,
         'Very short.', 'dot prints a dot for a passed test and F for a failed one.'),
    quiz(1, 'Which pytest option writes JUnit XML?', ['--html', '--junitxml', '--xml', '-rA'], 1,
         'junit plus xml.', '--junitxml=path writes the XML file.'),
    quiz(1, 'What makes a failure in a report quick to understand?', ['more colours', 'the error, a screenshot at failure and a trace', 'a longer test name', 'running it again'], 1,
         'Evidence.', 'With the error, the screenshot and the trace, you can often see the cause without rerunning.'),
    quiz(2, 'What does pytest-playwright add to a pytest-html report by itself?', ['nothing', 'the screenshot, video and trace link it kept for a failed test', 'an Allure link', 'a PDF'], 1,
         'Its artifacts.', 'pytest-playwright 0.10 adds the screenshot, video and trace link it kept to pytest-html.'),
    quiz(2, 'Why does the Java EvidenceListener take the screenshot in onTestFailure?', ['it is faster', 'TestNG calls it before @AfterMethod, while the page is still open', 'Allure requires it', 'for parallel runs'], 1,
         'Order of calls.', 'onTestFailure runs before the @AfterMethod that closes the context, so the page still shows the failure.'),
    quiz(2, 'Which folder does each Allure adapter write?', ['allure-report', 'raw results such as allure-results', 'playwright-report', 'target/site'], 1,
         'Raw first.', 'Adapters write raw results, and allure generate builds the report folder from them.'),
    quiz(2, 'Which TestNG interface builds a report once after the whole suite?', ['ITestListener', 'IReporter', 'IRetryAnalyzer', 'IHookable'], 1,
         'generateReport.', 'IReporter.generateReport receives every result when the suite has finished.'),
    quiz(2, 'Which Playwright Test reporter callback runs after each test?', ['onBegin', 'onTestEnd', 'onEnd', 'onStdOut'], 1,
         'End of a test.', 'onTestEnd receives the test and its result.'),
    quiz(3, 'A custom reporter prints that everything is fine, but a test failed. What exit code does the run end with?', ['0', '1', '2', 'it depends on the reporter'], 1,
         'Reporters only describe.', 'The run still fails with exit code 1, so CI marks it red.'),
    quiz(3, 'How do you get one HTML report from four Playwright Test shards?', ['run html on each and zip them', 'write blob reports, then npx playwright merge-reports --reporter html', 'use the json reporter', 'it is not possible'], 1,
         'blob, then merge.', 'Each shard writes a blob report and merge-reports builds one report from all of them.'),
    quiz(3, 'Why do Python and Java shards not need a merge step for CI counts?', ['they cannot be sharded', 'CI servers read many JUnit XML files at once', 'their reports are already HTML', 'Allure merges them by itself'], 1,
         'Many files.', 'Patterns such as target/surefire-reports/*.xml read every shard\'s file.'),
]

CALC = [
    calc(1, 'A run has 8 tests and 1 fails. How many passed?', 7, '8 - 1', ['8 - 1 = 7']),
    calc(1, 'The JSON stats say expected 7 and unexpected 1. How many tests ran?', 8, '7 + 1', ['7 + 1 = 8']),
    calc(2, 'Allure shows 7 of 8 passed. What is the pass rate in percent, to one decimal place?', 87.5, '7 / 8 × 100', ['7 / 8 = 0.875', '0.875 × 100 = 87.5']),
    calc(2, 'A failure screenshot is 60 KB. A nightly run of 400 tests has 12 failures. How many KB of screenshots is that?', 720, '12 × 60', ['only failures keep screenshots', '12 × 60 = 720']),
    calc(2, 'The test expected ₹1,199 and the page showed ₹1,299. How many rupees apart are they?', 100, '1299 - 1199', ['1299 - 1199 = 100']),
    calc(3, 'Two shards ran 4 and 4 tests. The merged report shows how many tests?', 8, '4 + 4', ['4 + 4 = 8']),
    calc(3, 'A team keeps Allure history for 20 runs, one run a night. How many days of trend does the report show?', 20, 'one run per night', ['20 runs × 1 per night = 20 days']),
    calc(3, 'Video is kept only on failure. With 2 failures out of 50 tests, what percentage of tests keep a video?', 4, '2 / 50 × 100', ['2 / 50 = 0.04', '0.04 × 100 = 4']),
]

LABS = [
    {'id': 'fixprice', 'title': 'Fix the test the report flagged', 'name': 'the desk lamp costs ₹1,299',
     'task': 'The reports showed this test failing because the lamp now costs <b>₹1,299</b>. On <code>/products</code>, check that the card with the test id <code>product-3</code> contains the new price.',
     'goal': 'The check uses the current price and passes.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the desk lamp costs ₹1,299', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('product-3')).toContainText('₹1,199');
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the desk lamp costs ₹1,299', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('product-3')).toContainText('₹1,299');
});'''},
     'hint': 'Only the expected price is out of date. Change <code>₹1,199</code> to <code>₹1,299</code>.',
     'why': 'The report showed the expected and the received value side by side, so the fix took one look. When a product really changes, the test data changes with it.',
     'check': [["/1,299/.test(ctx.code) && !/1,199/.test(ctx.code)", 'The test expects ₹1,299'], ["ctx.url.includes('/products')", 'The products page is open']]},
    {'id': 'precise', 'title': 'Make a weak check precise', 'name': 'the coffee mug costs ₹199',
     'task': 'This test only checks that the words <b>Coffee mug</b> are on the page, so a wrong price would never show up in a report. Check that the card with the test id <code>product-2</code> contains <b>₹199</b>.',
     'goal': 'The check names the card and the price.', 'start': '/products',
     'code': {'ts': '''import { test, expect } from '@playwright/test';

test('the coffee mug costs ₹199', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByText('Coffee mug')).toBeVisible();
});'''},
     'answer': {'ts': '''import { test, expect } from '@playwright/test';

test('the coffee mug costs ₹199', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('product-2')).toContainText('₹199');
});'''},
     'hint': "Use the card: <code>page.getByTestId('product-2')</code>, and check its text with <code>toContainText('₹199')</code>.",
     'why': 'If the price ever changes, this test fails, and the report shows the expected ₹199 next to the price on the page. The old check would have passed and hidden the problem.',
     'check': [["/product-2/.test(ctx.code)", 'The check uses the mug card'], ["/199/.test(ctx.code)", 'The check names the price']]},
]

T = {
    'slug': 'pw-reports', 'title': 'Reporting labs', 'short': 'Reporting labs', 'emoji': '📊', 'module': MODULE, 'minutes': 35,
    'lead': 'Hands-on labs for test reports in TypeScript, JavaScript, Python and Java: built-in reporters and JUnit XML, HTML reports with screenshots and traces, Allure in every language, ExtentReports, your own reporter, and merged reports in CI.',
    'desc': 'Playwright reporting labs in four languages: list, line, dot, html, json, junit, blob and github reporters, pytest --junitxml and pytest-html, Maven Surefire XML, ExtentReports with a TestNG IReporter and listener, Allure Report with allure-playwright, allure-pytest and allure-testng, failure screenshots as evidence, custom reporters with onTestEnd, pytest hooks and ITestListener, and merge-reports for shards.',
    'summary': 'One out of date test failed in every lab, and each report showed it: JUnit XML and JSON counts, the Playwright HTML report, pytest-html and ExtentReports with screenshots, Allure Report in all four languages, a custom summary, and one HTML report merged from two shards.',
    'keywords': ['report', 'reporter', 'reporting', 'Allure', 'ExtentReports', 'Extent', 'pytest-html', 'HTML report', 'JUnit XML', 'JSON', 'custom reporter', 'merge-reports', 'listener', 'evidence'],
    'plain': 'A report is the record of a test run. Machines read the XML to count passes and failures, and people open the HTML report to see the error, the screenshot and the trace of a failed test.',
    'parts': PARTS, 'codes': CODES, 'dg': DG, 'info': INFO, 'real': REAL, 'say': SAY, 'quiz': QUIZ, 'calc': CALC, 'labs': LABS,
}
