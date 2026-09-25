# Pubky Passport

**Status on 25 September 2026:** Passport is a public web signer at [passport.pubky.app](https://passport.pubky.app). Pubky App 1.11.0 ships its Google sign-in and sign-up integration, but the UI appears only when a deployment configures `PUBKY_RUNTIME_PASSPORT_URL`. The 1.11.0 release notes tell operators to verify real Google and Homegate journeys before enabling it; production Pubky App keeps it off when that variable is absent.

## How it works

Passport creates the Pubky keypair in the browser. The browser encrypts the secret with AES-256-GCM and stores `passport.json` in Google Drive's app-data area, with a visible backup copy in a Pubky Passport folder. Google receives ciphertext, not the secret.

Recovery is **2-of-2**. Google provides the encrypted file and a fresh Google sign-in. The Passport server verifies the Google ID token and derives the per-account wrapping key with HKDF from its server secret. The browser combines the Drive file and wrapping key and decrypts locally. Neither Google nor Passport alone can recover the key. Homegate has a separate role: it issues the Homeserver signup token for a new Passport identity; it is not the wrapping-key service.

A Google account can restore its catalog of Passport identities on a new browser. Passport keeps identity material in browser storage, supports encrypted recovery-file download, migration to [[Pubky Ring]], and detachment from Google. Detachment deletes the Drive copies and leaves a browser-held, self-managed identity.

## Signing into Pubky apps

A Pubky app opens Passport's `/authorize` popup with an SDK authorization URL. The user reviews the request, Passport posts encrypted approval to the relay, and the Pubky SDK returns the authenticated `Session`. Popup messages report UI outcome; they do not themselves authenticate the app.

## Sources

- [Official Passport README](https://github.com/pubky/pubky-passport)
- [Pubky App 1.11.0](https://github.com/pubky/pubky-app/releases/tag/v1.11.0)
- [Pubky App Passport integration PR #2587](https://github.com/pubky/pubky-app/pull/2587)
- [Passport integration guide](https://github.com/pubky/pubky-passport/blob/main/docs/integration.md)
