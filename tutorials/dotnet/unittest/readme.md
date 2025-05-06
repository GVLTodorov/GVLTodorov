# Report

install the following tools

```
dotnet tool install -g dotnet-coverage
dotnet tool install -g coverlet.console
dotnet tool install -g dotnet-reportgenerator-globaltool
```

open console and go to repository 

```coverlet ./Z.O.UnitTests/bin/Debug/net6.0/Z.*.UnitTests.dll --target "dotnet" --targetargs "test --no-build"```

```dotnet test --collect:"XPlat Code Coverage" --results-directory ./report```

```reportgenerator -reports:".\report\*\coverage.cobertura.xml" -targetdir:"report" -assemblyfilters:"-Name.Of.The.Project" -reporttypes:Html```
