FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR app
COPY . .
RUN dotnet restore
RUN dotnet publish -o /app
RUN ls -la /
RUN ls -la /app