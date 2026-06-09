# Test Doubles & Mocking

## Taxonomy (Meszaros)

| Double | Purpose | Verifies |
|--------|---------|----------|
| **Dummy** | Filler passed but never used | nothing |
| **Stub** | Returns canned data for inputs the SUT reads | nothing (state) |
| **Spy** | Stub that also records how it was called | calls, after the fact |
| **Mock** | Pre-programmed with expected calls; fails if not met | interactions |
| **Fake** | Working lightweight implementation (in-memory DB/repo) | behavior via state |

## Decision guide

Ask: *does the test care about the **value returned** by the collaborator, or the **interaction** with it?*

- Care about a returned **value** the SUT consumes → **stub** (or fake).
- Care that an **interaction happened** (email sent, event published, payment charged) → **mock** or **spy**.
- Collaborator is **stateful** and you'd otherwise write many brittle stubs → **fake** (in-memory implementation).
- Collaborator is irrelevant to this test but required by the signature → **dummy**.

## What to mock vs what NOT to mock

Mock at **architectural boundaries** where the real thing is slow, non-deterministic, or has side effects:
- Network / HTTP clients, external APIs.
- Databases, message queues, caches (prefer a fake/in-memory over deep mocks).
- Clock / time source, random number generators, UUID generators.
- Filesystem, environment, process exit.

Do **NOT** mock:
- The system under test itself (or its private methods).
- Pure functions and value objects — just call them.
- Types you don't own without an adapter (mock your own wrapper instead, then have one integration test for the wrapper).
- Language/standard-library primitives.

## Anti-patterns

- **Over-specified interaction tests:** asserting exact call order/args of internal helpers → breaks on refactor. Assert only the meaningful boundary interaction.
- **Mock returning a mock returning a mock:** deep stub chains signal a design/seam problem; introduce a fake.
- **Tautological test:** the only assertions are `verify(mock).foo()` for a method the test itself wired — proves nothing about real behavior.
- **Leaky global mocks:** patching globally without restoring → cross-test contamination. Always scope/teardown.

## Injecting determinism

- **Time:** inject a `Clock`/`now()` function or use a freezer (`freezegun`, `@sinonjs/fake-timers`/Jest fake timers, `clockwork` in Ruby, libfaketime). Never `datetime.now()` directly in code under test.
- **Randomness:** inject an RNG or seed it; assert on properties, not exact random values.
- **IDs/UUIDs:** inject a generator.

## Per-language tooling

| Language | Mocking | Time | HTTP |
|----------|---------|------|------|
| Python | `unittest.mock`, `pytest-mock` | `freezegun`, `time-machine` | `responses`, `respx`, `httpx` mock transport |
| JS/TS | `jest.fn`/`vi.fn`, `jest.mock`/`vi.mock` | Jest/Vitest fake timers, `@sinonjs/fake-timers` | `msw`, `nock` |
| Go | hand-written fakes + interfaces, `gomock`, `testify/mock` | inject `clock` interface, `github.com/jonboulle/clockwork` | `httptest.Server` |
| Java | Mockito, EasyMock | `Clock.fixed`, `java-time` injection | WireMock, MockWebServer |
| Ruby | RSpec mocks, `minitest/mock` | `timecop`, `ActiveSupport::Testing::TimeHelpers` | WebMock, VCR |
| C#/.NET | Moq, NSubstitute, FakeItEasy | `TimeProvider` (NET 8), inject `IClock` | `HttpMessageHandler` fake, WireMock.Net |
| Rust | `mockall`, trait objects + fakes | inject clock trait | `wiremock`, `httpmock` |

## Go idiom note

Go's culture favors small interfaces and hand-written fakes over mock frameworks. Define a narrow interface at the consumer, pass a struct fake in tests. Reach for `gomock` only when interaction verification is genuinely needed.
