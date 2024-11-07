# Build stage
FROM maven:3.8-openjdk-17-slim AS build
WORKDIR /app
# Copy pom.xml and source code
COPY pom.xml .
COPY src ./src
# Build the application
RUN mvn clean package -DskipTests

# Run stage
FROM openjdk:17-jdk-slim
WORKDIR /app
# Copy the built JAR from build stage
COPY --from=build /app/target/html-sanitizer-0.0.1-SNAPSHOT.jar html-sanitizer.jar
EXPOSE 80
ENTRYPOINT ["java", "-jar", "html-sanitizer.jar"]
