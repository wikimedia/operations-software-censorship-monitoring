# Changelog

## 0.1.1 (2020-04-02)

**Added**

- Allow remote connections to `metadb` in case a user does not have a local
  copy. We do this by explicitly passing the connection parameters to
  `psycopg2` using the values from the updated `cescout.cfg` file.

**Fixed**

- Assume UTC and not the local timezone for the current time (in case the
  `until` argument is not passed).

## 0.1.0 (2020-03-02)

**Notes**

Initial release of the cescout project.

**Changed**

- Package the individual censorship monitoring scripts into one package,
  cescout.
