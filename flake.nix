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
          buildInputs = with pkgs; with python.pkgs; [
            pip
            black
            isort
            lupa
            setuptools
            imagemagick
          ];
          shellHook = ''
            export PIP_PREFIX=$(pwd)/pip_packages
            export PYTHONPATH=$PIP_PREFIX/lib/python${python.pythonVersion}/site-packages:$PYTHONPATH
            export PYTHONPATH=$(pwd):$PYTHONPATH
            export PATH=$PIP_PREFIX/bin:$PATH

            mkdir -p $PIP_PREFIX
            mkdir -p tmp
            pip install -e .
          '';
        };

        packages.default = python.pkgs.buildPythonPackage {
          pname = "chroma";
          version = "0.6.0";
          src = ./.;
          propagatedBuildInputs = with pkgs; with python.pkgs; [ lupa imagemagick ];
          buildInputs = [ python.pkgs.setuptools ]; 
        };
      });
}
