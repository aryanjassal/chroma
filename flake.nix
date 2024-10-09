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
          buildInputs = with python.pkgs; [
            pip
            black
            isort
            lupa
            pywal
            setuptools
          ];
          shellHook = ''
            export PIP_PREFIX=$(pwd)/pip_packages
            export PYTHONPATH=$PIP_PREFIX/lib/python${python.pythonVersion}/site-packages:$PYTHONPATH
            export PATH=$PIP_PREFIX/bin:$PATH

            mkdir -p $PIP_PREFIX
            mkdir -p tmp
            pip install -e .
          '';
        };

        packages.default = python.pkgs.buildPythonPackage {
          pname = "chroma";
          version = "0.3.7";
          src = ./.;
          propagatedBuildInputs = with python.pkgs; [ lupa pywal ];
          buildInputs = [ python.pkgs.setuptools ]; 
        };
      });
}
