---
name: test-debug
description: Execute and debug E2E tests collaboratively with real-time log monitoring. Use when running Playwright or similar E2E tests where both Claude and the user need to observe execution simultaneously - Claude monitors logs while user watches the browser. Supports headed/UI mode execution, log capture, real-time monitoring, screenshot analysis, and collaborative debugging workflows.
---

# E2E Collaborative Testing

Execute E2E tests in collaborative mode where Claude monitors logs in real-time while the user observes the browser execution. Enables simultaneous debugging from both perspectives.

## Quick Start

### Execute Test with Log Capture

```bash
# Terminal 1: Execute test in headed mode with log capture
cd projects/miicel.io
npm run test:e2e -- --project=mercadopago-sandbox tests/e2e/specs/complete-purchase-flow-mercadopago-sandbox.spec.ts --headed --reporter=list,html 2>&1 | tee test-debug.log

# Terminal 2: Monitor logs in real-time (for Claude)
tail -f test-debug.log | grep -E "✓|❌|📍|⏳|Error:|Timeout|Selected|Found"
```

### Execute Test in UI Mode

```bash
# Execute in UI mode (user watches, Claude monitors via logs)
npm run test:e2e:ui -- --project=mercadopago-sandbox tests/e2e/specs/complete-purchase-flow-mercadopago-sandbox.spec.ts 2>&1 | tee test-ui-output.log
```

## Workflow Patterns

### Pattern 1: Headed Mode with Log Capture (Recommended)

**User sees:** Browser window executing test steps  
**Claude sees:** Real-time logs via `test-debug.log`

```bash
# Execute with headed mode
npm run test:e2e -- <test-file> --headed --reporter=list,html 2>&1 | tee test-debug.log

# Claude monitors via:
tail -f test-debug.log | grep -E "✓|❌|📍|⏳|Error:|Timeout"
```

**Benefits:**
- User can see what's happening visually
- Claude can read logs without UI interference
- Screenshots/videos captured automatically on failure
- HTML report generated for post-execution analysis

### Pattern 2: UI Mode with Background Logging

**User sees:** Playwright UI with step-by-step execution  
**Claude sees:** Logs captured to file (may be limited due to UI interactivity)

```bash
# Execute in UI mode with background logging
npm run test:e2e:ui -- <test-file> 2>&1 | tee test-ui-output.log &
```

**Note:** UI mode is interactive and may not capture all logs perfectly. Use headed mode for better log capture.

### Pattern 3: Dual Terminal Monitoring

**Terminal 1:** Test execution  
**Terminal 2:** Real-time log filtering

```bash
# Terminal 1
npm run test:e2e -- <test-file> --headed 2>&1 | tee test-debug.log

# Terminal 2 (run simultaneously)
tail -f test-debug.log | grep -E "✓|❌|📍|⏳|Error:|Timeout|payment|MercadoPago"
```

## Debugging Workflow

### 1. Execute Test

Start test execution with appropriate mode:
- **Headed:** For visual observation + log capture
- **UI:** For step-by-step debugging
- **Headless:** For CI/CD or when visual observation not needed

### 2. Monitor Progress

Claude monitors logs for:
- **Progress indicators:** `✓`, `📍`, `⏳` (success, location, waiting)
- **Errors:** `❌`, `Error:`, `Timeout`
- **Key events:** Payment flows, redirects, form submissions
- **Debug info:** URLs, page titles, element detection

### 3. Analyze Failures

When test fails, check:

**Screenshots:**
```bash
find tests/test-results -name "*.png" -type f -mmin -10 | sort | tail -1 | xargs open
```

**Videos:**
```bash
find tests/test-results -name "*.webm" -type f -mmin -10 | sort | tail -1 | xargs open
```

**Error Context:**
```bash
find tests/test-results -name "error-context.md" -exec cat {} \;
```

**HTML Report:**
```bash
npm run test:e2e:report
# or
open tests/reports/index.html
```

### 4. Collaborative Debugging

**User reports:** What they see in the browser (e.g., "MP page is asking for login", "Form not visible", "Redirect not happening")

**Claude analyzes:** Logs, screenshots, error context to identify root cause

**Solution:** Claude updates test code/helpers based on both perspectives

## Log Patterns to Monitor

### Success Indicators
- `✓ Found form elements` - Elements detected successfully
- `✓ Selected payment method` - Payment method selection worked
- `✓ Redirected to:` - Successful redirect back to platform
- `✓ Successfully redirected back to platform` - Complete redirect flow

### Error Indicators
- `❌ Could not find` - Element not found
- `Error:` - Test error occurred
- `Timeout` - Operation timed out
- `Target page, context or browser has been closed` - Browser closed unexpectedly

### Progress Indicators
- `📍 MercadoPago page loaded:` - Navigation to external service
- `📄 Page title:` - Page identification
- `⏳ Waiting for redirect` - Waiting for async operation

## Scripts

### monitor-test.sh

Real-time log monitor with filtering. See [scripts/monitor-test.sh](scripts/monitor-test.sh) for usage.

```bash
./scripts/monitor-test.sh
```

Monitors `test-debug.log` and highlights important events.

## Common Issues

### Browser Closes Unexpectedly

**Symptom:** `Error: page.title: Target page, context or browser has been closed`

**Solution:** 
- Don't manually close browser during test execution
- Increase timeouts if test is slow
- Check if test is hitting timeout limits

### Logs Not Capturing

**Symptom:** Empty or incomplete log file

**Solution:**
- Use `tee` to capture both stdout and stderr: `2>&1 | tee log.txt`
- Avoid UI mode for critical log capture (use headed instead)
- Check if process is still running: `ps aux | grep playwright`

### Test Hangs

**Symptom:** Test stops progressing, no new logs

**Solution:**
- Check browser window for errors/captchas
- Look for network issues in browser DevTools
- Increase timeouts in test configuration
- Check if external service (e.g., MercadoPago) is blocking automation

## Best Practices

1. **Always capture logs:** Use `tee` to save logs even when watching browser
2. **Use headed mode for collaboration:** Better log capture than UI mode
3. **Monitor key events:** Filter logs for important patterns
4. **Save screenshots on failure:** Automatic with Playwright, review them
5. **Check HTML report:** Comprehensive view of test execution
6. **Share observations:** User reports visual issues, Claude analyzes logs

## References

- **Debug Guide:** See [references/debug-guide.md](references/debug-guide.md) for detailed debugging workflows
- **Playwright Config:** See [references/playwright-patterns.md](references/playwright-patterns.md) for configuration patterns

