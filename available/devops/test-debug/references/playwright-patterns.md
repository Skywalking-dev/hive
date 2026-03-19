# Playwright Configuration Patterns

Common Playwright configuration patterns for collaborative E2E testing.

## Timeout Configuration

### Extended Timeouts for External Services

```typescript
// playwright.config.ts
export default defineConfig({
  timeout: 60 * 1000, // 60s per test
  globalTimeout: 15 * 60 * 1000, // 15min total
  
  use: {
    navigationTimeout: 60000, // 60s for navigation
    actionTimeout: 15000, // 15s for actions
  },
  
  projects: [
    {
      name: 'external-service-tests',
      testMatch: /.*external.*\.spec\.ts/,
      timeout: 120 * 1000, // 2min for external service tests
      use: {
        navigationTimeout: 90000,
        actionTimeout: 20000,
      },
    },
  ],
})
```

## Reporter Configuration

### Multiple Reporters

```typescript
reporter: [
  ['list'], // Console output
  ['html', { outputFolder: 'tests/reports' }], // HTML report
  ['json', { outputFile: 'tests/test-results.json' }], // JSON for CI
  ['junit', { outputFile: 'tests/junit.xml' }], // JUnit for CI
]
```

## Screenshot and Video Configuration

### Capture on Failure

```typescript
use: {
  screenshot: 'only-on-failure', // Screenshot when test fails
  video: 'retain-on-failure', // Video when test fails
  trace: 'on-first-retry', // Trace on retry
}
```

### Full Page Screenshots

```typescript
await page.screenshot({ 
  path: 'debug-screenshot.png',
  fullPage: true 
})
```

## Browser Configuration

### Headed Mode

```typescript
// In test
test('my test', async ({ page }) => {
  // Test runs with visible browser
})

// Via CLI
npx playwright test --headed
```

### Multiple Browsers

```typescript
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
]
```

## Network Configuration

### Wait Strategies

```typescript
// Wait for DOM (faster, more reliable)
await page.waitForLoadState('domcontentloaded')

// Wait for network (slower, may timeout)
await page.waitForLoadState('networkidle')

// Wait for specific URL
await page.waitForURL(/checkout\/success/)
```

### Network Interception

```typescript
// Mock API responses
await page.route('/api/checkout', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ success: true }),
  })
})
```

## Error Handling Patterns

### Retry Configuration

```typescript
retries: process.env.CI ? 2 : 0, // Retry on CI only
```

### Custom Error Messages

```typescript
try {
  await page.click(selector)
} catch (error) {
  await page.screenshot({ path: 'error-screenshot.png' })
  throw new Error(`Failed to click ${selector}: ${error.message}`)
}
```

## Environment-Specific Configuration

### Local vs Production

```typescript
projects: [
  {
    name: 'local',
    use: {
      baseURL: 'http://localhost:3000',
    },
  },
  {
    name: 'production',
    use: {
      baseURL: 'https://production.com',
      navigationTimeout: 60000, // Longer for network latency
    },
  },
]
```

## Helper Patterns

### Page Object Model

```typescript
// pages/checkout.page.ts
export class CheckoutPage {
  constructor(private page: Page) {}
  
  async fillForm(data: FormData) {
    await this.page.fill('[data-testid="name"]', data.name)
    await this.page.fill('[data-testid="email"]', data.email)
  }
  
  async submit() {
    await this.page.click('[data-testid="submit"]')
  }
}
```

### Custom Helpers

```typescript
// helpers/payment.helper.ts
export class PaymentHelper {
  constructor(private page: Page) {}
  
  async selectPaymentMethod(method: string) {
    await this.page.click(`[data-testid="payment-${method}"]`)
  }
  
  async fillCardData(card: CardData) {
    // Implementation
  }
}
```

