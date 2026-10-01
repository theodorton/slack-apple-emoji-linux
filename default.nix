# Slack with Apple emoji instead of Google emoji.
#
#   pkgs.callPackage ./default.nix { }
#
# or through the overlay in flake.nix (overlays.default).
{ slack, python3 }:

slack.overrideAttrs (old: {
  pname = "${old.pname}-apple-emoji";

  nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [ python3 ];

  postInstall = (old.postInstall or "") + ''
    asar=$out/lib/slack/resources/app.asar
    python3 ${./patch-asar.py} $asar app.asar ${./apple-emoji.cjs}
    install -m 444 app.asar $asar
  '';
})
