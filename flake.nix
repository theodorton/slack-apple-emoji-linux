{
  description = "Slack with Apple emoji instead of Google emoji";

  outputs =
    { self }:
    {
      overlays.default = final: prev: {
        slack = final.callPackage ./default.nix { inherit (prev) slack; };
      };
    };
}
