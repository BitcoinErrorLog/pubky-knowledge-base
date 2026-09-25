# Pubky Passport

**Status on 25 September 2026:** [Pubky Passport 1.0.0](https://github.com/pubky/pubky-passport) shipped on 19 September. Pubky App 1.11.0 ships Continue with Google on the landing, sign-in, and onboarding Join surfaces, but the integration is gated by `PUBKY_RUNTIME_PASSPORT_URL` and is off in production until a real Google sign-up is verified against the intended Passport and Homegate deployment.

## How it works

Passport creates a Pubky identity in the browser after Google sign-in. The browser encrypts `passport.json` with AES-256-GCM and stores it in the user's Google Drive. Homegate derives the wrapping key server-side with HKDF and hands it out only for a fresh Google ID token. Recovery is therefore 2-of-2: Google and Passport are both required, and neither can recover the identity alone. Homegate's Google verification endpoint is the only endpoint Passport speaks to.

Passport 1.0.0 also ships a multi-identity catalog, password-protected backup download, migration to [[PubkyRing|Pubky Ring]], guided Google detachment, and Homeserver record republishing.

## Signing into Pubky apps

Pubky App opens Passport at `/authorize#d=` and polls the relay. Only the Pubky SDK `Session` authenticates the user. The integration adds `/onboarding/join` and redesigned landing and sign-in surfaces.

## Sources

- [Official Passport repository](https://github.com/pubky/pubky-passport)
- [Pubky App 1.11.0](https://github.com/pubky/pubky-app/releases/tag/v1.11.0)
- [Pubky App Passport integration PR #2587](https://github.com/pubky/pubky-app/pull/2587)
