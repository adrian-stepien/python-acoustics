{ lib
, buildPythonPackage
, flit-core
, pytest
, numpy
, scipy
, matplotlib
, pandas
, tabulate
, soundfile
, glibcLocales ? null
}:

buildPythonPackage rec {
  pname = "acoustics";
  version = "0.3.0";
  format = "pyproject";

  src = ./.;

  nativeBuildInputs = [
    flit-core
  ];

  propagatedBuildInputs = [ numpy scipy matplotlib pandas tabulate soundfile ];

  nativeCheckInputs = [ pytest ] ++ lib.optional (glibcLocales != null) glibcLocales;

  checkPhase = ''
    LC_ALL="en_US.UTF-8" pytest tests
  '';

  pythonImportsCheck = [ "acoustics" ];

  meta = with lib; {
    description = "Acoustics tools for Python";
    homepage = "https://github.com/adrian-stepien/python-acoustics";
    license = licenses.bsd3;
  };
}
