# E2E Test Debugging Guide

Comprehensive guide for debugging E2E tests collaboratively.

## Execution Modes

### Headed Mode (Recommended for Collaboration)

```bash
npm run test:e2e -- <test-file> --headed --reporter=list,html 2>&1 | tee test-debug.log
```

**When to use:**
- User needs to see browser execution
- Claude needs to monitor logs
- Debugging visual issues
- Testing user interactions

**Benefits:**
- Full log capture
- Visual observation
- Automatic screenshots/videos on failure
- HTML report generation

### UI Mode

```bash
npm run test:e2e:ui -- <test-file>
```

**When to use:**
- Step-by-step debugging
- Inspecting elements
- Manual test execution control
- Learning test flow

**Limitations:**
- Limited log capture (interactive mode)
- May not work well with background processes

### Headless Mode

```bash
npm run test:e2e -- <test-file>
```

**When to use:**
- CI/CD pipelines
- Quick test runs
- When visual observation not needed

## Log Analysis

### Key Log Patterns

**Navigation:**
```
📍 MercadoPago page loaded: <URL>
📄 Page title: <Title>
```

**Success:**
```
✓ Found form elements on MP page
✓ Selected payment method with selector: <selector>
✓ Redirected to: <URL>
```

**Errors:**
```
❌ Could not find MP card field
Error: <error message>
Timeout: <operation> timed out
```

**Waiting:**
```
⏳ Waiting for redirect back to platform...
```

### Filtering Logs

**Success events only:**
```bash
grep -E "✓|Success" test-debug.log
```

**Errors only:**
```bash
grep -E "❌|Error:|Failed|Timeout" test-debug.log
```

**Payment flow:**
```bash
grep -iE "payment|mercadopago|checkout|mp" test-debug.log
```

**Progress tracking:**
```bash
grep -E "📍|📄|⏳" test-debug.log
```

## Debugging Common Issues

### Element Not Found

**Symptoms:**
- `❌ Could not find <element>`
- `Error: locator.isVisible: Timeout`

**Debug steps:**
1. Check screenshot: `find tests/test-results -name "*.png" | tail -1 | xargs open`
2. Verify selector in browser DevTools
3. Check if element loads asynchronously
4. Increase timeout if needed
5. Try alternative selectors

**Solution patterns:**
- Add wait for element: `await page.waitForSelector(selector, { timeout: 10000 })`
- Use more specific selector
- Check if element is in iframe
- Verify page fully loaded

### Timeout Errors

**Symptoms:**
- `TimeoutError: page.waitForURL: Timeout`
- `TimeoutError: page.waitForLoadState: Timeout`

**Debug steps:**
1. Check current URL: Look for `📍` logs
2. Verify network connectivity
3. Check if external service is slow
4. Review timeout values in config

**Solution patterns:**
- Increase timeout: `timeout: 60000` (60s)
- Use `domcontentloaded` instead of `networkidle`
- Add explicit waits for slow operations
- Check for blocking elements (captchas, modals)

### Browser Closed Unexpectedly

**Symptoms:**
- `Error: Target page, context or browser has been closed`
- Test stops mid-execution

**Debug steps:**
1. Verify user didn't close browser manually
2. Check for crashes in browser console
3. Review memory usage
4. Check for timeout that closed browser

**Solution patterns:**
- Add page closure check: `if (page.isClosed()) throw error`
- Increase global timeout
- Check for memory leaks
- Verify test doesn't exceed time limits

### Redirect Not Happening

**Symptoms:**
- `⏳ Waiting for redirect` but never completes
- Test hangs waiting for URL change

**Debug steps:**
1. Check current URL in logs
2. Verify redirect URL is correct
3. Check if external service requires manual action
4. Look for "Volver al sitio" button

**Solution patterns:**
- Click redirect button if present
- Verify redirect URL format
- Check if redirect happens in iframe
- Add fallback timeout with error message

## Artifact Analysis

### Screenshots

**Location:** `tests/test-results/**/*.png`

**When to check:**
- Test fails
- Element not found
- Unexpected page state

**How to view:**
```bash
# Latest screenshot
open $(find tests/test-results -name "*.png" -type f -mmin -10 | sort | tail -1)

# All recent screenshots
find tests/test-results -name "*.png" -type f -mmin -10
```

### Videos

**Location:** `tests/test-results/**/*.webm`

**When to check:**
- Understanding test flow
- Seeing what happened before failure
- Debugging timing issues

**How to view:**
```bash
# Latest video
open $(find tests/test-results -name "*.webm" -type f -mmin -10 | sort | tail -1)
```

### HTML Reports

**Location:** `tests/reports/index.html`

**When to check:**
- Post-execution analysis
- Sharing results
- Comprehensive test overview

**How to view:**
```bash
npm run test:e2e:report
# or
open tests/reports/index.html
```

### Error Context

**Location:** `tests/test-results/**/error-context.md`

**Contains:**
- Error message
- Stack trace
- Page state at failure
- Network requests

**How to view:**
```bash
find tests/test-results -name "error-context.md" -exec cat {} \;
```

## Collaborative Debugging Workflow

### 1. User Observation

User watches browser and reports:
- What page is showing
- What's happening visually
- Any errors in browser console
- Unexpected behavior

### 2. Claude Log Analysis

Claude monitors logs and identifies:
- Test progress
- Error locations
- Timeout points
- Missing elements

### 3. Combined Analysis

Both perspectives combined:
- User: "MP page shows login form"
- Claude: "Logs show redirect to MP but no form detection"
- Solution: Add login handling or use different MP account

### 4. Code Updates

Claude updates test code based on findings:
- Add missing waits
- Fix selectors
- Handle edge cases
- Improve error messages

### 5. Re-test

Repeat process until test passes or issue is resolved.

## Best Practices

1. **Always capture logs:** Use `tee` for dual output
2. **Use headed mode:** Better for collaboration than UI mode
3. **Monitor key events:** Filter logs for important patterns
4. **Save artifacts:** Screenshots/videos help debug
5. **Share observations:** User and Claude communicate findings
6. **Iterate quickly:** Fix issues and re-test immediately
7. **Document patterns:** Note what works for future tests

