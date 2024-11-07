FROM mcr.microsoft.com/dotnet/sdk

WORKDIR /app
RUN dotnet new web
RUN dotnet add package HtmlSanitizer --version 8.0.865
COPY app/Program.cs ./Program.cs
COPY app/Properties/ Properties/

ENTRYPOINT dotnet run