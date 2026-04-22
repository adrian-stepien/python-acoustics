{
  description = "Acoustics tools for Python.";

  inputs.nixpkgs.url = "nixpkgs/nixpkgs-unstable";
  inputs.utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, utils }: let
    attribute = "acoustics";
    inherit (nixpkgs) lib;

    overlay = final: prev: {
      pythonPackagesOverrides = (prev.pythonPackagesOverrides or []) ++ [
        (python-final: python-prev: {
          "${attribute}" = python-final.callPackage ./. {};
        })
      ];
    };
  in {
    overlays = {
      default = overlay;
    };
  } // (utils.lib.eachSystem [ "x86_64-linux" ] (system: let
    pkgs = import nixpkgs {
      inherit system;
      overlays = [
        overlay
      ];
    };
    python = pkgs.python3;
    pkg = python.pkgs."${attribute}";
  in rec {
    packages = {
      "${attribute}" = pkg;
      default = pkg;
    };

    devShells = {
      default = pkgs.mkShell {
        packages = [
          python
          pkg
        ] ++ lib.optionals (pkgs ? uv) [
          pkgs.uv
        ] ++ lib.optionals (pkgs ? ruff) [
          pkgs.ruff
        ];

        shellHook = ''
          export PYTHONPATH="$PWD:$PYTHONPATH"
        '';
      };
    };

    checks = {
      default = pkg;
      "${attribute}" = pkg;
    };
  }));
}
