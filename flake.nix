{
  description = "Dynamic color scheme updater";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
      in {
        devShells.default = pkgs.mkShell {
          name = "chroma";
          buildInputs = with python.pkgs; [ pip black isort lupa pywal ];
        };
      });
}
