# How to Ignore Files and Folders

This guide explains how to configure Intelephense Watcher to ignore specific files, folders, or patterns when reporting diagnostics.

## Quick Start

1. Create a file named `intelephense.json` in your project root
2. Add an `ignore` array with glob patterns:

```json
{
  "ignore": [
    "vendor/**",
    "node_modules/**"
  ]
}
```

3. Run Intelephense Watcher - matched files will be excluded from diagnostics

## Configuration File

### Location

The configuration file must be named `intelephense.json` and placed in your project root directory (the same directory you pass to `start.bat`).

```
my-project/
  intelephense.json    <-- Config file here
  src/
  vendor/
  tests/
```

### Schema

```json
{
  "ignore": [
    "pattern1",
    "pattern2"
  ]
}
```

The `ignore` key accepts an array of glob patterns as strings.

## Pattern Types

### Directory Patterns

Ignore entire directories and all their contents:

```json
{
  "ignore": [
    "vendor/**",
    "node_modules/**",
    "storage/**",
    "cache/**"
  ]
}
```

The `**` wildcard matches any files and subdirectories recursively.

### Specific Subdirectories

Ignore specific subdirectories while keeping parent directories:

```json
{
  "ignore": [
    "tests/fixtures/**",
    "tests/data/**",
    "src/legacy/**"
  ]
}
```

### File Extension Patterns

Ignore files by extension anywhere in the project:

```json
{
  "ignore": [
    "**/*.generated.php",
    "**/*.backup.php",
    "**/*.min.js"
  ]
}
```

### Specific Files

Ignore specific files by path:

```json
{
  "ignore": [
    "src/legacy/old_code.php",
    "config/deprecated.php"
  ]
}
```

### Root-Level Files

Ignore files only at the project root:

```json
{
  "ignore": [
    "bootstrap.php",
    "config.php"
  ]
}
```

## Common Use Cases

### Laravel Project

```json
{
  "ignore": [
    "vendor/**",
    "node_modules/**",
    "storage/**",
    "bootstrap/cache/**",
    "public/build/**"
  ]
}
```

### Symfony Project

```json
{
  "ignore": [
    "vendor/**",
    "var/**",
    "node_modules/**",
    "public/bundles/**"
  ]
}
```

### WordPress Project

```json
{
  "ignore": [
    "wp-admin/**",
    "wp-includes/**",
    "wp-content/plugins/**",
    "wp-content/themes/*/vendor/**"
  ]
}
```

### Test Fixtures

Ignore test data files that intentionally contain errors:

```json
{
  "ignore": [
    "tests/fixtures/**",
    "tests/data/**",
    "tests/stubs/**"
  ]
}
```

### Generated Code

Ignore auto-generated files:

```json
{
  "ignore": [
    "**/*.generated.php",
    "src/Generated/**",
    "cache/**"
  ]
}
```

## Underscore-Prefixed Symbols

In addition to file-based ignoring, Intelephense Watcher automatically ignores "unused" hints for underscore-prefixed symbols. This is a PHP convention indicating "intentionally unused."

### What Gets Ignored

**Variables:**
```php
$_unused = getValue();  // Ignored: "Symbol '$_unused' is declared but not used."
```

**Methods:**
```php
private function _createTestData(): array
{
    // Ignored: "Method '_createTestData' is declared but never used."
    // Ready for future test cases
}
```

**Functions:**
```php
function _helperForFuture(): void
{
    // Ignored: "Function '_helperForFuture' is declared but never used."
}
```

### Disabling This Behavior

To show all unused symbol warnings including underscore-prefixed ones:

```batch
start.bat . --no-ignore-unused-underscore
```

## Glob Pattern Reference

| Pattern | Matches |
|---------|---------|
| `*` | Any characters except `/` |
| `**` | Any characters including `/` (recursive) |
| `?` | Any single character |
| `[abc]` | Any character in brackets |
| `[!abc]` | Any character not in brackets |

### Examples

| Pattern | Matches | Does Not Match |
|---------|---------|----------------|
| `vendor/**` | `vendor/lib.php`, `vendor/foo/bar.php` | `src/vendor.php` |
| `*.php` | `file.php` (root only) | `src/file.php` |
| `**/*.php` | `file.php`, `src/file.php`, `a/b/c.php` | `file.txt` |
| `tests/fixtures/**` | `tests/fixtures/data.php` | `tests/unit/test.php` |
| `src/[Ll]egacy/**` | `src/Legacy/old.php`, `src/legacy/old.php` | `src/LEGACY/old.php` |

## Troubleshooting

### Config File Not Working

1. Verify the file is named exactly `intelephense.json` (lowercase)
2. Ensure it's in the project root (same directory passed to `start.bat`)
3. Check for valid JSON syntax (no trailing commas, proper quotes)

### Pattern Not Matching

1. Use forward slashes `/` in patterns (even on Windows)
2. For recursive matching, use `**` not just `*`
3. Patterns are relative to the project root

### Invalid JSON

If your config has syntax errors, the watcher will continue without ignoring anything. Check for:
- Missing commas between array items
- Trailing commas after the last item
- Unquoted strings
- Single quotes instead of double quotes

Example of **correct** JSON:
```json
{
  "ignore": [
    "vendor/**",
    "tests/fixtures/**"
  ]
}
```

Example of **incorrect** JSON:
```json
{
  "ignore": [
    'vendor/**',           // Wrong: single quotes
    "tests/fixtures/**",   // Wrong: trailing comma
  ]
}
```

## MCP Server Support

The ignore configuration also works with the MCP server. When you call `get_diagnostics` with a project path, the server automatically loads `intelephense.json` from that project and applies the ignore patterns.
