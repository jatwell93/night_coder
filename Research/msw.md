#digitall-twin-universe 
# DeepWiki Q&A with Code Context for Repository: mswjs/msw
## Q1
Would this project be an example of a tool that could be used to run thousands of scenarios without costs, rate limits for external dependencies like Slack, Stripe etc.
### Answer
Yes. Mock Service Worker (MSW) intercepts requests at the network level and returns mocked responses, so your application never hits real external services like Slack or Stripe. This means you can run thousands of scenarios locally or in CI without incurring costs or hitting rate limits. MSW works in browsers via Service Workers and in Node.js via low-level interceptors, and you can reuse the same handlers across unit, integration, and E2E tests.
## How MSW avoids costs and rate limits

- Network-level interception: In browsers, MSW uses the Service Worker API to intercept requests after they leave your app. In Node.js, it uses custom interceptors. Either way, the request never reaches the real external API.
- No stubbing of fetch/axios: Because interception happens at the network layer, your application code remains unchanged and unaware of mocking.
- Reusable handlers: Define request handlers once and reuse them across local development, unit, integration, and E2E tests. This scales to thousands of scenarios without additional external calls.

## Example: Mocking Stripe GraphQL API

The following test mocks a Stripe GraphQL mutation without contacting Stripe:

```ts
import { graphql, HttpResponse } from 'msw'
import { setupWorker } from 'msw/browser'

const stripe = graphql.link('https://api.stripe.com/graphql')

const worker = setupWorker(
  stripe.mutation('Payment', ({ variables }) => {
    return HttpResponse.json({
      data: {
        bankAccount: {
          totalFunds: 100 + variables.amount,
        },
      },
    })
  }),
)

await worker.start()
```

The corresponding test asserts the mocked response, confirming no real network call to Stripe occurs.

## Example: Mocking HTTP REST APIs

You can mock any REST endpoint similarly:

```ts
import { http, HttpResponse } from 'msw'
import { setupWorker } from 'msw/browser'

const worker = setupWorker(
  http.get('https://api.stripe.com/v1/checkout/sessions/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      mode: 'payment',
      status: 'open',
    })
  }),
)

await worker.start()
```

This pattern works for Slack, Stripe, or any external service, ensuring zero cost and no rate-limit exposure msw.

## Notes

- MSW also supports response patching via `bypass` if you need to augment real responses selectively msw:1-22 .
- For WebSocket APIs, MSW provides `ws.link` to mock connections without hitting real servers msw:26-39 .

### Citations
**File:** README.md (L19-21)
```markdown
- **Seamless**. A dedicated layer of requests interception at your disposal. Keep your application's code and tests unaware of whether something is mocked or not.
- **Deviation-free**. Request the same production resources and test the actual behavior of your app. Augment an existing API, or design it as you go when there is none.
- **Familiar & Powerful**. Use [Express](https://github.com/expressjs/express)-like routing syntax to intercept requests. Use parameters, wildcards, and regular expressions to match requests, and respond with necessary status codes, headers, cookies, delays, or completely custom resolvers.
```
**File:** README.md (L55-67)
```markdown
In-browser usage is what sets Mock Service Worker apart from other tools. Utilizing the [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API), which can intercept requests for the purpose of caching, Mock Service Worker responds to intercepted requests with your mock definition on the network level. This way your application knows nothing about the mocking.

**Take a look at this quick presentation on how Mock Service Worker functions in a browser:**

[![What is Mock Service Worker?](https://raw.githubusercontent.com/mswjs/msw/main/media/msw-video-thumbnail.jpg)](https://youtu.be/HcQCqboatZk)

### How is it different?

- This library intercepts requests on the network level, which means _after_ they have been performed and "left" your application. As a result, the entirety of your code runs, giving you more confidence when mocking;
- Imagine your application as a box. Every API mocking library out there opens your box and removes the part that does the request, placing a blackbox in its stead. Mock Service Worker leaves your box intact, 1-1 as it is in production. Instead, MSW lives in a separate box next to yours;
- No more stubbing of `fetch`, `axios`, `react-query`, you-name-it;
- You can reuse the same mock definition for the unit, integration, and E2E testing. Did we mention local development and debugging? Yep. All running against the same network description without the need for adapters or bloated configurations.

```
**File:** README.md (L107-112)
```markdown
There's no such thing as Service Workers in Node.js. Instead, MSW implements a [low-level interception algorithm](https://github.com/mswjs/interceptors) that can utilize the very same request handlers you have for the browser. This blends the boundary between environments, allowing you to focus on your network behaviors.

### How is it different?

- Does not stub `fetch`, `axios`, etc. As a result, your tests know _nothing_ about mocking;
- You can reuse the same request handlers for local development and debugging, as well as for testing. Truly a single source of truth for your network behavior across all environments and all tools.
```
**File:** README.md (L126-147)
```markdown
app.get(
  '/checkout/session',
  server.boundary((req, res) => {
    // Describe the network for this Express route.
    server.use(
      http.get(
        'https://api.stripe.com/v1/checkout/sessions/:id',
        ({ params }) => {
          return HttpResponse.json({
            id: params.id,
            mode: 'payment',
            status: 'open',
          })
        },
      ),
    )

    // Continue with processing the checkout session.
    handleSession(req, res)
  }),
)
```
```
**File:** test/browser/graphql-api/link.mocks.ts (L1-6)
```typescript
import { graphql, HttpResponse } from 'msw'
import { setupWorker } from 'msw/browser'

const github = graphql.link('https://api.github.com/graphql')
const stripe = graphql.link('https://api.stripe.com/graphql')

```
**File:** test/browser/graphql-api/link.mocks.ts (L41-52)
```typescript
  stripe.mutation<PaymentQuery, { amount: number }>(
    'Payment',
    ({ variables }) => {
      return HttpResponse.json({
        data: {
          bankAccount: {
            totalFunds: 100 + variables.amount,
          },
        },
      })
    },
  ),
```
**File:** test/browser/graphql-api/link.test.ts (L56-87)
```typescript
test('mocks a GraphQL mutation to the Stripe GraphQL API', async ({
  loadExample,
  query,
}) => {
  await loadExample(LINK_EXAMPLE)

  const res = await query('https://api.stripe.com/graphql', {
    query: gql`
      mutation Payment($amount: Int!) {
        bankAccount {
          totalFunds
        }
      }
    `,
    variables: {
      amount: 350,
    },
  })

  const headers = await res.allHeaders()
  const body = await res.json()

  expect(res.status()).toBe(200)
  expect(headers).toHaveProperty('content-type', 'application/json')
  expect(body).toEqual({
    data: {
      bankAccount: {
        totalFunds: 450,
      },
    },
  })
})
```
**File:** test/browser/rest-api/response-patching.mocks.ts (L1-22)
```typescript
import { http, HttpResponse, bypass } from 'msw'
import { setupWorker } from 'msw/browser'

const worker = setupWorker(
  http.get('*/user', async ({ request }) => {
    const originalResponse = await fetch(bypass(request.url))
    const body = await originalResponse.json()

    return HttpResponse.json(
      {
        name: body.name,
        location: body.location,
        mocked: true,
      },
      {
        headers: {
          'X-Source': 'msw',
        },
      },
    )
  }),

```
**File:** test/node/ws-api/ws.server.connect.test.ts (L26-39)
```typescript
it('does not connect to the actual server by default', async () => {
  const serverConnectionListener = vi.fn()
  const mockConnectionListener = vi.fn()

  originalServer.once('connection', serverConnectionListener)
  server.use(service.addEventListener('connection', mockConnectionListener))

  new WebSocket(originalServer.url)

  await vi.waitFor(() => {
    expect(mockConnectionListener).toHaveBeenCalledTimes(1)
    expect(serverConnectionListener).not.toHaveBeenCalled()
  })
})
```

---

## Official / 2026 links

- [MSW Node integration](https://mswjs.io/docs/integrations/node/) · [MSW 2.0 announcement](https://mswjs.io/blog/introducing-msw-2-0)
- [`findings_dtu_mockoon_keploy_msw.md`](research_overnight_stack_web/findings_dtu_mockoon_keploy_msw.md)
- [LocalStack](https://docs.localstack.cloud/getting-started/installation/) · [Playwright Docker](https://playwright.dev/docs/docker) — [`findings_gap_dtu_localstack_browserless.md`](research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md)
