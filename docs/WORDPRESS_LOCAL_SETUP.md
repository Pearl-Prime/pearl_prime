# WordPress Local Setup

Fastest path for Phoenix Omega on this Mac.

## What this does

- stores the WordPress application password in your macOS Keychain
- keeps site URL and username in a local file: `.env.wordpress.local`
- gives you one command to dry-run the existing WordPress publisher

## One-time setup

Run:

```bash
./scripts/integrations/setup_wordpress_local.sh
```

It will ask for:

- WordPress site URL
- WordPress username
- WordPress application password

The password is stored in Keychain under service `phoenix-omega-wordpress`.

## Open the two pages you need

Run:

```bash
./scripts/integrations/open_wordpress_setup.sh
```

This opens:

- your WordPress profile page, where Application Passwords live
- the Qwen-Agent GitHub Actions secrets page

## Test locally

Run:

```bash
./scripts/integrations/test_wordpress_local.sh
```

This performs a dry-run using the existing publisher:

- loads site URL and username from `.env.wordpress.local`
- loads the app password from macOS Keychain
- validates the environment without posting

## Publish for real later

Draft posting wrapper is included:

```bash
/bin/zsh ./scripts/integrations/post_wordpress_draft_local.sh
```

Or post a draft from an article JSON:

```bash
/bin/zsh ./scripts/integrations/post_wordpress_draft_local.sh artifacts/pearl_news/drafts/article_001.json
```

We can also wire the same values into GitHub Actions secrets after the local test passes.

## Notes

- `.env.wordpress.local` is gitignored.
- The app password is not stored in the repo.
- This only covers WordPress because it is the cleanest working integration already present in this repo.
- Messenger, WhatsApp, WeChat, and iMessage each need separate account/platform setup and cannot be fully auto-created by me.
