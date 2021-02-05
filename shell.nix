{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
      black
      python38Packages.django      
      python38Packages.python-dotenv
    ];
}
