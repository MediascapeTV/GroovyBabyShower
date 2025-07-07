{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.pandas
    pkgs.python311Packages.jinja2
    pkgs.python311Packages.uvicorn
  ];
}
