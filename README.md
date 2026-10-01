# slack-apple-emoji

A Nix overlay that patches the Linux Slack desktop app to show Apple emoji instead of Google emoji.

## Usage

Add the flake as an input and apply the overlay. Slack is unfree, so `allowUnfree` must be enabled.

```nix
{
  inputs.slack-emoji.url = "github:theodorton/slack-emoji"; # or "path:/path/to/slack-emoji"

  outputs = { nixpkgs, slack-emoji, ... }: {
    nixosConfigurations.<host> = nixpkgs.lib.nixosSystem {
      modules = [
        ({ pkgs, ... }: {
          nixpkgs.overlays = [ slack-emoji.overlays.default ];
          nixpkgs.config.allowUnfree = true;
          environment.systemPackages = [ pkgs.slack ]; # now the patched build
        })
      ];
    };
  };
}
```

The overlay replaces `slack` with a build named `slack-apple-emoji`. The flake has no inputs of its own, so it always patches your nixpkgs' version of Slack.

Without flakes:

```nix
pkgs.callPackage ./default.nix { }
```

### Without Nix

You only need Python 3. Quit Slack completely, then patch `app.asar` in place. With the `.deb` and `.rpm` packages it is in `/usr/lib/slack/resources/`:

```sh
cd /usr/lib/slack/resources
sudo cp app.asar app.asar.orig
python3 /path/to/patch-asar.py app.asar.orig /tmp/app.asar /path/to/apple-emoji.cjs
sudo cp /tmp/app.asar app.asar
```

Always patch from the unmodified archive. The patcher refuses an archive it has already patched. To undo, copy `app.asar.orig` back. Slack updates replace `app.asar`, so run it again after each update, and make a fresh `app.asar.orig` first. The Flatpak and Snap packages are read-only, so this doesn't work with them.

## How it works

Slack loads emoji images from its CDN, from paths like
`production-standard-emoji-assets/15.0/google-medium/1f44d.png`. The same images exist under `apple-*`.

- `apple-emoji.cjs` runs in Slack's main process and redirects every `google-*` emoji request to the matching `apple-*` one, in every session.
- `patch-asar.py` adds that script to `resources/app.asar` and makes `dist/boot.bundle.cjs` load it first. It doesn't rebuild the archive: it adds the two changed files at the end and updates the archive's index, so `app.asar.unpacked` (the native modules) keeps working.
- `default.nix` runs the patcher in `postInstall` on nixpkgs' `slack`.

## Disclaimer

This patches a proprietary app and is not affiliated with or endorsed by Slack. Use it at your own risk, and read the source before you run it.

## License

MIT. See [LICENSE](LICENSE). This covers only the files in this repo, not Slack.
