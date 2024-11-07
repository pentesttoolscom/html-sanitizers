# Use the official Ruby image as the base image
FROM ruby:latest

# Set the working directory in the container
WORKDIR /app

# Copy the Gemfile and Gemfile.lock into the container
COPY Gemfile Gemfile.lock ./

# Install dependencies using Bundler
RUN bundle install

# Copy the application code into the container
COPY . .

# Expose port 8080 to the outside world
EXPOSE 8080

# Command to run the application when the container starts
CMD ["ruby", "app.rb"]
