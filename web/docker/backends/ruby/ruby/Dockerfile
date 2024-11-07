# Use the official Ruby image as the base image
FROM ruby:latest
# Set the working directory in the container
WORKDIR /app
# Copy the application code into the container
COPY . .
# Install dependencies using Bundler
RUN bundle install
# Expose port 80 to the outside world
EXPOSE 80
# Command to run the application when the container starts
CMD ["ruby", "app.rb"]
