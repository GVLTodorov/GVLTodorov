FROM shared/shared:latest as shared
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /release
COPY . .
COPY --from=shared /app /shared
RUN dotnet restore
RUN dotnet publish -o app

FROM mcr.microsoft.com/dotnet/aspnet:7.0 as runtime
ENV ASPNETCORE_ENVIRONMENT=Development
EXPOSE 80
EXPOSE 443

WORKDIR /app
COPY --from=build /release/app ./
COPY --from=shared /app ./
RUN ls -la /
RUN ls -la /app

ENTRYPOINT [ "dotnet", "weather.dll" ]