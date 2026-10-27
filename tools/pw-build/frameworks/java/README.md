# Brainy Shop tests

End to end tests for Brainy Shop, written with Playwright for Java, TestNG and Maven.

## Run them

    mvn test                              # every test, from testng.xml
    mvn test -Dsuite=testng-smoke.xml     # only the smoke group
    mvn test -DbaseUrl=https://staging.example -Dheadless=false

## Folders

- src/main/java/.../config: settings that change between machines
- src/main/java/.../data: test users and products
- src/main/java/.../api: API helpers for fast set up
- src/main/java/.../components: parts that appear on many pages
- src/main/java/.../pages: one page object per screen
- src/test/java/.../base: BaseTest, which opens and closes the browser
- src/test/java/.../tests: test classes, one package per feature
