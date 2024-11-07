FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o server
ENTRYPOINT ["/app/server"]
